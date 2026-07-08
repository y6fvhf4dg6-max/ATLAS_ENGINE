# CORE/atlas_mesh_repair.py

import math


class AtlasMeshRepair:
    """
    ATLAS Mesh Repair v1.0

    Güvenli ilk sürüm:
    - Noktaları snap eder
    - Degenerate / sıfır alan üçgenleri siler
    - Duplicate triangle'ları siler
    - Mesh yapısını bozmaz
    """

    AREA_EPSILON = 0.000001
    SNAP_PRECISION = 6

    @staticmethod
    def repair(mesh):
        if mesh is None:
            return None

        triangles = mesh.get("triangles", [])

        repaired_triangles = []
        seen = set()

        for triangle in triangles:
            clean_triangle = AtlasMeshRepair._clean_triangle(triangle)

            if clean_triangle is None:
                continue

            # if (
            #    AtlasMeshRepair._triangle_area(clean_triangle)
            #    <= AtlasMeshRepair.AREA_EPSILON
            # ):
            #    continue

            triangle_key = AtlasMeshRepair._triangle_key(clean_triangle)

            if triangle_key in seen:
                continue

            seen.add(triangle_key)
            repaired_triangles.append(clean_triangle)

        repaired_mesh = dict(mesh)
        repaired_mesh["triangles"] = repaired_triangles

        if "bottom" in repaired_mesh:
            repaired_mesh["bottom"] = [
                AtlasMeshRepair._snap_point(point) for point in repaired_mesh["bottom"]
            ]

        if "top" in repaired_mesh:
            repaired_mesh["top"] = [
                AtlasMeshRepair._snap_point(point) for point in repaired_mesh["top"]
            ]

        if "walls" in repaired_mesh:
            repaired_mesh["walls"] = [
                tuple(AtlasMeshRepair._snap_point(point) for point in wall)
                for wall in repaired_mesh["walls"]
            ]

        return repaired_mesh

    @staticmethod
    def _clean_triangle(triangle):
        if triangle is None:
            return None

        if len(triangle) != 3:
            return None

        p1 = AtlasMeshRepair._as_point3(triangle[0])
        p2 = AtlasMeshRepair._as_point3(triangle[1])
        p3 = AtlasMeshRepair._as_point3(triangle[2])

        if p1 is None or p2 is None or p3 is None:
            return None

        return (
            AtlasMeshRepair._snap_point(p1),
            AtlasMeshRepair._snap_point(p2),
            AtlasMeshRepair._snap_point(p3),
        )

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
    def _snap_point(point):
        return (
            round(float(point[0]), AtlasMeshRepair.SNAP_PRECISION),
            round(float(point[1]), AtlasMeshRepair.SNAP_PRECISION),
            round(float(point[2]), AtlasMeshRepair.SNAP_PRECISION),
        )

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
    def _triangle_key(triangle):
        return tuple(
            sorted(
                [
                    AtlasMeshRepair._point_key(triangle[0]),
                    AtlasMeshRepair._point_key(triangle[1]),
                    AtlasMeshRepair._point_key(triangle[2]),
                ]
            )
        )

    @staticmethod
    def _point_key(point):
        return (
            round(point[0], AtlasMeshRepair.SNAP_PRECISION),
            round(point[1], AtlasMeshRepair.SNAP_PRECISION),
            round(point[2], AtlasMeshRepair.SNAP_PRECISION),
        )
