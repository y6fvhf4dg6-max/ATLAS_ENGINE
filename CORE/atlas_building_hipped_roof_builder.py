"""
ATLAS Building Hipped Roof Builder v0.1

Normal şehir binaları için dört eğimli kırma çatı üretir.

İlkeler:
- Yalnız building_roof_profile == "hipped" için çalışır
- Mevcut düz üst kapak üçgenlerini kaldırır
- Footprint sınırını merkez tepe noktasına bağlar
- Gövde duvarları ile tek kapalı dış kabuk oluşturur
- Gerçek AtlasMeshBuilder nokta-Z sözleşmesini destekler
- Geçersiz girdide mesh'i değiştirmeden döndürür
"""

import math


class AtlasBuildingHippedRoofBuilder:
    POINT_PRECISION = 9
    Z_TOLERANCE = 1e-7

    ROOF_SHORT_SPAN_RATIO = 0.24
    ROOF_BODY_HEIGHT_RATIO = 0.14

    MIN_ROOF_HEIGHT_MM = 0.60
    MAX_ROOF_HEIGHT_MM = 2.80

    @staticmethod
    def apply(mesh):
        if not mesh:
            return mesh

        if mesh.get("building_roof_profile") != "hipped":
            return mesh

        top_points = mesh.get("top", [])
        bottom_points = mesh.get("bottom", [])

        if len(top_points) < 3:
            return mesh

        top_z = mesh.get("top_z")
        bottom_z = mesh.get("bottom_z")

        if top_z is None:
            top_z = (
                AtlasBuildingHippedRoofBuilder
                ._derive_z_level(
                    points=top_points,
                    mode="max",
                )
            )

        if bottom_z is None:
            bottom_z = (
                AtlasBuildingHippedRoofBuilder
                ._derive_z_level(
                    points=bottom_points,
                    mode="min",
                )
            )

        if top_z is None or bottom_z is None:
            return mesh

        ring = AtlasBuildingHippedRoofBuilder._clean_ring(
            top_points
        )

        if len(ring) < 3:
            return mesh

        remaining_triangles = []
        removed_top_count = 0

        for triangle in mesh.get("triangles", []):
            if AtlasBuildingHippedRoofBuilder._is_top_triangle(
                triangle=triangle,
                top_z=top_z,
            ):
                removed_top_count += 1
                continue

            remaining_triangles.append(triangle)

        if removed_top_count == 0:
            return mesh

        xs = [point[0] for point in ring]
        ys = [point[1] for point in ring]

        width_mm = max(xs) - min(xs)
        depth_mm = max(ys) - min(ys)
        short_span_mm = min(width_mm, depth_mm)

        if short_span_mm <= 0.0:
            return mesh

        body_height_mm = max(
            0.0,
            float(top_z) - float(bottom_z),
        )

        roof_height_mm = max(
            short_span_mm
            * AtlasBuildingHippedRoofBuilder
            .ROOF_SHORT_SPAN_RATIO,
            body_height_mm
            * AtlasBuildingHippedRoofBuilder
            .ROOF_BODY_HEIGHT_RATIO,
            AtlasBuildingHippedRoofBuilder
            .MIN_ROOF_HEIGHT_MM,
        )

        roof_height_mm = min(
            roof_height_mm,
            AtlasBuildingHippedRoofBuilder
            .MAX_ROOF_HEIGHT_MM,
        )

        centroid_x = (
            sum(point[0] for point in ring)
            / len(ring)
        )
        centroid_y = (
            sum(point[1] for point in ring)
            / len(ring)
        )

        apex = (
            centroid_x,
            centroid_y,
            float(top_z) + roof_height_mm,
        )

        roof_triangles = []

        for index, point_1 in enumerate(ring):
            point_2 = ring[(index + 1) % len(ring)]

            roof_triangles.append(
                (
                    point_1,
                    point_2,
                    apex,
                )
            )

        mesh["triangles"] = [
            *remaining_triangles,
            *roof_triangles,
        ]

        mesh["body_top_z"] = float(top_z)
        mesh["roof_top_z"] = apex[2]
        mesh["top_z"] = apex[2]

        mesh["roof_apex"] = apex
        mesh["roof_height_mm"] = roof_height_mm
        mesh["roof_geometry"] = "hipped"

        mesh["building_hipped_removed_top_triangles"] = (
            removed_top_count
        )
        mesh["building_hipped_roof_triangles"] = (
            roof_triangles
        )
        mesh["building_hipped_roof_applied"] = True

        return mesh

    @staticmethod
    def _derive_z_level(points, mode):
        values = []

        for point in points:
            if point is None or len(point) < 3:
                continue

            try:
                value = float(point[2])
            except (TypeError, ValueError):
                continue

            if not math.isfinite(value):
                continue

            values.append(value)

        if not values:
            return None

        if mode == "min":
            return min(values)

        if mode == "max":
            return max(values)

        raise ValueError(
            f"Unsupported Z derivation mode: {mode}"
        )

    @staticmethod
    def _clean_ring(points):
        clean = []

        for point in points:
            if point is None or len(point) < 3:
                continue

            current = (
                float(point[0]),
                float(point[1]),
                float(point[2]),
            )

            if (
                clean
                and AtlasBuildingHippedRoofBuilder
                ._same_point(clean[-1], current)
            ):
                continue

            clean.append(current)

        if (
            len(clean) > 1
            and AtlasBuildingHippedRoofBuilder
            ._same_point(clean[0], clean[-1])
        ):
            clean.pop()

        return clean

    @staticmethod
    def _is_top_triangle(triangle, top_z):
        if triangle is None or len(triangle) != 3:
            return False

        for point in triangle:
            if point is None or len(point) < 3:
                return False

            if (
                abs(float(point[2]) - float(top_z))
                > AtlasBuildingHippedRoofBuilder
                .Z_TOLERANCE
            ):
                return False

        return True

    @staticmethod
    def _same_point(point_1, point_2):
        return (
            round(
                float(point_1[0]),
                AtlasBuildingHippedRoofBuilder
                .POINT_PRECISION,
            )
            == round(
                float(point_2[0]),
                AtlasBuildingHippedRoofBuilder
                .POINT_PRECISION,
            )
            and round(
                float(point_1[1]),
                AtlasBuildingHippedRoofBuilder
                .POINT_PRECISION,
            )
            == round(
                float(point_2[1]),
                AtlasBuildingHippedRoofBuilder
                .POINT_PRECISION,
            )
            and round(
                float(point_1[2]),
                AtlasBuildingHippedRoofBuilder
                .POINT_PRECISION,
            )
            == round(
                float(point_2[2]),
                AtlasBuildingHippedRoofBuilder
                .POINT_PRECISION,
            )
        )
