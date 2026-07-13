import importlib.util
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from CORE.atlas_coordinate_engine import AtlasCoordinateEngine
from CORE.atlas_scale_engine import AtlasScaleEngine
from CORE.atlas_terrain_pipeline import AtlasTerrainPipeline
from CORE.atlas_foundation_first_engine import (
    AtlasFoundationFirstEngine,
)
from CORE.atlas_castle_shell_builder import (
    AtlasCastleShellBuilder,
)
from CORE.atlas_coastline_water_builder import (
    AtlasCoastlineWaterBuilder,
)
from CORE.atlas_water_foundation_builder import (
    AtlasWaterFoundationBuilder,
)
from EXPORT.atlas_stl_writer import AtlasSTLWriter

RECONSTRUCTION_PATH = (
    PROJECT_ROOT / "Test/test_rumeli_tower_footprint_reconstruction.py"
)

LOCAL_Z_PATH = PROJECT_ROOT / "Test/test_rumeli_tower_local_z_attachment.py"

OUTPUT_PATH = (
    PROJECT_ROOT / "OUTPUT/STL/" "rumeli_hisari_castle_shell_local_z_towers_test.stl"
)

TERRAIN_OUTPUT_PATH = (
    PROJECT_ROOT / "OUTPUT/STL/" "rumeli_hisari_terrain.stl"
)

WATER_OUTPUT_PATH = (
    PROJECT_ROOT / "OUTPUT/STL/" "rumeli_hisari_water.stl"
)

CASTLE_SHELL_OUTPUT_PATH = (
    PROJECT_ROOT / "OUTPUT/STL/" "rumeli_hisari_castle_shell.stl"
)

