"""
ATLAS Engine

Atlas Polygon Validator v1.0

Validates building footprints before mesh generation.
Rejects invalid polygons that would create broken STL meshes.
"""


class AtlasPolygonValidator:

    @staticmethod
    def has_enough_points(points):
        return len(points) >= 3

    @staticmethod
    def has_duplicate_points(points):
        return len(points) != len(set(points))

    @staticmethod
    def polygon_area(points):
        area = 0.0

        for i in range(len(points)):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)]

            area += x1 * y2
            area -= x2 * y1

        return abs(area) / 2.0

    @staticmethod
    def has_valid_area(points):
        return AtlasPolygonValidator.polygon_area(points) > 0.0

    @staticmethod
    def validate(points):

        if not AtlasPolygonValidator.has_enough_points(points):
            return False

        if AtlasPolygonValidator.has_duplicate_points(points):
            return False

        if not AtlasPolygonValidator.has_valid_area(points):
            return False

        return True
