from CORE.atlas_foundation_first_engine import AtlasFoundationFirstEngine
from CORE.atlas_product_area_engine import AtlasProductAreaEngine


PBF_PATH = "Data/OSM/anitkabir-test.osm.pbf"
OUTPUT_PATH = "OUTPUT/STL/personalized_map_product_200mm.stl"

CENTER_LAT = 39.92505
CENTER_LON = 32.83695

PRODUCT_SIZE_MM = 200.0
SCALE_RATIO = 5500.0


def main():
    bbox = AtlasProductAreaEngine.build_bbox_from_center(
        center_lat=CENTER_LAT,
        center_lon=CENTER_LON,
        product_size_mm=PRODUCT_SIZE_MM,
        scale_ratio=SCALE_RATIO,
        debug=True,
    )

    result = AtlasFoundationFirstEngine.generate_city_stl(
        pbf_path=PBF_PATH,
        bbox=bbox,
        output_path=OUTPUT_PATH,
        target_size_mm=PRODUCT_SIZE_MM,
        bed_width_mm=256,
        bed_depth_mm=256,
        margin_mm=15,
        max_buildings=None,
        min_points=4,
        max_points=300,
        z_scale=SCALE_RATIO,
        terrain_provider_name="srtm",
        fixed_xy_scale=SCALE_RATIO,
        use_fixed_xy_scale=True,
        debug=True,
    )

    print("")
    print("=" * 70)
    print("ATLAS PERSONALIZED MAP PRODUCT")
    print("=" * 70)
    print(f"Center              : {CENTER_LAT:.8f}, {CENTER_LON:.8f}")
    print(f"Requested size      : {PRODUCT_SIZE_MM:.2f} mm")
    print(f"Requested scale     : 1:{SCALE_RATIO:.0f}")
    print(f"Output              : {OUTPUT_PATH}")
    print(f"Resolved XY scale   : 1:{result['xy_scale']:.2f}")
    print(
        "Terrain size       : "
        f"{result['terrain_size_x_mm']:.2f} × "
        f"{result['terrain_size_y_mm']:.2f} mm"
    )
    print("=" * 70)
    print("")
    print(result)


if __name__ == "__main__":
    main()