TOWERS_OUTPUT_PATH = (
    PROJECT_ROOT / "OUTPUT/STL/" "rumeli_hisari_towers.stl"
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

local_z_test = load_module(
    module_name="atlas_rumeli_local_z",
    file_path=LOCAL_Z_PATH,
)


def count_triangles(meshes):
    total = 0

    for mesh in meshes:
        if mesh is None:
            continue

        if isinstance(mesh, dict):
            triangles = mesh.get(
                "triangles",
                [],
            )

        else:
            triangles = getattr(
                mesh,
                "triangles",
                [],
            )

        total += len(triangles or [])

    return total


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
        raise RuntimeError("No relation castle found in Rumeli Hisarı test data.")

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
        z_scale=(reconstruction.Z_SCALE),
    )

    terrain_mesh = AtlasTerrainPipeline.build_terrain_slab(
        bbox=(reconstruction.BBOX),
        target_size_mm=(reconstruction.TARGET_SIZE_MM),
        z_scale=(reconstruction.Z_SCALE),
        base_z=(AtlasFoundationFirstEngine.BASE_PLATE_HEIGHT_MM),
        bottom_z=0.0,
        grid_size=25,
        terrain_provider_name="srtm",
        debug=False,
    )

    coastline_water_polygons = (
        AtlasCoastlineWaterBuilder.build_water_polygons(
            coastlines=data.get(
                "coastlines",
                [],
            ),
            bbox=reconstruction.BBOX,
            debug=True,
        )
    )

    water_meshes = (
        AtlasWaterFoundationBuilder.build_coastline_water_meshes(
            water_polygons=coastline_water_polygons,
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_mesh,
            debug=True,
        )
    )

    shell_meshes = AtlasCastleShellBuilder.build_shells(
        castles=[castle],
        coordinate_engine=(coordinate_engine),
        terrain_mesh=(terrain_mesh),
        debug=True,
    )

    if not shell_meshes:
        raise RuntimeError("Castle shell could not be generated.")

    shell_mesh = shell_meshes[0]

    shell_height_mm = float(shell_mesh["shell_height_mm"])

    assert shell_height_mm >= 6.0, (
        "Relation tabanlı kale kabuğu baskıda en az "
        f"6.0 mm olmalı; mevcut={shell_height_mm:.6f} mm"
    )

    tower_height_mm = float(shell_mesh["tower_height_mm"])

    cap_extra_height_mm = tower_height_mm - shell_height_mm

    (
        chord_regions,
        region_reports,
    ) = local_z_test.build_chord_regions()

    if not chord_regions:
        raise RuntimeError("No reconstructed tower footprints were generated.")

    tower_meshes = []
    tower_reports = []

    for region, region_report in zip(
        chord_regions,
        region_reports,
    ):
        local_result = local_z_test.build_local_z_cap(
            region=region,
            terrain_mesh=(terrain_mesh),
            shell_height_mm=(shell_height_mm),
            cap_extra_height_mm=(cap_extra_height_mm),
            x_offset=0.0,
            z_offset=0.0,
        )

        tower_mesh = {
            "type": ("castle_tower_" "local_z_diagnostic"),
            "source_id": castle.get("id"),
            "run_index": (region_report["run_index"]),
            "area_mm2": (region_report["area_mm2"]),
            "minimum_bottom_z": (local_result["minimum_bottom_z"]),
            "maximum_bottom_z": (local_result["maximum_bottom_z"]),
            "bottom_range_mm": (local_result["bottom_range_mm"]),
            "top_z": (local_result["top_z"]),
            "triangles": (local_result["triangles"]),
            "placement_mode": ("foundation_first_local_z"),
        }

        tower_meshes.append(tower_mesh)

        tower_reports.append(
            {
                "run_index": (region_report["run_index"]),
                "area_mm2": (region_report["area_mm2"]),
                "minimum_bottom_z": (local_result["minimum_bottom_z"]),
                "maximum_bottom_z": (local_result["maximum_bottom_z"]),
                "bottom_range_mm": (local_result["bottom_range_mm"]),
                "top_z": (local_result["top_z"]),
                "triangles": len(local_result["triangles"]),
            }
        )

    meshes = [
        terrain_mesh,
        *water_meshes,
        *shell_meshes,
        *tower_meshes,
    ]

    AtlasSTLWriter.write(
        meshes=meshes,
        output_path=str(OUTPUT_PATH),
        solid_name=("ATLAS_RUMELI_CASTLE_" "SHELL_LOCAL_Z_TOWERS"),
    )

    AtlasSTLWriter.write(
        meshes=[terrain_mesh],
        output_path=str(TERRAIN_OUTPUT_PATH),
        solid_name="ATLAS_RUMELI_TERRAIN",
    )

    AtlasSTLWriter.write(
        meshes=water_meshes,
        output_path=str(WATER_OUTPUT_PATH),
        solid_name="ATLAS_RUMELI_WATER",
    )

    AtlasSTLWriter.write(
        meshes=shell_meshes,
        output_path=str(CASTLE_SHELL_OUTPUT_PATH),
        solid_name="ATLAS_RUMELI_CASTLE_SHELL",
    )

    AtlasSTLWriter.write(
        meshes=tower_meshes,
        output_path=str(TOWERS_OUTPUT_PATH),
        solid_name="ATLAS_RUMELI_TOWERS",
    )

    terrain_triangle_count = count_triangles([terrain_mesh])

    water_triangle_count = count_triangles(water_meshes)

    shell_triangle_count = count_triangles(shell_meshes)

    tower_triangle_count = count_triangles(tower_meshes)

    print("")
    print("=" * 92)
    print("ATLAS RUMELI CASTLE SHELL + " "LOCAL Z TOWERS DIAGNOSTIC REPORT")
    print("=" * 92)

    print(f"Castle relation               : " f"{castle.get('id')}")

    print(f"Terrain meshes                : 1")

    print(f"Water meshes                  : " f"{len(water_meshes)}")

    print(f"Castle shell meshes           : " f"{len(shell_meshes)}")

    print(f"Tower meshes                  : " f"{len(tower_meshes)}")

    print(f"Shell height                  : " f"{shell_height_mm:.6f} mm")

    print(f"Tower height                  : " f"{tower_height_mm:.6f} mm")

    print(f"Cap extra height              : " f"{cap_extra_height_mm:.6f} mm")

    print(f"Terrain triangles             : " f"{terrain_triangle_count}")

    print(f"Water triangles               : " f"{water_triangle_count}")

    print(f"Shell triangles               : " f"{shell_triangle_count}")

    print(f"Tower triangles               : " f"{tower_triangle_count}")

    print(f"Combined triangles            : " f"{count_triangles(meshes)}")

    print(f"Output                        : " f"{OUTPUT_PATH}")

    for report in tower_reports:
        print("")
        print(f"Tower run " f"{report['run_index']}")

        print(f"Footprint area                : " f"{report['area_mm2']:.6f} mm²")

        print(
            f"Minimum bottom Z              : " f"{report['minimum_bottom_z']:.6f} mm"
        )

        print(
            f"Maximum bottom Z              : " f"{report['maximum_bottom_z']:.6f} mm"
        )

        print(f"Bottom Z range                : " f"{report['bottom_range_mm']:.6f} mm")

        print(f"Flat top Z                    : " f"{report['top_z']:.6f} mm")

        print(f"Tower triangles               : " f"{report['triangles']}")

    print("=" * 92)


if __name__ == "__main__":
    main()
