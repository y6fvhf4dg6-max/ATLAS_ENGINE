from __future__ import annotations

import math

from shapely.geometry import MultiPoint, Point, Polygon
from shapely.ops import triangulate

from CORE.atlas_water_surface_texture import (
    AtlasWaterSurfaceTexture,
)


class AtlasWaterTexturedSolidMesher:
    """Yoğunlaştırılmış dalgalı üst yüzeye sahip kapalı su katısı."""

    POINT_PRECISION = 9
    GEOMETRY_EPSILON = 1e-9

    @staticmethod
    def _positive_float(
        value,
        field_name,
    ):
        try:
            resolved = float(value)
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"{field_name} must be positive"
            ) from error

        if (
            not math.isfinite(resolved)
            or resolved <= 0.0
        ):
            raise ValueError(
                f"{field_name} must be positive"
            )

        return resolved

    @staticmethod
    def _finite_float(
        value,
        field_name,
    ):
        try:
            resolved = float(value)
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"{field_name} must be finite"
            ) from error

        if not math.isfinite(resolved):
            raise ValueError(
                f"{field_name} must be finite"
            )

        return resolved

    @classmethod
    def _point_key(
        cls,
        point,
    ):
        return (
            round(
                float(point[0]),
                cls.POINT_PRECISION,
            ),
            round(
                float(point[1]),
                cls.POINT_PRECISION,
            ),
        )

    @classmethod
    def _deduplicate_points(
        cls,
        points,
    ):
        unique = []
        seen = set()

        for point in points:
            key = cls._point_key(point)

            if key in seen:
                continue

            seen.add(key)
            unique.append(
                (
                    float(point[0]),
                    float(point[1]),
                )
            )

        return tuple(unique)

    @classmethod
    def _densify_boundary(
        cls,
        boundary_points,
        maximum_edge_length_mm,
    ):
        dense = []
        count = len(boundary_points)

        for index in range(count):
            start = boundary_points[index]
            end = boundary_points[
                (index + 1) % count
            ]

            dx = float(end[0]) - float(start[0])
            dy = float(end[1]) - float(start[1])
            length = math.hypot(dx, dy)

            segment_count = max(
                1,
                int(
                    math.ceil(
                        length
                        / maximum_edge_length_mm
                    )
                ),
            )

            for step in range(segment_count):
                progress = (
                    step / segment_count
                )

                dense.append(
                    (
                        float(start[0])
                        + dx * progress,
                        float(start[1])
                        + dy * progress,
                    )
                )

        return cls._deduplicate_points(
            dense
        )

    @classmethod
    def _interior_grid_points(
        cls,
        polygon,
        maximum_edge_length_mm,
    ):
        minimum_x, minimum_y, maximum_x, maximum_y = (
            polygon.bounds
        )

        points = []

        x = (
            minimum_x
            + maximum_edge_length_mm
        )

        while x < (
            maximum_x
            - cls.GEOMETRY_EPSILON
        ):
            y = (
                minimum_y
                + maximum_edge_length_mm
            )

            while y < (
                maximum_y
                - cls.GEOMETRY_EPSILON
            ):
                point = Point(x, y)

                if polygon.contains(point):
                    points.append(
                        (
                            float(x),
                            float(y),
                        )
                    )

                y += maximum_edge_length_mm

            x += maximum_edge_length_mm

        return tuple(points)

    @staticmethod
    def _signed_area(
        points,
    ):
        return 0.5 * sum(
            (
                first[0] * second[1]
                - second[0] * first[1]
            )
            for first, second in zip(
                points,
                (
                    *points[1:],
                    points[0],
                ),
            )
        )

    @classmethod
    def _surface_triangles(
        cls,
        polygon,
        all_points,
    ):
        candidates = triangulate(
            MultiPoint(all_points)
        )

        resolved = []

        for candidate in candidates:
            if (
                candidate.is_empty
                or candidate.area
                <= cls.GEOMETRY_EPSILON
            ):
                continue

            if not polygon.covers(candidate):
                continue

            coordinates = [
                (
                    float(x),
                    float(y),
                )
                for x, y in list(
                    candidate.exterior.coords
                )[:-1]
            ]

            if len(coordinates) != 3:
                continue

            if cls._signed_area(
                coordinates
            ) < 0.0:
                coordinates = [
                    coordinates[0],
                    coordinates[2],
                    coordinates[1],
                ]

            resolved.append(
                tuple(coordinates)
            )

        if not resolved:
            raise ValueError(
                "Water surface triangulation produced no triangles"
            )

        return tuple(resolved)

    @classmethod
    def build(
        cls,
        *,
        boundary_points,
        water_bottom_z,
        water_surface_z,
        texture,
        maximum_edge_length_mm,
    ):
        maximum_edge_length_mm = (
            cls._positive_float(
                maximum_edge_length_mm,
                "maximum_edge_length_mm",
            )
        )

        water_bottom_z = cls._finite_float(
            water_bottom_z,
            "water_bottom_z",
        )
        water_surface_z = cls._finite_float(
            water_surface_z,
            "water_surface_z",
        )

        if water_surface_z <= water_bottom_z:
            raise ValueError(
                "water_surface_z must be greater than water_bottom_z"
            )

        if not isinstance(
            texture,
            AtlasWaterSurfaceTexture,
        ):
            raise TypeError(
                "texture must be an AtlasWaterSurfaceTexture"
            )

        boundary_points = (
            cls._deduplicate_points(
                boundary_points
            )
        )

        if len(boundary_points) < 3:
            raise ValueError(
                "boundary_points requires at least three points"
            )

        polygon = Polygon(boundary_points)

        if not polygon.is_valid:
            polygon = polygon.buffer(0)

        if (
            polygon.is_empty
            or polygon.geom_type != "Polygon"
            or polygon.area
            <= cls.GEOMETRY_EPSILON
        ):
            raise ValueError(
                "boundary_points must form one valid polygon"
            )

        dense_boundary = cls._densify_boundary(
            boundary_points=tuple(
                (
                    float(x),
                    float(y),
                )
                for x, y in list(
                    polygon.exterior.coords
                )[:-1]
            ),
            maximum_edge_length_mm=(
                maximum_edge_length_mm
            ),
        )

        interior_points = (
            cls._interior_grid_points(
                polygon=polygon,
                maximum_edge_length_mm=(
                    maximum_edge_length_mm
                ),
            )
        )

        all_points = cls._deduplicate_points(
            (
                *dense_boundary,
                *interior_points,
            )
        )

        surface_triangles_xy = (
            cls._surface_triangles(
                polygon=polygon,
                all_points=all_points,
            )
        )

        boundary_keys = {
            cls._point_key(point)
            for point in dense_boundary
        }

        top_by_key = {}
        bottom_by_key = {}

        for x, y in all_points:
            key = cls._point_key(
                (x, y)
            )

            edge_distance_mm = (
                polygon.boundary.distance(
                    Point(x, y)
                )
            )

            offset_mm = texture.offset_at(
                x_mm=x,
                y_mm=y,
                edge_distance_mm=(
                    edge_distance_mm
                ),
            )

            if key in boundary_keys:
                offset_mm = 0.0

            top_by_key[key] = (
                float(x),
                float(y),
                (
                    water_surface_z
                    + offset_mm
                ),
            )
            bottom_by_key[key] = (
                float(x),
                float(y),
                water_bottom_z,
            )

        top_triangles = []
        bottom_triangles = []

        for triangle_xy in surface_triangles_xy:
            keys = tuple(
                cls._point_key(point)
                for point in triangle_xy
            )

            top_triangle = tuple(
                top_by_key[key]
                for key in keys
            )
            bottom_triangle = tuple(
                bottom_by_key[key]
                for key in reversed(keys)
            )

            top_triangles.append(
                top_triangle
            )
            bottom_triangles.append(
                bottom_triangle
            )

        walls = []
        wall_triangles = []

        for index in range(
            len(dense_boundary)
        ):
            next_index = (
                index + 1
            ) % len(dense_boundary)

            first_key = cls._point_key(
                dense_boundary[index]
            )
            second_key = cls._point_key(
                dense_boundary[next_index]
            )

            bottom_first = bottom_by_key[
                first_key
            ]
            bottom_second = bottom_by_key[
                second_key
            ]
            top_first = top_by_key[first_key]
            top_second = top_by_key[
                second_key
            ]

            walls.append(
                (
                    bottom_first,
                    bottom_second,
                    top_second,
                    top_first,
                )
            )

            wall_triangles.extend(
                (
                    (
                        bottom_first,
                        bottom_second,
                        top_second,
                    ),
                    (
                        bottom_first,
                        top_second,
                        top_first,
                    ),
                )
            )

        boundary_top = tuple(
            top_by_key[
                cls._point_key(point)
            ]
            for point in dense_boundary
        )

        interior_top = tuple(
            top_by_key[
                cls._point_key(point)
            ]
            for point in all_points
            if (
                cls._point_key(point)
                not in boundary_keys
            )
        )

        top = tuple(
            top_by_key[
                cls._point_key(point)
            ]
            for point in all_points
        )
        bottom = tuple(
            bottom_by_key[
                cls._point_key(point)
            ]
            for point in all_points
        )

        triangles = (
            *top_triangles,
            *bottom_triangles,
            *wall_triangles,
        )

        return {
            "type": "water_textured_solid",
            "top": top,
            "bottom": bottom,
            "boundary_top": boundary_top,
            "interior_top": interior_top,
            "walls": tuple(walls),
            "triangles": tuple(triangles),
            "surface_texture_enabled": (
                texture.enabled
            ),
            "surface_vertex_count": len(top),
            "boundary_vertex_count": len(
                boundary_top
            ),
            "interior_vertex_count": len(
                interior_top
            ),
            "maximum_edge_length_mm": (
                maximum_edge_length_mm
            ),
        }
