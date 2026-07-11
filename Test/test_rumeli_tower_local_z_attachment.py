import importlib.util
import math
import sys
from pathlib import Path

from shapely.geometry import Polygon

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from CORE.atlas_foundation_first_engine import (
    AtlasFoundationFirstEngine,
)
from CORE.atlas_foundation_sampler import (
    AtlasFoundationSampler,
)
from CORE.atlas_terrain_pipeline import (
    AtlasTerrainPipeline,
)
from CORE.atlas_castle_shell_triangulator import (
    AtlasCastleShellTriangulator,
)

RECONSTRUCTION_TEST_PATH = (
    PROJECT_ROOT / "Test/test_rumeli_tower_footprint_reconstruction.py"
)

OUTPUT_PATH = (
    PROJECT_ROOT / "OUTPUT/STL/" "rumeli_hisari_tower_local_z_attachment_test.stl"
)

FIXED_X_OFFSET_MM = 0.0
LOCAL_X_OFFSET_MM = 30.0

SHELL_HEIGHT_M_DEFAULT = 10.0
MIN_SHELL_HEIGHT_MM = 1.80

FIXED_DISPLAY_Z_OFFSET = 0.0
LOCAL_DISPLAY_Z_OFFSET = 0.0

EPSILON = 1e-9


def load_reconstruction_module():
    spec = importlib.util.spec_from_file_location(
        "atlas_rumeli_reconstruction",
        RECONSTRUCTION_TEST_PATH,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "Reconstruction test module could not be loaded: "
            f"{RECONSTRUCTION_TEST_PATH}"
        )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module


reconstruction = load_reconstruction_module()


def read_positive_float(
    value,
    default,
):
    try:
        parsed = float(value)

    except (
        TypeError,
        ValueError,
    ):
        return float(default)

    if parsed <= 0.0:
        return float(default)

    return parsed


def triangle_signed_area(
    triangle,
):
    p1, p2, p3 = triangle

    return (
        p1[0] * (p2[1] - p3[1]) + p2[0] * (p3[1] - p1[1]) + p3[0] * (p1[1] - p2[1])
    ) / 2.0


def triangle_normal(
    triangle,
):
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
        return (
            0.0,
            0.0,
            0.0,
        )

    return (
        nx / length,
        ny / length,
        nz / length,
    )


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
        stl_file.write("solid atlas_tower_local_z_attachment\n")

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

        stl_file.write("endsolid atlas_tower_local_z_attachment\n")


def translated_point(
    point,
    x_offset,
    z_offset,
):
    return (
        float(point[0]) + x_offset,
        float(point[1]),
        float(point[2]) + z_offset,
    )


def terrain_z_at_point(
    terrain_mesh,
    point,
):
    return AtlasFoundationSampler.terrain_z_at_xy(
        terrain_mesh=terrain_mesh,
        x=float(point[0]),
        y=float(point[1]),
    )


def region_rings(
    region,
):
    outer_ring = [
        (
            float(x),
            float(y),
        )
        for x, y in list(region.exterior.coords)[:-1]
    ]

    inner_rings = [
        [
            (
                float(x),
                float(y),
            )
            for x, y in list(interior.coords)[:-1]
        ]
        for interior in region.interiors
    ]

    return (
        outer_ring,
        inner_rings,
    )


