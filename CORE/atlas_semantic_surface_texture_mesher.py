import math

from shapely import constrained_delaunay_triangles
from shapely.geometry import Point, Polygon

from CORE.atlas_foundation_sampler import (
    AtlasFoundationSampler,
)
from CORE.atlas_semantic_surface_texture_pattern import (
    AtlasSemanticSurfaceTexturePattern,
)


class AtlasSemanticSurfaceTextureMesher:
    GEOMETRY_EPSILON = 1e-9
    POINT_PRECISION = 9

    @classmethod
    def _positive_float(
        cls,
        value,
        name,
    ):
        try:
            parsed = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{name} must be positive"
            ) from exc

        if (
            not math.isfinite(parsed)
            or parsed <= 0.0
        ):
            raise ValueError(
                f"{name} must be positive"
            )

        return parsed

    @classmethod
    def _finite_float(
        cls,
        value,
        name,
    ):
        try:
            parsed = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{name} must be finite"
            ) from exc

        if not math.isfinite(parsed):
            raise ValueError(
                f"{name} must be finite"
            )

        return parsed

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

            dx = (
                float(end[0])
                - float(start[0])
            )
            dy = (
                float(end[1])
                - float(start[1])
            )

            length = math.hypot(
                dx,
                dy,
            )

            segment_count = max(
                1,
                int(
                    math.ceil(
                        length
                        / maximum_edge_length_mm
                    )
                ),
            )

            for step in range(
                segment_count
            ):
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
        (
            minimum_x,
            minimum_y,
            maximum_x,
            maximum_y,
        ) = polygon.bounds

        points = []

        x = (
            minimum_x
            + maximum_edge_length_mm
        )

        while (
            x
            < maximum_x
            - cls.GEOMETRY_EPSILON
        ):
            y = (
                minimum_y
                + maximum_edge_length_mm
            )

            while (
                y
                < maximum_y
                - cls.GEOMETRY_EPSILON
            ):
                point = Point(
                    x,
                    y,
                )

                if polygon.contains(
                    point
                ):
                    points.append(
                        (
                            float(x),
                            float(y),
                        )
                    )

                y += maximum_edge_length_mm

            x += maximum_edge_length_mm

        return tuple(
            points
        )

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
        maximum_edge_length_mm,
    ):
        constrained = (
            constrained_delaunay_triangles(
                polygon
            )
        )

        resolved = []

        def normalized_triangle(
            points,
        ):
            coordinates = [
                (
                    float(point[0]),
                    float(point[1]),
                )
                for point in points
            ]

            if (
                abs(
                    cls._signed_area(
                        coordinates
                    )
                )
                <= cls.GEOMETRY_EPSILON
            ):
                return None

            if (
                cls._signed_area(
                    coordinates
                )
                < 0.0
            ):
                coordinates = [
                    coordinates[0],
                    coordinates[2],
                    coordinates[1],
                ]

            return tuple(
                coordinates
            )

        def point_on_segment(
            point,
            first,
            second,
        ):
            px, py = point
            ax, ay = first
            bx, by = second

            dx = bx - ax
            dy = by - ay

            length = math.hypot(
                dx,
                dy,
            )

            if (
                length
                <= cls.GEOMETRY_EPSILON
            ):
                return False

            cross = abs(
                (
                    px - ax
                ) * dy
                - (
                    py - ay
                ) * dx
            )

            if (
                cross
                > (
                    cls.GEOMETRY_EPSILON
                    * max(
                        1.0,
                        length,
                    )
                )
            ):
                return False

            dot = (
                (
                    px - ax
                ) * (
                    px - bx
                )
                + (
                    py - ay
                ) * (
                    py - by
                )
            )

            return (
                dot
                <= cls.GEOMETRY_EPSILON
            )

        for candidate in (
            constrained.geoms
        ):
            if (
                candidate.is_empty
                or candidate.area
                <= cls.GEOMETRY_EPSILON
            ):
                continue

            triangle = normalized_triangle(
                list(
                    candidate.exterior.coords
                )[:-1]
            )

            if triangle is not None:
                resolved.append(
                    triangle
                )

        if not resolved:
            raise ValueError(
                "Semantic surface triangulation "
                "produced no triangles"
            )

        vertex_keys = {
            cls._point_key(
                point
            )
            for triangle in resolved
            for point in triangle
        }

        for raw_point in all_points:
            point = (
                float(raw_point[0]),
                float(raw_point[1]),
            )

            key = cls._point_key(
                point
            )

            if key in vertex_keys:
                continue

            def point_in_triangle(
                point,
                triangle,
            ):
                first, second, third = triangle

                def cross(
                    origin,
                    edge_end,
                    test_point,
                ):
                    return (
                        (
                            edge_end[0]
                            - origin[0]
                        )
                        * (
                            test_point[1]
                            - origin[1]
                        )
                        - (
                            edge_end[1]
                            - origin[1]
                        )
                        * (
                            test_point[0]
                            - origin[0]
                        )
                    )

                values = (
                    cross(
                        first,
                        second,
                        point,
                    ),
                    cross(
                        second,
                        third,
                        point,
                    ),
                    cross(
                        third,
                        first,
                        point,
                    ),
                )

                tolerance = (
                    cls.GEOMETRY_EPSILON
                    * max(
                        1.0,
                        *(
                            math.hypot(
                                edge_end[0]
                                - origin[0],
                                edge_end[1]
                                - origin[1],
                            )
                            for origin, edge_end
                            in (
                                (
                                    first,
                                    second,
                                ),
                                (
                                    second,
                                    third,
                                ),
                                (
                                    third,
                                    first,
                                ),
                            )
                        ),
                    )
                )

                has_negative = any(
                    value < -tolerance
                    for value in values
                )

                has_positive = any(
                    value > tolerance
                    for value in values
                )

                return not (
                    has_negative
                    and has_positive
                )

            containing = {
                index
                for index, triangle
                in enumerate(
                    resolved
                )
                if point_in_triangle(
                    point,
                    triangle,
                )
            }

            if not containing:
                continue

            next_resolved = []

            for index, triangle in enumerate(
                resolved
            ):
                if index not in containing:
                    next_resolved.append(
                        triangle
                    )
                    continue

                first, second, third = (
                    triangle
                )

                edge_match = None

                for (
                    edge_first,
                    edge_second,
                    opposite,
                ) in (
                    (
                        first,
                        second,
                        third,
                    ),
                    (
                        second,
                        third,
                        first,
                    ),
                    (
                        third,
                        first,
                        second,
                    ),
                ):
                    if point_on_segment(
                        point,
                        edge_first,
                        edge_second,
                    ):
                        edge_match = (
                            edge_first,
                            edge_second,
                            opposite,
                        )
                        break

                if edge_match is None:
                    pieces = (
                        (
                            first,
                            second,
                            point,
                        ),
                        (
                            second,
                            third,
                            point,
                        ),
                        (
                            third,
                            first,
                            point,
                        ),
                    )
                else:
                    (
                        edge_first,
                        edge_second,
                        opposite,
                    ) = edge_match

                    pieces = (
                        (
                            edge_first,
                            point,
                            opposite,
                        ),
                        (
                            point,
                            edge_second,
                            opposite,
                        ),
                    )

                for piece in pieces:
                    candidate = (
                        normalized_triangle(
                            piece
                        )
                    )

                    if candidate is not None:
                        next_resolved.append(
                            candidate
                        )

            resolved = next_resolved
            vertex_keys.add(
                key
            )

        boundary_coordinates = tuple(
            (
                float(x),
                float(y),
            )
            for x, y in list(
                polygon.exterior.coords
            )[:-1]
        )

        boundary_edges = {
            tuple(
                sorted(
                    (
                        cls._point_key(
                            boundary_coordinates[index]
                        ),
                        cls._point_key(
                            boundary_coordinates[
                                (index + 1)
                                % len(boundary_coordinates)
                            ]
                        ),
                    )
                )
            )
            for index in range(
                len(boundary_coordinates)
            )
        }

        edge_limit = (
            maximum_edge_length_mm
            * 2.0
        )

        while True:
            edge_owners = {}

            for triangle_index, triangle in enumerate(
                resolved
            ):
                for first, second in (
                    (
                        triangle[0],
                        triangle[1],
                    ),
                    (
                        triangle[1],
                        triangle[2],
                    ),
                    (
                        triangle[2],
                        triangle[0],
                    ),
                ):
                    edge = tuple(
                        sorted(
                            (
                                cls._point_key(
                                    first
                                ),
                                cls._point_key(
                                    second
                                ),
                            )
                        )
                    )

                    edge_owners.setdefault(
                        edge,
                        [],
                    ).append(
                        (
                            triangle_index,
                            first,
                            second,
                        )
                    )

            candidates = []

            for edge, owners in (
                edge_owners.items()
            ):
                if (
                    edge in boundary_edges
                    or len(owners) != 2
                ):
                    continue

                first = owners[0][1]
                second = owners[0][2]

                length = math.hypot(
                    float(second[0])
                    - float(first[0]),
                    float(second[1])
                    - float(first[1]),
                )

                if (
                    length
                    > edge_limit
                    + cls.GEOMETRY_EPSILON
                ):
                    candidates.append(
                        (
                            -length,
                            edge,
                            owners,
                        )
                    )

            if not candidates:
                break

            candidates.sort(
                key=lambda item: (
                    item[0],
                    item[1],
                )
            )

            _, edge, owners = (
                candidates[0]
            )

            first = owners[0][1]
            second = owners[0][2]

            midpoint = (
                (
                    float(first[0])
                    + float(second[0])
                )
                / 2.0,
                (
                    float(first[1])
                    + float(second[1])
                )
                / 2.0,
            )

            owner_indices = {
                owner[0]
                for owner in owners
            }

            next_resolved = []

            for triangle_index, triangle in enumerate(
                resolved
            ):
                if (
                    triangle_index
                    not in owner_indices
                ):
                    next_resolved.append(
                        triangle
                    )
                    continue

                edge_keys = set(
                    edge
                )

                opposite = next(
                    point
                    for point in triangle
                    if (
                        cls._point_key(
                            point
                        )
                        not in edge_keys
                    )
                )

                for piece in (
                    (
                        first,
                        midpoint,
                        opposite,
                    ),
                    (
                        midpoint,
                        second,
                        opposite,
                    ),
                ):
                    candidate = (
                        normalized_triangle(
                            piece
                        )
                    )

                    if candidate is not None:
                        next_resolved.append(
                            candidate
                        )

            resolved = next_resolved

        return tuple(
            resolved
        )

    @classmethod
    def build(
        cls,
        *,
        boundary_points,
        bottom_z,
        surface_z,
        pattern,
        maximum_edge_length_mm,
    ):
        maximum_edge_length_mm = (
            cls._positive_float(
                maximum_edge_length_mm,
                "maximum_edge_length_mm",
            )
        )

        bottom_z = cls._finite_float(
            bottom_z,
            "bottom_z",
        )

        surface_z = cls._finite_float(
            surface_z,
            "surface_z",
        )

        if surface_z <= bottom_z:
            raise ValueError(
                "surface_z must be greater than bottom_z"
            )

        if not isinstance(
            pattern,
            AtlasSemanticSurfaceTexturePattern,
        ):
            raise TypeError(
                "pattern must be an "
                "AtlasSemanticSurfaceTexturePattern"
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

        polygon = Polygon(
            boundary_points
        )

        if not polygon.is_valid:
            polygon = polygon.buffer(
                0
            )

        if (
            polygon.is_empty
            or polygon.geom_type != "Polygon"
            or polygon.area
            <= cls.GEOMETRY_EPSILON
        ):
            raise ValueError(
                "boundary_points must form "
                "one valid polygon"
            )

        dense_boundary = (
            cls._densify_boundary(
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
        )

        all_points = (
            cls._deduplicate_points(
                dense_boundary
            )
        )

        surface_polygon = Polygon(
            dense_boundary
        )

        surface_triangles_xy = (
            cls._surface_triangles(
                polygon=surface_polygon,
                all_points=all_points,
                maximum_edge_length_mm=(
                    maximum_edge_length_mm
                ),
            )
        )

        all_points = (
            cls._deduplicate_points(
                (
                    *all_points,
                    *(
                        point
                        for triangle
                        in surface_triangles_xy
                        for point in triangle
                    ),
                )
            )
        )

        boundary_keys = {
            cls._point_key(
                point
            )
            for point in dense_boundary
        }

        top_by_key = {}
        bottom_by_key = {}

        for x, y in all_points:
            key = cls._point_key(
                (
                    x,
                    y,
                )
            )

            offset_mm = pattern.offset_at(
                x,
                y,
            )

            if key in boundary_keys:
                offset_mm = 0.0

            top_by_key[key] = (
                float(x),
                float(y),
                float(
                    surface_z
                    + offset_mm
                ),
            )

            bottom_by_key[key] = (
                float(x),
                float(y),
                float(bottom_z),
            )

        top_triangles = []
        bottom_triangles = []

        for triangle_xy in (
            surface_triangles_xy
        ):
            keys = tuple(
                cls._point_key(
                    point
                )
                for point in triangle_xy
            )

            top_triangle = tuple(
                top_by_key[key]
                for key in keys
            )

            bottom_triangle = tuple(
                bottom_by_key[key]
                for key in reversed(
                    keys
                )
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
            len(
                dense_boundary
            )
        ):
            next_index = (
                index + 1
            ) % len(
                dense_boundary
            )

            first_key = cls._point_key(
                dense_boundary[
                    index
                ]
            )

            second_key = cls._point_key(
                dense_boundary[
                    next_index
                ]
            )

            bottom_first = (
                bottom_by_key[
                    first_key
                ]
            )
            bottom_second = (
                bottom_by_key[
                    second_key
                ]
            )
            top_first = (
                top_by_key[
                    first_key
                ]
            )
            top_second = (
                top_by_key[
                    second_key
                ]
            )

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
                cls._point_key(
                    point
                )
            ]
            for point in dense_boundary
        )

        interior_top = tuple(
            top_by_key[
                cls._point_key(
                    point
                )
            ]
            for point in all_points
            if (
                cls._point_key(
                    point
                )
                not in boundary_keys
            )
        )

        top = tuple(
            top_by_key[
                cls._point_key(
                    point
                )
            ]
            for point in all_points
        )

        bottom = tuple(
            bottom_by_key[
                cls._point_key(
                    point
                )
            ]
            for point in all_points
        )

        triangles = [
            *top_triangles,
            *bottom_triangles,
            *wall_triangles,
        ]

        return {
            "type": (
                "semantic_surface_texture"
            ),
            "bottom": bottom,
            "top": top,
            "walls": tuple(
                walls
            ),
            "triangles": triangles,
            "boundary_top": (
                boundary_top
            ),
            "interior_top": (
                interior_top
            ),
            "surface_texture_enabled": True,
            "surface_vertex_count": len(
                top
            ),
            "maximum_edge_length_mm": (
                maximum_edge_length_mm
            ),
            "texture_language": (
                pattern.texture_language
            ),
            "relief_depth_mm": (
                pattern.relief_depth_mm
            ),
            "feature_pitch_mm": (
                pattern.feature_pitch_mm
            ),
        }

    @classmethod
    def build_terrain_following(
        cls,
        *,
        boundary_points,
        terrain_mesh,
        foundation_height_mm,
        pattern,
        maximum_edge_length_mm,
    ):
        foundation_height_mm = cls._positive_float(
            foundation_height_mm,
            "foundation_height_mm",
        )

        base = cls.build(
            boundary_points=boundary_points,
            bottom_z=0.0,
            surface_z=foundation_height_mm,
            pattern=pattern,
            maximum_edge_length_mm=maximum_edge_length_mm,
        )

        bottom_by_key = {}
        top_by_key = {}

        for bottom_point, top_point in zip(
            base["bottom"],
            base["top"],
        ):
            x = float(bottom_point[0])
            y = float(bottom_point[1])

            terrain_z = (
                AtlasFoundationSampler
                .terrain_z_at_xy(
                    terrain_mesh=terrain_mesh,
                    x=x,
                    y=y,
                )
            )

            semantic_offset = (
                float(top_point[2])
                - foundation_height_mm
            )

            key = cls._point_key(
                (x, y)
            )

            bottom_by_key[key] = (
                x,
                y,
                float(terrain_z),
            )

            top_by_key[key] = (
                x,
                y,
                float(
                    terrain_z
                    + foundation_height_mm
                    + semantic_offset
                ),
            )

        def remap_point(point):
            key = cls._point_key(
                point
            )

            if (
                abs(float(point[2]))
                <= cls.GEOMETRY_EPSILON
            ):
                return bottom_by_key[key]

            return top_by_key[key]

        result = dict(base)

        result["bottom"] = tuple(
            bottom_by_key[
                cls._point_key(point)
            ]
            for point in base["bottom"]
        )

        result["top"] = tuple(
            top_by_key[
                cls._point_key(point)
            ]
            for point in base["top"]
        )

        result["boundary_top"] = tuple(
            top_by_key[
                cls._point_key(point)
            ]
            for point in base["boundary_top"]
        )

        result["interior_top"] = tuple(
            top_by_key[
                cls._point_key(point)
            ]
            for point in base["interior_top"]
        )

        result["walls"] = tuple(
            tuple(
                remap_point(point)
                for point in wall
            )
            for wall in base["walls"]
        )

        result["triangles"] = tuple(
            tuple(
                remap_point(point)
                for point in triangle
            )
            for triangle in base["triangles"]
        )

        result["placement_mode"] = (
            "terrain_following"
        )
        result["foundation_height_mm"] = (
            foundation_height_mm
        )

        return result
