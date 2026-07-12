from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from CORE.atlas_foundation_first_engine import (
    AtlasFoundationFirstEngine,
)

PBF_PATH = PROJECT_ROOT / "Data/OSM/hohenneuffen-test.osm.pbf"

OUTPUT_PATH = PROJECT_ROOT / "OUTPUT/STL/hohenneuffen_castle_preview.stl"

BBOX = (
    48.5520,
    9.3875,
    48.5595,
    9.3975,
)


def main():
    if not PBF_PATH.exists():
        raise FileNotFoundError(f"PBF bulunamadı: {PBF_PATH}")

    result = AtlasFoundationFirstEngine.generate_city_stl(
        pbf_path=str(PBF_PATH),
        bbox=BBOX,
        output_path=str(OUTPUT_PATH),
        target_size_mm=180,
        bed_width_mm=256,
        bed_depth_mm=256,
        margin_mm=10,
        max_buildings=None,
        min_points=3,
        max_points=500,
        z_scale=5500,
        terrain_provider_name="srtm",
        nature_provider_names=(),
        debug=True,
    )

    print("")
    print("=" * 88)
    print("ATLAS HOHENNEUFFEN FULL SCENE REPORT")
    print("=" * 88)

    print(f"Reader buildings              : " f"{result.get('reader_buildings', 0)}")

    print(f"Reader trees                  : " f"{result.get('reader_trees', 0)}")

    print(f"Reader roads                  : " f"{result.get('reader_roads', 0)}")

    print(
        f"Reader pedestrian paths       : "
        f"{result.get('reader_pedestrian_paths', 0)}"
    )

    print(f"Reader parks                  : " f"{result.get('reader_parks', 0)}")

    print(f"Reader castles                : " f"{result.get('reader_castles', 0)}")

    print(f"Reader castle walls           : " f"{result.get('reader_castle_walls', 0)}")

    print(f"Building meshes               : " f"{result.get('buildings', 0)}")

    print(f"Castle wall meshes            : " f"{result.get('castle_wall_meshes', 0)}")

    print(f"Castle shell meshes           : " f"{result.get('castle_shell_meshes', 0)}")

    print(
        f"Castle tower cap meshes       : "
        f"{result.get('castle_tower_cap_meshes', 0)}"
    )

    print(f"Total meshes                  : " f"{result.get('meshes', 0)}")

    print(f"Total triangles               : " f"{result.get('triangles', 0)}")

    print(f"Output                        : " f"{OUTPUT_PATH}")

    print("=" * 88)


if __name__ == "__main__":
    main()