def build_fixed_bottom_cap(
    region,
    terrain_mesh,
    shell_height_mm,
    cap_extra_height_mm,
    x_offset,
    z_offset,
):
    outer_ring, inner_rings = region_rings(region)

    flat_triangles = AtlasCastleShellTriangulator.triangulate(
        outer_ring=outer_ring,
        inner_rings=inner_rings,
    )

    all_points = list(outer_ring)

    for inner_ring in inner_rings:
        all_points.extend(inner_ring)

    terrain_values = [
        terrain_z_at_point(
            terrain_mesh,
            point,
        )
        for point in all_points
    ]

    fixed_bottom_z = max(terrain_values) + shell_height_mm

    flat_top_z = fixed_bottom_z + cap_extra_height_mm

    triangles = []

    for flat_triangle in flat_triangles:
        p1, p2, p3 = flat_triangle

        if triangle_signed_area(flat_triangle) < 0.0:
            p2, p3 = p3, p2

        b1 = translated_point(
            (
                p1[0],
                p1[1],
                fixed_bottom_z,
            ),
            x_offset,
            z_offset,
        )

        b2 = translated_point(
            (
                p2[0],
                p2[1],
                fixed_bottom_z,
            ),
            x_offset,
            z_offset,
        )

        b3 = translated_point(
            (
                p3[0],
                p3[1],
                fixed_bottom_z,
            ),
            x_offset,
            z_offset,
        )

        t1 = translated_point(
            (
                p1[0],
                p1[1],
                flat_top_z,
            ),
            x_offset,
            z_offset,
        )

        t2 = translated_point(
            (
                p2[0],
                p2[1],
                flat_top_z,
            ),
            x_offset,
            z_offset,
        )

        t3 = translated_point(
            (
                p3[0],
                p3[1],
                flat_top_z,
            ),
            x_offset,
            z_offset,
        )

        triangles.append(
            (
                t1,
                t2,
                t3,
            )
        )

        triangles.append(
            (
                b3,
                b2,
                b1,
            )
        )

    add_fixed_ring_walls(
        ring=outer_ring,
        bottom_z=fixed_bottom_z,
        top_z=flat_top_z,
        x_offset=x_offset,
        z_offset=z_offset,
        triangles=triangles,
        is_hole=False,
    )

    for inner_ring in inner_rings:
        add_fixed_ring_walls(
            ring=inner_ring,
            bottom_z=fixed_bottom_z,
            top_z=flat_top_z,
            x_offset=x_offset,
            z_offset=z_offset,
            triangles=triangles,
            is_hole=True,
        )

    return {
        "triangles": triangles,
        "minimum_bottom_z": fixed_bottom_z,
        "maximum_bottom_z": fixed_bottom_z,
        "top_z": flat_top_z,
        "bottom_range_mm": 0.0,
    }


def add_fixed_ring_walls(
    ring,
    bottom_z,
    top_z,
    x_offset,
    z_offset,
    triangles,
    is_hole,
):
    for index in range(len(ring)):
        next_index = (index + 1) % len(ring)

        p1 = ring[index]
        p2 = ring[next_index]

        b1 = translated_point(
            (
                p1[0],
                p1[1],
                bottom_z,
            ),
            x_offset,
            z_offset,
        )

        b2 = translated_point(
            (
                p2[0],
                p2[1],
                bottom_z,
            ),
            x_offset,
            z_offset,
        )

        t1 = translated_point(
            (
                p1[0],
                p1[1],
                top_z,
            ),
            x_offset,
            z_offset,
        )

        t2 = translated_point(
            (
                p2[0],
                p2[1],
                top_z,
            ),
            x_offset,
            z_offset,
        )

        if is_hole:
            triangles.append(
                (
                    b1,
                    t2,
                    b2,
                )
            )

            triangles.append(
                (
                    b1,
                    t1,
                    t2,
                )
            )

        else:
            triangles.append(
                (
                    b1,
                    b2,
                    t2,
                )
            )

            triangles.append(
                (
                    b1,
                    t2,
                    t1,
                )
            )


def extract_directed_boundary_edges(flat_triangles):
    """
    Triangulation içindeki yalnız bir üçgene ait kenarları bulur.

    Üçgenlerin yönü CCW olduğu için dönen directed boundary edge'lerde
    polygon malzemesi kenarın sol tarafında kalır.

    Bu yön:
    - outer sınırda CCW,
    - hole sınırında CW

    olur. Böylece outer/hole için ayrı duvar yönü gerekmez.
    """
    edge_records = {}

    def point_key(point):
        return (
            round(float(point[0]), 9),
            round(float(point[1]), 9),
        )

    for triangle in flat_triangles:
        p1, p2, p3 = triangle

        directed_edges = (
            (p1, p2),
            (p2, p3),
            (p3, p1),
        )

        for start, end in directed_edges:
            start_key = point_key(start)
            end_key = point_key(end)

            undirected_key = tuple(
                sorted(
                    (
                        start_key,
                        end_key,
                    )
                )
            )

            if undirected_key not in edge_records:
                edge_records[undirected_key] = {
                    "count": 0,
                    "start": (
                        float(start[0]),
                        float(start[1]),
                    ),
                    "end": (
                        float(end[0]),
                        float(end[1]),
                    ),
                }

            edge_records[undirected_key]["count"] += 1

    return [
        (
            record["start"],
            record["end"],
        )
        for record in edge_records.values()
        if record["count"] == 1
    ]


