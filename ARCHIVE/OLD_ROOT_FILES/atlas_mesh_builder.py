"""
ATLAS Engine

Atlas Mesh Builder v1.0
Converts analyzed AtlasBuilding objects into printable STL meshes.
"""

from CORE.atlas_geometry_simplifier import AtlasGeometrySimplifier


class AtlasMeshBuilder:
    MIN_HEIGHT_MM = 2.0
    MAX_HEIGHT_MM = 35.0

    @staticmethod
    def calculate_height(building, coordinate_engine):
        height_mm = coordinate_engine.height_to_stl_mm(building.estimated_height)

        if height_mm < AtlasMeshBuilder.MIN_HEIGHT_MM:
            return AtlasMeshBuilder.MIN_HEIGHT_MM

        if height_mm > AtlasMeshBuilder.MAX_HEIGHT_MM:
            return AtlasMeshBuilder.MAX_HEIGHT_MM

        return height_mm

    @staticmethod
    def prepare_geometry(building, coordinate_engine):
        points = building.geometry
        points = AtlasGeometrySimplifier.simplify(points)

        if len(points) < 3:
            return None

        scaled_points = coordinate_engine.geometry_to_stl_mm(points)

        return scaled_points

    @staticmethod
    def build_mesh(building, coordinate_engine):
        scaled_points = AtlasMeshBuilder.prepare_geometry(
            building,
            coordinate_engine,
        )

        if scaled_points is None:
            return None

        height_mm = AtlasMeshBuilder.calculate_height(
            building,
            coordinate_engine,
        )

        mesh = {
            "bottom": [],
            "top": [],
            "walls": [],
        }

        for x, y in scaled_points:
            mesh["bottom"].append((x, y, 0.0))
            mesh["top"].append((x, y, height_mm))

        point_count = len(scaled_points)

        for i in range(point_count):
            p1 = mesh["bottom"][i]
            p2 = mesh["bottom"][(i + 1) % point_count]
            p3 = mesh["top"][(i + 1) % point_count]
            p4 = mesh["top"][i]

            mesh["walls"].append((p1, p2, p3, p4))

        return mesh
