import math
import sys
from collections import defaultdict, deque
from pathlib import Path

from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from CORE.atlas_local_osm_reader import AtlasLocalOSMReader
from CORE.atlas_scale_engine import AtlasScaleEngine
from CORE.atlas_coordinate_engine import AtlasCoordinateEngine
from CORE.atlas_castle_shell_triangulator import (
    AtlasCastleShellTriangulator,
)
from CORE.atlas_castle_shell_height_profiler import (
    AtlasCastleShellHeightProfiler,
)

PBF_PATH = PROJECT_ROOT / "Data/OSM/rumeli-hisari-test.osm.pbf"

OUTPUT_PATH = (
    PROJECT_ROOT / "OUTPUT/STL/" "rumeli_hisari_tower_footprint_reconstruction_test.stl"
)

BBOX = (
    41.08050,
    29.04850,
    41.08850,
    29.05950,
)

TARGET_SIZE_MM = 200
BED_WIDTH_MM = 256
BED_DEPTH_MM = 256
MARGIN_MM = 15
Z_SCALE = 5500

POINT_PRECISION = 9
EPSILON = 1e-9
AREA_TOLERANCE = 1e-8

THICKNESS_PERCENTILE = 0.75
INFLUENCE_FACTOR = 0.50

MIN_CLIPPED_AREA_MM2 = 0.005
MIN_OVERLAP_RATIO = 0.025
MAX_REGION_DISTANCE_MM = 0.02
MAX_GROWTH_ROUNDS = 4

RAW_BOTTOM_Z = 0.20
CHORD_BOTTOM_Z = 1.20
ADAPTIVE_BOTTOM_Z = 2.20
PLATE_HEIGHT_MM = 0.60

ADAPTIVE_SAMPLE_COUNT = 20
MIN_CHORD_LENGTH_MM = 0.05

ADAPTIVE_INSET_CHORD_FACTOR = 0.18
ADAPTIVE_INSET_THICKNESS_FACTOR = 0.20
ADAPTIVE_INSET_ARC_FACTOR = 0.25

TANGENT_HANDLE_CHORD_FACTOR = 0.22
TANGENT_INTERIOR_BLEND = 0.40


def point_key(point):
    return (
        round(float(point[0]), POINT_PRECISION),
        round(float(point[1]), POINT_PRECISION),
    )


def edge_key(point_1, point_2):
    return tuple(
        sorted(
            (
                point_key(point_1),
                point_key(point_2),
            )
        )
    )


def percentile(values, ratio):
    ordered = sorted(values)

    if not ordered:
        return 0.0

    position = ratio * (len(ordered) - 1)

    lower_index = int(math.floor(position))
    upper_index = int(math.ceil(position))

    if lower_index == upper_index:
        return ordered[lower_index]

    fraction = position - lower_index

    return ordered[lower_index] * (1.0 - fraction) + ordered[upper_index] * fraction


def geometry_components(geometry):
    if geometry is None or geometry.is_empty:
        return []

    if geometry.geom_type == "Polygon":
        return [geometry]

    if geometry.geom_type == "MultiPolygon":
        return list(geometry.geoms)

    return [
        item for item in getattr(geometry, "geoms", []) if item.geom_type == "Polygon"
    ]


def largest_polygon(geometry):
    components = geometry_components(geometry)

    if not components:
        return None

    return max(
        components,
        key=lambda item: item.area,
    )


def polygon_preserving_reference(
    geometry,
    reference_polygon,
):
    if geometry is None or geometry.is_empty:
        return None

    repaired = geometry

    if not repaired.is_valid:
        repaired = repaired.buffer(0)

    components = geometry_components(repaired)

    if not components:
        return None

    if len(components) == 1:
        return components[0]

    return max(
        components,
        key=lambda component: (
            component.intersection(reference_polygon).area,
            component.area,
        ),
    )


def repair_polygon(geometry):
    if geometry is None or geometry.is_empty:
        return None

    repaired = geometry

    if not repaired.is_valid:
        repaired = repaired.buffer(0)

    polygon = largest_polygon(repaired)

    if polygon is None or polygon.is_empty or polygon.area <= EPSILON:
        return None

    return polygon


def triangle_edges(triangle):
    return (
        (triangle[0], triangle[1]),
        (triangle[1], triangle[2]),
        (triangle[2], triangle[0]),
    )


