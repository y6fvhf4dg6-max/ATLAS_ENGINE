# EXPORT/atlas_stl_writer.py
# ATLAS STL Writer v3.0
# Responsibility:
# - Does NOT understand polygons
# - Does NOT triangulate
# - Does NOT create geometry
# - Only writes ready triangles/faces to ASCII STL

import math
from CORE.atlas_mesh_repair import AtlasMeshRepair


class AtlasSTLWriter:
    """
    ATLAS STL Writer v3.0

    Expected mesh formats:

    mesh = {
        "triangles": [
            ((x1, y1, z1), (x2, y2, z2), (x3, y3, z3)),
            ...
        ]
    }

    or:

    mesh = {
        "faces": [
            ((x1, y1, z1), (x2, y2, z2), (x3, y3, z3)),
            ...
        ]
    }
    """

    @staticmethod
    def _as_point3(point):
        if point is None:
            return None

        if len(point) == 2:
            return (float(point[0]), float(point[1]), 0.0)

        if len(point) >= 3:
            return (float(point[0]), float(point[1]), float(point[2]))

        return None

    @staticmethod
    def _triangle_normal(p1, p2, p3):
        ux = p2[0] - p1[0]
        uy = p2[1] - p1[1]
        uz = p2[2] - p1[2]

        vx = p3[0] - p1[0]
        vy = p3[1] - p1[1]
        vz = p3[2] - p1[2]

        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz = ux * vy - uy * vx

        length = math.sqrt(nx * nx + ny * ny + nz * nz)

        if length == 0:
            return (0.0, 0.0, 0.0)

        return (nx / length, ny / length, nz / length)

    @staticmethod
    def _triangle_area(triangle):
        p1, p2, p3 = triangle

        ux = p2[0] - p1[0]
        uy = p2[1] - p1[1]
        uz = p2[2] - p1[2]

        vx = p3[0] - p1[0]
        vy = p3[1] - p1[1]
        vz = p3[2] - p1[2]

        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz = ux * vy - uy * vx

        return math.sqrt(nx * nx + ny * ny + nz * nz) / 2.0

    @staticmethod
    def _get_mesh_triangles(mesh):
        if mesh is None:
            return []

        if isinstance(mesh, dict):
            if "triangles" in mesh and mesh["triangles"] is not None:
                return mesh["triangles"]

            if "faces" in mesh and mesh["faces"] is not None:
                return mesh["faces"]

        if hasattr(mesh, "triangles"):
            return mesh.triangles

        if hasattr(mesh, "faces"):
            return mesh.faces

        return []

    @staticmethod
    def _clean_triangle(triangle):
        if triangle is None:
            return None

        if len(triangle) != 3:
            return None

        p1 = AtlasSTLWriter._as_point3(triangle[0])
        p2 = AtlasSTLWriter._as_point3(triangle[1])
        p3 = AtlasSTLWriter._as_point3(triangle[2])

        if p1 is None or p2 is None or p3 is None:
            return None

        return (p1, p2, p3)

    @staticmethod
    def write(meshes, output_path, solid_name="ATLAS_MODEL"):
        if meshes is None:
            meshes = []

        valid_triangles = []

        for mesh in meshes:
            mesh = AtlasMeshRepair.repair(mesh)
            triangles = AtlasSTLWriter._get_mesh_triangles(mesh)

            for triangle in triangles:
                clean_triangle = AtlasSTLWriter._clean_triangle(triangle)

                if clean_triangle is not None:
                    valid_triangles.append(clean_triangle)

        with open(output_path, "w", encoding="utf-8") as file:
            file.write(f"solid {solid_name}\n")

            for triangle in valid_triangles:
                p1, p2, p3 = triangle
                normal = AtlasSTLWriter._triangle_normal(p1, p2, p3)

                file.write(
                    f"  facet normal {normal[0]:.6f} {normal[1]:.6f} {normal[2]:.6f}\n"
                )
                file.write("    outer loop\n")
                file.write(f"      vertex {p1[0]:.6f} {p1[1]:.6f} {p1[2]:.6f}\n")
                file.write(f"      vertex {p2[0]:.6f} {p2[1]:.6f} {p2[2]:.6f}\n")
                file.write(f"      vertex {p3[0]:.6f} {p3[1]:.6f} {p3[2]:.6f}\n")
                file.write("    endloop\n")
                file.write("  endfacet\n")

            file.write(f"endsolid {solid_name}\n")

        print(f"STL written: {output_path}")
        print(f"Triangles: {len(valid_triangles)}")

        return output_path

    @staticmethod
    def write_many(meshes, output_path, solid_name="ATLAS_MODEL"):
        return AtlasSTLWriter.write(
            meshes=meshes, output_path=output_path, solid_name=solid_name
        )
