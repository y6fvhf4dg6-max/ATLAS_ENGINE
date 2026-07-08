"""
ATLAS Engine

Atlas Polygon Cleaner v1.1

Removes unnecessary geometry artifacts before mesh generation.
Preserves polygon point order.
"""


class AtlasPolygonCleaner:

    @staticmethod
    def remove_closing_point(points):
        if not points:
            return []

        if len(points) > 1 and points[0] == points[-1]:
            return points[:-1]

        return list(points)

    @staticmethod
    def remove_consecutive_duplicate_points(points):
        if not points:
            return []

        cleaned = []

        previous = None

        for point in points:
            if point != previous:
                cleaned.append(point)

            previous = point

        return cleaned

    @staticmethod
    def clean(points):
        points = AtlasPolygonCleaner.remove_closing_point(points)
        points = AtlasPolygonCleaner.remove_consecutive_duplicate_points(points)

        return points
