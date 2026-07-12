# CORE/atlas_scale_engine.py

import math


class AtlasScaleEngine:
    """
    ATLAS Scale Engine v1.3

    Görev:
    Seçilen harita alanını veya bina kümesini gerçek dünya
    metrelerinden 3D yazıcı tablasına uygun STL milimetre
    ölçülerine dönüştürür.

    v1.2:
    - XY ölçeğini koruyarak dikdörtgen model boyutlarını hesaplar
    - X ve Y eksenlerinde aynı ölçeği kullanır
    - Eski calculate_xy_scale_from_bbox davranışını korur

    v1.3:
    - Sabit XY ölçeğinden gerçek dikdörtgen model ölçülerini hesaplar
    - Castle-focus modunda 1:5500 gibi sabit ölçeklerin korunmasını sağlar
    """

    @staticmethod
    def calculate_dimensions_from_scale(
        bbox,
        xy_scale,
        debug=True,
    ):
        """
        Verilen bbox için sabit XY ölçeğini değiştirmeden
        modelin fiziksel X ve Y ölçülerini hesaplar.

        Örnek:
        xy_scale=5500 değeri 1:5500 ölçeğini temsil eder.
        """

        if xy_scale <= 0.0:
            raise ValueError("xy_scale sıfırdan büyük olmalıdır.")

        south, west, north, east = bbox

        width_m, depth_m = AtlasScaleEngine._bbox_size_meters(
            south=south,
            west=west,
            north=north,
            east=east,
        )

        size_x_mm = width_m * 1000.0 / xy_scale

        size_y_mm = depth_m * 1000.0 / xy_scale

        result = {
            "bbox": bbox,
            "world_width_m": width_m,
            "world_depth_m": depth_m,
            "xy_scale": float(xy_scale),
            "size_x_mm": size_x_mm,
            "size_y_mm": size_y_mm,
        }

        if debug:
            AtlasScaleEngine._print_fixed_scale_report(
                width_m=width_m,
                depth_m=depth_m,
                xy_scale=xy_scale,
                size_x_mm=size_x_mm,
                size_y_mm=size_y_mm,
            )

        return result

    @staticmethod
    def calculate_fit_from_bbox(
        bbox,
        target_size_mm=180,
        bed_width_mm=256,
        bed_depth_mm=256,
        margin_mm=15,
        debug=True,
    ):
        south, west, north, east = bbox

        width_m, depth_m = AtlasScaleEngine._bbox_size_meters(
            south=south,
            west=west,
            north=north,
            east=east,
        )

        xy_scale = AtlasScaleEngine._calculate_xy_scale(
            width_m=width_m,
            depth_m=depth_m,
            target_size_mm=target_size_mm,
            bed_width_mm=bed_width_mm,
            bed_depth_mm=bed_depth_mm,
            margin_mm=margin_mm,
        )

        size_x_mm = width_m * 1000.0 / xy_scale if xy_scale > 0.0 else 0.0

        size_y_mm = depth_m * 1000.0 / xy_scale if xy_scale > 0.0 else 0.0

        result = {
            "bbox": bbox,
            "world_width_m": width_m,
            "world_depth_m": depth_m,
            "xy_scale": xy_scale,
            "size_x_mm": size_x_mm,
            "size_y_mm": size_y_mm,
        }

        if debug:
            AtlasScaleEngine._print_report(
                title="ATLAS SCALE ENGINE REPORT - BBOX FIT",
                width_m=width_m,
                depth_m=depth_m,
                target_size_mm=target_size_mm,
                bed_width_mm=bed_width_mm,
                bed_depth_mm=bed_depth_mm,
                margin_mm=margin_mm,
                xy_scale=xy_scale,
                size_x_mm=size_x_mm,
                size_y_mm=size_y_mm,
            )

        return result

    @staticmethod
    def calculate_xy_scale_from_bbox(
        bbox,
        target_size_mm=180,
        bed_width_mm=256,
        bed_depth_mm=256,
        margin_mm=15,
        debug=True,
    ):
        fit = AtlasScaleEngine.calculate_fit_from_bbox(
            bbox=bbox,
            target_size_mm=target_size_mm,
            bed_width_mm=bed_width_mm,
            bed_depth_mm=bed_depth_mm,
            margin_mm=margin_mm,
            debug=debug,
        )

        return fit["xy_scale"]

    @staticmethod
    def calculate_xy_scale_from_buildings(
        buildings,
        target_size_mm=180,
        bed_width_mm=256,
        bed_depth_mm=256,
        margin_mm=15,
        debug=True,
    ):
        scene_bbox = AtlasScaleEngine.calculate_buildings_bbox(buildings)

        if scene_bbox is None:
            return AtlasScaleEngine.calculate_xy_scale_from_bbox(
                bbox=(0, 0, 0.001, 0.001),
                target_size_mm=target_size_mm,
                bed_width_mm=bed_width_mm,
                bed_depth_mm=bed_depth_mm,
                margin_mm=margin_mm,
                debug=debug,
            )

        fit = AtlasScaleEngine.calculate_fit_from_bbox(
            bbox=scene_bbox,
            target_size_mm=target_size_mm,
            bed_width_mm=bed_width_mm,
            bed_depth_mm=bed_depth_mm,
            margin_mm=margin_mm,
            debug=debug,
        )

        return fit["xy_scale"]

    @staticmethod
    def calculate_buildings_bbox(
        buildings,
    ):
        lats = []
        lons = []

        for building in buildings:
            geometry = AtlasScaleEngine._extract_geometry(building)

            for point in geometry:
                if not point or len(point) < 2:
                    continue

                lat, lon = point

                lats.append(float(lat))

                lons.append(float(lon))

        if not lats or not lons:
            return None

        return (
            min(lats),
            min(lons),
            max(lats),
            max(lons),
        )

    @staticmethod
    def _calculate_xy_scale(
        width_m,
        depth_m,
        target_size_mm,
        bed_width_mm,
        bed_depth_mm,
        margin_mm,
    ):
        usable_width_mm = bed_width_mm - (margin_mm * 2)

        usable_depth_mm = bed_depth_mm - (margin_mm * 2)

        usable_target_mm = min(
            target_size_mm,
            usable_width_mm,
            usable_depth_mm,
        )

        largest_world_dimension_m = max(
            width_m,
            depth_m,
        )

        if largest_world_dimension_m <= 0:
            return 1000.0

        return largest_world_dimension_m * 1000.0 / usable_target_mm

    @staticmethod
    def _bbox_size_meters(
        south,
        west,
        north,
        east,
    ):
        mean_lat = math.radians((south + north) / 2.0)

        meters_per_degree_lat = 111_320

        meters_per_degree_lon = 111_320 * math.cos(mean_lat)

        width_m = abs(east - west) * meters_per_degree_lon

        depth_m = abs(north - south) * meters_per_degree_lat

        return width_m, depth_m

    @staticmethod
    def _extract_geometry(
        building,
    ):
        if building is None:
            return []

        if isinstance(building, dict):
            return building.get("geometry") or building.get("points") or []

        if hasattr(
            building,
            "geometry",
        ):
            return building.geometry

        if hasattr(
            building,
            "points",
        ):
            return building.points

        return []

    @staticmethod
    def _print_fixed_scale_report(
        width_m,
        depth_m,
        xy_scale,
        size_x_mm,
        size_y_mm,
    ):
        print("")
        print("=" * 60)
        print("ATLAS SCALE ENGINE REPORT - FIXED SCALE")
        print("=" * 60)
        print(f"World width       : " f"{width_m:.2f} m")
        print(f"World depth       : " f"{depth_m:.2f} m")
        print(f"Fixed XY scale    : " f"1:{xy_scale:.2f}")
        print(f"Model width       : " f"{size_x_mm:.2f} mm")
        print(f"Model depth       : " f"{size_y_mm:.2f} mm")
        print("=" * 60)
        print("")

    @staticmethod
    def _print_report(
        title,
        width_m,
        depth_m,
        target_size_mm,
        bed_width_mm,
        bed_depth_mm,
        margin_mm,
        xy_scale,
        size_x_mm=None,
        size_y_mm=None,
    ):
        usable_width_mm = bed_width_mm - (margin_mm * 2)

        usable_depth_mm = bed_depth_mm - (margin_mm * 2)

        usable_target_mm = min(
            target_size_mm,
            usable_width_mm,
            usable_depth_mm,
        )

        print("")
        print("=" * 60)
        print(title)
        print("=" * 60)
        print(f"World width       : " f"{width_m:.2f} m")
        print(f"World depth       : " f"{depth_m:.2f} m")
        print(f"Target size       : " f"{target_size_mm:.2f} mm")
        print(f"Usable bed width  : " f"{usable_width_mm:.2f} mm")
        print(f"Usable bed depth  : " f"{usable_depth_mm:.2f} mm")
        print(f"Used target size  : " f"{usable_target_mm:.2f} mm")
        print(f"Calculated scale  : " f"{xy_scale:.2f}")

        if size_x_mm is not None:
            print(f"Model width       : " f"{size_x_mm:.2f} mm")

        if size_y_mm is not None:
            print(f"Model depth       : " f"{size_y_mm:.2f} mm")

        print("=" * 60)
        print("")
