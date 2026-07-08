# CORE/atlas_area_selector.py

import math


class AtlasAreaSelector:
    """
    ATLAS Area Selector v1.0

    Görev:
    Kullanıcının seçtiği merkez koordinattan,
    gerçek dünya metre ölçüsüne göre bbox üretmek.

    ATLAS ürün mantığı:
    Kullanıcı bina seçmez.
    Kullanıcı alan seçer.
    """

    @staticmethod
    def bbox_from_center(
        center_lat,
        center_lon,
        width_m,
        depth_m=None,
        debug=True,
    ):
        if depth_m is None:
            depth_m = width_m

        meters_per_degree_lat = 111_320
        meters_per_degree_lon = 111_320 * math.cos(math.radians(center_lat))

        half_width_m = width_m / 2.0
        half_depth_m = depth_m / 2.0

        delta_lat = half_depth_m / meters_per_degree_lat
        delta_lon = half_width_m / meters_per_degree_lon

        bbox = (
            center_lat - delta_lat,  # south
            center_lon - delta_lon,  # west
            center_lat + delta_lat,  # north
            center_lon + delta_lon,  # east
        )

        if debug:
            AtlasAreaSelector._print_report(
                center_lat=center_lat,
                center_lon=center_lon,
                width_m=width_m,
                depth_m=depth_m,
                bbox=bbox,
            )

        return bbox

    @staticmethod
    def _print_report(center_lat, center_lon, width_m, depth_m, bbox):
        print("")
        print("=" * 60)
        print("ATLAS AREA SELECTOR REPORT")
        print("=" * 60)
        print(f"Center lat : {center_lat}")
        print(f"Center lon : {center_lon}")
        print(f"Width      : {width_m:.2f} m")
        print(f"Depth      : {depth_m:.2f} m")
        print(f"BBox       : {bbox}")
        print("=" * 60)
        print("")
