"""
ATLAS Engine

Atlas Polygon Triangulator v2.0

Converts validated polygons into triangle lists.
Uses ear clipping triangulation for simple concave polygons.
This module knows NOTHING about STL.
"""


class AtlasPolygonTriangulator:

    EPSILON = 1e-9

    @staticmethod
    def _area(points):
        area = 0.0

        for i in range(len(points)):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)]

            area += x1 * y2
            area -= x2 * y1

        return area / 2.0

    @staticmethod
    def _is_convex(prev_point, current_point, next_point):
        ax = current_point[0] - prev_point[0]
        ay = current_point[1] - prev_point[1]

        bx = next_point[0] - current_point[0]
        by = next_point[1] - current_point[1]

        cross = (ax * by) - (ay * bx)

        return cross > AtlasPolygonTriangulator.EPSILON

    @staticmethod
    def _point_in_triangle(point, a, b, c):
        px, py = point
        ax, ay = a
        bx, by = b
        cx, cy = c

        v0x = cx - ax
        v0y = cy - ay
        v1x = bx - ax
        v1y = by - ay
        v2x = px - ax
        v2y = py - ay

        dot00 = v0x * v0x + v0y * v0y
        dot01 = v0x * v1x + v0y * v1y
        dot02 = v0x * v2x + v0y * v2y
        dot11 = v1x * v1x + v1y * v1y
        dot12 = v1x * v2x + v1y * v2y

        denominator = (dot00 * dot11) - (dot01 * dot01)

        if abs(denominator) < AtlasPolygonTriangulator.EPSILON:
            return False

        inv_denominator = 1.0 / denominator

        u = ((dot11 * dot02) - (dot01 * dot12)) * inv_denominator
        v = ((dot00 * dot12) - (dot01 * dot02)) * inv_denominator

        return (
            u > AtlasPolygonTriangulator.EPSILON
            and v > AtlasPolygonTriangulator.EPSILON
            and (u + v) < 1.0 - AtlasPolygonTriangulator.EPSILON
        )

    @staticmethod
    def _is_ear(points, index):
        point_count = len(points)

        prev_index = (index - 1) % point_count
        next_index = (index + 1) % point_count

        prev_point = points[prev_index]
        current_point = points[index]
        next_point = points[next_index]

        if not AtlasPolygonTriangulator._is_convex(
            prev_point,
            current_point,
            next_point,
        ):
            return False

        for other_index, other_point in enumerate(points):
            if other_index in (prev_index, index, next_index):
                continue

            if AtlasPolygonTriangulator._point_in_triangle(
                other_point,
                prev_point,
                current_point,
                next_point,
            ):
                return False

        return True

    @staticmethod
    def triangulate(points):
        if points is None:
            return []

        if len(points) < 3:
            return []

        working_points = list(points)

        if AtlasPolygonTriangulator._area(working_points) < 0:
            working_points.reverse()

        triangles = []
        guard = 0
        max_guard = len(working_points) * len(working_points)

        while len(working_points) > 3 and guard < max_guard:
            ear_found = False

            for index in range(len(working_points)):
                if AtlasPolygonTriangulator._is_ear(working_points, index):
                    point_count = len(working_points)

                    prev_index = (index - 1) % point_count
                    next_index = (index + 1) % point_count

                    triangle = (
                        working_points[prev_index],
                        working_points[index],
                        working_points[next_index],
                    )

                    triangles.append(triangle)

                    del working_points[index]

                    ear_found = True
                    break

            if not ear_found:
                return []

            guard += 1

        if len(working_points) == 3:
            triangles.append(
                (
                    working_points[0],
                    working_points[1],
                    working_points[2],
                )
            )

        return triangles

    @staticmethod
    def _fan_fallback(points):
        if len(points) < 3:
            return []

        triangles = []
        origin = points[0]

        for i in range(1, len(points) - 1):
            triangles.append(
                (
                    origin,
                    points[i],
                    points[i + 1],
                )
            )

        return triangles
