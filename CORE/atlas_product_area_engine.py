# CORE/atlas_product_area_engine.py

import math


class AtlasProductAreaEngine:
    """
    ATLAS Product Area Engine v1.0

    Görev:
    Sabit ölçek + ürün boyutundan gerçek dünya bbox üretir.

    Yeni ticari ürün mantığı:
    - Ölçek sabit kalır.
    - Ürün boyutu değiştikçe kapsanan gerçek alan değişir.

    Örnek:
    scale_ratio = 5500
    product_size_mm = 200

    200 mm * 5500 = 1,100,000 mm = 1100 m
    """

    DEFAULT_SCALE_RATIO = 5500

    @staticmethod
    def build_bbox_from_center(
        center_lat,
        center_lon,
        product_size_mm,
        scale_ratio=DEFAULT_SCALE_RATIO,
        debug=True,
    ):
        real_world_size_m = (product_size_mm * scale_ratio) / 1000.0
        half_size_m = real_world_size_m / 2.0

        meters_per_degree_lat = 111_320.0
        meters_per_degree_lon = 111_320.0 * math.cos(math.radians(center_lat))

        delta_lat = half_size_m / meters_per_degree_lat
        delta_lon = half_size_m / meters_per_degree_lon

        south = center_lat - delta_lat
        north = center_lat + delta_lat
        west = center_lon - delta_lon
        east = center_lon + delta_lon

        bbox = (south, west, north, east)

        if debug:
            print("")
            print("=" * 60)
            print("ATLAS PRODUCT AREA ENGINE REPORT")
            print("=" * 60)
            print(f"Center lat/lon     : {center_lat:.8f}, {center_lon:.8f}")
            print(f"Product size       : {product_size_mm:.2f} mm")
            print(f"Scale ratio        : 1:{scale_ratio}")
            print(f"Real world size    : {real_world_size_m:.2f} m")
            print(
                f"Approx area        : {(real_world_size_m ** 2) / 1_000_000:.3f} km²"
            )
            print(f"BBox south/west    : {south:.8f}, {west:.8f}")
            print(f"BBox north/east    : {north:.8f}, {east:.8f}")
            print("=" * 60)
            print("")

        return bbox

    @staticmethod
    def describe_product_sizes(scale_ratio=DEFAULT_SCALE_RATIO):
        sizes = [140, 200, 260]

        report = []

        for size_mm in sizes:
            real_world_size_m = (size_mm * scale_ratio) / 1000.0
            area_km2 = (real_world_size_m**2) / 1_000_000

            report.append(
                {
                    "product_size_mm": size_mm,
                    "scale_ratio": scale_ratio,
                    "real_world_size_m": real_world_size_m,
                    "area_km2": area_km2,
                }
            )

        return report