def connected_components(
    triangle_indices,
    adjacency,
):
    remaining = set(triangle_indices)
    components = []

    while remaining:
        start = next(iter(remaining))

        queue = deque([start])
        remaining.remove(start)

        component = []

        while queue:
            current = queue.popleft()
            component.append(current)

            for neighbor in adjacency[current]:
                if neighbor not in remaining:
                    continue

                remaining.remove(neighbor)
                queue.append(neighbor)

        components.append(component)

    return components


def signed_area(points):
    area = 0.0

    for index in range(len(points)):
        next_index = (index + 1) % len(points)

        x1, y1 = points[index]
        x2, y2 = points[next_index]

        area += x1 * y2
        area -= x2 * y1

    return area / 2.0


def ensure_ccw(points):
    if signed_area(points) < 0:
        return list(reversed(points))

    return list(points)


def ensure_cw(points):
    if signed_area(points) > 0:
        return list(reversed(points))

    return list(points)


def triangle_signed_area(triangle):
    p1, p2, p3 = triangle

    return (
        p1[0] * (p2[1] - p3[1]) + p2[0] * (p3[1] - p1[1]) + p3[0] * (p1[1] - p2[1])
    ) / 2.0


def triangle_normal(triangle):
    p1, p2, p3 = triangle

    ux = p2[0] - p1[0]
    uy = p2[1] - p1[1]
    uz = p2[2] - p1[2]

    vx = p3[0] - p1[0]
    vy = p3[1] - p1[1]
    vz = p3[2] - p1[2]

    nx = uy * vz - uz * vy
    ny = uz * vx - ux * vz
    nz = ux * vy - uy * vx

    length = math.sqrt(nx * nx + ny * ny + nz * nz)

    if length <= EPSILON:
        return (0.0, 0.0, 0.0)

    return (
        nx / length,
        ny / length,
        nz / length,
    )


def add_ring_walls(
    ring,
    bottom_z,
    top_z,
    triangles,
    is_hole,
):
    point_count = len(ring)

    for index in range(point_count):
        next_index = (index + 1) % point_count

        p1 = ring[index]
        p2 = ring[next_index]

        b1 = (
            p1[0],
            p1[1],
            bottom_z,
        )

        b2 = (
            p2[0],
            p2[1],
            bottom_z,
        )

        t1 = (
            p1[0],
            p1[1],
            top_z,
        )

        t2 = (
            p2[0],
            p2[1],
            top_z,
        )

        if is_hole:
            triangles.append((b1, t2, b2))

            triangles.append((b1, t1, t2))

        else:
            triangles.append((b1, b2, t2))

            triangles.append((b1, t2, t1))


def extrude_polygon(
    polygon,
    bottom_z,
    height_mm,
):
    if (
        polygon is None
        or polygon.is_empty
        or not polygon.is_valid
        or polygon.area <= EPSILON
    ):
        return []

    top_z = bottom_z + height_mm

    outer_ring = [
        (
            float(x),
            float(y),
        )
        for x, y in list(polygon.exterior.coords)[:-1]
    ]

    inner_rings = [
        [
            (
                float(x),
                float(y),
            )
            for x, y in list(interior.coords)[:-1]
        ]
        for interior in polygon.interiors
    ]

    outer_ring = ensure_ccw(outer_ring)

    inner_rings = [ensure_cw(ring) for ring in inner_rings]

    flat_triangles = AtlasCastleShellTriangulator.triangulate(
        outer_ring=outer_ring,
        inner_rings=inner_rings,
    )

    triangles = []

    for flat_triangle in flat_triangles:
        p1, p2, p3 = flat_triangle

        if triangle_signed_area(flat_triangle) < 0:
            p2, p3 = p3, p2

        b1 = (
            p1[0],
            p1[1],
            bottom_z,
        )

        b2 = (
            p2[0],
            p2[1],
            bottom_z,
        )

        b3 = (
            p3[0],
            p3[1],
            bottom_z,
        )

        t1 = (
            p1[0],
            p1[1],
            top_z,
        )

        t2 = (
            p2[0],
            p2[1],
            top_z,
        )

        t3 = (
            p3[0],
            p3[1],
            top_z,
        )

        triangles.append((t1, t2, t3))

        triangles.append((b3, b2, b1))

    add_ring_walls(
        ring=outer_ring,
        bottom_z=bottom_z,
        top_z=top_z,
        triangles=triangles,
        is_hole=False,
    )

    for hole in inner_rings:
        add_ring_walls(
            ring=hole,
            bottom_z=bottom_z,
            top_z=top_z,
            triangles=triangles,
            is_hole=True,
        )

    return triangles


