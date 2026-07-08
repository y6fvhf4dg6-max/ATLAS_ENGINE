# Test/test_fixed_scale_eiffel.py

from CORE.atlas_product_area_engine import AtlasProductAreaEngine


def main():
    # Paris Eiffel Tower approximate center
    center_lat = 48.858370
    center_lon = 2.294481

    product_size_mm = 200
    scale_ratio = 5500

    bbox = AtlasProductAreaEngine.build_bbox_from_center(
        center_lat=center_lat,
        center_lon=center_lon,
        product_size_mm=product_size_mm,
        scale_ratio=scale_ratio,
        debug=True,
    )

    print("Generated bbox:")
    print(bbox)


if __name__ == "__main__":
    main()