def build_local_z_cap(
    region,
    terrain_mesh,
    shell_height_mm,
    cap_extra_height_mm,
    x_offset,
    z_offset,
):
    outer_ring, inner_rings = region_rings(region)

    flat_triangles = AtlasCastleShellTriangulator.triangulate(
        outer_ring=outer_ring,
        inner_rings=inner_rings,
    )

    bottom_z_cache = {}

    def local_bottom_z(point):
        key = (
            round(
                float(point[0]),
                9,
            ),
            round(
                float(point[1]),
                9,
            ),
        )

        cached = bottom_z_cache.get(key)

        if cached is not None:
            return cached

        value = (
            terrain_z_at_point(
                terrain_mesh,
                point,
            )
            + shell_height_mm
        )

        bottom_z_cache[key] = value
        return value

    all_points = list(outer_ring)

    for inner_ring in inner_rings:
        all_points.extend(inner_ring)

    all_bottom_values = [local_bottom_z(point) for point in all_points]

    minimum_bottom_z = min(all_bottom_values)

    maximum_bottom_z = max(all_bottom_values)

    flat_top_z = maximum_bottom_z + cap_extra_height_mm

    triangles = []

    for flat_triangle in flat_triangles:
        p1, p2, p3 = flat_triangle

        if triangle_signed_area(flat_triangle) < 0.0:
            p2, p3 = p3, p2

        b1 = translated_point(
            (
                p1[0],
                p1[1],
                local_bottom_z(p1),
            ),
            x_offset,
            z_offset,
        )

        b2 = translated_point(
            (
                p2[0],
                p2[1],
                local_bottom_z(p2),
            ),
            x_offset,
            z_offset,
        )

        b3 = translated_point(
            (
                p3[0],
                p3[1],
                local_bottom_z(p3),
            ),
            x_offset,
            z_offset,
        )

        t1 = translated_point(
            (
                p1[0],
                p1[1],
                flat_top_z,
            ),
            x_offset,
            z_offset,
        )

        t2 = translated_point(
            (
                p2[0],
                p2[1],
                flat_top_z,
            ),
            x_offset,
            z_offset,
        )

        t3 = translated_point(
            (
                p3[0],
                p3[1],
                flat_top_z,
            ),
            x_offset,
            z_offset,
        )

        triangles.append(
            (
                t1,
                t2,
                t3,
            )
        )

        triangles.append(
            (
                b3,
                b2,
                b1,
            )
        )

    boundary_edges = extract_directed_boundary_edges(flat_triangles)
    add_local_boundary_walls(
        boundary_edges=boundary_edges,
        local_bottom_z=local_bottom_z,
        top_z=flat_top_z,
        x_offset=x_offset,
        z_offset=z_offset,
        triangles=triangles,
    )

    return {
        "triangles": triangles,
        "minimum_bottom_z": (minimum_bottom_z),
        "maximum_bottom_z": (maximum_bottom_z),
        "top_z": flat_top_z,
        "bottom_range_mm": (maximum_bottom_z - minimum_bottom_z),
    }


def add_local_boundary_walls(
    boundary_edges,
    local_bottom_z,
    top_z,
    x_offset,
    z_offset,
    triangles,
):
    for p1, p2 in boundary_edges:
        bottom_z_1 = local_bottom_z(p1)
        bottom_z_2 = local_bottom_z(p2)

        b1 = translated_point(
            (
                p1[0],
                p1[1],
                bottom_z_1,
            ),
            x_offset,
            z_offset,
        )

        b2 = translated_point(
            (
                p2[0],
                p2[1],
                bottom_z_2,
            ),
            x_offset,
            z_offset,
        )

        t1 = translated_point(
            (
                p1[0],
                p1[1],
                top_z,
            ),
            x_offset,
            z_offset,
        )

        t2 = translated_point(
            (
                p2[0],
                p2[1],
                top_z,
            ),
            x_offset,
            z_offset,
        )

        triangles.append(
            (
                b1,
                b2,
                t2,
            )
        )

        triangles.append(
            (
                b1,
                t2,
                t1,
            )
        )


