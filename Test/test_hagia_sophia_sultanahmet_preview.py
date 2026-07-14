# Test/test_hagia_sophia_sultanahmet_preview.py

from CORE.atlas_foundation_first_engine import AtlasFoundationFirstEngine


PBF_PATH = (
    "Data/OSM/"
    "hagia-sophia-sultanahmet-test.osm.pbf"
)

OUTPUT_PATH = (
    "OUTPUT/STL/"
    "hagia_sophia_sultanahmet_preview.stl"
)

BBOX = (
    41.0025,
    28.9715,
    41.0095,
    28.9845,
)


def main():
    result = AtlasFoundationFirstEngine.generate_city_stl(
        pbf_path=PBF_PATH,
        bbox=BBOX,
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

    print()
    print("=" * 78)
    print("HAGIA SOPHIA + SULTANAHMET PREVIEW RESULT")
    print("=" * 78)
    print(result)


if __name__ == "__main__":
    main()
