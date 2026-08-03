import math

from CORE.atlas_bridge_builder import AtlasBridgeGeometry
from CORE.atlas_bridge_longitudinal_profile import (
    AtlasBridgeLongitudinalProfile,
)
from CORE.atlas_bridge_segmented_deck_builder import (
    AtlasBridgeSegmentedDeckBuilder,
)
from CORE.atlas_castle_shell_triangulator import (
    AtlasCastleShellTriangulator,
)
from CORE.atlas_lighthouse_builder import AtlasLighthouseGeometry
from CORE.atlas_rock_cut_tomb_builder import AtlasRockCutTombGeometry
from CORE.atlas_tower_builder import AtlasTowerGeometry


class AtlasLandmarkGeometryMesher:
    @classmethod
    def build(cls, geometry):
        if isinstance(geometry, AtlasBridgeGeometry):
            return cls._build_bridge_mesh(geometry)

        if isinstance(geometry, AtlasLighthouseGeometry):
            return cls._build_lighthouse_mesh(geometry)

        if isinstance(geometry, AtlasTowerGeometry):
            return cls._build_tower_mesh(geometry)

        if isinstance(geometry, AtlasRockCutTombGeometry):
            return cls._build_rock_cut_tomb_mesh(geometry)

        raise TypeError(
            f"Unsupported landmark geometry: {type(geometry).__name__}"
        )

    @classmethod
    def _build_rock_cut_tomb_mesh(cls, geometry):
        footprint = tuple(
            (
                float(x),
                float(y),
            )
            for x, y in geometry.footprint
        )

        if len(footprint) < 3:
            raise ValueError(
                "Rock-cut tomb footprint requires at least three points"
            )

        height = float(geometry.height_m)

        if height <= 0.0:
            raise ValueError(
                "Rock-cut tomb height must be positive"
            )

        bottom = tuple(
            (
                x,
                y,
                0.0,
            )
            for x, y in footprint
        )

        top = tuple(
            (
                x,
                y,
                height,
            )
            for x, y in footprint
        )

        triangles = []

        triangles.extend(
            cls._polygon_triangulate(
                bottom,
                reverse=True,
            )
        )

        triangles.extend(
            cls._polygon_triangulate(top)
        )

        for index in range(len(footprint)):
            next_index = (
                index + 1
            ) % len(footprint)

            bottom_left = bottom[index]
            bottom_right = bottom[next_index]
            top_left = top[index]
            top_right = top[next_index]

            triangles.extend(
                (
                    (
                        bottom_left,
                        bottom_right,
                        top_right,
                    ),
                    (
                        bottom_left,
                        top_right,
                        top_left,
                    ),
                )
            )

        return {
            "type": "rock_cut_tomb",
            "triangles": triangles,
            "bottom": bottom,
            "top": top,
        }

    @staticmethod
    def _fan_triangulate(ring, reverse=False):
        triangles = []
        if len(ring) < 3:
            return triangles

        anchor = ring[0]
        for index in range(1, len(ring) - 1):
            triangle = (
                anchor,
                ring[index],
                ring[index + 1],
            )
            if reverse:
                triangle = (
                    triangle[0],
                    triangle[2],
                    triangle[1],
                )
            triangles.append(triangle)

        return triangles

    @staticmethod
    def _polygon_triangulate(ring, reverse=False):
        if len(ring) < 3:
            return []

        z_values = {
            round(float(point[2]), 12)
            for point in ring
        }

        if len(z_values) != 1:
            raise ValueError(
                "Polygon triangulation requires a planar horizontal ring"
            )

        z = float(ring[0][2])

        triangles_2d = (
            AtlasCastleShellTriangulator.triangulate(
                outer_ring=[
                    (float(x), float(y))
                    for x, y, _ in ring
                ],
                inner_rings=[],
            )
        )

        triangles = []

        for triangle_2d in triangles_2d:
            triangle = tuple(
                (
                    float(x),
                    float(y),
                    z,
                )
                for x, y in triangle_2d
            )

            if reverse:
                triangle = (
                    triangle[0],
                    triangle[2],
                    triangle[1],
                )

            triangles.append(triangle)

        return triangles

    @staticmethod
    def _xy_key(point):
        return (
            round(float(point[0]), 12),
            round(float(point[1]), 12),
        )

    @staticmethod
    def _point_is_between_on_segment(
        start,
        point,
        end,
        tolerance=1e-9,
    ):
        start_x, start_y = start[:2]
        point_x, point_y = point[:2]
        end_x, end_y = end[:2]

        edge_x = end_x - start_x
        edge_y = end_y - start_y

        relative_x = point_x - start_x
        relative_y = point_y - start_y

        cross = (
            edge_x * relative_y
            - edge_y * relative_x
        )

        scale = max(
            1.0,
            abs(edge_x),
            abs(edge_y),
        )

        if abs(cross) > tolerance * scale:
            return False

        dot = (
            relative_x * edge_x
            + relative_y * edge_y
        )

        squared_length = (
            edge_x * edge_x
            + edge_y * edge_y
        )

        return (
            -tolerance
            <= dot
            <= squared_length + tolerance
        )

    @classmethod
    def _ring_chain(
        cls,
        ring,
        start_index,
        end_index,
        step,
    ):
        chain = [ring[start_index]]
        index = start_index
        count = len(ring)

        while index != end_index:
            index = (index + step) % count
            chain.append(ring[index])

        return tuple(chain)

    @classmethod
    def _resolve_collinear_boundary_chain(
        cls,
        ring,
        start,
        end,
    ):
        index_by_xy = {
            cls._xy_key(point): index
            for index, point in enumerate(ring)
        }

        start_index = index_by_xy.get(
            cls._xy_key(start)
        )
        end_index = index_by_xy.get(
            cls._xy_key(end)
        )

        if (
            start_index is None
            or end_index is None
            or start_index == end_index
        ):
            return None

        candidates = (
            cls._ring_chain(
                ring=ring,
                start_index=start_index,
                end_index=end_index,
                step=1,
            ),
            cls._ring_chain(
                ring=ring,
                start_index=start_index,
                end_index=end_index,
                step=-1,
            ),
        )

        for chain in candidates:
            if len(chain) <= 2:
                continue

            if all(
                cls._point_is_between_on_segment(
                    start=chain[0],
                    point=point,
                    end=chain[-1],
                )
                for point in chain[1:-1]
            ):
                return chain

        return None

    @classmethod
    def _refine_surface_boundary_edges(
        cls,
        triangles,
        ring,
    ):
        pending = list(triangles)
        refined = []

        while pending:
            triangle = pending.pop()
            first, second, third = triangle

            edge_records = (
                (first, second, third),
                (second, third, first),
                (third, first, second),
            )

            was_split = False

            for edge_start, edge_end, opposite in edge_records:
                chain = cls._resolve_collinear_boundary_chain(
                    ring=ring,
                    start=edge_start,
                    end=edge_end,
                )

                if chain is None:
                    continue

                for index in range(len(chain) - 1):
                    pending.append(
                        (
                            chain[index],
                            chain[index + 1],
                            opposite,
                        )
                    )

                was_split = True
                break

            if not was_split:
                refined.append(triangle)

        return refined

    @classmethod
    def _polygon_surface_triangulate(
        cls,
        ring,
        reverse=False,
    ):
        if len(ring) < 3:
            return []

        z_by_xy = {
            (
                round(float(x), 12),
                round(float(y), 12),
            ): float(z)
            for x, y, z in ring
        }

        triangles_2d = (
            AtlasCastleShellTriangulator.triangulate(
                outer_ring=[
                    (float(x), float(y))
                    for x, y, _ in ring
                ],
                inner_rings=[],
            )
        )

        triangles = []

        for triangle_2d in triangles_2d:
            triangle = tuple(
                (
                    float(x),
                    float(y),
                    z_by_xy[
                        (
                            round(float(x), 12),
                            round(float(y), 12),
                        )
                    ],
                )
                for x, y in triangle_2d
            )

            if reverse:
                triangle = (
                    triangle[0],
                    triangle[2],
                    triangle[1],
                )

            triangles.append(triangle)

        return cls._refine_surface_boundary_edges(
            triangles=triangles,
            ring=ring,
        )

    @staticmethod
    def _densify_ring(
        ring,
        maximum_edge_length,
    ):
        ring = tuple(
            (float(x), float(y))
            for x, y in ring
        )
        maximum_edge_length = float(
            maximum_edge_length
        )

        if maximum_edge_length <= 0.0:
            raise ValueError(
                "maximum_edge_length must be greater than 0"
            )

        if len(ring) < 3:
            raise ValueError(
                "Ring requires at least 3 points"
            )

        densified = []

        for index, start in enumerate(ring):
            end = ring[
                (index + 1) % len(ring)
            ]

            start_x, start_y = start
            end_x, end_y = end

            edge_length = math.hypot(
                end_x - start_x,
                end_y - start_y,
            )

            segment_count = max(
                1,
                math.ceil(
                    edge_length
                    / maximum_edge_length
                ),
            )

            for segment_index in range(
                segment_count
            ):
                ratio = (
                    segment_index
                    / segment_count
                )

                densified.append(
                    (
                        start_x
                        + (end_x - start_x)
                        * ratio,
                        start_y
                        + (end_y - start_y)
                        * ratio,
                    )
                )

        return tuple(densified)

    @staticmethod
    def _bridge_longitudinal_frame(footprint):
        center_x = (
            sum(x for x, _ in footprint)
            / len(footprint)
        )
        center_y = (
            sum(y for _, y in footprint)
            / len(footprint)
        )

        covariance_xx = sum(
            (x - center_x) ** 2
            for x, _ in footprint
        )
        covariance_yy = sum(
            (y - center_y) ** 2
            for _, y in footprint
        )
        covariance_xy = sum(
            (x - center_x) * (y - center_y)
            for x, y in footprint
        )

        angle = 0.5 * math.atan2(
            2.0 * covariance_xy,
            covariance_xx - covariance_yy,
        )

        axis_x = math.cos(angle)
        axis_y = math.sin(angle)

        projections = tuple(
            (
                (x - center_x) * axis_x
                + (y - center_y) * axis_y
            )
            for x, y in footprint
        )

        minimum = min(projections)
        maximum = max(projections)
        span = maximum - minimum

        if span <= 1e-12:
            raise ValueError(
                "Bridge footprint has no longitudinal span"
            )

        return (
            center_x,
            center_y,
            axis_x,
            axis_y,
            minimum,
            span,
        )

    @staticmethod
    def _bridge_position_at(point, frame):
        (
            center_x,
            center_y,
            axis_x,
            axis_y,
            minimum,
            span,
        ) = frame

        x, y = point

        projection = (
            (x - center_x) * axis_x
            + (y - center_y) * axis_y
        )

        position = (
            projection - minimum
        ) / span

        return min(
            1.0,
            max(0.0, position),
        )

    @classmethod
    def _bridge_longitudinal_positions(
        cls,
        footprint,
    ):
        frame = cls._bridge_longitudinal_frame(
            footprint
        )

        return tuple(
            cls._bridge_position_at(
                point,
                frame,
            )
            for point in footprint
        )

    @staticmethod
    def _center_fan_triangulate(ring, reverse=False):
        if len(ring) < 3:
            return []

        center = (
            sum(point[0] for point in ring) / len(ring),
            sum(point[1] for point in ring) / len(ring),
            sum(point[2] for point in ring) / len(ring),
        )

        triangles = []

        for index in range(len(ring)):
            next_index = (index + 1) % len(ring)

            triangle = (
                center,
                ring[index],
                ring[next_index],
            )

            if reverse:
                triangle = (
                    triangle[0],
                    triangle[2],
                    triangle[1],
                )

            triangles.append(triangle)

        return triangles

    @staticmethod
    def _connect_rings(lower, upper):
        triangles = []
        count = len(lower)

        for index in range(count):
            next_index = (index + 1) % count

            a = lower[index]
            b = lower[next_index]
            c = upper[next_index]
            d = upper[index]

            triangles.append((a, b, c))
            triangles.append((a, c, d))

        return triangles

    @classmethod
    def _build_segmented_bridge_deck(
        cls,
        footprint,
        top_z,
        deck_thickness_m,
        shore_top_m,
        approach_ratio,
    ):
        section_records = (
            AtlasBridgeSegmentedDeckBuilder.split(
                footprint=footprint,
                approach_ratio=approach_ratio,
            )
        )

        profile = AtlasBridgeLongitudinalProfile(
            shore_top_m=shore_top_m,
            center_top_m=top_z,
            approach_ratio=approach_ratio,
            deck_thickness_m=deck_thickness_m,
        )

        frame = cls._bridge_longitudinal_frame(
            footprint
        )

        deck_sections = []
        all_bottom = []
        all_top = []
        all_walls = []
        all_triangles = []

        for record in section_records:
            section_footprint = tuple(
                (
                    float(x),
                    float(y),
                )
                for x, y in record["footprint"]
            )

            positions = tuple(
                cls._bridge_position_at(
                    point,
                    frame,
                )
                for point in section_footprint
            )

            bottom = tuple(
                (
                    x,
                    y,
                    profile.bottom_z_at(position),
                )
                for (x, y), position in zip(
                    section_footprint,
                    positions,
                )
            )

            top = tuple(
                (
                    x,
                    y,
                    profile.top_z_at(position),
                )
                for (x, y), position in zip(
                    section_footprint,
                    positions,
                )
            )

            walls = []
            triangles = []

            triangles.extend(
                cls._polygon_surface_triangulate(
                    bottom,
                    reverse=True,
                )
            )
            triangles.extend(
                cls._polygon_surface_triangulate(
                    top,
                )
            )

            for index in range(len(bottom)):
                next_index = (
                    index + 1
                ) % len(bottom)

                wall = (
                    bottom[index],
                    bottom[next_index],
                    top[next_index],
                    top[index],
                )

                walls.append(wall)

                triangles.append(
                    (
                        bottom[index],
                        bottom[next_index],
                        top[next_index],
                    )
                )
                triangles.append(
                    (
                        bottom[index],
                        top[next_index],
                        top[index],
                    )
                )

            section = {
                "kind": record["kind"],
                "longitudinal_bounds": (
                    record[
                        "longitudinal_bounds"
                    ]
                ),
                "footprint": section_footprint,
                "bottom": bottom,
                "top": top,
                "walls": tuple(walls),
                "triangles": tuple(triangles),
            }

            deck_sections.append(section)
            all_bottom.extend(bottom)
            all_top.extend(top)
            all_walls.extend(walls)
            all_triangles.extend(triangles)

        return {
            "deck_sections": tuple(
                deck_sections
            ),
            "bottom": tuple(all_bottom),
            "top": tuple(all_top),
            "walls": tuple(all_walls),
            "triangles": list(all_triangles),
        }

    @classmethod
    def _build_bridge_mesh(cls, geometry):
        footprint = tuple(
            (float(x), float(y))
            for x, y in geometry.footprint
        )

        if len(footprint) < 3:
            raise ValueError("Bridge footprint requires at least 3 points")

        deck_thickness_m = float(
            geometry.metadata.get(
                "bridge_deck_thickness_m",
                geometry.height_m,
            )
        )
        top_z = float(geometry.height_m)
        bottom_z = max(0.0, top_z - deck_thickness_m)

        segmented_deck_enabled = bool(
            geometry.metadata.get(
                "bridge_segmented_deck",
                False,
            )
        )

        approach_profile_enabled = bool(
            geometry.metadata.get(
                "bridge_approach_profile",
                False,
            )
        )

        full_span_convex_enabled = bool(
            geometry.metadata.get(
                "bridge_full_span_convex",
                False,
            )
        )

        if full_span_convex_enabled:
            footprint = cls._densify_ring(
                ring=footprint,
                maximum_edge_length=3.0,
            )

        if segmented_deck_enabled:
            segmented = (
                cls._build_segmented_bridge_deck(
                    footprint=footprint,
                    top_z=top_z,
                    deck_thickness_m=(
                        deck_thickness_m
                    ),
                    shore_top_m=float(
                        geometry.metadata[
                            "bridge_shore_top_m"
                        ]
                    ),
                    approach_ratio=float(
                        geometry.metadata.get(
                            "bridge_approach_ratio",
                            0.20,
                        )
                    ),
                )
            )

            bottom = segmented["bottom"]
            top = segmented["top"]
            walls = list(
                segmented["walls"]
            )
            triangles = list(
                segmented["triangles"]
            )

        elif (
            approach_profile_enabled
            or full_span_convex_enabled
        ):
            longitudinal_positions = (
                cls._bridge_longitudinal_positions(
                    footprint
                )
            )

            profile = AtlasBridgeLongitudinalProfile(
                shore_top_m=float(
                    geometry.metadata[
                        "bridge_shore_top_m"
                    ]
                ),
                center_top_m=top_z,
                approach_ratio=float(
                    geometry.metadata.get(
                        "bridge_approach_ratio",
                        0.20,
                    )
                ),
                deck_thickness_m=deck_thickness_m,
                full_span_convex=(
                    full_span_convex_enabled
                ),
            )

            bottom = tuple(
                (
                    x,
                    y,
                    profile.bottom_z_at(position),
                )
                for (x, y), position in zip(
                    footprint,
                    longitudinal_positions,
                )
            )
            top = tuple(
                (
                    x,
                    y,
                    profile.top_z_at(position),
                )
                for (x, y), position in zip(
                    footprint,
                    longitudinal_positions,
                )
            )
        else:
            bottom = tuple(
                (x, y, bottom_z)
                for x, y in footprint
            )
            top = tuple(
                (x, y, top_z)
                for x, y in footprint
            )

        if not segmented_deck_enabled:
            walls = []
            triangles = []

        if segmented_deck_enabled:
            pass
        elif (
            approach_profile_enabled
            or full_span_convex_enabled
        ):
            triangles.extend(
                cls._polygon_surface_triangulate(
                    bottom,
                    reverse=True,
                )
            )
            triangles.extend(
                cls._polygon_surface_triangulate(
                    top
                )
            )
        else:
            triangles.extend(
                cls._polygon_triangulate(
                    bottom,
                    reverse=True,
                )
            )
            triangles.extend(
                cls._polygon_triangulate(top)
            )

        if not segmented_deck_enabled:
            for index in range(len(bottom)):
                next_index = (
                    index + 1
                ) % len(bottom)

                wall = (
                    bottom[index],
                    bottom[next_index],
                    top[next_index],
                    top[index],
                )
                walls.append(wall)

                triangles.append(
                    (
                        bottom[index],
                        bottom[next_index],
                        top[next_index],
                    )
                )
                triangles.append(
                    (
                        bottom[index],
                        top[next_index],
                        top[index],
                    )
                )

        piers = []
        pier_positions = tuple(
            geometry.metadata.get("bridge_pier_positions", ())
        )

        if pier_positions:
            edge_dx = footprint[1][0] - footprint[0][0]
            edge_dy = footprint[1][1] - footprint[0][1]
            edge_length = math.hypot(edge_dx, edge_dy)

            if edge_length <= 0.0:
                raise ValueError("Bridge footprint has a zero-length axis")

            axis_x = edge_dx / edge_length
            axis_y = edge_dy / edge_length
            normal_x = -axis_y
            normal_y = axis_x

            pier_width_m = float(
                geometry.metadata.get("bridge_pier_width_m", 2.0)
            )
            pier_depth_m = float(
                geometry.metadata.get("bridge_pier_depth_m", 1.0)
            )
            pier_base_m = float(
                geometry.metadata.get("bridge_pier_base_m", 0.0)
            )
            pier_top_m = float(
                geometry.metadata.get("bridge_pier_top_m", bottom_z)
            )

            half_width = pier_width_m / 2.0
            half_depth = pier_depth_m / 2.0

            for center_x, center_y in pier_positions:
                center_x = float(center_x)
                center_y = float(center_y)

                pier_footprint = (
                    (
                        center_x - axis_x * half_depth - normal_x * half_width,
                        center_y - axis_y * half_depth - normal_y * half_width,
                    ),
                    (
                        center_x + axis_x * half_depth - normal_x * half_width,
                        center_y + axis_y * half_depth - normal_y * half_width,
                    ),
                    (
                        center_x + axis_x * half_depth + normal_x * half_width,
                        center_y + axis_y * half_depth + normal_y * half_width,
                    ),
                    (
                        center_x - axis_x * half_depth + normal_x * half_width,
                        center_y - axis_y * half_depth + normal_y * half_width,
                    ),
                )

                pier_bottom = tuple(
                    (x, y, pier_base_m)
                    for x, y in pier_footprint
                )
                pier_top = tuple(
                    (x, y, pier_top_m)
                    for x, y in pier_footprint
                )

                pier_triangles = []
                pier_triangles.extend(
                    cls._fan_triangulate(pier_bottom, reverse=True)
                )
                pier_triangles.extend(
                    cls._fan_triangulate(pier_top)
                )
                pier_triangles.extend(
                    cls._connect_rings(pier_bottom, pier_top)
                )

                piers.append(
                    {
                        "bottom": pier_bottom,
                        "top": pier_top,
                        "triangles": pier_triangles,
                    }
                )
                triangles.extend(pier_triangles)

        result = {
            "type": "bridge",
            "bottom": bottom,
            "top": top,
            "walls": walls,
            "piers": piers,
            "triangles": triangles,
            "metadata": dict(geometry.metadata),
        }

        if segmented_deck_enabled:
            result["deck_sections"] = (
                segmented["deck_sections"]
            )

        return result

    @classmethod
    def _build_tower_mesh(cls, geometry):
        footprint = tuple(
            (float(x), float(y))
            for x, y in geometry.footprint
        )

        if len(footprint) < 3:
            raise ValueError("Tower footprint requires at least 3 points")

        if geometry.profile == "observation":
            return cls._build_observation_tower_mesh(geometry)

        if geometry.profile == "clock":
            return cls._build_clock_tower_mesh(geometry)

        total_height = float(geometry.height_m)
        roof_shape = getattr(
            geometry,
            "roof_shape",
            None,
        )
        roof_height = float(
            getattr(
                geometry,
                "roof_height_m",
                0.0,
            )
        )

        use_pyramidal_roof = (
            roof_shape == "pyramidal"
            and roof_height > 0.0
            and roof_height < total_height
        )

        body_top_z = (
            total_height - roof_height
            if use_pyramidal_roof
            else total_height
        )

        bottom = tuple(
            (x, y, 0.0)
            for x, y in footprint
        )
        body_top = tuple(
            (x, y, body_top_z)
            for x, y in footprint
        )

        walls = []
        triangles = []

        triangles.extend(
            cls._fan_triangulate(bottom, reverse=True)
        )

        for index in range(len(bottom)):
            next_index = (index + 1) % len(bottom)

            wall = (
                bottom[index],
                bottom[next_index],
                body_top[next_index],
                body_top[index],
            )
            walls.append(wall)

            triangles.append(
                (
                    bottom[index],
                    bottom[next_index],
                    body_top[next_index],
                )
            )
            triangles.append(
                (
                    bottom[index],
                    body_top[next_index],
                    body_top[index],
                )
            )

        roof_triangles = []

        if use_pyramidal_roof:
            center_x = sum(
                x
                for x, _ in footprint
            ) / len(footprint)
            center_y = sum(
                y
                for _, y in footprint
            ) / len(footprint)

            apex = (
                center_x,
                center_y,
                total_height,
            )

            for index in range(len(body_top)):
                next_index = (
                    index + 1
                ) % len(body_top)

                roof_triangles.append(
                    (
                        body_top[index],
                        body_top[next_index],
                        apex,
                    )
                )

            triangles.extend(roof_triangles)
            top = (apex,)
        else:
            triangles.extend(
                cls._fan_triangulate(body_top)
            )
            top = body_top

        return {
            "type": "tower",
            "profile": geometry.profile,
            "roof_shape": (
                "pyramidal"
                if use_pyramidal_roof
                else None
            ),
            "bottom": bottom,
            "top": top,
            "body_top": body_top,
            "body_top_z": body_top_z,
            "roof_top_z": total_height,
            "roof_triangles": roof_triangles,
            "walls": walls,
            "triangles": triangles,
        }

    @classmethod
    def _build_clock_tower_mesh(cls, geometry):
        footprint = tuple(
            (float(x), float(y))
            for x, y in geometry.footprint
        )

        if len(footprint) < 3:
            raise ValueError(
                "Clock tower footprint requires at least 3 points"
            )

        total_height = float(geometry.height_m)
        roof_shape = getattr(
            geometry,
            "roof_shape",
            None,
        )
        roof_height = float(
            getattr(
                geometry,
                "roof_height_m",
                0.0,
            )
        )

        use_pyramidal_roof = (
            roof_shape == "pyramidal"
            and roof_height > 0.0
            and roof_height < total_height
        )

        body_top_z = (
            total_height - roof_height
            if use_pyramidal_roof
            else total_height
        )

        center_x = (
            sum(x for x, _ in footprint)
            / len(footprint)
        )
        center_y = (
            sum(y for _, y in footprint)
            / len(footprint)
        )

        def scaled_ring(
            *,
            scale,
            z_level,
        ):
            return tuple(
                (
                    center_x
                    + (x - center_x) * scale,
                    center_y
                    + (y - center_y) * scale,
                    float(z_level),
                )
                for x, y in footprint
            )

        rings = (
            scaled_ring(
                scale=1.00,
                z_level=0.0,
            ),
            scaled_ring(
                scale=1.00,
                z_level=body_top_z * 0.70,
            ),
            scaled_ring(
                scale=1.10,
                z_level=body_top_z * 0.72,
            ),
            scaled_ring(
                scale=1.10,
                z_level=body_top_z * 0.86,
            ),
            scaled_ring(
                scale=0.72,
                z_level=body_top_z,
            ),
        )

        triangles = []
        walls = []

        triangles.extend(
            cls._fan_triangulate(
                rings[0],
                reverse=True,
            )
        )

        for lower_ring, upper_ring in zip(
            rings,
            rings[1:],
        ):
            triangles.extend(
                cls._connect_rings(
                    lower_ring,
                    upper_ring,
                )
            )

            point_count = len(lower_ring)

            for index in range(point_count):
                next_index = (
                    index + 1
                ) % point_count

                walls.append(
                    (
                        lower_ring[index],
                        lower_ring[next_index],
                        upper_ring[next_index],
                        upper_ring[index],
                    )
                )

        roof_base = rings[-1]
        roof_triangles = []

        if use_pyramidal_roof:
            apex = (
                center_x,
                center_y,
                total_height,
            )

            for index in range(len(roof_base)):
                next_index = (
                    index + 1
                ) % len(roof_base)

                roof_triangles.append(
                    (
                        roof_base[index],
                        roof_base[next_index],
                        apex,
                    )
                )

            triangles.extend(roof_triangles)
            top = (apex,)
        else:
            triangles.extend(
                cls._fan_triangulate(
                    roof_base
                )
            )
            top = roof_base

        min_x = min(x for x, _ in footprint)
        max_x = max(x for x, _ in footprint)
        min_y = min(y for _, y in footprint)
        max_y = max(y for _, y in footprint)

        footprint_width = max_x - min_x
        footprint_depth = max_y - min_y
        short_span = min(
            footprint_width,
            footprint_depth,
        )

        # Merkez konumları sabit tutulur.
        # Fiziksel yarıçap, merkez ile ana kule arasındaki gerçek
        # geometrik mesafeye göre büyütülür.
        placement_radius = max(
            short_span * 0.22,
            0.20,
        )

        turret_body_top_z = total_height * 0.48
        turret_cap_top_z = total_height * 0.62
        turret_segments = 12

        # Rathaus Köpenick:
        # Yan kuleler ana kulenin iki yanında bulunur.
        # Ana kule footprint'ine gömülmez; yalnızca teğet temas eder.
        # max_y yönü Rathaus dış cephesidir.
        # Üç kule merkezinin aynı cephe doğrusu üzerinde
        # bulunması gerekir. Ana kuleyi içeride bırakmamak için
        # yan kulelerin Y merkezi ana kule merkeziyle aynıdır.
        exterior_y = center_y

        turret_specs = (
            {
                "side": "left",
                "center": (
                    min_x - placement_radius,
                    exterior_y,
                ),
            },
            {
                "side": "right",
                "center": (
                    max_x + placement_radius,
                    exterior_y,
                ),
            },
        )

        from shapely.geometry import Point, Polygon

        main_tower_polygon = Polygon(footprint)

        if not main_tower_polygon.is_valid:
            main_tower_polygon = (
                main_tower_polygon.buffer(0)
            )

        # 12-gen gövdenin herhangi bir açıdaki radyal kaybını da
        # karşılayarak 0.08 mm fiziksel bindirme oluşturur.
        polygon_support_factor = math.cos(
            math.pi / turret_segments
        )
        contact_overlap_mm = 0.08

        fixed_centers = tuple(
            turret_spec["center"]
            for turret_spec in turret_specs
        )

        required_radii = tuple(
            (
                Point(center).distance(
                    main_tower_polygon
                )
                + contact_overlap_mm
            )
            / polygon_support_factor
            for center in fixed_centers
        )

        turret_radius = max(
            placement_radius * 1.18,
            *required_radii,
        )

        side_turrets = []

        for turret_spec in turret_specs:
            turret_center_x, turret_center_y = (
                turret_spec["center"]
            )

            body_bottom = tuple(
                (
                    turret_center_x
                    + turret_radius
                    * math.cos(
                        2.0
                        * math.pi
                        * index
                        / turret_segments
                    ),
                    turret_center_y
                    + turret_radius
                    * math.sin(
                        2.0
                        * math.pi
                        * index
                        / turret_segments
                    ),
                    0.0,
                )
                for index in range(turret_segments)
            )

            body_top = tuple(
                (
                    x,
                    y,
                    turret_body_top_z,
                )
                for x, y, _ in body_bottom
            )

            cap_apex = (
                turret_center_x,
                turret_center_y,
                turret_cap_top_z,
            )

            body_triangles = [
                *cls._fan_triangulate(
                    body_bottom,
                    reverse=True,
                ),
                *cls._connect_rings(
                    body_bottom,
                    body_top,
                ),
            ]

            cap_triangles = []

            for index in range(turret_segments):
                next_index = (
                    index + 1
                ) % turret_segments

                cap_triangles.append(
                    (
                        body_top[index],
                        body_top[next_index],
                        cap_apex,
                    )
                )

            turret_triangles = [
                *body_triangles,
                *cap_triangles,
            ]

            side_turrets.append(
                {
                    "type": "clock_tower_side_turret",
                    "side": turret_spec["side"],
                    "center": turret_spec["center"],
                    "radius": turret_radius,
                    "placement_radius": placement_radius,
                    "contact_overlap_mm": contact_overlap_mm,
                    "body_rings": (
                        body_bottom,
                        body_top,
                    ),
                    "cap_apex": cap_apex,
                    "cap_triangles": cap_triangles,
                    "triangles": turret_triangles,
                }
            )

            triangles.extend(
                turret_triangles
            )

        return {
            "type": "tower",
            "profile": "clock",
            "roof_shape": (
                "pyramidal"
                if use_pyramidal_roof
                else None
            ),
            "bottom": rings[0],
            "top": top,
            "rings": rings,
            "body_top": roof_base,
            "body_top_z": body_top_z,
            "roof_top_z": total_height,
            "roof_triangles": roof_triangles,
            "walls": walls,
            "triangles": triangles,
            "clock_tower_stage_count": len(rings) - 1,
            "clock_tower_side_turrets": side_turrets,
            "clock_tower_side_turret_count": len(
                side_turrets
            ),
        }

    @classmethod
    def _build_observation_tower_mesh(cls, geometry):
        footprint = tuple(
            (float(x), float(y))
            for x, y in geometry.footprint
        )

        center_x = sum(x for x, _ in footprint) / len(footprint)
        center_y = sum(y for _, y in footprint) / len(footprint)

        base_radius = max(
            math.hypot(x - center_x, y - center_y)
            for x, y in footprint
        )

        levels = (
            (0.00, 1.00, "prismatic"),
            (0.58, 1.00, "prismatic"),
            (0.62, 1.20, "radial"),
            (0.66, 1.45, "radial"),
            (0.70, 1.45, "radial"),
            (0.73, 1.62, "radial"),
            (0.77, 1.62, "radial"),
            (0.80, 2.05, "radial"),
            (0.88, 2.05, "radial"),
            (0.92, 1.88, "radial"),
            (0.97, 1.35, "radial"),
            (1.00, 0.55, "radial"),
        )

        rings = []
        segments = 16

        min_x = min(x for x, _ in footprint)
        max_x = max(x for x, _ in footprint)
        min_y = min(y for _, y in footprint)
        max_y = max(y for _, y in footprint)

        half_width = (max_x - min_x) / 2.0
        half_height = (max_y - min_y) / 2.0

        prismatic_xy = []

        for index in range(segments):
            angle = 2.0 * math.pi * index / segments
            direction_x = math.cos(angle)
            direction_y = math.sin(angle)

            scale_candidates = []

            if abs(direction_x) > 1e-12:
                scale_candidates.append(
                    half_width / abs(direction_x)
                )

            if abs(direction_y) > 1e-12:
                scale_candidates.append(
                    half_height / abs(direction_y)
                )

            distance = min(scale_candidates)

            prismatic_xy.append(
                (
                    center_x + direction_x * distance,
                    center_y + direction_y * distance,
                )
            )

        body_scale = 0.78

        prismatic_xy = tuple(
            (
                center_x + (x - center_x) * body_scale,
                center_y + (y - center_y) * body_scale,
            )
            for x, y in prismatic_xy
        )

        for height_ratio, radius_ratio, ring_kind in levels:
            z = float(geometry.height_m) * height_ratio

            if ring_kind == "prismatic":
                ring = tuple(
                    (x, y, z)
                    for x, y in prismatic_xy
                )
            else:
                radius = base_radius * radius_ratio
                ring = tuple(
                    (
                        center_x + radius * math.cos(
                            2.0 * math.pi * index / segments
                        ),
                        center_y + radius * math.sin(
                            2.0 * math.pi * index / segments
                        ),
                        z,
                    )
                    for index in range(segments)
                )

            rings.append(ring)

        triangles = []
        walls = []

        triangles.extend(
            cls._center_fan_triangulate(rings[0], reverse=True)
        )

        for lower, upper in zip(rings, rings[1:]):
            triangles.extend(
                cls._connect_rings(lower, upper)
            )

            for index in range(segments):
                next_index = (index + 1) % segments
                walls.append(
                    (
                        lower[index],
                        lower[next_index],
                        upper[next_index],
                        upper[index],
                    )
                )

        triangles.extend(
            cls._center_fan_triangulate(rings[-1])
        )

        return {
            "type": "tower",
            "profile": "observation",
            "bottom": rings[0],
            "top": rings[-1],
            "rings": tuple(rings),
            "walls": walls,
            "triangles": triangles,
        }

    @classmethod
    def _build_lighthouse_mesh(cls, geometry):
        footprint = tuple(
            (float(x), float(y))
            for x, y in geometry.footprint
        )

        if len(footprint) < 3:
            raise ValueError(
                "Lighthouse footprint requires at least 3 points"
            )

        center_x = sum(x for x, _ in footprint) / len(footprint)
        center_y = sum(y for _, y in footprint) / len(footprint)

        base_radius = max(
            math.hypot(x - center_x, y - center_y)
            for x, y in footprint
        )

        levels = (
            (0.00, 1.00),
            (0.62, 0.72),
            (0.72, 1.00),
            (0.80, 1.00),
            (0.88, 0.72),
            (0.95, 0.72),
            (1.00, 0.18),
        )

        segments = 16
        rings = []

        for height_ratio, radius_ratio in levels:
            z = float(geometry.height_m) * height_ratio
            radius = base_radius * radius_ratio

            ring = tuple(
                (
                    center_x + radius * math.cos(
                        2.0 * math.pi * index / segments
                    ),
                    center_y + radius * math.sin(
                        2.0 * math.pi * index / segments
                    ),
                    z,
                )
                for index in range(segments)
            )
            rings.append(ring)

        triangles = []
        triangles.extend(
            cls._fan_triangulate(rings[0], reverse=True)
        )

        for lower, upper in zip(rings, rings[1:]):
            triangles.extend(
                cls._connect_rings(lower, upper)
            )

        triangles.extend(
            cls._fan_triangulate(rings[-1])
        )

        return {
            "type": "lighthouse",
            "profile": "multistage",
            "bottom": rings[0],
            "top": rings[-1],
            "rings": tuple(rings),
            "walls": [],
            "triangles": triangles,
        }
