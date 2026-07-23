"""
ATLAS Building Gable Roof Builder v0.1

Normal şehir binaları için yönlendirilmiş beşik çatı hacmi üretir.

İlkeler:
- Yalnız building_roof_profile == "gable" için çalışır
- Mevcut bina gövdesi üçgenlerini korur
- Minimum döndürülmüş dikdörtgenden ana ekseni bulur
- Mahyayı uzun eksen boyunca yönlendirir
- Çatıyı kapalı bir hacim olarak üretir
- Geçersiz girdide mesh'i değiştirmeden döndürür
"""

import math
import warnings

from shapely.geometry import Polygon


class AtlasBuildingGableRoofBuilder:
    EMBED_DEPTH_MM = 0.04

    ROOF_SHORT_SPAN_RATIO = 0.34
    ROOF_BODY_HEIGHT_RATIO = 0.16

    MIN_ROOF_HEIGHT_MM = 0.60
    MAX_ROOF_HEIGHT_MM = 3.20

    MIN_RECTANGLE_SIDE_MM = 0.20
    MAX_RECTANGLE_AREA_RATIO = 1.34

    @staticmethod
    def apply(mesh):
        if not mesh:
            return mesh

        if mesh.get("building_roof_profile") != "gable":
            return mesh

        top_points = mesh.get("top", [])
        bottom_points = mesh.get("bottom", [])

        if len(top_points) < 4:
            return mesh

        top_z = mesh.get("top_z")
        bottom_z = mesh.get("bottom_z")

        if top_z is None:
            top_z = (
                AtlasBuildingGableRoofBuilder
                ._derive_z_level(
                    points=top_points,
                    mode="max",
                )
            )

        if bottom_z is None:
            bottom_z = (
                AtlasBuildingGableRoofBuilder
                ._derive_z_level(
                    points=bottom_points,
                    mode="min",
                )
            )

        if top_z is None or bottom_z is None:
            return mesh

        ring = AtlasBuildingGableRoofBuilder._clean_ring(
            top_points
        )

        if len(ring) < 4:
            return mesh

        rectangle = (
            AtlasBuildingGableRoofBuilder
            ._minimum_rotated_rectangle(ring)
        )

        if rectangle is None:
            return mesh

        ordered = (
            AtlasBuildingGableRoofBuilder
            ._order_rectangle_for_gable(rectangle)
        )

        if ordered is None:
            return mesh

        long_side_mm = ordered["long_side_mm"]
        short_side_mm = ordered["short_side_mm"]

        if (
            long_side_mm
            < AtlasBuildingGableRoofBuilder
            .MIN_RECTANGLE_SIDE_MM
            or short_side_mm
            < AtlasBuildingGableRoofBuilder
            .MIN_RECTANGLE_SIDE_MM
        ):
            return mesh

        body_height_mm = max(
            0.0,
            float(top_z) - float(bottom_z),
        )

        roof_height_mm = max(
            short_side_mm
            * AtlasBuildingGableRoofBuilder
            .ROOF_SHORT_SPAN_RATIO,
            body_height_mm
            * AtlasBuildingGableRoofBuilder
            .ROOF_BODY_HEIGHT_RATIO,
            AtlasBuildingGableRoofBuilder
            .MIN_ROOF_HEIGHT_MM,
        )

        roof_height_mm = min(
            roof_height_mm,
            AtlasBuildingGableRoofBuilder
            .MAX_ROOF_HEIGHT_MM,
        )

        base_z = (
            float(top_z)
            - AtlasBuildingGableRoofBuilder
            .EMBED_DEPTH_MM
        )
        ridge_z = float(top_z) + roof_height_mm

        eave_1_start = ordered["eave_1_start"]
        eave_1_end = ordered["eave_1_end"]
        eave_2_start = ordered["eave_2_start"]
        eave_2_end = ordered["eave_2_end"]

        a = (
            eave_1_start[0],
            eave_1_start[1],
            base_z,
        )
        b = (
            eave_1_end[0],
            eave_1_end[1],
            base_z,
        )
        c = (
            eave_2_end[0],
            eave_2_end[1],
            base_z,
        )
        d = (
            eave_2_start[0],
            eave_2_start[1],
            base_z,
        )

        ridge_start = (
            (
                eave_1_start[0]
                + eave_2_start[0]
            )
            / 2.0,
            (
                eave_1_start[1]
                + eave_2_start[1]
            )
            / 2.0,
            ridge_z,
        )

        ridge_end = (
            (
                eave_1_end[0]
                + eave_2_end[0]
            )
            / 2.0,
            (
                eave_1_end[1]
                + eave_2_end[1]
            )
            / 2.0,
            ridge_z,
        )

        roof_triangles = [
            # Birinci eğimli yüzey
            (
                a,
                b,
                ridge_end,
            ),
            (
                a,
                ridge_end,
                ridge_start,
            ),
            # İkinci eğimli yüzey
            (
                d,
                ridge_start,
                ridge_end,
            ),
            (
                d,
                ridge_end,
                c,
            ),
            # Ön üçgen alın
            (
                a,
                ridge_start,
                d,
            ),
            # Arka üçgen alın
            (
                b,
                c,
                ridge_end,
            ),
            # Kapalı alt yüzey
            (
                a,
                d,
                c,
            ),
            (
                a,
                c,
                b,
            ),
        ]

        mesh["triangles"] = [
            *mesh.get("triangles", []),
            *roof_triangles,
        ]

        mesh["body_top_z"] = float(top_z)
        mesh["roof_top_z"] = ridge_z
        mesh["top_z"] = ridge_z

        mesh["building_gable_roof_triangles"] = (
            roof_triangles
        )
        mesh["roof_height_mm"] = roof_height_mm
        mesh["roof_long_side_mm"] = long_side_mm
        mesh["roof_short_side_mm"] = short_side_mm
        mesh["roof_ridge_start"] = ridge_start
        mesh["roof_ridge_end"] = ridge_end
        mesh["roof_geometry"] = "gable"
        mesh["building_gable_roof_applied"] = True

        return mesh

    @staticmethod
    def _derive_z_level(points, mode):
        values = []

        for point in points:
            if len(point) < 3:
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
        ring = []

        for point in points:
            if len(point) < 2:
                continue

            candidate = (
                float(point[0]),
                float(point[1]),
            )

            if not ring or candidate != ring[-1]:
                ring.append(candidate)

        if len(ring) > 1 and ring[0] == ring[-1]:
            ring.pop()

        return ring

    @staticmethod
    def _minimum_rotated_rectangle(ring):
        polygon = Polygon(ring)

        if polygon.is_empty:
            return None

        if not polygon.is_valid:
            polygon = polygon.buffer(0)

        if (
            polygon.is_empty
            or not polygon.is_valid
            or polygon.area <= 0.0
        ):
            return None

        with warnings.catch_warnings():
            warnings.simplefilter(
                "ignore",
                category=RuntimeWarning,
            )
            rectangle = (
                polygon.minimum_rotated_rectangle
            )

        if rectangle.is_empty or not rectangle.is_valid:
            return None

        rectangle_area_ratio = (
            rectangle.area
            / max(polygon.area, 1e-12)
        )

        if (
            rectangle_area_ratio
            > AtlasBuildingGableRoofBuilder
            .MAX_RECTANGLE_AREA_RATIO
        ):
            return None

        coordinates = list(
            rectangle.exterior.coords
        )

        if len(coordinates) < 5:
            return None

        result = [
            (
                float(x),
                float(y),
            )
            for x, y in coordinates[:-1]
        ]

        if len(result) != 4:
            return None

        return result

    @staticmethod
    def _order_rectangle_for_gable(rectangle):
        if len(rectangle) != 4:
            return None

        edge_lengths = []

        for index in range(4):
            start = rectangle[index]
            end = rectangle[(index + 1) % 4]

            edge_lengths.append(
                math.hypot(
                    end[0] - start[0],
                    end[1] - start[1],
                )
            )

        long_edge_index = max(
            range(4),
            key=lambda index: edge_lengths[index],
        )

        opposite_edge_index = (
            long_edge_index + 2
        ) % 4

        eave_1_start = rectangle[
            long_edge_index
        ]
        eave_1_end = rectangle[
            (long_edge_index + 1) % 4
        ]

        eave_2_start = rectangle[
            (opposite_edge_index + 1) % 4
        ]
        eave_2_end = rectangle[
            opposite_edge_index
        ]

        long_side_mm = edge_lengths[
            long_edge_index
        ]

        short_side_mm = min(
            edge_lengths[
                (long_edge_index + 1) % 4
            ],
            edge_lengths[
                (long_edge_index - 1) % 4
            ],
        )

        return {
            "eave_1_start": eave_1_start,
            "eave_1_end": eave_1_end,
            "eave_2_start": eave_2_start,
            "eave_2_end": eave_2_end,
            "long_side_mm": long_side_mm,
            "short_side_mm": short_side_mm,
        }
