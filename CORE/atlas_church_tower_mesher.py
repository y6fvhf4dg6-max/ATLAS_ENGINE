from __future__ import annotations

import math

from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points

from CORE.atlas_church_footprint_resolver import (
    AtlasChurchFootprintFrame,
)
from CORE.atlas_church_tower_profile_system import (
    AtlasChurchTowerProfileCollection,
)


class AtlasChurchTowerMesher:
    @staticmethod
    def _world(
        *,
        frame,
        longitudinal,
        lateral,
        z,
    ):
        x, y = frame.to_world(
            longitudinal=longitudinal,
            lateral=lateral,
        )

        return (
            float(x),
            float(y),
            float(z),
        )

    @classmethod
    def _polygon_ring(
        cls,
        *,
        frame,
        center_longitudinal,
        center_lateral,
        longitudinal_span,
        lateral_span,
        z,
        sides,
    ):
        radius_longitudinal = (
            float(longitudinal_span) / 2.0
        )
        radius_lateral = (
            float(lateral_span) / 2.0
        )

        return tuple(
            cls._world(
                frame=frame,
                longitudinal=(
                    center_longitudinal
                    + math.cos(
                        2.0 * math.pi * index / sides
                    )
                    * radius_longitudinal
                ),
                lateral=(
                    center_lateral
                    + math.sin(
                        2.0 * math.pi * index / sides
                    )
                    * radius_lateral
                ),
                z=z,
            )
            for index in range(sides)
        )

    @classmethod
    def _polygon_body(
        cls,
        *,
        frame,
        center_longitudinal,
        center_lateral,
        longitudinal_span,
        lateral_span,
        min_z,
        max_z,
        sides,
    ):
        bottom_ring = cls._polygon_ring(
            frame=frame,
            center_longitudinal=center_longitudinal,
            center_lateral=center_lateral,
            longitudinal_span=longitudinal_span,
            lateral_span=lateral_span,
            z=min_z,
            sides=sides,
        )
        top_ring = cls._polygon_ring(
            frame=frame,
            center_longitudinal=center_longitudinal,
            center_lateral=center_lateral,
            longitudinal_span=longitudinal_span,
            lateral_span=lateral_span,
            z=max_z,
            sides=sides,
        )

        triangles = []

        for index in range(sides):
            next_index = (
                index + 1
            ) % sides

            bottom_a = bottom_ring[index]
            bottom_b = bottom_ring[next_index]
            top_a = top_ring[index]
            top_b = top_ring[next_index]

            triangles.extend(
                (
                    (
                        bottom_a,
                        bottom_b,
                        top_b,
                    ),
                    (
                        bottom_a,
                        top_b,
                        top_a,
                    ),
                )
            )

        for index in range(1, sides - 1):
            triangles.append(
                (
                    bottom_ring[0],
                    bottom_ring[index + 1],
                    bottom_ring[index],
                )
            )

        return {
            "body_bottom_ring": bottom_ring,
            "body_top_ring": top_ring,
            "body_triangles": triangles,
        }

    @classmethod
    def _box_body(
        cls,
        *,
        frame,
        center_longitudinal,
        center_lateral,
        longitudinal_span,
        lateral_span,
        min_z,
        max_z,
    ):
        half_longitudinal = (
            longitudinal_span / 2.0
        )
        half_lateral = (
            lateral_span / 2.0
        )

        bottom_ring = (
            cls._world(
                frame=frame,
                longitudinal=(
                    center_longitudinal
                    - half_longitudinal
                ),
                lateral=(
                    center_lateral
                    - half_lateral
                ),
                z=min_z,
            ),
            cls._world(
                frame=frame,
                longitudinal=(
                    center_longitudinal
                    + half_longitudinal
                ),
                lateral=(
                    center_lateral
                    - half_lateral
                ),
                z=min_z,
            ),
            cls._world(
                frame=frame,
                longitudinal=(
                    center_longitudinal
                    + half_longitudinal
                ),
                lateral=(
                    center_lateral
                    + half_lateral
                ),
                z=min_z,
            ),
            cls._world(
                frame=frame,
                longitudinal=(
                    center_longitudinal
                    - half_longitudinal
                ),
                lateral=(
                    center_lateral
                    + half_lateral
                ),
                z=min_z,
            ),
        )

        top_ring = tuple(
            (
                x,
                y,
                float(max_z),
            )
            for x, y, _ in bottom_ring
        )

        triangles = []

        for index in range(4):
            next_index = (
                index + 1
            ) % 4

            triangles.extend(
                (
                    (
                        bottom_ring[index],
                        bottom_ring[next_index],
                        top_ring[next_index],
                    ),
                    (
                        bottom_ring[index],
                        top_ring[next_index],
                        top_ring[index],
                    ),
                )
            )

        triangles.extend(
            (
                (
                    bottom_ring[0],
                    bottom_ring[2],
                    bottom_ring[1],
                ),
                (
                    bottom_ring[0],
                    bottom_ring[3],
                    bottom_ring[2],
                ),
            )
        )

        return {
            "body_bottom_ring": bottom_ring,
            "body_top_ring": top_ring,
            "body_triangles": triangles,
        }

    @classmethod
    def _scaled_polygon_ring(
        cls,
        *,
        frame,
        center_longitudinal,
        center_lateral,
        source_ring,
        scale,
        z,
    ):
        center_x, center_y = frame.to_world(
            longitudinal=center_longitudinal,
            lateral=center_lateral,
        )

        return tuple(
            (
                float(center_x)
                + (
                    float(point[0])
                    - float(center_x)
                )
                * float(scale),
                float(center_y)
                + (
                    float(point[1])
                    - float(center_y)
                )
                * float(scale),
                float(z),
            )
            for point in source_ring
        )

    @staticmethod
    def _connect_polygon_rings(
        lower_ring,
        upper_ring,
    ):
        lower_ring = tuple(lower_ring)
        upper_ring = tuple(upper_ring)

        if len(lower_ring) != len(upper_ring):
            raise ValueError(
                "Transition rings must have matching point counts"
            )

        if len(lower_ring) < 3:
            raise ValueError(
                "Transition rings require at least three points"
            )

        triangles = []

        for index in range(len(lower_ring)):
            next_index = (
                index + 1
            ) % len(lower_ring)

            triangles.extend(
                (
                    (
                        lower_ring[index],
                        lower_ring[next_index],
                        upper_ring[next_index],
                    ),
                    (
                        lower_ring[index],
                        upper_ring[next_index],
                        upper_ring[index],
                    ),
                )
            )

        return triangles

    @classmethod
    def _polygon_spire(
        cls,
        *,
        frame,
        center_longitudinal,
        center_lateral,
        top_z,
        base_ring,
    ):
        base_ring = tuple(base_ring)

        if len(base_ring) < 3:
            raise ValueError(
                "Church tower spire requires at least three base points"
            )

        apex = cls._world(
            frame=frame,
            longitudinal=center_longitudinal,
            lateral=center_lateral,
            z=top_z,
        )

        triangles = []

        for index in range(len(base_ring)):
            triangles.append(
                (
                    base_ring[index],
                    base_ring[
                        (index + 1) % len(base_ring)
                    ],
                    apex,
                )
            )

        return {
            "roof_base_ring": base_ring,
            "roof_apex": apex,
            "roof_triangles": triangles,
        }

    @classmethod
    def _resolve_footprint_safe_center(
        cls,
        *,
        frame,
        desired_longitudinal,
        desired_lateral,
        longitudinal_span,
        lateral_span,
    ):
        footprint = Polygon(frame.footprint)

        desired_x, desired_y = frame.to_world(
            longitudinal=desired_longitudinal,
            lateral=desired_lateral,
        )
        desired_point = Point(
            desired_x,
            desired_y,
        )

        half_longitudinal = (
            float(longitudinal_span) / 2.0
        )
        half_lateral = (
            float(lateral_span) / 2.0
        )

        clearance = math.hypot(
            half_longitudinal,
            half_lateral,
        ) * 0.72

        safe_area = footprint.buffer(
            -clearance
        )

        if safe_area.is_empty:
            safe_area = footprint.buffer(
                -clearance * 0.40
            )

        if safe_area.is_empty:
            safe_area = footprint

        if safe_area.covers(desired_point):
            resolved_point = desired_point
        else:
            resolved_point = nearest_points(
                safe_area,
                desired_point,
            )[0]

        return frame.to_local(
            (
                resolved_point.x,
                resolved_point.y,
            )
        )

    @classmethod
    def build(
        cls,
        *,
        frame,
        profile,
        building_height,
    ):
        if not isinstance(
            frame,
            AtlasChurchFootprintFrame,
        ):
            raise TypeError(
                "frame must be AtlasChurchFootprintFrame"
            )

        if not isinstance(
            profile,
            AtlasChurchTowerProfileCollection,
        ):
            raise TypeError(
                "profile must be AtlasChurchTowerProfileCollection"
            )

        building_height = float(
            building_height
        )

        if building_height <= 0.0:
            raise ValueError(
                "building_height must be greater than zero"
            )

        towers = []

        resolved_outer_center = None

        for candidate_profile in profile.towers:
            if (
                candidate_profile.tower_type
                != "outer_polygon_tower"
            ):
                continue

            candidate_longitudinal_span = (
                frame.longitudinal_span
                * candidate_profile.longitudinal_ratio
            )
            candidate_lateral_span = (
                frame.lateral_span
                * candidate_profile.lateral_ratio
            )

            resolved_outer_center = (
                cls._resolve_footprint_safe_center(
                    frame=frame,
                    desired_longitudinal=(
                        frame.longitudinal_span
                        * candidate_profile
                        .center_longitudinal_ratio
                    ),
                    desired_lateral=(
                        frame.lateral_span
                        * candidate_profile
                        .center_lateral_ratio
                    ),
                    longitudinal_span=(
                        candidate_longitudinal_span
                    ),
                    lateral_span=(
                        candidate_lateral_span
                    ),
                )
            )
            break

        for tower_profile in profile.towers:
            center_longitudinal = (
                frame.longitudinal_span
                * tower_profile
                .center_longitudinal_ratio
            )
            center_lateral = (
                frame.lateral_span
                * tower_profile
                .center_lateral_ratio
            )

            if (
                tower_profile.tower_type
                == "crossing_tower"
                and resolved_outer_center is not None
            ):
                (
                    center_longitudinal,
                    center_lateral,
                ) = resolved_outer_center

            longitudinal_span = (
                frame.longitudinal_span
                * tower_profile.longitudinal_ratio
            )
            lateral_span = (
                frame.lateral_span
                * tower_profile.lateral_ratio
            )

            if (
                tower_profile.tower_type
                == "outer_polygon_tower"
            ):
                (
                    center_longitudinal,
                    center_lateral,
                ) = cls._resolve_footprint_safe_center(
                    frame=frame,
                    desired_longitudinal=(
                        center_longitudinal
                    ),
                    desired_lateral=(
                        center_lateral
                    ),
                    longitudinal_span=(
                        longitudinal_span
                    ),
                    lateral_span=lateral_span,
                )

            body_top_z = (
                building_height
                * tower_profile.body_top_ratio
            )
            roof_top_z = (
                building_height
                * tower_profile.roof_top_ratio
            )

            if tower_profile.body_shape == "polygon":
                body = cls._polygon_body(
                    frame=frame,
                    center_longitudinal=center_longitudinal,
                    center_lateral=center_lateral,
                    longitudinal_span=longitudinal_span,
                    lateral_span=lateral_span,
                    min_z=0.0,
                    max_z=body_top_z,
                    sides=tower_profile.polygon_sides,
                )
            elif tower_profile.body_shape == "box":
                body = cls._box_body(
                    frame=frame,
                    center_longitudinal=center_longitudinal,
                    center_lateral=center_lateral,
                    longitudinal_span=longitudinal_span,
                    lateral_span=lateral_span,
                    min_z=0.0,
                    max_z=body_top_z,
                )
            else:
                raise ValueError(
                    "Unsupported church tower body shape: "
                    f"{tower_profile.body_shape}"
                )

            roof_transition_type = None
            roof_transition_lower_ring = None
            roof_transition_upper_ring = None
            roof_transition_upper_z = None
            roof_transition_triangles = []
            roof_height_basis = "profile_ratio"

            roof_base_ring = body["body_top_ring"]

            if (
                tower_profile.tower_type
                == "crossing_tower"
            ):
                roof_transition_type = (
                    "two_stage_octagonal_taper"
                )
                roof_transition_lower_ring = tuple(
                    body["body_top_ring"]
                )

                roof_transition_upper_z = (
                    body_top_z
                    + (
                        roof_top_z
                        - body_top_z
                    )
                    * 0.30
                )

                roof_transition_upper_ring = (
                    cls._scaled_polygon_ring(
                        frame=frame,
                        center_longitudinal=(
                            center_longitudinal
                        ),
                        center_lateral=(
                            center_lateral
                        ),
                        source_ring=(
                            roof_transition_lower_ring
                        ),
                        scale=0.72,
                        z=roof_transition_upper_z,
                    )
                )

                roof_transition_triangles = (
                    cls._connect_polygon_rings(
                        roof_transition_lower_ring,
                        roof_transition_upper_ring,
                    )
                )

                roof_base_ring = (
                    roof_transition_upper_ring
                )

                transition_x_values = [
                    point[0]
                    for point in roof_transition_upper_ring
                ]
                transition_y_values = [
                    point[1]
                    for point in roof_transition_upper_ring
                ]

                transition_span = max(
                    max(transition_x_values)
                    - min(transition_x_values),
                    max(transition_y_values)
                    - min(transition_y_values),
                )

                roof_pitch_degrees = 30.0
                roof_height = (
                    transition_span
                    / 2.0
                    * math.tan(
                        math.radians(
                            roof_pitch_degrees
                        )
                    )
                )

                roof_top_z = (
                    roof_transition_upper_z
                    + roof_height
                )
                roof_height_basis = (
                    "upper_transition_ring_span_30_degree_pitch"
                )

            roof = cls._polygon_spire(
                frame=frame,
                center_longitudinal=center_longitudinal,
                center_lateral=center_lateral,
                top_z=roof_top_z,
                base_ring=roof_base_ring,
            )

            triangles = [
                *body["body_triangles"],
                *roof_transition_triangles,
                *roof["roof_triangles"],
            ]

            towers.append(
                {
                    "tower_type": tower_profile.tower_type,
                    "body_shape": tower_profile.body_shape,
                    "roof_shape": tower_profile.roof_shape,
                    "center_longitudinal": center_longitudinal,
                    "center_lateral": center_lateral,
                    "longitudinal_span": longitudinal_span,
                    "lateral_span": lateral_span,
                    "body_top_z": body_top_z,
                    "roof_top_z": roof_top_z,
                    "body_bottom_ring": (
                        body["body_bottom_ring"]
                    ),
                    "body_top_ring": (
                        body["body_top_ring"]
                    ),
                    "roof_transition_type": (
                        roof_transition_type
                    ),
                    "roof_transition_lower_ring": (
                        roof_transition_lower_ring
                    ),
                    "roof_transition_upper_ring": (
                        roof_transition_upper_ring
                    ),
                    "roof_transition_upper_z": (
                        roof_transition_upper_z
                    ),
                    "roof_transition_triangles": (
                        roof_transition_triangles
                    ),
                    "roof_height_basis": (
                        roof_height_basis
                    ),
                    "roof_pitch_degrees": (
                        30.0
                        if tower_profile.tower_type
                        == "crossing_tower"
                        else None
                    ),
                    "roof_base_ring": (
                        roof["roof_base_ring"]
                    ),
                    "roof_apex": roof["roof_apex"],
                    "triangles": triangles,
                }
            )

        return {
            "type": "church_tower_system",
            "towers": towers,
            "triangles": [
                triangle
                for tower in towers
                for triangle in tower["triangles"]
            ],
        }
