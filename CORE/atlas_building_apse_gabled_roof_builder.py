"""
ATLAS Building Apse-Gabled Roof Builder v0.2

Apsis footprint'ini bağlantı sınırının orta noktasından apsis ucuna
uzanan gerçek bir mahya ile iki çatı yüzeyine ayırır.
"""

import math

from shapely.geometry import (
    LineString,
    Point,
    Polygon,
)
from shapely.ops import (
    split,
    unary_union,
)

from CORE.atlas_polygon_triangulator import (
    AtlasPolygonTriangulator,
)


class AtlasBuildingApseGabledRoofBuilder:
    Z_TOLERANCE = 1e-7
    XY_TOLERANCE = 1e-7
    EAVE_LIFT_MM = 0.04

    CONTACT_BUFFER_MM = 0.05
    CONTACT_RATIO_MINIMUM = 0.90

    DEFAULT_ROOF_HEIGHT_RATIO = 0.24
    MIN_ROOF_HEIGHT_MM = 0.50
    MAX_INFERRED_ROOF_HEIGHT_MM = 4.00

    @staticmethod
    def apply(
        mesh,
        roof_height_m=None,
        coordinate_engine=None,
        adjacent_footprints=None,
    ):
        if not mesh:
            return mesh

        if mesh.get("building_roof_profile") != "apse_gabled":
            return mesh

        if mesh.get("is_castle_building") is True:
            return mesh

        ring = AtlasBuildingApseGabledRoofBuilder._clean_ring(
            mesh.get("top", [])
        )

        if len(ring) < 4:
            return mesh

        body_top_z = mesh.get("top_z")

        if body_top_z is None:
            body_top_z = (
                AtlasBuildingApseGabledRoofBuilder
                ._derive_z_level(
                    points=ring,
                    mode="max",
                )
            )

        bottom_z = mesh.get("bottom_z")

        if bottom_z is None:
            bottom_z = (
                AtlasBuildingApseGabledRoofBuilder
                ._derive_z_level(
                    points=mesh.get("bottom", []),
                    mode="min",
                )
            )

        if body_top_z is None:
            return mesh

        footprint = [
            (float(point[0]), float(point[1]))
            for point in ring
        ]

        ridge_context = (
            AtlasBuildingApseGabledRoofBuilder
            ._resolve_ridge_context(
                footprint=footprint,
                adjacent_footprints=adjacent_footprints,
            )
        )

        if ridge_context is None:
            return mesh

        connection_indices = list(
            ridge_context["connection_edge_indices"]
        )
        connection_start = ridge_context[
            "connection_start"
        ]
        connection_end = ridge_context[
            "connection_end"
        ]
        ridge_start_xy = ridge_context[
            "connection_midpoint"
        ]
        apse_tip_index = int(
            ridge_context["apse_tip_index"]
        )
        ridge_end_xy = footprint[apse_tip_index]

        roof_height_mm = (
            AtlasBuildingApseGabledRoofBuilder
            ._resolve_roof_height_mm(
                roof_height_m=roof_height_m,
                coordinate_engine=coordinate_engine,
                ring=ring,
                body_top_z=float(body_top_z),
                bottom_z=bottom_z,
            )
        )

        if roof_height_mm <= 0.0:
            return mesh

        count = len(footprint)

        architectural_context = (
            AtlasBuildingApseGabledRoofBuilder
            ._regularize_architectural_polygon(
                footprint=footprint,
                connection_edge_indices=connection_indices,
            )
        )

        if architectural_context is None:
            return mesh

        eave_z = (
            float(body_top_z)
            + AtlasBuildingApseGabledRoofBuilder
            .EAVE_LIFT_MM
        )
        ridge_z = float(body_top_z) + roof_height_mm

        roof_eave_points = [
            (
                float(point[0]),
                float(point[1]),
                eave_z,
            )
            for point in ring
        ]

        architectural_polygon = Polygon(
            architectural_context["architectural_ring"]
        )
        architectural_centroid = (
            architectural_polygon.centroid
        )

        roof_apex = (
            float(architectural_centroid.x),
            float(architectural_centroid.y),
            ridge_z,
        )

        roof_surface_triangles = []

        for index, first_eave_point in enumerate(
            roof_eave_points
        ):
            second_eave_point = roof_eave_points[
                (index + 1) % count
            ]

            roof_surface_triangles.append(
                (
                    first_eave_point,
                    second_eave_point,
                    roof_apex,
                )
            )

        remaining_triangles = []
        removed_top_count = 0

        for triangle in mesh.get("triangles", []):
            if (
                AtlasBuildingApseGabledRoofBuilder
                ._is_top_triangle(
                    triangle=triangle,
                    top_z=float(body_top_z),
                )
            ):
                removed_top_count += 1
                continue

            remaining_triangles.append(triangle)

        if removed_top_count == 0:
            return mesh

        side_triangles = []

        for index, body_point_1 in enumerate(ring):
            next_index = (index + 1) % count

            body_point_2 = ring[next_index]
            roof_point_1 = roof_eave_points[index]
            roof_point_2 = roof_eave_points[next_index]

            side_triangles.extend(
                [
                    (
                        body_point_1,
                        body_point_2,
                        roof_point_2,
                    ),
                    (
                        body_point_1,
                        roof_point_2,
                        roof_point_1,
                    ),
                ]
            )

        roof_triangles = [
            *roof_surface_triangles,
            *side_triangles,
        ]

        mesh["triangles"] = [
            *remaining_triangles,
            *roof_triangles,
        ]

        mesh["body_top_z"] = float(body_top_z)
        mesh["roof_top_z"] = ridge_z
        mesh["top_z"] = ridge_z
        mesh["roof_height_mm"] = roof_height_mm
        mesh["roof_geometry"] = "apse_gabled"

        mesh["roof_apex"] = roof_apex
        mesh["roof_ridge_start"] = roof_apex
        mesh["roof_ridge_end"] = (
            float(ridge_end_xy[0]),
            float(ridge_end_xy[1]),
            ridge_z,
        )

        mesh["apse_connection_edge_indices"] = (
            connection_indices
        )
        mesh["apse_connection_start"] = connection_start
        mesh["apse_connection_end"] = connection_end
        mesh["apse_tip"] = ridge_end_xy
        mesh["apse_architectural_ring"] = (
            architectural_context["architectural_ring"]
        )
        mesh["apse_roof_geometry"] = (
            "radial_polygon"
        )

        mesh[
            "building_apse_gabled_removed_top_triangles"
        ] = removed_top_count
        mesh["building_apse_gabled_roof_points"] = (
            roof_eave_points
        )
        mesh[
            "building_apse_gabled_surface_triangles"
        ] = roof_surface_triangles
        mesh["building_apse_gabled_roof_triangles"] = (
            roof_triangles
        )
        mesh["building_flat_roof_triangles"] = []
        mesh["building_roof_triangles"] = roof_triangles
        mesh["building_apse_gabled_roof_applied"] = True

        return mesh

    @staticmethod
    def _regularize_architectural_polygon(
        footprint,
        connection_edge_indices,
    ):
        if (
            not footprint
            or len(footprint) < 4
            or not connection_edge_indices
        ):
            return None

        try:
            normalized = [
                (
                    float(point[0]),
                    float(point[1]),
                )
                for point in footprint
            ]
        except (
            TypeError,
            ValueError,
            IndexError,
        ):
            return None

        polygon = Polygon(normalized)

        if polygon.is_empty or not polygon.is_valid:
            return None

        count = len(normalized)

        connection_indices = list(
            connection_edge_indices
        )

        first_connection_index = int(
            connection_indices[0]
        )
        last_connection_index = int(
            connection_indices[-1]
        )

        if (
            first_connection_index < 0
            or first_connection_index >= count
            or last_connection_index < 0
            or last_connection_index >= count
        ):
            return None

        connection_start = normalized[
            first_connection_index
        ]
        connection_end = normalized[
            (last_connection_index + 1) % count
        ]

        exposed_start_index = (
            last_connection_index + 1
        ) % count
        exposed_end_index = first_connection_index

        exposed_path = [
            normalized[exposed_start_index]
        ]
        cursor = exposed_start_index

        while cursor != exposed_end_index:
            cursor = (cursor + 1) % count

            if len(exposed_path) > count:
                return None

            exposed_path.append(
                normalized[cursor]
            )

        if len(exposed_path) < 3:
            return None

        xs = [
            point[0]
            for point in exposed_path
        ]
        ys = [
            point[1]
            for point in exposed_path
        ]

        diagonal = math.hypot(
            max(xs) - min(xs),
            max(ys) - min(ys),
        )

        tolerance = max(
            diagonal * 0.04,
            0.20,
            AtlasBuildingApseGabledRoofBuilder
            .XY_TOLERANCE,
        )

        simplified_line = LineString(
            exposed_path
        ).simplify(
            tolerance,
            preserve_topology=False,
        )

        simplified_exposed = [
            (
                float(point[0]),
                float(point[1]),
            )
            for point in simplified_line.coords
        ]

        if len(simplified_exposed) < 3:
            simplified_exposed = list(
                exposed_path
            )

        simplified_exposed[0] = connection_end
        simplified_exposed[-1] = connection_start

        architectural_ring = [
            connection_start,
            *simplified_exposed[:-1],
        ]

        cleaned_ring = []

        for point in architectural_ring:
            if (
                not cleaned_ring
                or point != cleaned_ring[-1]
            ):
                cleaned_ring.append(point)

        if (
            len(cleaned_ring) > 1
            and cleaned_ring[0] == cleaned_ring[-1]
        ):
            cleaned_ring.pop()

        if len(cleaned_ring) < 5:
            return None

        architectural_polygon = Polygon(
            cleaned_ring
        )

        if (
            architectural_polygon.is_empty
            or not architectural_polygon.is_valid
            or architectural_polygon.area <= 0.0
        ):
            return None

        return {
            "architectural_ring": cleaned_ring,
            "exposed_eave_points": cleaned_ring[1:],
            "connection_start": connection_start,
            "connection_end": connection_end,
        }

    @staticmethod
    def _resolve_ridge_context(
        footprint,
        adjacent_footprints,
    ):
        polygon = Polygon(footprint)

        if polygon.is_empty or not polygon.is_valid:
            return None

        contact_indices = []

        adjacent_polygons = []

        for adjacent in adjacent_footprints or []:
            try:
                adjacent_polygon = Polygon(adjacent)
            except (TypeError, ValueError):
                continue

            if (
                adjacent_polygon.is_empty
                or not adjacent_polygon.is_valid
            ):
                continue

            adjacent_polygons.append(adjacent_polygon)

        if adjacent_polygons:
            adjacent_union = unary_union(adjacent_polygons)
            contact_zone = adjacent_union.buffer(
                AtlasBuildingApseGabledRoofBuilder
                .CONTACT_BUFFER_MM
            )

            for index, start in enumerate(footprint):
                end = footprint[
                    (index + 1) % len(footprint)
                ]
                edge = LineString([start, end])

                if edge.length <= 0.0:
                    continue

                overlap = edge.intersection(
                    contact_zone
                ).length

                if (
                    overlap / edge.length
                    >= AtlasBuildingApseGabledRoofBuilder
                    .CONTACT_RATIO_MINIMUM
                ):
                    contact_indices.append(index)

        if contact_indices:
            groups = (
                AtlasBuildingApseGabledRoofBuilder
                ._contiguous_circular_groups(
                    contact_indices,
                    len(footprint),
                )
            )

            connection_indices = max(
                groups,
                key=lambda group: (
                    len(group),
                    sum(
                        LineString(
                            [
                                footprint[index],
                                footprint[
                                    (index + 1)
                                    % len(footprint)
                                ],
                            ]
                        ).length
                        for index in group
                    ),
                ),
            )
        else:
            connection_indices = [
                max(
                    range(len(footprint)),
                    key=lambda index: LineString(
                        [
                            footprint[index],
                            footprint[
                                (index + 1)
                                % len(footprint)
                            ],
                        ]
                    ).length,
                )
            ]

        first_index = connection_indices[0]
        last_index = connection_indices[-1]

        connection_start = footprint[first_index]
        connection_end = footprint[
            (last_index + 1) % len(footprint)
        ]

        connection_midpoint = (
            AtlasBuildingApseGabledRoofBuilder
            ._polyline_midpoint(
                points=[
                    footprint[
                        connection_indices[0]
                    ],
                    *[
                        footprint[
                            (index + 1)
                            % len(footprint)
                        ]
                        for index
                        in connection_indices
                    ],
                ]
            )
        )

        if connection_midpoint is None:
            return None

        connection_set = set(connection_indices)

        exposed_indices = [
            index
            for index in range(len(footprint))
            if (
                index not in connection_set
                and (
                    (index - 1) % len(footprint)
                ) not in connection_set
            )
        ]

        if not exposed_indices:
            return None

        tip_index = max(
            exposed_indices,
            key=lambda index: math.hypot(
                footprint[index][0]
                - connection_midpoint[0],
                footprint[index][1]
                - connection_midpoint[1],
            ),
        )

        return {
            "connection_edge_indices": list(
                connection_indices
            ),
            "connection_start": connection_start,
            "connection_end": connection_end,
            "connection_midpoint": connection_midpoint,
            "apse_tip": footprint[tip_index],
            "apse_tip_index": tip_index,
        }

    @staticmethod
    def _xy_point_key(point):
        return (
            round(float(point[0]), 8),
            round(float(point[1]), 8),
        )

    @staticmethod
    def _xy_edge_key(first, second):
        return tuple(
            sorted(
                (
                    AtlasBuildingApseGabledRoofBuilder
                    ._xy_point_key(first),
                    AtlasBuildingApseGabledRoofBuilder
                    ._xy_point_key(second),
                )
            )
        )

    @staticmethod
    def _triangle_contains_xy_edge(
        triangle,
        edge_keys,
    ):
        if len(triangle) != 3:
            return False

        triangle_edge_keys = {
            AtlasBuildingApseGabledRoofBuilder
            ._xy_edge_key(
                triangle[index],
                triangle[(index + 1) % 3],
            )
            for index in range(3)
        }

        return bool(
            triangle_edge_keys & edge_keys
        )

    @staticmethod
    def _build_split_roof_surface(
        footprint,
        ridge_start,
        ridge_end,
        eave_z,
        ridge_z,
    ):
        polygon = Polygon(footprint)

        if polygon.is_empty or not polygon.is_valid:
            return []

        ridge_line = LineString(
            [ridge_start, ridge_end]
        )

        try:
            split_result = split(
                polygon,
                ridge_line,
            )
        except ValueError:
            return []

        roof_polygons = [
            geometry
            for geometry in split_result.geoms
            if (
                geometry.geom_type == "Polygon"
                and geometry.area > 0.0
            )
        ]

        if len(roof_polygons) != 2:
            return []

        roof_triangles = []

        for roof_polygon in roof_polygons:
            coordinates = list(
                roof_polygon.exterior.coords
            )[:-1]

            surface_triangles = (
                AtlasPolygonTriangulator.triangulate(
                    coordinates
                )
            )

            for triangle in surface_triangles:
                mapped = []

                for x, y in triangle:
                    is_ridge_point = (
                        Point(float(x), float(y))
                        .distance(ridge_line)
                        <= AtlasBuildingApseGabledRoofBuilder
                        .XY_TOLERANCE
                    )

                    mapped.append(
                        (
                            float(x),
                            float(y),
                            (
                                ridge_z
                                if is_ridge_point
                                else eave_z
                            ),
                        )
                    )

                roof_triangles.append(tuple(mapped))

        return roof_triangles

    @staticmethod
    def _polyline_midpoint(points):
        if not points or len(points) < 2:
            return None

        segments = []
        total_length = 0.0

        for start, end in zip(
            points,
            points[1:],
        ):
            length = math.hypot(
                float(end[0]) - float(start[0]),
                float(end[1]) - float(start[1]),
            )

            if length <= 0.0:
                continue

            segments.append(
                (
                    start,
                    end,
                    length,
                )
            )
            total_length += length

        if total_length <= 0.0:
            return None

        target_length = total_length / 2.0
        traversed = 0.0

        for start, end, length in segments:
            segment_end = traversed + length

            if target_length <= segment_end:
                ratio = (
                    target_length - traversed
                ) / length

                return (
                    float(start[0])
                    + (
                        float(end[0])
                        - float(start[0])
                    )
                    * ratio,
                    float(start[1])
                    + (
                        float(end[1])
                        - float(start[1])
                    )
                    * ratio,
                )

            traversed = segment_end

        final_point = points[-1]

        return (
            float(final_point[0]),
            float(final_point[1]),
        )

    @staticmethod
    def _contiguous_circular_groups(
        indices,
        count,
    ):
        ordered = sorted(set(indices))

        if not ordered:
            return []

        groups = [[ordered[0]]]

        for index in ordered[1:]:
            if index == groups[-1][-1] + 1:
                groups[-1].append(index)
            else:
                groups.append([index])

        if (
            len(groups) > 1
            and groups[0][0] == 0
            and groups[-1][-1] == count - 1
        ):
            groups[0] = groups[-1] + groups[0]
            groups.pop()

        return groups

    @staticmethod
    def _resolve_roof_height_mm(
        roof_height_m,
        coordinate_engine,
        ring,
        body_top_z,
        bottom_z,
    ):
        parsed_height_m = (
            AtlasBuildingApseGabledRoofBuilder
            ._parse_positive_float(roof_height_m)
        )

        if (
            parsed_height_m is not None
            and coordinate_engine is not None
        ):
            try:
                resolved_height_mm = float(
                    coordinate_engine.height_to_stl_mm(
                        parsed_height_m
                    )
                )
            except (
                AttributeError,
                TypeError,
                ValueError,
            ):
                resolved_height_mm = None

            if (
                resolved_height_mm is not None
                and math.isfinite(resolved_height_mm)
                and resolved_height_mm > 0.0
            ):
                return resolved_height_mm

        xs = [point[0] for point in ring]
        ys = [point[1] for point in ring]

        short_span_mm = min(
            max(xs) - min(xs),
            max(ys) - min(ys),
        )

        body_height_mm = 0.0

        if bottom_z is not None:
            body_height_mm = max(
                0.0,
                float(body_top_z) - float(bottom_z),
            )

        inferred_height_mm = max(
            short_span_mm
            * AtlasBuildingApseGabledRoofBuilder
            .DEFAULT_ROOF_HEIGHT_RATIO,
            body_height_mm
            * AtlasBuildingApseGabledRoofBuilder
            .DEFAULT_ROOF_HEIGHT_RATIO,
            AtlasBuildingApseGabledRoofBuilder
            .MIN_ROOF_HEIGHT_MM,
        )

        return min(
            inferred_height_mm,
            AtlasBuildingApseGabledRoofBuilder
            .MAX_INFERRED_ROOF_HEIGHT_MM,
        )

    @staticmethod
    def _parse_positive_float(value):
        if value is None:
            return None

        try:
            parsed = float(
                str(value)
                .strip()
                .lower()
                .replace("meters", "")
                .replace("meter", "")
                .replace("metres", "")
                .replace("metre", "")
                .replace("m", "")
                .strip()
            )
        except (TypeError, ValueError):
            return None

        if parsed <= 0.0:
            return None

        return parsed

    @staticmethod
    def _clean_ring(points):
        cleaned = []

        for point in points:
            if len(point) < 3:
                continue

            normalized = (
                float(point[0]),
                float(point[1]),
                float(point[2]),
            )

            if cleaned and normalized == cleaned[-1]:
                continue

            cleaned.append(normalized)

        if (
            len(cleaned) > 1
            and cleaned[0] == cleaned[-1]
        ):
            cleaned.pop()

        return cleaned

    @staticmethod
    def _derive_z_level(points, mode):
        values = []

        for point in points:
            if len(point) < 3:
                continue

            try:
                value = float(point[2])
            except (TypeError, ValueError):
                continue

            if math.isfinite(value):
                values.append(value)

        if not values:
            return None

        return (
            max(values)
            if mode == "max"
            else min(values)
        )

    @staticmethod
    def _is_top_triangle(
        triangle,
        top_z,
    ):
        if len(triangle) != 3:
            return False

        return all(
            len(point) >= 3
            and abs(float(point[2]) - top_z)
            <= AtlasBuildingApseGabledRoofBuilder
            .Z_TOLERANCE
            for point in triangle
        )
