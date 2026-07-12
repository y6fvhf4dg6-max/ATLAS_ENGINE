"""
ATLAS Castle Multi-Gable Roof Builder v0.1

Tek bir minimum rotated rectangle ile güvenli biçimde
örtülemeyen karmaşık kale kanatlarını birkaç basit parçaya
ayırır ve her uygun parçaya ayrı beşik çatı ekler.

Temel ilkeler:
- Yalnız castle_wing profiline uygulanır
- Mevcut tek beşik çatı başarılıysa işlem yapmaz
- Ham bina footprint'ini değiştirmez
- Ana eksene dik geometrik bölmeler kullanır
- Çok küçük veya güvensiz parçaları atlar
- Çatı parçalarını kapalı hacim olarak üretir
"""

import math
import warnings

from shapely.affinity import scale
from shapely.affinity import translate
from shapely.geometry import LineString
from shapely.geometry import Polygon
from shapely.ops import split


class AtlasCastleMultiGableRoofBuilder:
    SUPPORTED_PROFILES = {
        "castle_wing",
        "chapel",
    }

    MAX_ACCEPTED_RECTANGLE_RATIO = 1.30
    MAX_RECURSION_DEPTH = 3
    MIN_PIECE_AREA_RATIO = 0.10
    MIN_RECTANGLE_SIDE_MM = 0.35
    MAX_ROOF_PIECES = 4

    ROOF_SHORT_SPAN_RATIO = {
        "castle_wing": 0.52,
        "chapel": 0.72,
    }
    ROOF_BODY_HEIGHT_RATIO = {
        "castle_wing": 0.30,
        "chapel": 0.42,
    }
    MIN_ROOF_HEIGHT_MM = 1.40
    MAX_ROOF_HEIGHT_MM = 4.40

    EMBED_DEPTH_MM = 0.04
    POINT_PRECISION = 9
    EPSILON = 1e-9

    SAFE_RECTANGLE_SHRINK_FACTOR = 0.94
    SAFE_RECTANGLE_MIN_SCALE = 0.55
    SAFE_RECTANGLE_MAX_STEPS = 12
    MIN_SAFE_RECTANGLE_COVERAGE = 0.55

    @staticmethod
    def apply(
        mesh,
        castle_profile,
    ):
        if not mesh:
            return mesh

        if castle_profile not in AtlasCastleMultiGableRoofBuilder.SUPPORTED_PROFILES:
            return mesh

        # Tek beşik çatı daha önce başarıyla üretildiyse
        # ikinci bir çatı sistemi uygulanmaz.
        if mesh.get("castle_gable_roof_applied"):
            return mesh

        top_z = mesh.get("top_z")
        bottom_z = mesh.get("bottom_z")
        top_points = mesh.get("top", [])

        if top_z is None or bottom_z is None or len(top_points) < 3:
            return mesh

        ring = AtlasCastleMultiGableRoofBuilder._clean_ring(top_points)

        polygon = AtlasCastleMultiGableRoofBuilder._polygon_from_ring(ring)

        if polygon is None:
            return mesh

        pieces = AtlasCastleMultiGableRoofBuilder._decompose_polygon(
            polygon=polygon,
            root_area=polygon.area,
            depth=0,
        )

        if not pieces:
            return mesh

        pieces = sorted(
            pieces,
            key=lambda current: current.area,
            reverse=True,
        )[: AtlasCastleMultiGableRoofBuilder.MAX_ROOF_PIECES]

        body_height_mm = max(
            0.0,
            float(top_z) - float(bottom_z),
        )

        all_roof_triangles = []
        roof_records = []
        maximum_roof_z = float(top_z)

        for piece_index, piece in enumerate(pieces):
            roof = AtlasCastleMultiGableRoofBuilder._build_piece_roof(
                polygon=piece,
                top_z=float(top_z),
                body_height_mm=body_height_mm,
                castle_profile=castle_profile,
            )

            if roof is None:
                continue

            all_roof_triangles.extend(roof["triangles"])

            maximum_roof_z = max(
                maximum_roof_z,
                roof["roof_top_z"],
            )

            roof_records.append(
                {
                    "piece_index": piece_index,
                    "polygon_area": piece.area,
                    "rectangle_ratio": roof["rectangle_ratio"],
                    "long_side_mm": roof["long_side_mm"],
                    "short_side_mm": roof["short_side_mm"],
                    "roof_height_mm": roof["roof_height_mm"],
                    "ridge_start": roof["ridge_start"],
                    "ridge_end": roof["ridge_end"],
                }
            )

        if not all_roof_triangles:
            return mesh

        mesh["triangles"] = [
            *mesh.get("triangles", []),
            *all_roof_triangles,
        ]

        mesh["body_top_z"] = float(top_z)
        mesh["roof_top_z"] = maximum_roof_z
        mesh["top_z"] = maximum_roof_z

        mesh["multi_gable_roof_triangles"] = all_roof_triangles
        mesh["multi_gable_roof_records"] = roof_records
        mesh["multi_gable_roof_piece_count"] = len(roof_records)
        mesh["roof_geometry"] = "multi_gable"
        mesh["castle_multi_gable_roof_applied"] = True

        return mesh

    @staticmethod
    def _decompose_polygon(
        polygon,
        root_area,
        depth,
    ):
        rectangle = AtlasCastleMultiGableRoofBuilder._minimum_rotated_rectangle(polygon)

        if rectangle is None:
            return []

        rectangle_ratio = rectangle.area / max(
            polygon.area,
            AtlasCastleMultiGableRoofBuilder.EPSILON,
        )

        if (
            rectangle_ratio
            <= AtlasCastleMultiGableRoofBuilder.MAX_ACCEPTED_RECTANGLE_RATIO
        ):
            return [polygon]

        if depth >= AtlasCastleMultiGableRoofBuilder.MAX_RECURSION_DEPTH:
            return []

        split_result = AtlasCastleMultiGableRoofBuilder._find_best_split(
            polygon=polygon,
            root_area=root_area,
        )

        if not split_result:
            return []

        accepted = []

        for child in split_result:
            accepted.extend(
                AtlasCastleMultiGableRoofBuilder._decompose_polygon(
                    polygon=child,
                    root_area=root_area,
                    depth=depth + 1,
                )
            )

        return accepted

    @staticmethod
    def _find_best_split(
        polygon,
        root_area,
    ):
        axis = AtlasCastleMultiGableRoofBuilder._principal_axis(polygon)

        if axis is None:
            return None

        ux, uy = axis
        vx, vy = -uy, ux

        centroid = polygon.centroid

        vertices = list(polygon.exterior.coords)[:-1]

        projections = []

        for x, y in vertices:
            projection = (x - centroid.x) * ux + (y - centroid.y) * uy

            projections.append(projection)

        if len(projections) < 4:
            return None

        minimum_projection = min(projections)
        maximum_projection = max(projections)

        span = maximum_projection - minimum_projection

        if span <= AtlasCastleMultiGableRoofBuilder.EPSILON:
            return None

        candidate_values = sorted(
            {
                round(value, 9)
                for value in projections
                if (
                    value > minimum_projection + span * 0.12
                    and value < maximum_projection - span * 0.12
                )
            }
        )

        if not candidate_values:
            candidate_values = [(minimum_projection + maximum_projection) / 2.0]

        best_parts = None
        best_score = None

        line_half_length = max(
            span * 5.0,
            1000.0,
        )

        for split_projection in candidate_values:
            split_center_x = centroid.x + ux * split_projection

            split_center_y = centroid.y + uy * split_projection

            cutter = LineString(
                [
                    (
                        split_center_x - vx * line_half_length,
                        split_center_y - vy * line_half_length,
                    ),
                    (
                        split_center_x + vx * line_half_length,
                        split_center_y + vy * line_half_length,
                    ),
                ]
            )

            try:
                result = split(
                    polygon,
                    cutter,
                )
            except Exception:
                continue

            parts = [
                geometry
                for geometry in result.geoms
                if (
                    geometry.geom_type == "Polygon"
                    and geometry.area
                    >= root_area * AtlasCastleMultiGableRoofBuilder.MIN_PIECE_AREA_RATIO
                )
            ]

            if len(parts) < 2:
                continue

            total_area = sum(part.area for part in parts)

            if total_area < polygon.area * 0.97:
                continue

            score = 0.0

            for part in parts:
                part_rectangle = (
                    AtlasCastleMultiGableRoofBuilder._minimum_rotated_rectangle(part)
                )

                if part_rectangle is None:
                    score = None
                    break

                part_ratio = part_rectangle.area / max(
                    part.area,
                    AtlasCastleMultiGableRoofBuilder.EPSILON,
                )

                score += part_ratio * part.area

            if score is None:
                continue

            score /= max(
                total_area,
                AtlasCastleMultiGableRoofBuilder.EPSILON,
            )

            if best_score is None or score < best_score:
                best_score = score
                best_parts = parts

        return best_parts

    @staticmethod
    def _principal_axis(
        polygon,
    ):
        rectangle = AtlasCastleMultiGableRoofBuilder._minimum_rotated_rectangle(polygon)

        if rectangle is None:
            return None

        coordinates = list(rectangle.exterior.coords)[:-1]

        if len(coordinates) != 4:
            return None

        best_vector = None
        best_length = -1.0

        for index, point_1 in enumerate(coordinates):
            point_2 = coordinates[(index + 1) % len(coordinates)]

            dx = point_2[0] - point_1[0]

            dy = point_2[1] - point_1[1]

            length = math.hypot(
                dx,
                dy,
            )

            if length > best_length:
                best_length = length
                best_vector = (
                    dx,
                    dy,
                )

        if (
            best_vector is None
            or best_length <= AtlasCastleMultiGableRoofBuilder.EPSILON
        ):
            return None

        return (
            best_vector[0] / best_length,
            best_vector[1] / best_length,
        )

    @staticmethod
    def _build_piece_roof(
        polygon,
        top_z,
        body_height_mm,
        castle_profile,
    ):
        outer_rectangle = AtlasCastleMultiGableRoofBuilder._minimum_rotated_rectangle(
            polygon
        )

        if outer_rectangle is None:
            return None

        outer_rectangle_ratio = outer_rectangle.area / max(
            polygon.area,
            AtlasCastleMultiGableRoofBuilder.EPSILON,
        )

        if (
            outer_rectangle_ratio
            > AtlasCastleMultiGableRoofBuilder.MAX_ACCEPTED_RECTANGLE_RATIO
        ):
            return None

        rectangle = AtlasCastleMultiGableRoofBuilder._fit_rectangle_inside_polygon(
            polygon=polygon,
            rectangle=outer_rectangle,
        )

        if rectangle is None:
            return None

        rectangle_ratio = rectangle.area / max(
            polygon.area,
            AtlasCastleMultiGableRoofBuilder.EPSILON,
        )

        if (
            rectangle_ratio
            < AtlasCastleMultiGableRoofBuilder.MIN_SAFE_RECTANGLE_COVERAGE
        ):
            return None

        rectangle_coordinates = list(rectangle.exterior.coords)[:-1]

        ordered = AtlasCastleMultiGableRoofBuilder._order_rectangle(
            rectangle_coordinates
        )

        if ordered is None:
            return None

        long_side_mm = ordered["long_side_mm"]
        short_side_mm = ordered["short_side_mm"]

        if (
            long_side_mm < AtlasCastleMultiGableRoofBuilder.MIN_RECTANGLE_SIDE_MM
            or short_side_mm < AtlasCastleMultiGableRoofBuilder.MIN_RECTANGLE_SIDE_MM
        ):
            return None

        short_span_ratio = AtlasCastleMultiGableRoofBuilder.ROOF_SHORT_SPAN_RATIO[
            castle_profile
        ]

        body_height_ratio = AtlasCastleMultiGableRoofBuilder.ROOF_BODY_HEIGHT_RATIO[
            castle_profile
        ]

        if castle_profile == "chapel":
            roof_height_mm = short_side_mm * short_span_ratio
        else:
            roof_height_mm = max(
                short_side_mm * short_span_ratio,
                body_height_mm * body_height_ratio,
            )

        minimum_roof_height_mm = (
            0.45
            if castle_profile == "chapel"
            else AtlasCastleMultiGableRoofBuilder.MIN_ROOF_HEIGHT_MM
        )

        roof_height_mm = max(
            roof_height_mm,
            minimum_roof_height_mm,
        )

        roof_height_mm = min(
            roof_height_mm,
            AtlasCastleMultiGableRoofBuilder.MAX_ROOF_HEIGHT_MM,
        )

        base_z = top_z - AtlasCastleMultiGableRoofBuilder.EMBED_DEPTH_MM

        ridge_z = top_z + roof_height_mm

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
            (eave_1_start[0] + eave_2_start[0]) / 2.0,
            (eave_1_start[1] + eave_2_start[1]) / 2.0,
            ridge_z,
        )

        ridge_end = (
            (eave_1_end[0] + eave_2_end[0]) / 2.0,
            (eave_1_end[1] + eave_2_end[1]) / 2.0,
            ridge_z,
        )

        triangles = [
            (a, b, ridge_end),
            (a, ridge_end, ridge_start),
            (d, ridge_start, ridge_end),
            (d, ridge_end, c),
            (a, ridge_start, d),
            (b, c, ridge_end),
            (a, d, c),
            (a, c, b),
        ]

        return {
            "triangles": triangles,
            "roof_top_z": ridge_z,
            "roof_height_mm": roof_height_mm,
            "rectangle_ratio": rectangle_ratio,
            "long_side_mm": long_side_mm,
            "short_side_mm": short_side_mm,
            "ridge_start": ridge_start,
            "ridge_end": ridge_end,
        }

    @staticmethod
    def _order_rectangle(
        rectangle,
    ):
        if len(rectangle) != 4:
            return None

        p0 = rectangle[0]
        p1 = rectangle[1]
        p2 = rectangle[2]
        p3 = rectangle[3]

        edge_01 = AtlasCastleMultiGableRoofBuilder._distance_xy(
            p0,
            p1,
        )

        edge_12 = AtlasCastleMultiGableRoofBuilder._distance_xy(
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
    def _minimum_rotated_rectangle(
        polygon,
    ):
        if polygon is None or polygon.is_empty:
            return None

        if polygon.geom_type != "Polygon":
            return None

        if not polygon.is_valid:
            polygon = polygon.buffer(0)

        if (
            polygon.is_empty
            or not polygon.is_valid
            or polygon.geom_type != "Polygon"
            or polygon.area <= AtlasCastleMultiGableRoofBuilder.EPSILON
        ):
            return None

        try:
            with warnings.catch_warnings():
                warnings.simplefilter(
                    "ignore",
                    RuntimeWarning,
                )

                rectangle = polygon.minimum_rotated_rectangle
        except Exception:
            return None

        if (
            rectangle is None
            or rectangle.is_empty
            or not rectangle.is_valid
            or rectangle.geom_type != "Polygon"
            or rectangle.area <= AtlasCastleMultiGableRoofBuilder.EPSILON
        ):
            return None

        coordinates = list(rectangle.exterior.coords)

        if not all(
            math.isfinite(float(x)) and math.isfinite(float(y)) for x, y in coordinates
        ):
            return None

        return rectangle

    @staticmethod
    def _fit_rectangle_inside_polygon(
        polygon,
        rectangle,
    ):
        if (
            polygon is None
            or rectangle is None
            or polygon.is_empty
            or rectangle.is_empty
        ):
            return None

        tolerance = max(
            AtlasCastleMultiGableRoofBuilder.EPSILON,
            1e-7,
        )

        safe_polygon = polygon.buffer(tolerance)

        if safe_polygon.is_empty or not safe_polygon.is_valid:
            return None

        if safe_polygon.covers(rectangle):
            return rectangle

        rectangle_coordinates = list(rectangle.exterior.coords)[:-1]

        if len(rectangle_coordinates) != 4:
            return None

        p0 = rectangle_coordinates[0]
        p1 = rectangle_coordinates[1]
        p2 = rectangle_coordinates[2]

        edge_01_x = float(p1[0]) - float(p0[0])
        edge_01_y = float(p1[1]) - float(p0[1])
        edge_12_x = float(p2[0]) - float(p1[0])
        edge_12_y = float(p2[1]) - float(p1[1])

        edge_01_length = math.hypot(
            edge_01_x,
            edge_01_y,
        )

        edge_12_length = math.hypot(
            edge_12_x,
            edge_12_y,
        )

        if (
            edge_01_length <= AtlasCastleMultiGableRoofBuilder.EPSILON
            or edge_12_length <= AtlasCastleMultiGableRoofBuilder.EPSILON
        ):
            return None

        axis_1 = (
            edge_01_x / edge_01_length,
            edge_01_y / edge_01_length,
        )

        axis_2 = (
            edge_12_x / edge_12_length,
            edge_12_y / edge_12_length,
        )

        offset_factors = (
            0.0,
            -0.04,
            0.04,
            -0.08,
            0.08,
            -0.12,
            0.12,
        )

        current_scale = 1.0

        for _ in range(AtlasCastleMultiGableRoofBuilder.SAFE_RECTANGLE_MAX_STEPS):
            current_scale *= (
                AtlasCastleMultiGableRoofBuilder.SAFE_RECTANGLE_SHRINK_FACTOR
            )

            if (
                current_scale
                < AtlasCastleMultiGableRoofBuilder.SAFE_RECTANGLE_MIN_SCALE
            ):
                break

            scaled_rectangle = scale(
                rectangle,
                xfact=current_scale,
                yfact=current_scale,
                origin="centroid",
            )

            if (
                scaled_rectangle.is_empty
                or not scaled_rectangle.is_valid
                or scaled_rectangle.area <= AtlasCastleMultiGableRoofBuilder.EPSILON
            ):
                continue

            if safe_polygon.covers(scaled_rectangle):
                return scaled_rectangle

            for factor_1 in offset_factors:
                for factor_2 in offset_factors:
                    if factor_1 == 0.0 and factor_2 == 0.0:
                        continue

                    offset_x = (
                        axis_1[0] * edge_01_length * factor_1
                        + axis_2[0] * edge_12_length * factor_2
                    )

                    offset_y = (
                        axis_1[1] * edge_01_length * factor_1
                        + axis_2[1] * edge_12_length * factor_2
                    )

                    candidate = translate(
                        scaled_rectangle,
                        xoff=offset_x,
                        yoff=offset_y,
                    )

                    if (
                        candidate.is_empty
                        or not candidate.is_valid
                        or candidate.area <= AtlasCastleMultiGableRoofBuilder.EPSILON
                    ):
                        continue

                    if safe_polygon.covers(candidate):
                        return candidate

        return None

    @staticmethod
    def _polygon_from_ring(
        ring,
    ):
        if len(ring) < 3:
            return None

        coordinates = [
            (
                float(point[0]),
                float(point[1]),
            )
            for point in ring
        ]

        if not all(math.isfinite(x) and math.isfinite(y) for x, y in coordinates):
            return None

        polygon = Polygon(coordinates)

        if polygon.is_empty:
            return None

        if not polygon.is_valid:
            polygon = polygon.buffer(0)

        if (
            polygon.is_empty
            or not polygon.is_valid
            or polygon.geom_type != "Polygon"
            or polygon.area <= 0.0
        ):
            return None

        return polygon

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

            if not all(math.isfinite(value) for value in current):
                continue

            if clean and AtlasCastleMultiGableRoofBuilder._same_point(
                clean[-1],
                current,
            ):
                continue

            clean.append(current)

        if len(clean) >= 2 and AtlasCastleMultiGableRoofBuilder._same_point(
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
                AtlasCastleMultiGableRoofBuilder.POINT_PRECISION,
            )
            == round(
                float(point_2[0]),
                AtlasCastleMultiGableRoofBuilder.POINT_PRECISION,
            )
            and round(
                float(point_1[1]),
                AtlasCastleMultiGableRoofBuilder.POINT_PRECISION,
            )
            == round(
                float(point_2[1]),
                AtlasCastleMultiGableRoofBuilder.POINT_PRECISION,
            )
            and round(
                float(point_1[2]),
                AtlasCastleMultiGableRoofBuilder.POINT_PRECISION,
            )
            == round(
                float(point_2[2]),
                AtlasCastleMultiGableRoofBuilder.POINT_PRECISION,
            )
        )