def write_ascii_stl(
    output_path,
    triangles,
):
    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="ascii",
    ) as stl_file:
        stl_file.write("solid " "atlas_tower_footprint_" "reconstruction\n")

        for triangle in triangles:
            normal = triangle_normal(triangle)

            stl_file.write(
                "  facet normal "
                f"{normal[0]:.9e} "
                f"{normal[1]:.9e} "
                f"{normal[2]:.9e}\n"
            )

            stl_file.write("    outer loop\n")

            for vertex in triangle:
                stl_file.write(
                    "      vertex "
                    f"{vertex[0]:.9e} "
                    f"{vertex[1]:.9e} "
                    f"{vertex[2]:.9e}\n"
                )

            stl_file.write("    endloop\n")

            stl_file.write("  endfacet\n")

        stl_file.write("endsolid " "atlas_tower_footprint_" "reconstruction\n")


def point_distance(
    point_1,
    point_2,
):
    return math.hypot(
        float(point_2[0]) - float(point_1[0]),
        float(point_2[1]) - float(point_1[1]),
    )


def normalize_vector(
    vector_x,
    vector_y,
):
    length = math.hypot(
        vector_x,
        vector_y,
    )

    if length <= EPSILON:
        return None

    return (
        vector_x / length,
        vector_y / length,
    )


def mean_point(points):
    if not points:
        return (0.0, 0.0)

    return (
        sum(float(point[0]) for point in points) / len(points),
        sum(float(point[1]) for point in points) / len(points),
    )


def straight_chord_closure(
    outer_arc,
):
    if len(outer_arc) < 2:
        return []

    return [
        outer_arc[-1],
        outer_arc[0],
    ]


def cubic_bezier_point(
    start,
    control_1,
    control_2,
    end,
    t,
):
    one_minus_t = 1.0 - t

    x = (
        one_minus_t**3 * float(start[0])
        + 3.0 * one_minus_t**2 * t * float(control_1[0])
        + 3.0 * one_minus_t * t**2 * float(control_2[0])
        + t**3 * float(end[0])
    )

    y = (
        one_minus_t**3 * float(start[1])
        + 3.0 * one_minus_t**2 * t * float(control_1[1])
        + 3.0 * one_minus_t * t**2 * float(control_2[1])
        + t**3 * float(end[1])
    )

    return (x, y)


