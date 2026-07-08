"""
ATLAS Engine

Atlas Geometry v1.1
Core geometry calculations for ATLAS.
"""

import math


class AtlasGeometry:
    @staticmethod
    def polygon_area_m2(geometry):
        if not geometry or len(geometry) < 3:
            return 0.0

        xy_points = AtlasGeometry.latlon_to_xy(geometry)

        area = 0.0

        for i in range(len(xy_points)):
            x1, y1 = xy_points[i]
            x2, y2 = xy_points[(i + 1) % len(xy_points)]

            area += x1 * y2
            area -= x2 * y1

        return abs(area) / 2

    @staticmethod
    def polygon_perimeter_m(geometry):
        if not geometry or len(geometry) < 2:
            return 0.0

        xy_points = AtlasGeometry.latlon_to_xy(geometry)

        perimeter = 0.0

        for i in range(len(xy_points)):
            x1, y1 = xy_points[i]
            x2, y2 = xy_points[(i + 1) % len(xy_points)]

            dx = x2 - x1
            dy = y2 - y1

            perimeter += math.sqrt(dx * dx + dy * dy)

        return perimeter

    @staticmethod
    def latlon_to_xy(geometry):
        meters_per_degree_lat = 111_320

        avg_lat = sum(point[0] for point in geometry) / len(geometry)
        meters_per_degree_lon = 111_320 * math.cos(math.radians(avg_lat))

        xy_points = []

        for lat, lon in geometry:
            x = lon * meters_per_degree_lon
            y = lat * meters_per_degree_lat
            xy_points.append((x, y))

        return xy_points
