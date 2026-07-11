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
from CORE.atlas_castle_tower_cap_builder import (
    AtlasCastleTowerCapBuilder,
)

RECONSTRUCTION_PATH = (
    PROJECT_ROOT / "Test/test_rumeli_tower_footprint_reconstruction.py"
)


BUFFER_VALUES_MM = (
    0.0,
    0.0001,
    0.00025,
    0.0005,
    0.001,
    0.0025,
    0.005,
    0.01,
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


def analyze_mesh(mesh):
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

    return {
        "open_edges": sum(1 for count in edge_counts.values() if count == 1),
        "non_manifold_edges": sum(1 for count in edge_counts.values() if count > 2),
    }


def build_inputs():
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

    return (
        castles,
        coordinate_engine,
        terrain_mesh,
    )


def main():
    (
        castles,
        coordinate_engine,
        terrain_mesh,
    ) = build_inputs()

    original_buffer = AtlasCastleTowerCapBuilder.TOPOLOGY_REPAIR_BUFFER_MM

    baseline_areas = None

    print("")
    print("=" * 104)
    print("ATLAS TOWER TOPOLOGY BUFFER SWEEP REPORT")
    print("=" * 104)

    try:
        for buffer_value in BUFFER_VALUES_MM:
            AtlasCastleTowerCapBuilder.TOPOLOGY_REPAIR_BUFFER_MM = buffer_value

            tower_meshes = AtlasCastleTowerCapBuilder.build_caps(
                castles=castles,
                coordinate_engine=coordinate_engine,
                terrain_mesh=terrain_mesh,
                debug=False,
            )

            areas = [
                float(
                    mesh.get(
                        "area_mm2",
                        0.0,
                    )
                )
                for mesh in tower_meshes
            ]

            if baseline_areas is None:
                baseline_areas = list(areas)

            print("")
            print(f"Buffer                        : " f"{buffer_value:.6f} mm")

            total_open_edges = 0
            total_non_manifold_edges = 0

            for mesh_index, mesh in enumerate(
                tower_meshes,
                start=1,
            ):
                topology = analyze_mesh(mesh)

                total_open_edges += topology["open_edges"]

                total_non_manifold_edges += topology["non_manifold_edges"]

                baseline_area = baseline_areas[mesh_index - 1]

                area_delta = (
                    mesh.get(
                        "area_mm2",
                        0.0,
                    )
                    - baseline_area
                )

                print(
                    f"Tower {mesh_index}                      : "
                    f"area={mesh.get('area_mm2', 0.0):.9f} "
                    f"delta={area_delta:+.9f} "
                    f"open={topology['open_edges']} "
                    f"non_manifold="
                    f"{topology['non_manifold_edges']}"
                )

            print(
                f"Total                         : "
                f"open={total_open_edges} "
                f"non_manifold="
                f"{total_non_manifold_edges}"
            )

    finally:
        AtlasCastleTowerCapBuilder.TOPOLOGY_REPAIR_BUFFER_MM = original_buffer

    print("")
    print("=" * 104)


if __name__ == "__main__":
    main()
