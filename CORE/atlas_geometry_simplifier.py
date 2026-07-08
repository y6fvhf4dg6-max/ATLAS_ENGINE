"""
ATLAS Engine

Atlas Geometry Simplifier v2.0
Safe geometry cleaner for OSM building footprints.
"""


class AtlasGeometrySimplifier:
    @staticmethod
    def remove_duplicate_points(points):
        clean = []

        for point in points:
            if not clean or point != clean[-1]:
                clean.append(point)

        if len(clean) > 1 and clean[0] == clean[-1]:
            clean.pop()

        return clean

    @staticmethod
    def triangle_area(a, b, c):
        ax, ay = a
        bx, by = b
        cx, cy = c

        return abs((ax * (by - cy) + bx * (cy - ay) + cx * (ay - by)) / 2.0)

    @staticmethod
    def remove_collinear_points(points, tolerance=0.00000001):
        if len(points) < 4:
            return points

        cleaned = []

        point_count = len(points)

        for i in range(point_count):
            prev_point = points[i - 1]
            current_point = points[i]
            next_point = points[(i + 1) % point_count]

            area = AtlasGeometrySimplifier.triangle_area(
                prev_point,
                current_point,
                next_point,
            )

            if area > tolerance:
                cleaned.append(current_point)

        if len(cleaned) < 3:
            return points

        return cleaned

    @staticmethod
    def polygon_area(points):
        area = 0.0

        for i in range(len(points)):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)]

            area += x1 * y2
            area -= x2 * y1

        return area / 2.0

    @staticmethod
    def has_self_intersection(points):
        def ccw(a, b, c):
            return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

        def intersect(a, b, c, d):
            return ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d)

        edge_count = len(points)

        for i in range(edge_count):
            a1 = points[i]
            a2 = points[(i + 1) % edge_count]

            for j in range(i + 1, edge_count):
                if abs(i - j) <= 1:
                    continue

                if i == 0 and j == edge_count - 1:
                    continue

                b1 = points[j]
                b2 = points[(j + 1) % edge_count]

                if intersect(a1, a2, b1, b2):
                    return True

        return False

    @staticmethod
    def simplify(points):
        if not points or len(points) < 3:
            return points

        points = AtlasGeometrySimplifier.remove_duplicate_points(points)

        if len(points) < 3:
            return []

        points = AtlasGeometrySimplifier.remove_collinear_points(points)

        if len(points) < 3:
            return []

        if AtlasGeometrySimplifier.has_self_intersection(points):
            return []

        return points
