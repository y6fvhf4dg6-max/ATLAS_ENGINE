import importlib.util
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from CORE.atlas_coordinate_engine import AtlasCoordinateEngine
from CORE.atlas_scale_engine import AtlasScaleEngine
from CORE.atlas_terrain_pipeline import AtlasTerrainPipeline
from CORE.atlas_foundation_first_engine import AtlasFoundationFirstEngine
from CORE.atlas_castle_shell_builder import AtlasCastleShellBuilder
from CORE.atlas_castle_tower_cap_builder import (
    AtlasCastleTowerCapBuilder,
)
from EXPORT.atlas_stl_writer import AtlasSTLWriter

RECONSTRUCTION_PATH = (
    PROJECT_ROOT / "Test/test_rumeli_tower_footprint_reconstruction.py"
)

OUTPUT_PATH = (
    PROJECT_ROOT / "OUTPUT/STL/" "rumeli_hisari_core_tower_cap_local_z_test.stl"
)


def load_module(
    module_name,
    file_path,
):
    spec = importlib.util.spec_from_file_location(
        module_name,
        file_path,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Module could not be loaded: {file_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


reconstruction = load_module(
    module_name="atlas_rumeli_reconstruction",
    file_path=RECONSTRUCTION_PATH,
)


def count_triangles(meshes):
    return sum(
        len(mesh.get("triangles", [])) for mesh in meshes if isinstance(mesh, dict)
    )


def point_key(point):
    return (
        round(float(point[0]), 9),
        round(float(point[1]), 9),
        round(float(point[2]), 9),
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


def triangles_using_edge(
    mesh,
    target_edge,
):
    matches = []

    target = tuple(sorted(target_edge))

    for triangle_index, triangle in enumerate(mesh.get("triangles", [])):
        if len(triangle) != 3:
            continue

        point_1, point_2, point_3 = triangle

        triangle_edge_keys = (
            edge_key(point_1, point_2),
            edge_key(point_2, point_3),
            edge_key(point_3, point_1),
        )

        if target in triangle_edge_keys:
            matches.append(
                {
                    "triangle_index": triangle_index,
                    "triangle": triangle,
                }
            )

    return matches


def analyze_mesh_edges(mesh):
    edge_counts = Counter()

    triangles = mesh.get(
        "triangles",
        [],
    )

    for triangle in triangles:
        if len(triangle) != 3:
            continue

        point_1, point_2, point_3 = triangle

        edge_counts[edge_key(point_1, point_2)] += 1

        edge_counts[edge_key(point_2, point_3)] += 1

        edge_counts[edge_key(point_3, point_1)] += 1

    open_edges = [edge for edge, count in edge_counts.items() if count == 1]

    non_manifold_edges = [edge for edge, count in edge_counts.items() if count > 2]

    return {
        "open_edges": len(open_edges),
        "non_manifold_edges": len(non_manifold_edges),
        "open_edge_details": open_edges,
        "non_manifold_edge_details": [
            {
                "edge": edge,
                "count": edge_counts[edge],
            }
            for edge in non_manifold_edges
        ],
    }


def main():
    data = reconstruction.AtlasLocalOSMReader.read(
        str(reconstruction.PBF_PATH),
        reconstruction.BBOX,
    )

    castles = [
        item
        for item in data.get(
            "castles",
            [],
        )
        if item.get("geometry_type") == "relation"
    ]

    if not castles:
        raise RuntimeError("No relation castle found.")

    castle = castles[0]

    xy_scale = AtlasScaleEngine.calculate_xy_scale_from_bbox(
        bbox=reconstruction.BBOX,
        target_size_mm=(reconstruction.TARGET_SIZE_MM),
        bed_width_mm=(reconstruction.BED_WIDTH_MM),
        bed_depth_mm=(reconstruction.BED_DEPTH_MM),
        margin_mm=(reconstruction.MARGIN_MM),
        debug=False,
    )

    south, west, _north, _east = reconstruction.BBOX

    coordinate_engine = AtlasCoordinateEngine(
        origin_lat=south,
        origin_lon=west,
        xy_scale=xy_scale,
        z_scale=reconstruction.Z_SCALE,
    )

    terrain_mesh = AtlasTerrainPipeline.build_terrain_slab(
        bbox=reconstruction.BBOX,
        target_size_mm=(reconstruction.TARGET_SIZE_MM),
        z_scale=reconstruction.Z_SCALE,
        base_z=(AtlasFoundationFirstEngine.BASE_PLATE_HEIGHT_MM),
        bottom_z=0.0,
        grid_size=25,
        terrain_provider_name="srtm",
        debug=False,
    )

    shell_meshes = AtlasCastleShellBuilder.build_shells(
        castles=[castle],
        coordinate_engine=coordinate_engine,
        terrain_mesh=terrain_mesh,
        debug=True,
    )

    tower_cap_meshes = AtlasCastleTowerCapBuilder.build_caps(
        castles=[castle],
        coordinate_engine=coordinate_engine,
        terrain_mesh=terrain_mesh,
        debug=True,
    )

    if not shell_meshes:
        raise RuntimeError("Castle shell was not generated.")

    if not tower_cap_meshes:
        raise RuntimeError("CORE tower caps were not generated.")

    meshes = [
        terrain_mesh,
        *shell_meshes,
        *tower_cap_meshes,
    ]

    AtlasSTLWriter.write(
        meshes=meshes,
        output_path=str(OUTPUT_PATH),
        solid_name=("ATLAS_RUMELI_CORE_" "TOWER_CAP_LOCAL_Z"),
    )

    print("")
    print("=" * 92)
    print("ATLAS CORE TOWER CAP LOCAL-Z " "INTEGRATION REPORT")
    print("=" * 92)

    print(f"Castle relation               : " f"{castle.get('id')}")

    print(f"Tower cap meshes              : " f"{len(tower_cap_meshes)}")

    print(f"Terrain triangles             : " f"{count_triangles([terrain_mesh])}")

    print(f"Shell triangles               : " f"{count_triangles(shell_meshes)}")

    print(f"Tower cap triangles           : " f"{count_triangles(tower_cap_meshes)}")

    print(f"Combined triangles            : " f"{count_triangles(meshes)}")

    print(f"Output                        : " f"{OUTPUT_PATH}")

    total_open_edges = 0
    total_non_manifold_edges = 0

    for mesh in tower_cap_meshes:
        edge_report = analyze_mesh_edges(mesh)

        total_open_edges += edge_report["open_edges"]

        total_non_manifold_edges += edge_report["non_manifold_edges"]

        minimum_bottom_z = mesh.get("minimum_bottom_z")

        maximum_bottom_z = mesh.get("maximum_bottom_z")

        bottom_z_range = mesh.get("bottom_z_range_mm")

        print("")
        print(f"Tower run " f"{mesh.get('run_index')}")

        print(
            f"Area                          : " f"{mesh.get('area_mm2', 0.0):.6f} mm²"
        )

        print(f"Placement mode                : " f"{mesh.get('placement_mode')}")

        print(f"Minimum bottom Z              : " f"{minimum_bottom_z:.6f} mm")

        print(f"Maximum bottom Z              : " f"{maximum_bottom_z:.6f} mm")

        print(f"Bottom Z range                : " f"{bottom_z_range:.6f} mm")

        print(f"Flat top Z                    : " f"{mesh.get('top_z', 0.0):.6f} mm")

        print(f"Triangles                     : " f"{len(mesh.get('triangles', []))}")

        print(f"Open edges                    : " f"{edge_report['open_edges']}")

        print(
            f"Non-manifold edges            : " f"{edge_report['non_manifold_edges']}"
        )
        for detail_index, detail in enumerate(
            edge_report["non_manifold_edge_details"],
            start=1,
        ):
            print(
                f"Non-manifold edge "
                f"{detail_index:02d}         : "
                f"count={detail['count']} "
                f"{detail['edge'][0]} -> "
                f"{detail['edge'][1]}"
            )

            matching_triangles = triangles_using_edge(
                mesh=mesh,
                target_edge=detail["edge"],
            )

            for match in matching_triangles:
                print(
                    f"  Triangle "
                    f"{match['triangle_index']:03d}              : "
                    f"{match['triangle']}"
                )

    print("")
    print(f"Total tower open edges        : " f"{total_open_edges}")

    print(f"Total tower non-manifold      : " f"{total_non_manifold_edges}")

    print("=" * 92)


if __name__ == "__main__":
    main()
