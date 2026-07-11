import importlib.util
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from CORE.atlas_castle_tower_cap_builder import (
    AtlasCastleTowerCapBuilder,
)

SOURCE_TEST_PATH = PROJECT_ROOT / "Test/test_rumeli_core_tower_cap_local_z.py"


TOLERANCES = (
    1e-7,
    2.5e-7,
    5e-7,
    1e-6,
    2.5e-6,
    5e-6,
    1e-5,
    2.5e-5,
    5e-5,
    1e-4,
    2.5e-4,
    5e-4,
    1e-3,
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


core_test = load_module(
    module_name="atlas_core_local_z_test",
    file_path=SOURCE_TEST_PATH,
)


def build_inputs():
    data = core_test.reconstruction.AtlasLocalOSMReader.read(
        str(core_test.reconstruction.PBF_PATH),
        core_test.reconstruction.BBOX,
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

    xy_scale = core_test.AtlasScaleEngine.calculate_xy_scale_from_bbox(
        bbox=(core_test.reconstruction.BBOX),
        target_size_mm=(core_test.reconstruction.TARGET_SIZE_MM),
        bed_width_mm=(core_test.reconstruction.BED_WIDTH_MM),
        bed_depth_mm=(core_test.reconstruction.BED_DEPTH_MM),
        margin_mm=(core_test.reconstruction.MARGIN_MM),
        debug=False,
    )

    south, west, _north, _east = core_test.reconstruction.BBOX

    coordinate_engine = core_test.AtlasCoordinateEngine(
        origin_lat=south,
        origin_lon=west,
        xy_scale=xy_scale,
        z_scale=(core_test.reconstruction.Z_SCALE),
    )

    terrain_mesh = core_test.AtlasTerrainPipeline.build_terrain_slab(
        bbox=(core_test.reconstruction.BBOX),
        target_size_mm=(core_test.reconstruction.TARGET_SIZE_MM),
        z_scale=(core_test.reconstruction.Z_SCALE),
        base_z=(core_test.AtlasFoundationFirstEngine.BASE_PLATE_HEIGHT_MM),
        bottom_z=0.0,
        grid_size=25,
        terrain_provider_name="srtm",
        debug=False,
    )

    return (
        castle,
        coordinate_engine,
        terrain_mesh,
    )


def main():
    (
        castle,
        coordinate_engine,
        terrain_mesh,
    ) = build_inputs()

    original_tolerance = AtlasCastleTowerCapBuilder.COLLINEAR_TOLERANCE

    baseline_areas = None

    print("")
    print("=" * 112)
    print("ATLAS COLLINEAR TOLERANCE SWEEP REPORT")
    print("=" * 112)

    try:
        for tolerance in TOLERANCES:
            AtlasCastleTowerCapBuilder.COLLINEAR_TOLERANCE = tolerance

            tower_meshes = AtlasCastleTowerCapBuilder.build_caps(
                castles=[castle],
                coordinate_engine=(coordinate_engine),
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

            total_open = 0
            total_non_manifold = 0

            print("")
            print(f"Tolerance : " f"{tolerance:.9f}")

            for index, mesh in enumerate(
                tower_meshes,
                start=1,
            ):
                topology = core_test.analyze_mesh_edges(mesh)

                area = float(
                    mesh.get(
                        "area_mm2",
                        0.0,
                    )
                )

                area_delta = area - baseline_areas[index - 1]

                total_open += topology["open_edges"]

                total_non_manifold += topology["non_manifold_edges"]

                print(
                    f"Tower {index}    "
                    f"area={area:.9f} "
                    f"delta={area_delta:+.9f} "
                    f"triangles="
                    f"{len(mesh.get('triangles', []))} "
                    f"open="
                    f"{topology['open_edges']} "
                    f"non_manifold="
                    f"{topology['non_manifold_edges']}"
                )

            print(
                f"TOTAL      "
                f"open={total_open} "
                f"non_manifold="
                f"{total_non_manifold}"
            )

    finally:
        AtlasCastleTowerCapBuilder.COLLINEAR_TOLERANCE = original_tolerance

    print("")
    print("=" * 112)


if __name__ == "__main__":
    main()
