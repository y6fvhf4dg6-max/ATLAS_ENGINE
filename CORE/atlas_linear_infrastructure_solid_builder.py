import math

from CORE.atlas_foundation_sampler import AtlasFoundationSampler
from CORE.atlas_polygon_triangulator import AtlasPolygonTriangulator
from CORE.atlas_linear_infrastructure_geometry_builder import (
    AtlasLinearInfrastructureGeometryBuilder,
)


class AtlasLinearInfrastructureSolidBuilder:
    @classmethod
    def build_product_solid(
        cls,
        *,
        item,
        coordinate_engine,
        profile,
        terrain_mesh,
        height_mm,
    ):
        footprint = (
            AtlasLinearInfrastructureGeometryBuilder
            .build_product_footprint(
                item=item,
                coordinate_engine=coordinate_engine,
                profile=profile,
            )
        )

        if len(footprint) < 3:
            return None

        return cls.build_polygon_solid(
            points=footprint,
            terrain_mesh=terrain_mesh,
            height_mm=height_mm,
        )

    @staticmethod
    def build_polygon_solid(
        *,
        points,
        terrain_mesh,
        height_mm,
    ):
        height_mm = float(height_mm)

        if not math.isfinite(height_mm) or height_mm <= 0.0:
            raise ValueError(
                "height_mm must be a finite positive value."
            )

        polygon = list(points)

        if (
            len(polygon) >= 2
            and polygon[0] == polygon[-1]
        ):
            polygon = polygon[:-1]

        if len(polygon) < 3:
            return None

        flat_triangles = (
            AtlasPolygonTriangulator.triangulate(
                polygon
            )
        )

        if not flat_triangles:
            return None

        bottom = []
        top = []

        for x, y in polygon:
            terrain_z = (
                AtlasFoundationSampler
                .terrain_z_at_xy(
                    terrain_mesh=terrain_mesh,
                    x=x,
                    y=y,
                )
            )

            bottom.append(
                (x, y, terrain_z)
            )
            top.append(
                (
                    x,
                    y,
                    terrain_z + height_mm,
                )
            )

        triangles = []

        for triangle in flat_triangles:
            top_triangle = []
            bottom_triangle = []

            for x, y in triangle:
                terrain_z = (
                    AtlasFoundationSampler
                    .terrain_z_at_xy(
                        terrain_mesh=terrain_mesh,
                        x=x,
                        y=y,
                    )
                )

                bottom_triangle.append(
                    (x, y, terrain_z)
                )
                top_triangle.append(
                    (
                        x,
                        y,
                        terrain_z + height_mm,
                    )
                )

            triangles.append(
                tuple(top_triangle)
            )
            triangles.append(
                (
                    bottom_triangle[2],
                    bottom_triangle[1],
                    bottom_triangle[0],
                )
            )

        walls = []
        point_count = len(polygon)

        for index in range(point_count):
            next_index = (
                index + 1
            ) % point_count

            b1 = bottom[index]
            b2 = bottom[next_index]
            t1 = top[index]
            t2 = top[next_index]

            walls.append(
                (b1, b2, t2, t1)
            )

            triangles.extend(
                [
                    (b1, b2, t2),
                    (b1, t2, t1),
                ]
            )

        return {
            "type": (
                "linear_infrastructure_solid"
            ),
            "bottom": bottom,
            "top": top,
            "walls": walls,
            "triangles": triangles,
            "height_mm": height_mm,
        }
