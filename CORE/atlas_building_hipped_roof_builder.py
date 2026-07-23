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

from shapely.geometry import Point
from shapely.geometry import Polygon


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

        apex_xy = (
            AtlasBuildingHippedRoofBuilder
            ._select_apex_xy(ring)
        )

        if apex_xy is None:
            return mesh

        apex = (
            apex_xy[0],
            apex_xy[1],
            float(top_z) + roof_height_mm,
        )

        roof_triangles = []

        ring_coordinates = [
            (float(point[0]), float(point[1]))
            for point in ring
        ]

        ring_is_counter_clockwise = (
            AtlasBuildingHippedRoofBuilder
            ._signed_area_2d(ring_coordinates)
            > 0.0
        )

        for index, point_1 in enumerate(ring):
            point_2 = ring[(index + 1) % len(ring)]

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
    def _select_apex_xy(ring):
        polygon = Polygon(
            [
                (point[0], point[1])
                for point in ring
            ]
        )

        if polygon.is_empty or not polygon.is_valid:
            return None

        coordinates = [
            (float(point[0]), float(point[1]))
            for point in ring
        ]

        kernel = (
            AtlasBuildingHippedRoofBuilder
            ._build_visibility_kernel(coordinates)
        )

        if len(kernel) < 3:
            return None

        kernel_polygon = Polygon(kernel)

        if (
            kernel_polygon.is_empty
            or not kernel_polygon.is_valid
            or kernel_polygon.area
            <= AtlasBuildingHippedRoofBuilder.Z_TOLERANCE
        ):
            return None

        arithmetic_center = Point(
            sum(point[0] for point in coordinates)
            / len(coordinates),
            sum(point[1] for point in coordinates)
            / len(coordinates),
        )

        if kernel_polygon.covers(arithmetic_center):
            selected_point = arithmetic_center
        else:
            selected_point = kernel_polygon.centroid

            if not kernel_polygon.covers(selected_point):
                selected_point = (
                    kernel_polygon.representative_point()
                )

        if not kernel_polygon.covers(selected_point):
            return None

        return (
            float(selected_point.x),
            float(selected_point.y),
        )

    @staticmethod
    def _build_visibility_kernel(coordinates):
        if len(coordinates) < 3:
            return []

        xs = [point[0] for point in coordinates]
        ys = [point[1] for point in coordinates]

        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)

        span = max(
            max_x - min_x,
            max_y - min_y,
            1.0,
        )
        margin = span * 4.0

        kernel = [
            (min_x - margin, min_y - margin),
            (max_x + margin, min_y - margin),
            (max_x + margin, max_y + margin),
            (min_x - margin, max_y + margin),
        ]

        signed_area = (
            AtlasBuildingHippedRoofBuilder
            ._signed_area_2d(coordinates)
        )

        if abs(signed_area) <= (
            AtlasBuildingHippedRoofBuilder
            .Z_TOLERANCE
        ):
            return []

        orientation = 1.0 if signed_area > 0.0 else -1.0

        for index, edge_start in enumerate(coordinates):
            edge_end = coordinates[
                (index + 1) % len(coordinates)
            ]

            kernel = (
                AtlasBuildingHippedRoofBuilder
                ._clip_polygon_to_interior_half_plane(
                    polygon=kernel,
                    edge_start=edge_start,
                    edge_end=edge_end,
                    orientation=orientation,
                )
            )

            if len(kernel) < 3:
                return []

        return kernel

    @staticmethod
    def _clip_polygon_to_interior_half_plane(
        polygon,
        edge_start,
        edge_end,
        orientation,
    ):
        if not polygon:
            return []

        result = []

        previous = polygon[-1]
        previous_value = (
            AtlasBuildingHippedRoofBuilder
            ._oriented_edge_value(
                point=previous,
                edge_start=edge_start,
                edge_end=edge_end,
                orientation=orientation,
            )
        )
        previous_inside = previous_value >= (
            -AtlasBuildingHippedRoofBuilder
            .Z_TOLERANCE
        )

        for current in polygon:
            current_value = (
                AtlasBuildingHippedRoofBuilder
                ._oriented_edge_value(
                    point=current,
                    edge_start=edge_start,
                    edge_end=edge_end,
                    orientation=orientation,
                )
            )
            current_inside = current_value >= (
                -AtlasBuildingHippedRoofBuilder
                .Z_TOLERANCE
            )

            if current_inside != previous_inside:
                denominator = (
                    previous_value - current_value
                )

                if abs(denominator) > (
                    AtlasBuildingHippedRoofBuilder
                    .Z_TOLERANCE
                ):
                    ratio = previous_value / denominator

                    intersection = (
                        previous[0]
                        + ratio
                        * (current[0] - previous[0]),
                        previous[1]
                        + ratio
                        * (current[1] - previous[1]),
                    )
                    result.append(intersection)

            if current_inside:
                result.append(current)

            previous = current
            previous_value = current_value
            previous_inside = current_inside

        return result

    @staticmethod
    def _oriented_edge_value(
        point,
        edge_start,
        edge_end,
        orientation,
    ):
        edge_x = edge_end[0] - edge_start[0]
        edge_y = edge_end[1] - edge_start[1]

        point_x = point[0] - edge_start[0]
        point_y = point[1] - edge_start[1]

        cross_product = (
            edge_x * point_y
            - edge_y * point_x
        )

        return orientation * cross_product

    @staticmethod
    def _signed_area_2d(coordinates):
        area_twice = 0.0

        for index, point_1 in enumerate(coordinates):
            point_2 = coordinates[
                (index + 1) % len(coordinates)
            ]

            area_twice += (
                point_1[0] * point_2[1]
                - point_2[0] * point_1[1]
            )

        return area_twice * 0.5

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
