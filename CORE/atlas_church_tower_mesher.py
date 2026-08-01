from __future__ import annotations

import math

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

            longitudinal_span = (
                frame.longitudinal_span
                * tower_profile.longitudinal_ratio
            )
            lateral_span = (
                frame.lateral_span
                * tower_profile.lateral_ratio
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

            roof = cls._polygon_spire(
                frame=frame,
                center_longitudinal=center_longitudinal,
                center_lateral=center_lateral,
                top_z=roof_top_z,
                base_ring=body["body_top_ring"],
            )

            triangles = [
                *body["body_triangles"],
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
