from __future__ import annotations

import math

from CORE.atlas_church_footprint_resolver import (
    AtlasChurchFootprintFrame,
)
from CORE.atlas_church_roof_profile_system import (
    AtlasChurchRoofProfile,
)


class AtlasChurchRoofMesher:
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
    def _gable_section(
        cls,
        *,
        frame,
        section,
        center_longitudinal,
        center_lateral,
        longitudinal_span,
        lateral_span,
    ):
        half_longitudinal = (
            float(longitudinal_span) / 2.0
        )
        half_lateral = (
            float(lateral_span) / 2.0
        )

        eave_z = float(section.eave_z)
        ridge_z = float(section.ridge_z)

        if section.orientation == "longitudinal":
            a = cls._world(
                frame=frame,
                longitudinal=(
                    center_longitudinal
                    - half_longitudinal
                ),
                lateral=(
                    center_lateral
                    - half_lateral
                ),
                z=eave_z,
            )
            b = cls._world(
                frame=frame,
                longitudinal=(
                    center_longitudinal
                    + half_longitudinal
                ),
                lateral=(
                    center_lateral
                    - half_lateral
                ),
                z=eave_z,
            )
            c = cls._world(
                frame=frame,
                longitudinal=(
                    center_longitudinal
                    + half_longitudinal
                ),
                lateral=(
                    center_lateral
                    + half_lateral
                ),
                z=eave_z,
            )
            d = cls._world(
                frame=frame,
                longitudinal=(
                    center_longitudinal
                    - half_longitudinal
                ),
                lateral=(
                    center_lateral
                    + half_lateral
                ),
                z=eave_z,
            )

            ridge_start = cls._world(
                frame=frame,
                longitudinal=(
                    center_longitudinal
                    - half_longitudinal
                ),
                lateral=center_lateral,
                z=ridge_z,
            )
            ridge_end = cls._world(
                frame=frame,
                longitudinal=(
                    center_longitudinal
                    + half_longitudinal
                ),
                lateral=center_lateral,
                z=ridge_z,
            )
        else:
            a = cls._world(
                frame=frame,
                longitudinal=(
                    center_longitudinal
                    - half_longitudinal
                ),
                lateral=(
                    center_lateral
                    - half_lateral
                ),
                z=eave_z,
            )
            b = cls._world(
                frame=frame,
                longitudinal=(
                    center_longitudinal
                    - half_longitudinal
                ),
                lateral=(
                    center_lateral
                    + half_lateral
                ),
                z=eave_z,
            )
            c = cls._world(
                frame=frame,
                longitudinal=(
                    center_longitudinal
                    + half_longitudinal
                ),
                lateral=(
                    center_lateral
                    + half_lateral
                ),
                z=eave_z,
            )
            d = cls._world(
                frame=frame,
                longitudinal=(
                    center_longitudinal
                    + half_longitudinal
                ),
                lateral=(
                    center_lateral
                    - half_lateral
                ),
                z=eave_z,
            )

            ridge_start = cls._world(
                frame=frame,
                longitudinal=center_longitudinal,
                lateral=(
                    center_lateral
                    - half_lateral
                ),
                z=ridge_z,
            )
            ridge_end = cls._world(
                frame=frame,
                longitudinal=center_longitudinal,
                lateral=(
                    center_lateral
                    + half_lateral
                ),
                z=ridge_z,
            )

        triangles = [
            (
                a,
                b,
                ridge_end,
            ),
            (
                a,
                ridge_end,
                ridge_start,
            ),
            (
                d,
                ridge_start,
                ridge_end,
            ),
            (
                d,
                ridge_end,
                c,
            ),
            (
                a,
                ridge_start,
                d,
            ),
            (
                b,
                c,
                ridge_end,
            ),
            (
                a,
                d,
                c,
            ),
            (
                a,
                c,
                b,
            ),
        ]

        return {
            "section_type": section.section_type,
            "roof_shape": section.roof_shape,
            "orientation": section.orientation,
            "center_longitudinal": float(
                center_longitudinal
            ),
            "center_lateral": float(
                center_lateral
            ),
            "eave_z": eave_z,
            "ridge_z": ridge_z,
            "ridge": (
                ridge_start,
                ridge_end,
            ),
            "triangles": triangles,
        }

    @classmethod
    def _polygon_pyramid_section(
        cls,
        *,
        frame,
        section,
        center_longitudinal,
        center_lateral,
        longitudinal_span,
        lateral_span,
    ):
        sides = int(section.polygon_sides)

        if sides < 3:
            raise ValueError(
                "polygon roof requires at least three sides"
            )

        radius_longitudinal = (
            float(longitudinal_span) / 2.0
        )
        radius_lateral = (
            float(lateral_span) / 2.0
        )

        eave_z = float(section.eave_z)
        ridge_z = float(section.ridge_z)

        base_ring = tuple(
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
                z=eave_z,
            )
            for index in range(sides)
        )

        apex = cls._world(
            frame=frame,
            longitudinal=center_longitudinal,
            lateral=center_lateral,
            z=ridge_z,
        )

        triangles = []

        for index in range(sides):
            first = base_ring[index]
            second = base_ring[
                (index + 1) % sides
            ]

            triangles.append(
                (
                    first,
                    second,
                    apex,
                )
            )

        for index in range(1, sides - 1):
            triangles.append(
                (
                    base_ring[0],
                    base_ring[index + 1],
                    base_ring[index],
                )
            )

        return {
            "section_type": section.section_type,
            "roof_shape": section.roof_shape,
            "orientation": section.orientation,
            "center_longitudinal": float(
                center_longitudinal
            ),
            "center_lateral": float(
                center_lateral
            ),
            "eave_z": eave_z,
            "ridge_z": ridge_z,
            "base_ring": base_ring,
            "apex": apex,
            "triangles": triangles,
        }

    @classmethod
    def build(
        cls,
        *,
        frame,
        profile,
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
            AtlasChurchRoofProfile,
        ):
            raise TypeError(
                "profile must be AtlasChurchRoofProfile"
            )

        longitudinal_span = (
            frame.longitudinal_span
        )
        lateral_span = (
            frame.lateral_span
        )

        sections = []

        for section in profile.sections:
            section_longitudinal_span = (
                longitudinal_span
                * section.longitudinal_ratio
            )
            section_lateral_span = (
                lateral_span
                * section.lateral_ratio
            )

            center_longitudinal = 0.0
            center_lateral = 0.0

            if section.section_type == "outer_aisle_left":
                center_lateral = (
                    -lateral_span * 0.34
                )
            elif section.section_type == "outer_aisle_right":
                center_lateral = (
                    lateral_span * 0.34
                )
            elif section.section_type == "apse":
                center_longitudinal = (
                    longitudinal_span * 0.42
                )

            if section.roof_shape == "gable":
                mesh = cls._gable_section(
                    frame=frame,
                    section=section,
                    center_longitudinal=(
                        center_longitudinal
                    ),
                    center_lateral=(
                        center_lateral
                    ),
                    longitudinal_span=(
                        section_longitudinal_span
                    ),
                    lateral_span=(
                        section_lateral_span
                    ),
                )
            elif (
                section.roof_shape
                == "polygon_pyramid"
            ):
                mesh = (
                    cls._polygon_pyramid_section(
                        frame=frame,
                        section=section,
                        center_longitudinal=(
                            center_longitudinal
                        ),
                        center_lateral=(
                            center_lateral
                        ),
                        longitudinal_span=(
                            section_longitudinal_span
                        ),
                        lateral_span=(
                            section_lateral_span
                        ),
                    )
                )
            else:
                raise ValueError(
                    "Unsupported church roof shape: "
                    f"{section.roof_shape}"
                )

            sections.append(mesh)

        triangles = [
            triangle
            for section in sections
            for triangle in section["triangles"]
        ]

        return {
            "type": "church_roof_system",
            "sections": sections,
            "triangles": triangles,
        }