def add_local_ring_walls(
    ring,
    local_bottom_z,
    top_z,
    x_offset,
    z_offset,
    triangles,
    is_hole,
):
    for index in range(len(ring)):
        next_index = (index + 1) % len(ring)

        p1 = ring[index]
        p2 = ring[next_index]

        bottom_z_1 = local_bottom_z(p1)

        bottom_z_2 = local_bottom_z(p2)

        b1 = translated_point(
            (
                p1[0],
                p1[1],
                bottom_z_1,
            ),
            x_offset,
            z_offset,
        )

        b2 = translated_point(
            (
                p2[0],
                p2[1],
                bottom_z_2,
            ),
            x_offset,
            z_offset,
        )

        t1 = translated_point(
            (
                p1[0],
                p1[1],
                top_z,
            ),
            x_offset,
            z_offset,
        )

        t2 = translated_point(
            (
                p2[0],
                p2[1],
                top_z,
            ),
            x_offset,
            z_offset,
        )

        if is_hole:
            triangles.append(
                (
                    b1,
                    t2,
                    b2,
                )
            )

            triangles.append(
                (
                    b1,
                    t1,
                    t2,
                )
            )

        else:
            triangles.append(
                (
                    b1,
                    b2,
                    t2,
                )
            )

            triangles.append(
                (
                    b1,
                    t2,
                    t1,
                )
            )


def build_chord_regions():
    (
        _shell_polygon,
        raw_regions,
        reconstruction_data,
    ) = reconstruction.build_raw_regions()

    chord_regions = []
    reports = []

    for (
        raw_region,
        data_item,
    ) in zip(
        raw_regions,
        reconstruction_data,
    ):
        outer_arc = data_item["outer_arc"]

        chord_closure = reconstruction.straight_chord_closure(outer_arc)

        chord_fill = reconstruction.polygon_from_outer_arc_and_closure(
            outer_arc=outer_arc,
            closure_points=(chord_closure),
        )

        chord_region = reconstruction.union_preserving_raw(
            raw_region=raw_region,
            reconstruction_polygon=(chord_fill),
        )

        chord_regions.append(chord_region)

        reports.append(
            {
                "run_index": (data_item["run_index"]),
                "area_mm2": (chord_region.area),
            }
        )

    return (
        chord_regions,
        reports,
    )


