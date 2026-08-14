from __future__ import annotations

import json
import math
from pathlib import Path

from shapely.geometry import shape, Point, Polygon
from shapely import constrained_delaunay_triangles
from shapely.ops import unary_union

from CORE.providers.atlas_srtm_provider import AtlasSRTMProvider
from CORE.atlas_wall_collection_product_builder import (
    AtlasWallCollectionProductBuilder,
)
from CORE.atlas_wall_frame_spec import AtlasWallFrameSpec
from CORE.atlas_label_plate_spec import AtlasLabelPlateSpec
from CORE.atlas_label_text_spec import AtlasLabelTextSpec
from CORE.atlas_product_color_preview_renderer import (
    AtlasProductColorPreviewRenderer,
)
from CORE.atlas_product_color_preview_obj_exporter import (
    AtlasProductColorPreviewOBJExporter,
)
from CORE.atlas_product_preview_material_profile import (
    AtlasProductPreviewMaterialProfile,
)
from EXPORT.atlas_stl_writer import AtlasSTLWriter
from scipy.spatial import Delaunay


ISLAND_GEOJSON = Path(
    "OUTPUT/SEYCHELLES/seychelles_premium_archipelago_v1.geojson"
)

SEA_OUTPUT = Path(
    "OUTPUT/SEYCHELLES/seychelles_premium_archipelago_v1_SEA.stl"
)

ISLAND_OUTPUT = Path(
    "OUTPUT/SEYCHELLES/seychelles_premium_archipelago_v1_ISLAND_RELIEF.stl"
)

PRODUCT_OUTPUT = Path(
    "OUTPUT/SEYCHELLES/"
    "seychelles_premium_archipelago_v1_WALL_COLLECTION_170mm.stl"
)

MULTICOLOR_DIR = Path(
    "OUTPUT/SEYCHELLES/seychelles_premium_archipelago_v1_multicolor"
)

FRAME_OUTPUT = MULTICOLOR_DIR / "SEYCHELLES_FRAME_BLACK.stl"
SEA_COLOR_OUTPUT = MULTICOLOR_DIR / "SEYCHELLES_SEA_BLUE.stl"
ISLAND_COLOR_OUTPUT = MULTICOLOR_DIR / "SEYCHELLES_ISLAND_GREEN.stl"

SCENE_SIZE_MM = 150.0
ARCHIPELAGO_TARGET_SPAN_MM = 140.0

SEA_THICKNESS_MM = 1.6
ISLAND_BASE_Z_MM = 1.6
ISLAND_BASE_THICKNESS_MM = 0.8

RELIEF_HEIGHT_MM = 9.0

COAST_SIMPLIFY_DEGREES = 0.0015

CENTER_LAT = -4.54167040
CENTER_LON = 55.57813080


def _rectangle_slab(width_mm, height_mm, z0, z1):
    hx = width_mm / 2.0
    hy = height_mm / 2.0

    b = (
        (-hx, -hy, z0),
        ( hx, -hy, z0),
        ( hx,  hy, z0),
        (-hx,  hy, z0),
    )

    t = tuple((x, y, z1) for x, y, _ in b)

    triangles = [
        (b[0], b[2], b[1]),
        (b[0], b[3], b[2]),
        (t[0], t[1], t[2]),
        (t[0], t[2], t[3]),
    ]

    for i in range(4):
        j = (i + 1) % 4
        triangles.extend(
            (
                (b[i], b[j], t[j]),
                (b[i], t[j], t[i]),
            )
        )

    return {
        "type": "seychelles_sea_slab",
        "triangles": triangles,
    }



def _translate_mesh(mesh, dx, dy, dz=0.0):
    return {
        **mesh,
        "triangles": [
            tuple(
                (
                    float(x) + dx,
                    float(y) + dy,
                    float(z) + dz,
                )
                for x, y, z in triangle
            )
            for triangle in mesh["triangles"]
        ],
    }