def constrained_tangent_closure(
    outer_arc,
    base_thickness,
):
    if len(outer_arc) < 4:
        return {
            "points": (straight_chord_closure(outer_arc)),
            "inset_depth": 0.0,
            "handle_length": 0.0,
        }

    closure_start = outer_arc[-1]
    closure_end = outer_arc[0]

    start_previous = outer_arc[-2]
    end_next = outer_arc[1]

    chord_length = point_distance(
        closure_start,
        closure_end,
    )

    if chord_length <= MIN_CHORD_LENGTH_MM:
        return {
            "points": [
                closure_start,
                closure_end,
            ],
            "inset_depth": 0.0,
            "handle_length": 0.0,
        }

    chord_midpoint = (
        (float(closure_start[0]) + float(closure_end[0])) / 2.0,
        (float(closure_start[1]) + float(closure_end[1])) / 2.0,
    )

    arc_center = mean_point(outer_arc[1:-1])

    interior_direction = normalize_vector(
        arc_center[0] - chord_midpoint[0],
        arc_center[1] - chord_midpoint[1],
    )

    if interior_direction is None:
        return {
            "points": (straight_chord_closure(outer_arc)),
            "inset_depth": 0.0,
            "handle_length": 0.0,
        }

    arc_center_distance = point_distance(
        chord_midpoint,
        arc_center,
    )

    inset_depth = min(
        chord_length * ADAPTIVE_INSET_CHORD_FACTOR,
        base_thickness * ADAPTIVE_INSET_THICKNESS_FACTOR,
        arc_center_distance * ADAPTIVE_INSET_ARC_FACTOR,
    )

    inset_target = (
        chord_midpoint[0] + interior_direction[0] * inset_depth,
        chord_midpoint[1] + interior_direction[1] * inset_depth,
    )

    raw_start_tangent = normalize_vector(
        float(closure_start[0]) - float(start_previous[0]),
        float(closure_start[1]) - float(start_previous[1]),
    )

    raw_end_tangent = normalize_vector(
        float(closure_end[0]) - float(end_next[0]),
        float(closure_end[1]) - float(end_next[1]),
    )

    if raw_start_tangent is None or raw_end_tangent is None:
        return {
            "points": (straight_chord_closure(outer_arc)),
            "inset_depth": 0.0,
            "handle_length": 0.0,
        }

    start_to_target = normalize_vector(
        inset_target[0] - float(closure_start[0]),
        inset_target[1] - float(closure_start[1]),
    )

    end_to_target = normalize_vector(
        inset_target[0] - float(closure_end[0]),
        inset_target[1] - float(closure_end[1]),
    )

    if start_to_target is None or end_to_target is None:
        return {
            "points": (straight_chord_closure(outer_arc)),
            "inset_depth": 0.0,
            "handle_length": 0.0,
        }

    blended_start_tangent = normalize_vector(
        raw_start_tangent[0] * (1.0 - TANGENT_INTERIOR_BLEND)
        + start_to_target[0] * TANGENT_INTERIOR_BLEND,
        raw_start_tangent[1] * (1.0 - TANGENT_INTERIOR_BLEND)
        + start_to_target[1] * TANGENT_INTERIOR_BLEND,
    )

    blended_end_tangent = normalize_vector(
        raw_end_tangent[0] * (1.0 - TANGENT_INTERIOR_BLEND)
        + end_to_target[0] * TANGENT_INTERIOR_BLEND,
        raw_end_tangent[1] * (1.0 - TANGENT_INTERIOR_BLEND)
        + end_to_target[1] * TANGENT_INTERIOR_BLEND,
    )

    if blended_start_tangent is None or blended_end_tangent is None:
        return {
            "points": (straight_chord_closure(outer_arc)),
            "inset_depth": 0.0,
            "handle_length": 0.0,
        }

    handle_length = chord_length * TANGENT_HANDLE_CHORD_FACTOR

    control_1 = (
        float(closure_start[0]) + blended_start_tangent[0] * handle_length,
        float(closure_start[1]) + blended_start_tangent[1] * handle_length,
    )

    control_2 = (
        float(closure_end[0]) + blended_end_tangent[0] * handle_length,
        float(closure_end[1]) + blended_end_tangent[1] * handle_length,
    )

    control_1 = (
        (control_1[0] + inset_target[0]) / 2.0,
        (control_1[1] + inset_target[1]) / 2.0,
    )

    control_2 = (
        (control_2[0] + inset_target[0]) / 2.0,
        (control_2[1] + inset_target[1]) / 2.0,
    )

    closure_points = []

    for sample_index in range(ADAPTIVE_SAMPLE_COUNT + 1):
        t = sample_index / ADAPTIVE_SAMPLE_COUNT

        closure_points.append(
            cubic_bezier_point(
                start=closure_start,
                control_1=control_1,
                control_2=control_2,
                end=closure_end,
                t=t,
            )
        )

    return {
        "points": closure_points,
        "inset_depth": inset_depth,
        "handle_length": handle_length,
    }


def polygon_from_outer_arc_and_closure(
    outer_arc,
    closure_points,
):
    if len(outer_arc) < 2 or len(closure_points) < 2:
        return None

    coordinates = [
        (
            float(point[0]),
            float(point[1]),
        )
        for point in outer_arc
    ]

    coordinates.extend(
        (
            float(point[0]),
            float(point[1]),
        )
        for point in closure_points[1:-1]
    )

    polygon = Polygon(coordinates)

    return repair_polygon(polygon)


def union_preserving_raw(
    raw_region,
    reconstruction_polygon,
):
    if reconstruction_polygon is None:
        return raw_region

    merged = unary_union(
        [
            raw_region,
            reconstruction_polygon,
        ]
    )

    preserved = polygon_preserving_reference(
        geometry=merged,
        reference_polygon=raw_region,
    )

    if preserved is None:
        return raw_region

    raw_missing_area = raw_region.difference(preserved).area

    if raw_missing_area > AREA_TOLERANCE:
        merged_again = unary_union(
            [
                preserved,
                raw_region,
            ]
        )

        preserved_again = polygon_preserving_reference(
            geometry=merged_again,
            reference_polygon=(raw_region),
        )

        if preserved_again is not None:
            preserved = preserved_again

    return preserved


