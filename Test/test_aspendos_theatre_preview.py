from CORE.atlas_foundation_first_engine import (
    AtlasFoundationFirstEngine,
)


PBF_PATH = (
    "Data/OSM/"
    "aspendos-theatre-test.osm.pbf"
)

OUTPUT_PATH = (
    "OUTPUT/STL/"
    "aspendos_theatre_preview.stl"
)

BBOX = (
    36.9365,
    31.1695,
    36.9410,
    31.1750,
)


def main():
    result = (
        AtlasFoundationFirstEngine
        .generate_city_stl(
            pbf_path=PBF_PATH,
            bbox=BBOX,
            output_path=OUTPUT_PATH,
            target_size_mm=160,
            bed_width_mm=256,
            bed_depth_mm=256,
            margin_mm=15,
            max_buildings=None,
            min_points=4,
            max_points=300,
            z_scale=5500,
            terrain_provider_name="srtm",
            nature_provider_names=(),
            debug=True,
        )
    )

    print()
    print("=" * 78)
    print("ASPENDOS THEATRE BASELINE RESULT")
    print("=" * 78)
    print(result)


if __name__ == "__main__":
    main()
