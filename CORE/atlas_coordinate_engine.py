"""
ATLAS Engine

Atlas Coordinate Engine v1.1
Converts latitude/longitude coordinates into local STL coordinates.
Supports separate horizontal and vertical scales.
"""

import math


class AtlasCoordinateEngine:
    def __init__(self, origin_lat, origin_lon, xy_scale=5000, z_scale=500):
        self.origin_lat = origin_lat
        self.origin_lon = origin_lon

        self.xy_scale = xy_scale
        self.z_scale = z_scale

        self.meters_per_degree_lat = 111_320
        self.meters_per_degree_lon = 111_320 * math.cos(math.radians(origin_lat))

    def latlon_to_local_meters(self, lat, lon):
        x = (lon - self.origin_lon) * self.meters_per_degree_lon
        y = (lat - self.origin_lat) * self.meters_per_degree_lat

        return x, y

    def latlon_to_stl_mm(self, lat, lon):
        x_m, y_m = self.latlon_to_local_meters(lat, lon)

        x_mm = x_m * 1000 / self.xy_scale
        y_mm = y_m * 1000 / self.xy_scale

        return x_mm, y_mm

    def geometry_to_stl_mm(self, geometry):
        return [self.latlon_to_stl_mm(lat, lon) for lat, lon in geometry]

    def height_to_stl_mm(self, height_m):
        return height_m * 1000 / self.z_scale
