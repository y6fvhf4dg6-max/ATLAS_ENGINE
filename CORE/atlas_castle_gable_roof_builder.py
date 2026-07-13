"""
ATLAS Castle Gable Roof Builder v0.1

Kale içindeki şapel ve uzun kale kanatlarına yönlendirilmiş
beşik çatı geometrisi ekler.

Temel ilkeler:
- Kulelerin piramidal çatı sistemine dokunmaz
- Karmaşık bina footprint'ini değiştirmez
- Footprint'in minimum döndürülmüş dikdörtgeninden ana yönü bulur
- Çatıyı kapalı bir hacim olarak üretir
- Çatı tabanını bina üst yüzeyine çok az gömerek bağlantıyı güçlendirir
"""

import math
import warnings

from shapely.geometry import Polygon


class AtlasCastleGableRoofBuilder:
    SUPPORTED_PROFILES = {
        "chapel",
        "castle_wing",
        "defensive_tower",
        "gate_tower",
    }

    TOWER_PROFILES = {
        "defensive_tower",
        "gate_tower",
    }

    ROOF_SHORT_SPAN_RATIO = {
        "chapel": 0.72,
        "castle_wing": 0.52,
        "defensive_tower": 0.42,
        "gate_tower": 0.38,
    }

    ROOF_BODY_HEIGHT_RATIO = {
        "chapel": 0.42,
        "castle_wing": 0.30,
        "defensive_tower": 0.28,
        "gate_tower": 0.24,
    }

    MIN_ROOF_HEIGHT_MM = {
        "chapel": 1.90,
        "castle_wing": 1.40,
        "defensive_tower": 0.60,
        "gate_tower": 0.60,
    }

    MAX_ROOF_HEIGHT_MM = {
        "chapel": 5.80,
        "castle_wing": 4.40,
        "defensive_tower": 2.20,
        "gate_tower": 2.00,
    }

    MAX_RECTANGLE_AREA_RATIO = {
        "chapel": 1.45,
        "castle_wing": 1.30,
        "defensive_tower": 1.85,
        "gate_tower": 1.85,
    }

    EMBED_DEPTH_MM = 0.04
    MIN_RECTANGLE_SIDE_MM = 0.20
    POINT_PRECISION = 9

    @staticmethod
    def apply(
        mesh,
        castle_profile,
    ):
        if not mesh:
            return mesh

        if castle_profile not in AtlasCastleGableRoofBuilder.SUPPORTED_PROFILES:
            return mesh

        if (
            castle_profile in AtlasCastleGableRoofBuilder.TOWER_PROFILES
            and not mesh.get(
                "castle_roof_skipped_for_gable",
                False,
            )
        ):
            return mesh

        top_z = mesh.get("top_z")
        bottom_z = mesh.get("bottom_z")
        top_points = mesh.get("top", [])

        if top_z is None or bottom_z is None or len(top_points) < 3:
            return mesh

        ring = AtlasCastleGableRoofBuilder._clean_ring(top_points)

        if len(ring) < 3:
            return mesh

        rectangle = AtlasCastleGableRoofBuilder._minimum_rotated_rectangle(
            ring=ring,
            castle_profile=castle_profile,
        )

        if rectangle is None:
            return mesh

        ordered = AtlasCastleGableRoofBuilder._order_rectangle_for_gable(rectangle)

        if ordered is None:
            return mesh

        eave_1_start = ordered["eave_1_start"]
        eave_1_end = ordered["eave_1_end"]
        eave_2_start = ordered["eave_2_start"]
        eave_2_end = ordered["eave_2_end"]

        long_side_mm = ordered["long_side_mm"]
        short_side_mm = ordered["short_side_mm"]

        if (
            long_side_mm < AtlasCastleGableRoofBuilder.MIN_RECTANGLE_SIDE_MM
            or short_side_mm < AtlasCastleGableRoofBuilder.MIN_RECTANGLE_SIDE_MM
        ):
            return mesh

        body_height_mm = max(
            0.0,
            float(top_z) - float(bottom_z),
        )

        span_height_mm = (
            short_side_mm
            * AtlasCastleGableRoofBuilder.ROOF_SHORT_SPAN_RATIO[castle_profile]
        )

        body_height_target_mm = (
            body_height_mm
            * AtlasCastleGableRoofBuilder.ROOF_BODY_HEIGHT_RATIO[castle_profile]
        )

        roof_height_mm = max(
            span_height_mm,
            body_height_target_mm,
        )

        roof_height_mm = max(
            roof_height_mm,
            AtlasCastleGableRoofBuilder.MIN_ROOF_HEIGHT_MM[castle_profile],
        )

        roof_height_mm = min(
            roof_height_mm,
            AtlasCastleGableRoofBuilder.MAX_ROOF_HEIGHT_MM[castle_profile],
        )

        base_z = float(top_z) - AtlasCastleGableRoofBuilder.EMBED_DEPTH_MM

        ridge_z = float(top_z) + roof_height_mm

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
            (eave_1_start[0] + eave_2_start[0]) / 2.0,
            (eave_1_start[1] + eave_2_start[1]) / 2.0,
            ridge_z,
        )

        ridge_end = (
            (eave_1_end[0] + eave_2_end[0]) / 2.0,
            (eave_1_end[1] + eave_2_end[1]) / 2.0,
            ridge_z,
        )

        roof_triangles = [
            # Birinci çatı yamacı
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
            # İkinci çatı yamacı
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
            *mesh.get(
                "triangles",
                [],
            ),
            *roof_triangles,
        ]

        mesh["body_top_z"] = float(top_z)

        mesh["roof_top_z"] = ridge_z
        mesh["top_z"] = ridge_z

        mesh["gable_roof_triangles"] = roof_triangles
        mesh["roof_height_mm"] = roof_height_mm
        mesh["roof_long_side_mm"] = long_side_mm
        mesh["roof_short_side_mm"] = short_side_mm
        mesh["roof_ridge_start"] = ridge_start
        mesh["roof_ridge_end"] = ridge_end

        if castle_profile == "chapel":
            roof_geometry = "steep_gable"
        elif castle_profile in AtlasCastleGableRoofBuilder.TOWER_PROFILES:
            roof_geometry = "tower_gable"
        else:
            roof_geometry = "gable"

        mesh["roof_geometry"] = roof_geometry

        mesh["castle_gable_roof_applied"] = True

        return mesh

    @staticmethod
    def _minimum_rotated_rectangle(
        ring,
        castle_profile,
    ):
        coordinates = [
            (
                float(point[0]),
                float(point[1]),
            )
            for point in ring
        ]

        polygon = Polygon(coordinates)

        if polygon.is_empty:
            return None

        if not polygon.is_valid:
            polygon = polygon.buffer(0)

        if polygon.is_empty or not polygon.is_valid or polygon.area <= 0.0:
            return None

        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=(
                    "divide by zero encountered "
                    "in oriented_envelope"
                ),
                category=RuntimeWarning,
            )
            warnings.filterwarnings(
                "ignore",
                message=(
                    "invalid value encountered "
                    "in oriented_envelope"
                ),
                category=RuntimeWarning,
            )

            rectangle = (
                polygon.minimum_rotated_rectangle
            )

        if rectangle.is_empty or not rectangle.is_valid:
            return None

        rectangle_area_ratio = rectangle.area / max(
            polygon.area,
            1e-12,
        )

        if (
            rectangle_area_ratio
            > AtlasCastleGableRoofBuilder.MAX_RECTANGLE_AREA_RATIO[castle_profile]
        ):
            return None

        coordinates = list(rectangle.exterior.coords)

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

        if castle_profile in AtlasCastleGableRoofBuilder.TOWER_PROFILES:
            area_fill_ratio = polygon.area / max(
                rectangle.area,
                1e-12,
            )

            rectangle_scale = (
                math.sqrt(
                    max(
                        0.0,
                        min(
                            area_fill_ratio,
                            1.0,
                        ),
                    )
                )
                * 0.98
            )

            rectangle_scale = max(
                0.72,
                min(
                    rectangle_scale,
                    1.0,
                ),
            )

            center_x = sum(point[0] for point in result) / len(result)

            center_y = sum(point[1] for point in result) / len(result)

            result = [
                (
                    center_x + (point[0] - center_x) * rectangle_scale,
                    center_y + (point[1] - center_y) * rectangle_scale,
                )
                for point in result
            ]

        return result

    @staticmethod
    def _order_rectangle_for_gable(
        rectangle,
    ):
        if len(rectangle) != 4:
            return None

        p0 = rectangle[0]
        p1 = rectangle[1]
        p2 = rectangle[2]
        p3 = rectangle[3]

        edge_01 = AtlasCastleGableRoofBuilder._distance_xy(
            p0,
            p1,
        )

        edge_12 = AtlasCastleGableRoofBuilder._distance_xy(
            p1,
            p2,
        )

        if edge_01 >= edge_12:
            return {
                "eave_1_start": p0,
                "eave_1_end": p1,
                "eave_2_start": p3,
                "eave_2_end": p2,
                "long_side_mm": edge_01,
                "short_side_mm": edge_12,
            }

        return {
            "eave_1_start": p1,
            "eave_1_end": p2,
            "eave_2_start": p0,
            "eave_2_end": p3,
            "long_side_mm": edge_12,
            "short_side_mm": edge_01,
        }

    @staticmethod
    def _clean_ring(
        points,
    ):
        clean = []

        for point in points:
            if point is None or len(point) < 3:
                continue

            current = (
                float(point[0]),
                float(point[1]),
                float(point[2]),
            )

            if clean and AtlasCastleGableRoofBuilder._same_point(
                clean[-1],
                current,
            ):
                continue

            clean.append(current)

        if len(clean) >= 2 and AtlasCastleGableRoofBuilder._same_point(
            clean[0],
            clean[-1],
        ):
            clean.pop()

        return clean

    @staticmethod
    def _distance_xy(
        point_1,
        point_2,
    ):
        return math.hypot(
            float(point_2[0]) - float(point_1[0]),
            float(point_2[1]) - float(point_1[1]),
        )

    @staticmethod
    def _same_point(
        point_1,
        point_2,
    ):
        return (
            round(
                float(point_1[0]),
                AtlasCastleGableRoofBuilder.POINT_PRECISION,
            )
            == round(
                float(point_2[0]),
                AtlasCastleGableRoofBuilder.POINT_PRECISION,
            )
            and round(
                float(point_1[1]),
                AtlasCastleGableRoofBuilder.POINT_PRECISION,
            )
            == round(
                float(point_2[1]),
                AtlasCastleGableRoofBuilder.POINT_PRECISION,
            )
            and round(
                float(point_1[2]),
                AtlasCastleGableRoofBuilder.POINT_PRECISION,
            )
            == round(
                float(point_2[2]),
                AtlasCastleGableRoofBuilder.POINT_PRECISION,
            )
        )
