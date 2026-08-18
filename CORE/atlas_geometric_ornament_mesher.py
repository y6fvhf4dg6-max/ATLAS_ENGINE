from __future__ import annotations

from CORE.atlas_polygon_triangulator import (
    AtlasPolygonTriangulator,
)


class AtlasGeometricOrnamentMesher:
    @classmethod
    def build(
        cls,
        *,
        outline_points,
        base_z,
        depth_mm,
        metadata=None,
    ):
        points = tuple(
            (
                float(point[0]),
                float(point[1]),
            )
            for point in outline_points
        )

        if len(points) < 3:
            raise ValueError(
                "outline_points requires at least three points"
            )

        base_z = float(base_z)
        depth_mm = float(depth_mm)

        if depth_mm <= 0.0:
            raise ValueError(
                "depth_mm must be greater than zero"
            )

        triangles_2d = (
            AtlasPolygonTriangulator.triangulate(
                points
            )
        )

        if not triangles_2d:
            raise ValueError(
                "outline_points could not be triangulated"
            )

        top_z = base_z + depth_mm

        back_triangles = []
        front_triangles = []

        for triangle in triangles_2d:
            first, second, third = triangle

            back_triangles.append(
                (
                    (
                        first[0],
                        first[1],
                        base_z,
                    ),
                    (
                        third[0],
                        third[1],
                        base_z,
                    ),
                    (
                        second[0],
                        second[1],
                        base_z,
                    ),
                )
            )

            front_triangles.append(
                (
                    (
                        first[0],
                        first[1],
                        top_z,
                    ),
                    (
                        second[0],
                        second[1],
                        top_z,
                    ),
                    (
                        third[0],
                        third[1],
                        top_z,
                    ),
                )
            )

        side_triangles = []

        for index, first in enumerate(points):
            second = points[
                (index + 1) % len(points)
            ]

            back_first = (
                first[0],
                first[1],
                base_z,
            )
            back_second = (
                second[0],
                second[1],
                base_z,
            )
            front_first = (
                first[0],
                first[1],
                top_z,
            )
            front_second = (
                second[0],
                second[1],
                top_z,
            )

            side_triangles.extend(
                (
                    (
                        back_first,
                        back_second,
                        front_second,
                    ),
                    (
                        back_first,
                        front_second,
                        front_first,
                    ),
                )
            )

        triangles = [
            *back_triangles,
            *front_triangles,
            *side_triangles,
        ]

        result = {
            "triangles": triangles,
            "outline_points": points,
            "base_z": base_z,
            "top_z": top_z,
            "depth_mm": depth_mm,
            "component_type": "geometric_ornament",
            "source_system": "geometric_ornament_mesher",
            "geometry_type": "geometric_ornament_prism",
        }

        if metadata:
            result.update(
                dict(metadata)
            )

        return result