def pair_overlap_area(regions):
    overlap_area = 0.0

    for first_index in range(len(regions)):
        for second_index in range(
            first_index + 1,
            len(regions),
        ):
            overlap_area += (
                regions[first_index].intersection(regions[second_index]).area
            )

    return overlap_area


def build_raw_regions():
    data = AtlasLocalOSMReader.read(
        str(PBF_PATH),
        BBOX,
    )

    castle = next(
        item
        for item in data.get(
            "castles",
            [],
        )
        if item.get("geometry_type") == "relation"
    )

    xy_scale = AtlasScaleEngine.calculate_xy_scale_from_bbox(
        bbox=BBOX,
        target_size_mm=(TARGET_SIZE_MM),
        bed_width_mm=(BED_WIDTH_MM),
        bed_depth_mm=(BED_DEPTH_MM),
        margin_mm=MARGIN_MM,
        debug=False,
    )

    south, west, _north, _east = BBOX

    coordinate_engine = AtlasCoordinateEngine(
        origin_lat=south,
        origin_lon=west,
        xy_scale=xy_scale,
        z_scale=Z_SCALE,
    )

    osm_outer = coordinate_engine.geometry_to_stl_mm(castle["outer_geometries"][0])

    osm_inners = [
        coordinate_engine.geometry_to_stl_mm(geometry)
        for geometry in castle.get(
            "inner_geometries",
            [],
        )
    ]

    normalized = AtlasCastleShellTriangulator.normalize_rings(
        outer_ring=osm_outer,
        inner_rings=osm_inners,
    )

    outer_ring = normalized["outer_ring"]

    inner_rings = normalized["inner_rings"]

    shell_polygon = Polygon(
        shell=outer_ring,
        holes=inner_rings,
    )

    profile = AtlasCastleShellHeightProfiler.build_profile(
        outer_ring=outer_ring,
        inner_rings=inner_rings,
    )

    flat_triangles = AtlasCastleShellTriangulator.triangulate(
        outer_ring=osm_outer,
        inner_rings=osm_inners,
    )

    point_to_run = {}
    run_indices = {}

    for run_index, (
        start,
        end,
        _length,
    ) in enumerate(
        profile["tower_runs"],
        start=1,
    ):
        indices = []
        current = start

        while True:
            indices.append(current)

            point_to_run[point_key(outer_ring[current])] = run_index

            if current == end:
                break

            current = (current + 1) % len(outer_ring)

        run_indices[run_index] = indices

    records = []

    for triangle_index, triangle in enumerate(flat_triangles):
        votes = []

        for point in triangle:
            run_index = point_to_run.get(point_key(point))

            if run_index is not None:
                votes.append(run_index)

        unique_runs = set(votes)

        if len(unique_runs) > 1:
            category = "cross_run"
            run_index = None

        elif len(votes) == 3:
            category = "pure"
            run_index = votes[0]

        elif len(votes) == 2:
            category = "mixed_2"
            run_index = votes[0]

        elif len(votes) == 1:
            category = "mixed_1"
            run_index = votes[0]

        else:
            category = "wall"
            run_index = None

        polygon = Polygon(triangle)

        records.append(
            {
                "index": (triangle_index),
                "polygon": polygon,
                "category": category,
                "run_index": (run_index),
                "edge_keys": {
                    edge_key(
                        start_point,
                        end_point,
                    )
                    for (
                        start_point,
                        end_point,
                    ) in triangle_edges(triangle)
                },
            }
        )

    edge_to_triangles = defaultdict(list)

    for record in records:
        for current_edge in record["edge_keys"]:
            edge_to_triangles[current_edge].append(record["index"])

    adjacency = defaultdict(set)

    for triangle_indices in edge_to_triangles.values():
        if len(triangle_indices) != 2:
            continue

        first_index, second_index = triangle_indices

        adjacency[first_index].add(second_index)

        adjacency[second_index].add(first_index)

    raw_regions = []
    reconstruction_data = []

    for run_index in range(
        1,
        len(profile["tower_runs"]) + 1,
    ):
        seed_indices = {
            record["index"]
            for record in records
            if (
                record["run_index"] == run_index
                and record["category"]
                in {
                    "pure",
                    "mixed_2",
                }
            )
        }

        if not seed_indices:
            continue

        seed_components = connected_components(
            triangle_indices=(seed_indices),
            adjacency=adjacency,
        )

        seed_components.sort(
            key=lambda component: sum(
                records[index]["polygon"].area for index in component
            ),
            reverse=True,
        )

        active_triangle_indices = set(seed_components[0])

        core_union = unary_union(
            [records[index]["polygon"] for index in active_triangle_indices]
        )

        core_region = largest_polygon(core_union)

        if core_region is None:
            continue

        indices = run_indices[run_index]

        run_points = [outer_ring[index] for index in indices]

        run_thicknesses = [profile["smoothed_thicknesses"][index] for index in indices]

        base_thickness = percentile(
            run_thicknesses,
            THICKNESS_PERCENTILE,
        )

        influence_distance = base_thickness * INFLUENCE_FACTOR

        influence_zone_raw = (
            LineString(run_points)
            .buffer(
                influence_distance,
                cap_style=2,
                join_style=2,
            )
            .intersection(shell_polygon)
        )

        influence_zone = largest_polygon(influence_zone_raw)

        if influence_zone is None:
            continue

        current_region = core_region
        accepted_parts = []
        processed_candidates = set()

        for _growth_round in range(
            1,
            MAX_GROWTH_ROUNDS + 1,
        ):
            candidate_indices = set()

            for active_index in active_triangle_indices:
                for neighbor_index in adjacency[active_index]:
                    if neighbor_index in active_triangle_indices:
                        continue

                    if neighbor_index in processed_candidates:
                        continue

                    candidate_indices.add(neighbor_index)

            round_accepted = 0

            for candidate_index in sorted(candidate_indices):
                processed_candidates.add(candidate_index)

                candidate = records[candidate_index]

                if candidate["category"] == "cross_run":
                    continue

                if (
                    candidate["run_index"] is not None
                    and candidate["run_index"] != run_index
                ):
                    continue

                polygon = candidate["polygon"]

                if polygon.is_empty or not polygon.is_valid or polygon.area <= EPSILON:
                    continue

                clipped = polygon.intersection(influence_zone)

                clipped_polygon = largest_polygon(clipped)

                if clipped_polygon is None:
                    continue

                clipped_area = clipped_polygon.area

                overlap_ratio = clipped_area / max(
                    polygon.area,
                    EPSILON,
                )

                distance_to_region = clipped_polygon.distance(current_region)

                area_ok = clipped_area >= MIN_CLIPPED_AREA_MM2

                ratio_ok = overlap_ratio >= MIN_OVERLAP_RATIO

                touches_region = distance_to_region <= MAX_REGION_DISTANCE_MM

                if not (area_ok and ratio_ok and touches_region):
                    continue

                active_triangle_indices.add(candidate_index)

                accepted_parts.append(clipped_polygon)

                current_region = largest_polygon(
                    unary_union(
                        [
                            core_region,
                            *accepted_parts,
                        ]
                    )
                )

                round_accepted += 1

            if round_accepted == 0:
                break

        raw_region = repair_polygon(current_region)

        if raw_region is None:
            continue

        raw_regions.append(raw_region)

        reconstruction_data.append(
            {
                "run_index": run_index,
                "outer_arc": run_points,
                "base_thickness": (base_thickness),
                "core_region": (core_region),
            }
        )

    return (
        shell_polygon,
        raw_regions,
        reconstruction_data,
    )


