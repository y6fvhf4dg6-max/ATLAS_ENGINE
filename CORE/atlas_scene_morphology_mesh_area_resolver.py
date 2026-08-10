from __future__ import annotations

import math

from shapely.geometry import Polygon
from shapely.ops import unary_union


class AtlasSceneMorphologyMeshAreaResolver:
    @staticmethod
    def _triangle_xy_polygon(triangle):
        if (
            not isinstance(triangle, (list, tuple))
            or len(triangle) != 3
        ):
            return None

        try:
            points = [
                (
                    float(vertex[0]),
                    float(vertex[1]),
                )
                for vertex in triangle
            ]
        except (
            TypeError,
            ValueError,
            IndexError,
        ):
            return None

        if not all(
            math.isfinite(value)
            for point in points
            for value in point
        ):
            return None

        polygon = Polygon(points)

        if (
            not polygon.is_valid
            or polygon.area <= 0.0
        ):
            return None

        return polygon

    @classmethod
    def projected_xy_area_mm2(
        cls,
        meshes,
    ):
        polygons = []

        for mesh in meshes or ():
            if not isinstance(mesh, dict):
                continue

            for triangle in mesh.get(
                "triangles",
                (),
            ) or ():
                polygon = cls._triangle_xy_polygon(
                    triangle
                )

                if polygon is not None:
                    polygons.append(
                        polygon
                    )

        if not polygons:
            return 0.0

        return float(
            unary_union(polygons).area
        )
