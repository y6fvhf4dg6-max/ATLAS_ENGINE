# CORE/atlas_geometry_inspector.py


class AtlasGeometryInspector:
    """
    ATLAS Geometry Inspector v1.0

    Amaç:
    Garip / şüpheli bina footprint'lerini teşhis eder.
    STL üretimini değiştirmez.
    Sadece rapor üretir.
    """

    MIN_AREA_M2 = 20.0
    MIN_MODEL_WIDTH_MM = 1.20
    MIN_MODEL_DEPTH_MM = 1.20
    MIN_POINT_COUNT = 4
    TRIANGLE_POINT_COUNT = 3

    @staticmethod
    def inspect_building(building, scaled_points=None):
        report = {
            "building_id": getattr(building, "building_id", "unknown"),
            "source": getattr(building, "source", "unknown"),
            "building_type": getattr(building, "building_type", None),
            "area_m2": getattr(building, "area_m2", None),
            "perimeter_m": getattr(building, "perimeter_m", None),
            "point_count": getattr(building, "point_count", None),
            "estimated_height": getattr(building, "estimated_height", None),
            "tags": getattr(building, "tags", {}),
            "warnings": [],
        }

        area_m2 = report["area_m2"]
        point_count = report["point_count"]

        if area_m2 is not None and area_m2 < AtlasGeometryInspector.MIN_AREA_M2:
            report["warnings"].append("small_real_world_area")

        if (
            point_count is not None
            and point_count < AtlasGeometryInspector.MIN_POINT_COUNT
        ):
            report["warnings"].append("too_few_points")

        if point_count == AtlasGeometryInspector.TRIANGLE_POINT_COUNT:
            report["warnings"].append("triangle_footprint")

        if scaled_points:
            bounds = AtlasGeometryInspector._bounds_2d(scaled_points)

            if bounds:
                width_mm = bounds["max_x"] - bounds["min_x"]
                depth_mm = bounds["max_y"] - bounds["min_y"]

                report["model_width_mm"] = width_mm
                report["model_depth_mm"] = depth_mm

                if width_mm < AtlasGeometryInspector.MIN_MODEL_WIDTH_MM:
                    report["warnings"].append("too_narrow_model_width")

                if depth_mm < AtlasGeometryInspector.MIN_MODEL_DEPTH_MM:
                    report["warnings"].append("too_narrow_model_depth")

        report["suspect"] = len(report["warnings"]) > 0

        return report

    @staticmethod
    def print_report(report):
        if not report.get("suspect"):
            return

        print("")
        print("=" * 70)
        print("ATLAS GEOMETRY INSPECTOR — SUSPECT BUILDING")
        print("=" * 70)
        print(f"Building ID      : {report.get('building_id')}")
        print(f"Source           : {report.get('source')}")
        print(f"Building type    : {report.get('building_type')}")
        print(f"Area m²          : {report.get('area_m2')}")
        print(f"Perimeter m      : {report.get('perimeter_m')}")
        print(f"Point count      : {report.get('point_count')}")
        print(f"Height estimate  : {report.get('estimated_height')}")
        print(f"Model width mm   : {report.get('model_width_mm', '-')}")
        print(f"Model depth mm   : {report.get('model_depth_mm', '-')}")
        print(f"Warnings         : {', '.join(report.get('warnings', []))}")
        print(f"Tags             : {report.get('tags')}")
        print("=" * 70)
        print("")

    @staticmethod
    def _bounds_2d(points):
        if not points:
            return None

        xs = [point[0] for point in points]
        ys = [point[1] for point in points]

        return {
            "min_x": min(xs),
            "max_x": max(xs),
            "min_y": min(ys),
            "max_y": max(ys),
        }
