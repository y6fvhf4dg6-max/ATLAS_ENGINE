# Test/test_fixed_scale_city_preview.py

from CORE.atlas_engine import AtlasEngine
from CORE.atlas_product_area_engine import AtlasProductAreaEngine

# PBF_PATH = "Data/OSM/hessen-latest.osm.pbf"
PBF_PATH = "Data/OSM/turkey-latest.osm.pbf"
# PBF_PATH = "Data/OSM/ile-de-france-latest.osm.pbf"
# PBF_PATH = "Data/OSM/england-latest.osm.pbf"
OUTPUT_PATH = "OUTPUT/STL/latest.stl"


def main():
    # Current Frankfurt test center
    center_lat = 39.925054
    center_lon = 32.836944

    product_size_mm = 200
    scale_ratio = 5500

    bbox = AtlasProductAreaEngine.build_bbox_from_center(
        center_lat=center_lat,
        center_lon=center_lon,
        product_size_mm=product_size_mm,
        scale_ratio=scale_ratio,
        debug=True,
    )

    result = AtlasEngine.generate_city_stl(
        pbf_path=PBF_PATH,
        bbox=bbox,
        output_path=OUTPUT_PATH,
        target_size_mm=product_size_mm,
        bed_width_mm=256,
        bed_depth_mm=256,
        margin_mm=15,
        min_points=4,
        max_points=80,
        z_scale=5500,
        debug=True,
        use_recessed_roads=False,
    )

    print(result)


if __name__ == "__main__":
    main()
