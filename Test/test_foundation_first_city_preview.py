# Test/test_foundation_first_city_preview.py

from CORE.atlas_foundation_first_engine import AtlasFoundationFirstEngine

PBF_PATH = "Data/OSM/anitkabir-test.osm.pbf"
OUTPUT_PATH = "OUTPUT/STL/foundation_first_latest.stl"


def main():
    result = AtlasFoundationFirstEngine.generate_city_stl(
        pbf_path=PBF_PATH,
        bbox=(
            39.92180,
            32.83280,
            39.92830,
            32.84110,
        ),
        output_path=OUTPUT_PATH,
        target_size_mm=200,
        bed_width_mm=256,
        bed_depth_mm=256,
        margin_mm=15,
        max_buildings=None,
        min_points=4,
        max_points=300,
        z_scale=5500,
        terrain_provider_name="srtm",
        debug=True,
    )

    print(result)


if __name__ == "__main__":
    main()
