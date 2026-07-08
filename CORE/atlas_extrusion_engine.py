"""
ATLAS Engine

Atlas Extrusion Engine v1.4
Creates 3D prism mesh using shared AtlasCoordinateEngine.
"""

from CORE.atlas_coordinate_engine import AtlasCoordinateEngine
from CORE.atlas_geometry_simplifier import AtlasGeometrySimplifier


class AtlasExtrusionEngine:
    @staticmethod
    def clean_points(points):
        clean = []

        for point in points:
            if not clean or point != clean[-1]:
                clean.append(point)

        if len(clean) > 1 and clean[0] == clean[-1]:
            clean.pop()

        return clean

    @staticmethod
    def extrude(building, coordinate_engine=None):
        points = AtlasExtrusionEngine.clean_points(building.geometry)
        # points = AtlasGeometrySimplifier.simplify(points)

        if len(points) < 3:
            return None

        if coordinate_engine is None:
            origin_lat, origin_lon = building.centroid
            coordinate_engine = AtlasCoordinateEngine(
                origin_lat=origin_lat,
                origin_lon=origin_lon,
                xy_scale=5000,
                z_scale=500,
            )

        scaled_points = coordinate_engine.geometry_to_stl_mm(points)

        height_mm = coordinate_engine.height_to_stl_mm(building.estimated_height)

        mesh = {
            "bottom": [],
            "top": [],
            "walls": [],
        }

        for x, y in scaled_points:
            mesh["bottom"].append((x, y, 0.0))
            mesh["top"].append((x, y, height_mm))

        for i in range(len(scaled_points)):
            p1 = mesh["bottom"][i]
            p2 = mesh["bottom"][(i + 1) % len(scaled_points)]
            p3 = mesh["top"][(i + 1) % len(scaled_points)]
            p4 = mesh["top"][i]

            mesh["walls"].append((p1, p2, p3, p4))

        return mesh
