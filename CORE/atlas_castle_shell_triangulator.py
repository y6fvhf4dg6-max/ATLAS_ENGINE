"""
ATLAS Castle Shell Triangulator v0.2

Multipolygon kale geometrilerini triangulate eder.

Destek:
- Outer halka
- Bir veya daha fazla inner halka / hole
- Ters veya hatalı OSM rollerini geometrik olarak düzeltme
- mapbox_earcut tabanlı delikli polygon triangulation

Bu modül yalnızca 2D üçgen üretir.
Terrain, yükseklik ve STL işlemez.
"""

import mapbox_earcut
import numpy as np
from shapely.geometry import Polygon


class AtlasCastleShellTriangulator:
    EPSILON = 1e-9

    @staticmethod
    def triangulate(
        outer_ring,
        inner_rings=None,
    ):
        normalized = AtlasCastleShellTriangulator.normalize_rings(
            outer_ring=outer_ring,
            inner_rings=inner_rings,
        )

        outer = normalized["outer_ring"]
        holes = normalized["inner_rings"]

        if len(outer) < 3:
            return []

        outer = AtlasCastleShellTriangulator._ensure_ccw(outer)

        normalized_holes = [
            AtlasCastleShellTriangulator._ensure_cw(hole) for hole in holes
        ]

        rings = [outer]
        rings.extend(normalized_holes)

        vertices = []
        ring_end_indices = []
        running_total = 0

        for ring in rings:
            vertices.extend(ring)
            running_total += len(ring)
            ring_end_indices.append(running_total)

        vertex_array = np.asarray(
            vertices,
            dtype=np.float64,
        )

        ring_end_array = np.asarray(
            ring_end_indices,
            dtype=np.uint32,
        )

        try:
            index_array = mapbox_earcut.triangulate_float64(
                vertex_array,
                ring_end_array,
            )
        except (TypeError, ValueError, RuntimeError):
            return []

        if len(index_array) % 3 != 0:
            return []

        triangles = []
        degenerate_triangles = []

        for index in range(0, len(index_array), 3):
            i1 = int(index_array[index])
            i2 = int(index_array[index + 1])
            i3 = int(index_array[index + 2])

            if i1 >= len(vertices) or i2 >= len(vertices) or i3 >= len(vertices):
                return []

            triangle = (
                vertices[i1],
                vertices[i2],
                vertices[i3],
            )

            if (
                AtlasCastleShellTriangulator._triangle_area(triangle)
                <= AtlasCastleShellTriangulator.EPSILON
            ):
                degenerate_triangles.append(triangle)
                continue

            triangles.append(triangle)

        triangles = AtlasCastleShellTriangulator._repair_degenerate_t_junctions(
            triangles=triangles,
            degenerate_triangles=degenerate_triangles,
        )

        return triangles

    @staticmethod
    def normalize_rings(
        outer_ring,
        inner_rings=None,
    ):
        if inner_rings is None:
            inner_rings = []

        candidate_rings = []

        cleaned_outer = AtlasCastleShellTriangulator._clean_ring(outer_ring)

        if len(cleaned_outer) >= 3:
            candidate_rings.append(cleaned_outer)

        for ring in inner_rings:
            cleaned = AtlasCastleShellTriangulator._clean_ring(ring)

            if len(cleaned) >= 3:
                candidate_rings.append(cleaned)

        if not candidate_rings:
            return {
                "outer_ring": [],
                "inner_rings": [],
                "roles_corrected": False,
            }

        polygon_items = []

        for ring in candidate_rings:
            polygon = Polygon(ring)

            if (
                polygon.is_empty
                or not polygon.is_valid
                or polygon.area <= AtlasCastleShellTriangulator.EPSILON
            ):
                continue

            polygon_items.append(
                {
                    "ring": ring,
                    "polygon": polygon,
                    "area": polygon.area,
                }
            )

        if not polygon_items:
            return {
                "outer_ring": [],
                "inner_rings": [],
                "roles_corrected": False,
            }

        polygon_items.sort(
            key=lambda item: item["area"],
            reverse=True,
        )

        real_outer_item = polygon_items[0]

        holes = []

        for item in polygon_items[1:]:
            if real_outer_item["polygon"].contains(item["polygon"]):
                holes.append(item["ring"])

        roles_corrected = cleaned_outer != real_outer_item["ring"]

        return {
            "outer_ring": real_outer_item["ring"],
            "inner_rings": holes,
            "roles_corrected": roles_corrected,
        }

    @staticmethod
    def _clean_ring(points):
        clean = []

        if not points:
            return clean

        for point in points:
            if point is None or len(point) < 2:
                continue

            current = (
                float(point[0]),
                float(point[1]),
            )

            if clean and AtlasCastleShellTriangulator._same_point(
                clean[-1],
                current,
            ):
                continue

            clean.append(current)

        if len(clean) >= 2 and AtlasCastleShellTriangulator._same_point(
            clean[0],
            clean[-1],
        ):
            clean.pop()

        return clean

    @staticmethod
    def _ensure_ccw(points):
        if AtlasCastleShellTriangulator._signed_area(points) < 0:
            return list(reversed(points))

        return list(points)

    @staticmethod
    def _ensure_cw(points):
        if AtlasCastleShellTriangulator._signed_area(points) > 0:
            return list(reversed(points))

        return list(points)

    @staticmethod
    def _signed_area(points):
        area = 0.0

        for index in range(len(points)):
            next_index = (index + 1) % len(points)

            x1, y1 = points[index]
            x2, y2 = points[next_index]

            area += x1 * y2
            area -= x2 * y1

        return area / 2.0

    @staticmethod
    def _triangle_area(triangle):
        p1, p2, p3 = triangle

        return abs(
            (
                p1[0] * (p2[1] - p3[1])
                + p2[0] * (p3[1] - p1[1])
                + p3[0] * (p1[1] - p2[1])
            )
            / 2.0
        )

    @staticmethod
    def _repair_degenerate_t_junctions(
        triangles,
        degenerate_triangles,
    ):
        """
        Earcut tarafından kollinear sınır noktalarında üretilebilen
        sıfır alanlı köprü üçgenlerini gerçek mesh üçgenlerine dönüştürür.

        A---B---C doğrusal yapısında Earcut bir A-C uzun kenarı
        oluşturmuşsa, bu kenarı B noktasında ikiye böler.
        """
        repaired_triangles = list(triangles)

        for degenerate_triangle in degenerate_triangles:
            split_data = AtlasCastleShellTriangulator._get_collinear_split_points(
                degenerate_triangle
            )

            if split_data is None:
                continue

            edge_start, middle_point, edge_end = split_data

            matching_index = None
            opposite_point = None

            for triangle_index, triangle in enumerate(repaired_triangles):
                triangle_points = list(triangle)

                has_start = any(
                    AtlasCastleShellTriangulator._same_point(
                        point,
                        edge_start,
                    )
                    for point in triangle_points
                )

                has_end = any(
                    AtlasCastleShellTriangulator._same_point(
                        point,
                        edge_end,
                    )
                    for point in triangle_points
                )

                if not has_start or not has_end:
                    continue

                remaining_points = [
                    point
                    for point in triangle_points
                    if not AtlasCastleShellTriangulator._same_point(
                        point,
                        edge_start,
                    )
                    and not AtlasCastleShellTriangulator._same_point(
                        point,
                        edge_end,
                    )
                ]

                if len(remaining_points) != 1:
                    continue

                matching_index = triangle_index
                opposite_point = remaining_points[0]
                break

            if matching_index is None or opposite_point is None:
                continue

            original_triangle = repaired_triangles.pop(matching_index)

            original_sign = AtlasCastleShellTriangulator._triangle_signed_area(
                original_triangle
            )

            first_triangle = (
                edge_start,
                middle_point,
                opposite_point,
            )

            second_triangle = (
                middle_point,
                edge_end,
                opposite_point,
            )

            first_triangle = AtlasCastleShellTriangulator._match_triangle_orientation(
                first_triangle,
                original_sign,
            )

            second_triangle = AtlasCastleShellTriangulator._match_triangle_orientation(
                second_triangle,
                original_sign,
            )

            if (
                AtlasCastleShellTriangulator._triangle_area(first_triangle)
                > AtlasCastleShellTriangulator.EPSILON
            ):
                repaired_triangles.append(first_triangle)

            if (
                AtlasCastleShellTriangulator._triangle_area(second_triangle)
                > AtlasCastleShellTriangulator.EPSILON
            ):
                repaired_triangles.append(second_triangle)

        return repaired_triangles

    @staticmethod
    def _get_collinear_split_points(
        triangle,
    ):
        """
        Üç kollinear noktadan ortada olanı bulur ve
        (başlangıç, orta, bitiş) döndürür.
        """
        p1, p2, p3 = triangle

        candidates = (
            (p1, p2, p3),
            (p1, p3, p2),
            (p2, p1, p3),
        )

        for edge_start, middle_point, edge_end in candidates:
            if AtlasCastleShellTriangulator._point_on_segment(
                point=middle_point,
                segment_start=edge_start,
                segment_end=edge_end,
            ):
                return (
                    edge_start,
                    middle_point,
                    edge_end,
                )

        return None

    @staticmethod
    def _point_on_segment(
        point,
        segment_start,
        segment_end,
    ):
        cross_product = (point[0] - segment_start[0]) * (
            segment_end[1] - segment_start[1]
        ) - (point[1] - segment_start[1]) * (segment_end[0] - segment_start[0])

        if abs(cross_product) > AtlasCastleShellTriangulator.EPSILON:
            return False

        minimum_x = (
            min(
                segment_start[0],
                segment_end[0],
            )
            - AtlasCastleShellTriangulator.EPSILON
        )

        maximum_x = (
            max(
                segment_start[0],
                segment_end[0],
            )
            + AtlasCastleShellTriangulator.EPSILON
        )

        minimum_y = (
            min(
                segment_start[1],
                segment_end[1],
            )
            - AtlasCastleShellTriangulator.EPSILON
        )

        maximum_y = (
            max(
                segment_start[1],
                segment_end[1],
            )
            + AtlasCastleShellTriangulator.EPSILON
        )

        return (
            minimum_x <= point[0] <= maximum_x
            and minimum_y <= point[1] <= maximum_y
            and not AtlasCastleShellTriangulator._same_point(
                point,
                segment_start,
            )
            and not AtlasCastleShellTriangulator._same_point(
                point,
                segment_end,
            )
        )

    @staticmethod
    def _triangle_signed_area(
        triangle,
    ):
        p1, p2, p3 = triangle

        return (
            p1[0] * (p2[1] - p3[1]) + p2[0] * (p3[1] - p1[1]) + p3[0] * (p1[1] - p2[1])
        ) / 2.0

    @staticmethod
    def _match_triangle_orientation(
        triangle,
        target_sign,
    ):
        current_sign = AtlasCastleShellTriangulator._triangle_signed_area(triangle)

        if (target_sign < 0.0 and current_sign > 0.0) or (
            target_sign > 0.0 and current_sign < 0.0
        ):
            p1, p2, p3 = triangle
            return (p1, p3, p2)

        return triangle

    @staticmethod
    def _same_point(p1, p2):
        return (
            abs(p1[0] - p2[0]) <= AtlasCastleShellTriangulator.EPSILON
            and abs(p1[1] - p2[1]) <= AtlasCastleShellTriangulator.EPSILON
        )
