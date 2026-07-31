"""
ATLAS Building Pyramidal Roof Builder v0.1

Normal şehir binaları ve building:part kuleleri için piramidal çatı üretir.

İlkeler:
- Yalnız building_roof_profile == "pyramidal" için çalışır
- Mevcut düz üst kapak üçgenlerini kaldırır
- Footprint sınırını tek merkez tepe noktasına bağlar
- OSM roof:height değerini ürün ölçeğine dönüştürür
- Geçersiz girdide mesh'i değiştirmeden döndürür
"""


class AtlasBuildingPyramidalRoofBuilder:
    Z_TOLERANCE = 1e-7

    DEFAULT_ROOF_HEIGHT_RATIO = 0.35
    MIN_ROOF_HEIGHT_MM = 0.60
    MAX_INFERRED_ROOF_HEIGHT_MM = 8.00

    @staticmethod
    def apply(
        mesh,
        roof_height_m=None,
        coordinate_engine=None,
    ):
        if not mesh:
            return mesh

        if mesh.get("building_roof_profile") != "pyramidal":
            return mesh

        if mesh.get("is_castle_building") is True:
            return mesh

        top_points = AtlasBuildingPyramidalRoofBuilder._clean_ring(
            mesh.get("top", [])
        )

        if len(top_points) < 3:
            return mesh

        top_z = mesh.get("top_z")

        if top_z is None:
            top_z = AtlasBuildingPyramidalRoofBuilder._derive_z_level(
                top_points,
                mode="max",
            )

        bottom_z = mesh.get("bottom_z")

        if bottom_z is None:
            bottom_z = AtlasBuildingPyramidalRoofBuilder._derive_z_level(
                mesh.get("bottom", []),
                mode="min",
            )

        if top_z is None:
            return mesh

        remaining_triangles = []
        removed_top_count = 0

        for triangle in mesh.get("triangles", []):
            if AtlasBuildingPyramidalRoofBuilder._is_top_triangle(
                triangle,
                float(top_z),
            ):
                removed_top_count += 1
                continue

            remaining_triangles.append(triangle)

        if removed_top_count == 0:
            return mesh

        roof_height_mm = (
            AtlasBuildingPyramidalRoofBuilder
            ._resolve_roof_height_mm(
                roof_height_m=roof_height_m,
                coordinate_engine=coordinate_engine,
                top_points=top_points,
                top_z=float(top_z),
                bottom_z=bottom_z,
            )
        )

        if roof_height_mm <= 0.0:
            return mesh

        apex_x = (
            sum(float(point[0]) for point in top_points)
            / len(top_points)
        )
        apex_y = (
            sum(float(point[1]) for point in top_points)
            / len(top_points)
        )

        apex = (
            apex_x,
            apex_y,
            float(top_z) + roof_height_mm,
        )

        ring_is_counter_clockwise = (
            AtlasBuildingPyramidalRoofBuilder
            ._signed_area_2d(top_points)
            > 0.0
        )

        roof_triangles = []

        for index, point_1 in enumerate(top_points):
            point_2 = top_points[
                (index + 1) % len(top_points)
            ]

            if ring_is_counter_clockwise:
                triangle = (
                    point_1,
                    point_2,
                    apex,
                )
            else:
                triangle = (
                    point_2,
                    point_1,
                    apex,
                )

            roof_triangles.append(triangle)

        mesh["triangles"] = [
            *remaining_triangles,
            *roof_triangles,
        ]

        mesh["body_top_z"] = float(top_z)
        mesh["roof_top_z"] = apex[2]
        mesh["top_z"] = apex[2]

        mesh["roof_apex"] = apex
        mesh["roof_height_mm"] = roof_height_mm
        mesh["roof_geometry"] = "pyramidal"

        mesh[
            "building_pyramidal_removed_top_triangles"
        ] = removed_top_count
        mesh[
            "building_pyramidal_roof_triangles"
        ] = roof_triangles
        mesh["building_flat_roof_triangles"] = []
        mesh["building_roof_triangles"] = roof_triangles
        mesh["building_pyramidal_roof_applied"] = True

        return mesh

    @staticmethod
    def _resolve_roof_height_mm(
        roof_height_m,
        coordinate_engine,
        top_points,
        top_z,
        bottom_z,
    ):
        parsed_roof_height_m = (
            AtlasBuildingPyramidalRoofBuilder
            ._parse_positive_float(roof_height_m)
        )

        scale_ratio = getattr(
            coordinate_engine,
            "scale_ratio",
            None,
        )

        if (
            parsed_roof_height_m is not None
            and scale_ratio is not None
            and float(scale_ratio) > 0.0
        ):
            return (
                parsed_roof_height_m
                * 1000.0
                / float(scale_ratio)
            )

        xs = [float(point[0]) for point in top_points]
        ys = [float(point[1]) for point in top_points]

        short_span_mm = min(
            max(xs) - min(xs),
            max(ys) - min(ys),
        )

        body_height_mm = 0.0

        if bottom_z is not None:
            body_height_mm = max(
                0.0,
                float(top_z) - float(bottom_z),
            )

        inferred_height_mm = max(
            short_span_mm
            * AtlasBuildingPyramidalRoofBuilder
            .DEFAULT_ROOF_HEIGHT_RATIO,
            body_height_mm
            * AtlasBuildingPyramidalRoofBuilder
            .DEFAULT_ROOF_HEIGHT_RATIO,
            AtlasBuildingPyramidalRoofBuilder
            .MIN_ROOF_HEIGHT_MM,
        )

        return min(
            inferred_height_mm,
            AtlasBuildingPyramidalRoofBuilder
            .MAX_INFERRED_ROOF_HEIGHT_MM,
        )

    @staticmethod
    def _parse_positive_float(value):
        if value is None:
            return None

        try:
            parsed = float(
                str(value)
                .strip()
                .lower()
                .replace("meters", "")
                .replace("meter", "")
                .replace("metres", "")
                .replace("metre", "")
                .replace("m", "")
                .strip()
            )
        except (TypeError, ValueError):
            return None

        if parsed <= 0.0:
            return None

        return parsed

    @staticmethod
    def _clean_ring(points):
        cleaned = []

        for point in points:
            if len(point) < 3:
                continue

            normalized = (
                float(point[0]),
                float(point[1]),
                float(point[2]),
            )

            if cleaned and normalized == cleaned[-1]:
                continue

            cleaned.append(normalized)

        if (
            len(cleaned) > 1
            and cleaned[0] == cleaned[-1]
        ):
            cleaned.pop()

        return cleaned

    @staticmethod
    def _derive_z_level(points, mode):
        values = [
            float(point[2])
            for point in points
            if len(point) >= 3
        ]

        if not values:
            return None

        if mode == "max":
            return max(values)

        return min(values)

    @staticmethod
    def _is_top_triangle(triangle, top_z):
        if len(triangle) != 3:
            return False

        return all(
            len(point) >= 3
            and abs(float(point[2]) - top_z)
            <= AtlasBuildingPyramidalRoofBuilder.Z_TOLERANCE
            for point in triangle
        )

    @staticmethod
    def _signed_area_2d(points):
        area = 0.0

        for index, point_1 in enumerate(points):
            point_2 = points[
                (index + 1) % len(points)
            ]

            area += (
                float(point_1[0]) * float(point_2[1])
                - float(point_2[0]) * float(point_1[1])
            )

        return area * 0.5
