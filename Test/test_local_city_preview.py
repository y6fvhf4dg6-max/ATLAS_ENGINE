# Test/test_local_city_preview.py

from CORE.atlas_engine import AtlasEngine
from CORE.atlas_area_selector import AtlasAreaSelector

PBF_PATH = "Data/OSM/hessen-latest.osm.pbf"
OUTPUT_PATH = "OUTPUT/STL/latest.stl"


def main():
    bbox = AtlasAreaSelector.bbox_from_center(
        center_lat=50.1109,
        center_lon=8.6821,
        width_m=350,
    )

    result = AtlasEngine.generate_city_stl(
        pbf_path=PBF_PATH,
        bbox=bbox,
        output_path=OUTPUT_PATH,
        # ÜRÜN ÖLÇÜSÜ
        target_size_mm=180,
        bed_width_mm=256,
        bed_depth_mm=256,
        margin_mm=15,
        # TEST AMAÇLI SINIR
        # None yaparsak seçilen alan içindeki tüm uygun binaları işler.
        max_buildings=80,
        # GEOMETRİ FİLTRELERİ
        min_points=4,
        max_points=80,
        # DİKEY ÖLÇEK
        z_scale=6000,
        debug=True,
        use_recessed_roads=True,
    )

    print(result)


if __name__ == "__main__":
    main()