def main():
    (
        shell_polygon,
        raw_regions,
        reconstruction_data,
    ) = build_raw_regions()

    chord_regions = []
    adaptive_regions = []
    reports = []

    for (
        raw_region,
        data_item,
    ) in zip(
        raw_regions,
        reconstruction_data,
    ):
        outer_arc = data_item["outer_arc"]

        base_thickness = data_item["base_thickness"]

        core_region = data_item["core_region"]

        chord_closure = straight_chord_closure(outer_arc)

        chord_fill = polygon_from_outer_arc_and_closure(
            outer_arc=outer_arc,
            closure_points=(chord_closure),
        )

        chord_region = union_preserving_raw(
            raw_region=raw_region,
            reconstruction_polygon=(chord_fill),
        )

        adaptive_result = constrained_tangent_closure(
            outer_arc=outer_arc,
            base_thickness=(base_thickness),
        )

        adaptive_candidate = polygon_from_outer_arc_and_closure(
            outer_arc=outer_arc,
            closure_points=(adaptive_result["points"]),
        )

        if adaptive_candidate is None or chord_fill is None:
            constrained_fill = chord_fill

        else:
            constrained_fill_raw = adaptive_candidate.intersection(chord_fill)

            constrained_fill = polygon_preserving_reference(
                geometry=(constrained_fill_raw),
                reference_polygon=(adaptive_candidate),
            )

        adaptive_region = union_preserving_raw(
            raw_region=raw_region,
            reconstruction_polygon=(constrained_fill),
        )

        adaptive_outside_chord = adaptive_region.difference(chord_region).area

        if adaptive_outside_chord > AREA_TOLERANCE or adaptive_region.area > (
            chord_region.area + AREA_TOLERANCE
        ):
            adaptive_region = polygon_preserving_reference(
                geometry=(adaptive_region.intersection(chord_region)),
                reference_polygon=(raw_region),
            )

            if adaptive_region is None:
                adaptive_region = chord_region

        chord_regions.append(chord_region)

        adaptive_regions.append(adaptive_region)

        chord_length = point_distance(
            outer_arc[-1],
            outer_arc[0],
        )

        chord_core_preservation = chord_region.intersection(core_region).area / max(
            core_region.area,
            EPSILON,
        )

        adaptive_core_preservation = adaptive_region.intersection(
            core_region
        ).area / max(
            core_region.area,
            EPSILON,
        )

        raw_missing_from_chord = raw_region.difference(chord_region).area

        raw_missing_from_adaptive = raw_region.difference(adaptive_region).area

        adaptive_outside_chord = adaptive_region.difference(chord_region).area

        area_order_valid = raw_region.area <= (
            adaptive_region.area + AREA_TOLERANCE
        ) and adaptive_region.area <= (chord_region.area + AREA_TOLERANCE)

        reports.append(
            {
                "run_index": (data_item["run_index"]),
                "outer_arc_points": (len(outer_arc)),
                "base_thickness": (base_thickness),
                "chord_length": (chord_length),
                "adaptive_inset_depth": (adaptive_result["inset_depth"]),
                "adaptive_handle_length": (adaptive_result["handle_length"]),
                "raw_area": (raw_region.area),
                "chord_area": (chord_region.area),
                "adaptive_area": (adaptive_region.area),
                "chord_added_area": max(
                    chord_region.area - raw_region.area,
                    0.0,
                ),
                "adaptive_added_area": max(
                    adaptive_region.area - raw_region.area,
                    0.0,
                ),
                "raw_valid": (raw_region.is_valid),
                "chord_valid": (chord_region.is_valid),
                "adaptive_valid": (adaptive_region.is_valid),
                "chord_core_preservation": (chord_core_preservation),
                "adaptive_core_preservation": (adaptive_core_preservation),
                "raw_missing_from_chord": (raw_missing_from_chord),
                "raw_missing_from_adaptive": (raw_missing_from_adaptive),
                "adaptive_outside_chord": (adaptive_outside_chord),
                "area_order_valid": (area_order_valid),
                "adaptive_closure_points": (len(adaptive_result["points"])),
            }
        )

    all_triangles = []

    for region in raw_regions:
        all_triangles.extend(
            extrude_polygon(
                polygon=region,
                bottom_z=(RAW_BOTTOM_Z),
                height_mm=(PLATE_HEIGHT_MM),
            )
        )

    for region in chord_regions:
        all_triangles.extend(
            extrude_polygon(
                polygon=region,
                bottom_z=(CHORD_BOTTOM_Z),
                height_mm=(PLATE_HEIGHT_MM),
            )
        )

    for region in adaptive_regions:
        all_triangles.extend(
            extrude_polygon(
                polygon=region,
                bottom_z=(ADAPTIVE_BOTTOM_Z),
                height_mm=(PLATE_HEIGHT_MM),
            )
        )

    write_ascii_stl(
        output_path=OUTPUT_PATH,
        triangles=all_triangles,
    )

    raw_combined_area = sum(region.area for region in raw_regions)

    chord_combined_area = sum(region.area for region in chord_regions)

    adaptive_combined_area = sum(region.area for region in adaptive_regions)

    print("")
    print("=" * 92)
    print("ATLAS TOWER FOOTPRINT " "CONSTRAINED RECONSTRUCTION " "DIAGNOSTIC REPORT")
    print("=" * 92)

    print(f"Tower regions                 : " f"{len(raw_regions)}")

    print(f"Raw combined area             : " f"{raw_combined_area:.6f} mm²")

    print(f"Chord combined area           : " f"{chord_combined_area:.6f} mm²")

    print(f"Adaptive combined area        : " f"{adaptive_combined_area:.6f} mm²")

    print(
        f"Combined area order valid     : "
        f"{raw_combined_area <= adaptive_combined_area + AREA_TOLERANCE <= chord_combined_area + AREA_TOLERANCE}"
    )

    print(
        f"Raw shell share               : "
        f"{raw_combined_area / shell_polygon.area * 100.0:.2f}%"
    )

    print(
        f"Raw pair overlap              : " f"{pair_overlap_area(raw_regions):.9f} mm²"
    )

    print(
        f"Chord pair overlap            : "
        f"{pair_overlap_area(chord_regions):.9f} mm²"
    )

    print(
        f"Adaptive pair overlap         : "
        f"{pair_overlap_area(adaptive_regions):.9f} mm²"
    )

    print(
        f"Raw layer Z                   : "
        f"{RAW_BOTTOM_Z:.2f}–"
        f"{RAW_BOTTOM_Z + PLATE_HEIGHT_MM:.2f} mm"
    )

    print(
        f"Chord layer Z                 : "
        f"{CHORD_BOTTOM_Z:.2f}–"
        f"{CHORD_BOTTOM_Z + PLATE_HEIGHT_MM:.2f} mm"
    )

    print(
        f"Adaptive layer Z              : "
        f"{ADAPTIVE_BOTTOM_Z:.2f}–"
        f"{ADAPTIVE_BOTTOM_Z + PLATE_HEIGHT_MM:.2f} mm"
    )

    print(f"Total STL triangles           : " f"{len(all_triangles)}")

    print(f"Output                        : " f"{OUTPUT_PATH}")

    for report in reports:
        print("")
        print(f"Tower run " f"{report['run_index']}")

        print(f"Outer arc points              : " f"{report['outer_arc_points']}")

        print(f"Base thickness                : " f"{report['base_thickness']:.6f} mm")

        print(f"Chord length                  : " f"{report['chord_length']:.6f} mm")

        print(
            f"Adaptive inset depth          : "
            f"{report['adaptive_inset_depth']:.6f} mm"
        )

        print(
            f"Adaptive handle length        : "
            f"{report['adaptive_handle_length']:.6f} mm"
        )

        print(f"Raw area                      : " f"{report['raw_area']:.6f} mm²")

        print(f"Adaptive-final area           : " f"{report['adaptive_area']:.6f} mm²")

        print(f"Chord-closed area             : " f"{report['chord_area']:.6f} mm²")

        print(
            f"Adaptive added area           : "
            f"{report['adaptive_added_area']:.6f} mm²"
        )

        print(
            f"Chord added area              : " f"{report['chord_added_area']:.6f} mm²"
        )

        print(f"Area order valid              : " f"{report['area_order_valid']}")

        print(
            f"Raw / adaptive / chord valid  : "
            f"{report['raw_valid']} / "
            f"{report['adaptive_valid']} / "
            f"{report['chord_valid']}"
        )

        print(
            f"Chord core preservation       : "
            f"{report['chord_core_preservation'] * 100.0:.6f}%"
        )

        print(
            f"Adaptive core preservation    : "
            f"{report['adaptive_core_preservation'] * 100.0:.6f}%"
        )

        print(
            f"Raw missing from chord        : "
            f"{report['raw_missing_from_chord']:.9f} mm²"
        )

        print(
            f"Raw missing from adaptive     : "
            f"{report['raw_missing_from_adaptive']:.9f} mm²"
        )

        print(
            f"Adaptive outside chord        : "
            f"{report['adaptive_outside_chord']:.9f} mm²"
        )

        print(
            f"Adaptive closure points       : " f"{report['adaptive_closure_points']}"
        )

    print("=" * 92)


if __name__ == "__main__":
    main()