def main():
    collection = json.loads(
        ISLAND_GEOJSON.read_text(encoding="utf-8")
    )

    features = collection.get("features", [])

    island_polygons = []

    for feature in features:
        geometry = shape(feature["geometry"]).simplify(
            COAST_SIMPLIFY_DEGREES,
            preserve_topology=True,
        )

        if geometry.is_empty or not geometry.is_valid:
            continue

        island_polygons.append(geometry)

    if not island_polygons:
        raise RuntimeError(
            "Invalid Seychelles archipelago geometry"
        )

    archipelago = unary_union(island_polygons)

    if archipelago.is_empty or not archipelago.is_valid:
        raise RuntimeError(
            "Invalid Seychelles archipelago geometry"
        )

    cos_lat = math.cos(math.radians(CENTER_LAT))

    raw_points = [
        point
        for polygon in island_polygons
        for point in list(polygon.exterior.coords)[:-1]
    ]

    projected = [
        (
            (lon - CENTER_LON) * cos_lat,
            lat - CENTER_LAT,
        )
        for lon, lat in raw_points
    ]

    min_x = min(x for x, _ in projected)
    max_x = max(x for x, _ in projected)
    min_y = min(y for _, y in projected)
    max_y = max(y for _, y in projected)

    span_x_units = max_x - min_x
    span_y_units = max_y - min_y

    xy_factor = (
        ARCHIPELAGO_TARGET_SPAN_MM
        / max(span_x_units, span_y_units)
    )

    def lonlat_to_xy(lon, lat):
        x = (
            (lon - CENTER_LON)
            * cos_lat
            * xy_factor
        )
        y = (
            (lat - CENTER_LAT)
            * xy_factor
        )
        return x, y

    provider = AtlasSRTMProvider(debug=False)

    terrain_min_m = 0.0
    terrain_max_m = 830.0
    terrain_span_m = terrain_max_m - terrain_min_m

    height_cache = {}

    # Light DEM smoothing for premium terrain presentation.
    # Offsets correspond roughly to one active terrain-grid cell.
    west, south, east, north = archipelago.bounds

    smoothing_lon_step = (
        (east - west) / (281 - 1)
    )
    smoothing_lat_step = (
        (north - south) / (113 - 1)
    )

    smoothing_kernel = (
        (-1, -1, 1.0),
        ( 0, -1, 2.0),
        ( 1, -1, 1.0),
        (-1,  0, 2.0),
        ( 0,  0, 4.0),
        ( 1,  0, 2.0),
        (-1,  1, 1.0),
        ( 0,  1, 2.0),
        ( 1,  1, 1.0),
    )

    def smoothed_height(lat, lon):
        key = (
            round(float(lat), 8),
            round(float(lon), 8),
        )

        if key in height_cache:
            return height_cache[key]

        weighted_sum = 0.0
        weight_sum = 0.0

        for dx, dy, weight in smoothing_kernel:
            sample_lon = (
                lon
                + dx * smoothing_lon_step
            )
            sample_lat = (
                lat
                + dy * smoothing_lat_step
            )

            sample = provider.get_height(
                sample_lat,
                sample_lon,
            )

            if sample is None:
                continue

            weighted_sum += (
                max(0.0, float(sample))
                * weight
            )
            weight_sum += weight

        if weight_sum <= 0.0:
            height = 0.0
        else:
            height = weighted_sum / weight_sum

        height_cache[key] = height

        return height

    def top_z(lat, lon):
        height = smoothed_height(
            lat,
            lon,
        )

        relief = (
            (height - terrain_min_m)
            / terrain_span_m
            * RELIEF_HEIGHT_MM
        )

        return (
            ISLAND_BASE_Z_MM
            + ISLAND_BASE_THICKNESS_MM
            + relief
        )

    # Build one globally conforming triangulation from:
    # - the real simplified Seychelles coastlines
    # - regularly sampled interior SRTM points
    #
    # A single triangulation avoids duplicate cell-boundary edges
    # and the non-manifold vertical seams produced by per-cell
    # clipping/triangulation.
    GRID_COLS = 281
    GRID_ROWS = 113

    west, south, east, north = archipelago.bounds

    interior_points = []

    for row in range(1, GRID_ROWS - 1):
        lat = (
            south
            + (north - south)
            * row
            / (GRID_ROWS - 1)
        )

        for col in range(1, GRID_COLS - 1):
            lon = (
                west
                + (east - west)
                * col
                / (GRID_COLS - 1)
            )

            point = Point(lon, lat)

            if archipelago.contains(point):
                interior_points.append(point)

    # Constrained triangulation of the Seychelles archipelago polygons.
    # This keeps the real coastline as a mandatory boundary and
    # avoids branched/free Delaunay boundary topology.
    # Premium terrain tessellation:
    # combine the real Seychelles coastlines with a regular interior
    # sampling field, then build one Delaunay terrain network.
    #
    # This avoids the long radial triangle strips produced by
    # uniformly subdividing large constrained source triangles.
    GRID_COLS = 281
    GRID_ROWS = 113

    west, south, east, north = archipelago.bounds

    sample_lonlat = []

    # Preserve the real simplified coastline.
    for lon, lat in raw_points:
        sample_lonlat.append(
            (
                float(lon),
                float(lat),
            )
        )

    # Add approximately 1 mm physical interior terrain samples.
    for row in range(1, GRID_ROWS - 1):
        lat = (
            south
            + (north - south)
            * row
            / (GRID_ROWS - 1)
        )

        for col in range(1, GRID_COLS - 1):
            lon = (
                west
                + (east - west)
                * col
                / (GRID_COLS - 1)
            )

            if archipelago.contains(
                Point(lon, lat)
            ):
                sample_lonlat.append(
                    (
                        float(lon),
                        float(lat),
                    )
                )

    # Stable de-duplication before QHull.
    unique_lonlat = []
    seen = set()

    for lon, lat in sample_lonlat:
        key = (
            round(lon, 9),
            round(lat, 9),
        )

        if key in seen:
            continue

        seen.add(key)
        unique_lonlat.append(
            (
                lon,
                lat,
            )
        )

    physical_xy = [
        lonlat_to_xy(lon, lat)
        for lon, lat in unique_lonlat
    ]

    delaunay = Delaunay(
        physical_xy
    )

    top_triangles = []
    rejected_triangles = 0

    for simplex in delaunay.simplices:
        lonlat_triangle = [
            unique_lonlat[int(index)]
            for index in simplex
        ]

        footprint = Polygon(
            lonlat_triangle
        )

        if (
            footprint.is_empty
            or footprint.area <= 1e-14
            or not archipelago.covers(footprint)
        ):
            rejected_triangles += 1
            continue

        top_triangle = []

        for lon, lat in lonlat_triangle:
            x, y = lonlat_to_xy(
                lon,
                lat,
            )

            top_triangle.append(
                (
                    x,
                    y,
                    top_z(lat, lon),
                )
            )

        top_triangles.append(
            tuple(top_triangle)
        )

    print(
        "Terrain sample points:",
        len(unique_lonlat),
    )
    print(
        "Delaunay top triangles:",
        len(top_triangles),
    )
    print(
        "Rejected outside triangles:",
        rejected_triangles,
    )

    if not top_triangles:
        raise RuntimeError(
            "Seychelles archipelago relief produced no triangles"
        )

    # Seychelles is a true multi-island archipelago.
    # Do NOT keep only the largest connected component here;
    # that single-island cleanup would incorrectly delete
    # legitimate secondary islands.

    print(
        "Archipelago mode:",
        "preserve all disconnected island components",
    )

    # Separate disconnected island components that touch at only
    # one XY vertex. Such point contacts create four side faces on
    # one vertical edge and therefore a non-manifold print solid.
    from collections import defaultdict

    def mesh_edge_key(first, second):
        first_key = (
            round(float(first[0]), 7),
            round(float(first[1]), 7),
        )
        second_key = (
            round(float(second[0]), 7),
            round(float(second[1]), 7),
        )
        return tuple(sorted((first_key, second_key)))

    edge_owners = defaultdict(list)

    for triangle_index, triangle in enumerate(top_triangles):
        for first, second in (
            (triangle[0], triangle[1]),
            (triangle[1], triangle[2]),
            (triangle[2], triangle[0]),
        ):
            edge_owners[
                mesh_edge_key(first, second)
            ].append(triangle_index)

    adjacency = [
        set()
        for _ in top_triangles
    ]

    for triangle_indices in edge_owners.values():
        if len(triangle_indices) != 2:
            continue

        first_index, second_index = triangle_indices
        adjacency[first_index].add(second_index)
        adjacency[second_index].add(first_index)

    components = []
    unvisited = set(range(len(top_triangles)))

    while unvisited:
        seed = unvisited.pop()
        component = {seed}
        pending = [seed]

        while pending:
            current = pending.pop()

            for neighbor in adjacency[current]:
                if neighbor not in unvisited:
                    continue

                unvisited.remove(neighbor)
                component.add(neighbor)
                pending.append(neighbor)

        components.append(component)

    occupied_vertices = set()
    separated_top_triangles = list(top_triangles)
    separated_component_count = 0

    for component in sorted(
        components,
        key=lambda value: min(value),
    ):
        component_vertices = {
            (
                round(float(point[0]), 7),
                round(float(point[1]), 7),
            )
            for triangle_index in component
            for point in separated_top_triangles[triangle_index]
        }

        if component_vertices & occupied_vertices:
            component_points = [
                point
                for triangle_index in component
                for point in separated_top_triangles[triangle_index]
            ]
            center_x = sum(
                float(point[0])
                for point in component_points
            ) / len(component_points)
            center_y = sum(
                float(point[1])
                for point in component_points
            ) / len(component_points)

            length = (
                center_x * center_x
                + center_y * center_y
            ) ** 0.5

            if length <= 1e-12:
                offset_x = 0.0001
                offset_y = 0.0
            else:
                offset_x = center_x / length * 0.0001
                offset_y = center_y / length * 0.0001

            for triangle_index in component:
                separated_top_triangles[triangle_index] = tuple(
                    (
                        float(x) + offset_x,
                        float(y) + offset_y,
                        float(z),
                    )
                    for x, y, z in (
                        separated_top_triangles[triangle_index]
                    )
                )

            separated_component_count += 1
            component_vertices = {
                (
                    round(float(point[0]), 7),
                    round(float(point[1]), 7),
                )
                for triangle_index in component
                for point in separated_top_triangles[triangle_index]
            }

        occupied_vertices.update(component_vertices)

    top_triangles = separated_top_triangles

    print(
        "Separated point-touching island components:",
        separated_component_count,
    )

    # Use the exact same XY triangulation for the bottom.
    # This keeps internal edges paired and avoids a second,
    # incompatible triangulation.
    bottom_triangles = []

    for triangle in top_triangles:
        bottom_triangles.append(
            (
                (
                    triangle[2][0],
                    triangle[2][1],
                    ISLAND_BASE_Z_MM,
                ),
                (
                    triangle[1][0],
                    triangle[1][1],
                    ISLAND_BASE_Z_MM,
                ),
                (
                    triangle[0][0],
                    triangle[0][1],
                    ISLAND_BASE_Z_MM,
                ),
            )
        )

    # Derive the exact physical boundary from the top mesh,
    # including any coastline edge splits introduced by the
    # sampling grid. This prevents boundary T-junctions.
    from collections import Counter

    def xy_key(point):
        return (
            round(float(point[0]), 7),
            round(float(point[1]), 7),
        )

    def edge_key(a, b):
        aa = xy_key(a)
        bb = xy_key(b)

        if aa <= bb:
            return (aa, bb)

        return (bb, aa)

    edge_counts = Counter()
    edge_points = {}

    for triangle in top_triangles:
        for a, b in (
            (triangle[0], triangle[1]),
            (triangle[1], triangle[2]),
            (triangle[2], triangle[0]),
        ):
            key = edge_key(a, b)
            edge_counts[key] += 1
            edge_points[key] = (a, b)

    side_triangles = []

    for key, count in edge_counts.items():
        if count != 1:
            continue

        a, b = edge_points[key]

        a_bottom = (
            a[0],
            a[1],
            ISLAND_BASE_Z_MM,
        )
        b_bottom = (
            b[0],
            b[1],
            ISLAND_BASE_Z_MM,
        )

        side_triangles.extend(
            (
                (
                    a_bottom,
                    b_bottom,
                    b,
                ),
                (
                    a_bottom,
                    b,
                    a,
                ),
            )
        )

    island_mesh = {
        "type": "seychelles_archipelago_relief",
        "triangles": [
            *top_triangles,
            *bottom_triangles,
            *side_triangles,
        ],
    }

    sea_mesh = _rectangle_slab(
        SCENE_SIZE_MM,
        SCENE_SIZE_MM,
        0.0,
        SEA_THICKNESS_MM,
    )

    SEA_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    AtlasSTLWriter.write(
        meshes=[sea_mesh],
        output_path=SEA_OUTPUT,
        solid_name="SEYCHELLES_PREMIUM_SEA",
    )

    AtlasSTLWriter.write(
        meshes=[island_mesh],
        output_path=ISLAND_OUTPUT,
        solid_name="SEYCHELLES_PREMIUM_ARCHIPELAGO_RELIEF",
    )

    # Wall Collection integration.
    #
    # ProductBuilder expects city-local coordinates from 0..150 mm
    # and then translates them into the centered frame opening.
    city_sea_mesh = _translate_mesh(
        sea_mesh,
        SCENE_SIZE_MM / 2.0,
        SCENE_SIZE_MM / 2.0,
    )
    city_island_mesh = _translate_mesh(
        island_mesh,
        SCENE_SIZE_MM / 2.0,
        SCENE_SIZE_MM / 2.0,
    )

    city_result = {
        "terrain_size_x_mm": SCENE_SIZE_MM,
        "terrain_size_y_mm": SCENE_SIZE_MM,
        "mesh_groups": {
            "waters": [city_sea_mesh],
            "terrain": [city_island_mesh],
        },
    }

    frame_spec = AtlasWallFrameSpec(
        outer_width_mm=170.0,
        outer_height_mm=170.0,
        frame_width_mm=10.0,
    )

    label_plate_spec = AtlasLabelPlateSpec(
        width_mm=118.0,
        height_mm=9.0,
        depth_mm=1.2,
        corner_radius_mm=2.0,
    )

    label_text_spec = AtlasLabelTextSpec(
        primary_text="SEYCHELLEN",
        secondary_text="SILBERHOCHZEIT · 25 JAHRE",
        primary_height_mm=4.2,
        secondary_height_mm=2.8,
        depth_mm=0.6,
        max_width_mm=108.0,
    )

    product = AtlasWallCollectionProductBuilder.build(
        city_result=city_result,
        frame_spec=frame_spec,
        frame_depth_mm=6.0,
        label_plate_spec=label_plate_spec,
        label_text_spec=label_text_spec,
    )

    preview_profile = AtlasProductPreviewMaterialProfile(
        name="SEYCHELLES_ARCHIPELAGO_PREVIEW_V1",
        frame_rgb=(20, 20, 20),
        building_rgb=(245, 243, 237),
        building_wall_rgb=(245, 243, 237),
        building_roof_rgb=(245, 243, 237),
        landmark_rgb=(245, 243, 237),
        terrain_rgb=(73, 105, 58),
        road_rgb=(245, 243, 237),
        green_rgb=(73, 105, 58),
        tree_rgb=(73, 105, 58),
        water_rgb=(70, 140, 180),
        label_plate_rgb=(245, 243, 237),
        label_text_rgb=(20, 20, 20),
    )

    preview_scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=frame_spec,
        frame_depth_mm=6.0,
        material_profile=preview_profile,
        label_plate_spec=label_plate_spec,
        label_text_spec=label_text_spec,
    )

    preview_result = AtlasProductColorPreviewOBJExporter.export(
        scene=preview_scene,
        output_path=(
            "OUTPUT/SEYCHELLES/"
            "seychelles_premium_archipelago_v1_PREVIEW.obj"
        ),
    )

    AtlasSTLWriter.write(
        meshes=product["meshes"],
        output_path=PRODUCT_OUTPUT,
        solid_name="SEYCHELLES_PREMIUM_WALL_COLLECTION_V1",
    )

    # Fast physical color package.
    #
    # All three meshes already use the same centered Wall
    # Collection coordinate system, so they can be imported
    # together in Bambu Studio without manual positioning.
    MULTICOLOR_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    AtlasSTLWriter.write(
        meshes=product["frame_meshes"],
        output_path=FRAME_OUTPUT,
        solid_name="SEYCHELLES_FRAME_BLACK",
    )

    AtlasSTLWriter.write(
        meshes=[sea_mesh],
        output_path=SEA_COLOR_OUTPUT,
        solid_name="SEYCHELLES_SEA_BLUE",
    )

    AtlasSTLWriter.write(
        meshes=[island_mesh],
        output_path=ISLAND_COLOR_OUTPUT,
        solid_name="SEYCHELLES_ISLAND_GREEN",
    )

    label_plate_output = (
        MULTICOLOR_DIR
        / "SEYCHELLES_LABEL_PLATE_WHITE.stl"
    )
    label_text_rings_output = (
        MULTICOLOR_DIR
        / "SEYCHELLES_LABEL_TEXT_BLACK.stl"
    )

    AtlasSTLWriter.write(
        meshes=product["label_plate_meshes"],
        output_path=label_plate_output,
        solid_name="SEYCHELLES_LABEL_PLATE_WHITE",
    )

    AtlasSTLWriter.write(
        meshes=[
            *product["label_text_meshes"],
        ],
        output_path=label_text_rings_output,
        solid_name="SEYCHELLES_LABEL_TEXT_BLACK",
    )

    vertices = [
        p
        for tri in island_mesh["triangles"]
        for p in tri
    ]

    xs = [p[0] for p in vertices]
    ys = [p[1] for p in vertices]
    zs = [p[2] for p in vertices]

    print("=" * 72)
    print("SEYCHELLES PREMIUM ARCHIPELAGO V1")
    print("=" * 72)
    print(f"Coast vertices : {len(raw_points)}")
    print(f"Island width   : {max(xs)-min(xs):.3f} mm")
    print(f"Island height  : {max(ys)-min(ys):.3f} mm")
    print(f"Island Z       : {min(zs):.3f} .. {max(zs):.3f} mm")
    print(f"Top triangles  : {len(top_triangles)}")
    print(f"Total triangles: {len(island_mesh['triangles'])}")
    print(f"Sea STL        : {SEA_OUTPUT}")
    print(f"Island STL     : {ISLAND_OUTPUT}")
    print(f"Product STL    : {PRODUCT_OUTPUT}")
    print(f"Frame STL      : {FRAME_OUTPUT}")
    print(f"Sea STL        : {SEA_COLOR_OUTPUT}")
    print(f"Island STL     : {ISLAND_COLOR_OUTPUT}")
    print(f"Label plate STL: {label_plate_output}")
    print(f"Label text STL : {label_text_rings_output}")
    print(f"Preview OBJ    : {preview_result['obj_path']}")
    print(
        "Product size   : "
        f"{product['outer_width_mm']:.1f} x "
        f"{product['outer_height_mm']:.1f} mm"
    )
    print(
        "Opening        : "
        f"{product['opening_width_mm']:.1f} x "
        f"{product['opening_height_mm']:.1f} mm"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()