def main():
    data = reconstruction.AtlasLocalOSMReader.read(
        str(reconstruction.PBF_PATH),
        reconstruction.BBOX,
    )

    castle = next(
        item
        for item in data.get(
            "castles",
            [],
        )
        if item.get("geometry_type") == "relation"
    )

    tags = castle.get(
        "tags",
        {},
    )

    shell_height_m = read_positive_float(
        tags.get("height"),
        SHELL_HEIGHT_M_DEFAULT,
    )

    shell_height_mm = max(
        reconstruction.AtlasCoordinateEngine(
            origin_lat=(reconstruction.BBOX[0]),
            origin_lon=(reconstruction.BBOX[1]),
            xy_scale=(
                reconstruction.AtlasScaleEngine.calculate_xy_scale_from_bbox(
                    bbox=(reconstruction.BBOX),
                    target_size_mm=(reconstruction.TARGET_SIZE_MM),
                    bed_width_mm=(reconstruction.BED_WIDTH_MM),
                    bed_depth_mm=(reconstruction.BED_DEPTH_MM),
                    margin_mm=(reconstruction.MARGIN_MM),
                    debug=False,
                )
            ),
            z_scale=(reconstruction.Z_SCALE),
        ).height_to_stl_mm(shell_height_m),
        MIN_SHELL_HEIGHT_MM,
    )

    tower_height_mm = (
        shell_height_mm
        * reconstruction.AtlasCastleShellHeightProfiler.TOWER_HEIGHT_MULTIPLIER
    )

    cap_extra_height_mm = tower_height_mm - shell_height_mm

    terrain_mesh = AtlasTerrainPipeline.build_terrain_slab(
        bbox=(reconstruction.BBOX),
        target_size_mm=(reconstruction.TARGET_SIZE_MM),
        z_scale=(reconstruction.Z_SCALE),
        base_z=(AtlasFoundationFirstEngine.BASE_PLATE_HEIGHT_MM),
        bottom_z=0.0,
        grid_size=25,
        terrain_provider_name=("srtm"),
        debug=False,
    )

    (
        chord_regions,
        region_reports,
    ) = build_chord_regions()

    all_triangles = []
    final_reports = []

    for region, region_report in zip(
        chord_regions,
        region_reports,
    ):
        fixed_result = build_fixed_bottom_cap(
            region=region,
            terrain_mesh=(terrain_mesh),
            shell_height_mm=(shell_height_mm),
            cap_extra_height_mm=(cap_extra_height_mm),
            x_offset=(FIXED_X_OFFSET_MM),
            z_offset=(FIXED_DISPLAY_Z_OFFSET),
        )

        local_result = build_local_z_cap(
            region=region,
            terrain_mesh=(terrain_mesh),
            shell_height_mm=(shell_height_mm),
            cap_extra_height_mm=(cap_extra_height_mm),
            x_offset=(LOCAL_X_OFFSET_MM),
            z_offset=(LOCAL_DISPLAY_Z_OFFSET),
        )

        all_triangles.extend(fixed_result["triangles"])

        all_triangles.extend(local_result["triangles"])

        final_reports.append(
            {
                "run_index": (region_report["run_index"]),
                "area_mm2": (region_report["area_mm2"]),
                "fixed_bottom_z": (fixed_result["minimum_bottom_z"]),
                "local_minimum_bottom_z": (local_result["minimum_bottom_z"]),
                "local_maximum_bottom_z": (local_result["maximum_bottom_z"]),
                "local_bottom_range_mm": (local_result["bottom_range_mm"]),
                "fixed_top_z": (fixed_result["top_z"]),
                "local_top_z": (local_result["top_z"]),
                "fixed_triangles": len(fixed_result["triangles"]),
                "local_triangles": len(local_result["triangles"]),
            }
        )

    write_ascii_stl(
        output_path=OUTPUT_PATH,
        triangles=all_triangles,
    )

    print("")
    print("=" * 92)
    print("ATLAS TOWER LOCAL Z ATTACHMENT " "DIAGNOSTIC REPORT")
    print("=" * 92)

    print(f"Tower regions                 : " f"{len(chord_regions)}")

    print(f"Shell height                  : " f"{shell_height_mm:.6f} mm")

    print(f"Tower height                  : " f"{tower_height_mm:.6f} mm")

    print(f"Cap extra height              : " f"{cap_extra_height_mm:.6f} mm")

    print(f"Fixed group X offset          : " f"{FIXED_X_OFFSET_MM:.3f} mm")

    print(f"Local-Z group X offset        : " f"{LOCAL_X_OFFSET_MM:.3f} mm")

    print(f"Total STL triangles           : " f"{len(all_triangles)}")

    print(f"Output                        : " f"{OUTPUT_PATH}")

    for report in final_reports:
        print("")
        print(f"Tower run " f"{report['run_index']}")

        print(f"Footprint area                : " f"{report['area_mm2']:.6f} mm²")

        print(f"Fixed bottom Z                : " f"{report['fixed_bottom_z']:.6f} mm")

        print(
            f"Local minimum bottom Z        : "
            f"{report['local_minimum_bottom_z']:.6f} mm"
        )

        print(
            f"Local maximum bottom Z        : "
            f"{report['local_maximum_bottom_z']:.6f} mm"
        )

        print(
            f"Local bottom Z range          : "
            f"{report['local_bottom_range_mm']:.6f} mm"
        )

        print(
            f"Fixed / local top Z           : "
            f"{report['fixed_top_z']:.6f} / "
            f"{report['local_top_z']:.6f} mm"
        )

        print(
            f"Fixed / local triangles       : "
            f"{report['fixed_triangles']} / "
            f"{report['local_triangles']}"
        )

    print("=" * 92)


if __name__ == "__main__":
    main()
