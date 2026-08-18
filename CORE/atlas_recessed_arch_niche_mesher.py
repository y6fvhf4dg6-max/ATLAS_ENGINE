from __future__ import annotations

import math

from CORE.atlas_polygon_triangulator import (
    AtlasPolygonTriangulator,
)


class AtlasRecessedArchNicheMesher:
    MIN_ARCH_SEGMENTS = 4

    @classmethod
    def build(
        cls,
        *,
        center_x,
        center_z,
        width_mm,
        height_mm,
        spring_height_mm,
        recess_depth_mm,
        front_y=0.0,
        arch_segments=8,
        metadata=None,
    ):
        center_x = float(center_x)
        center_z = float(center_z)
        width_mm = float(width_mm)
        height_mm = float(height_mm)
        spring_height_mm = float(
            spring_height_mm
        )
        recess_depth_mm = float(
            recess_depth_mm
        )
        front_y = float(front_y)

        if width_mm <= 0.0:
            raise ValueError(
                "width_mm must be greater than zero"
            )

        if height_mm <= 0.0:
            raise ValueError(
                "height_mm must be greater than zero"
            )

        if not 0.0 < spring_height_mm < height_mm:
            raise ValueError(
                "spring_height_mm must satisfy "
                "0 < spring_height_mm < height_mm"
            )

        if recess_depth_mm <= 0.0:
            raise ValueError(
                "recess_depth_mm must be greater than zero"
            )

        if (
            isinstance(arch_segments, bool)
            or not isinstance(arch_segments, int)
            or arch_segments < cls.MIN_ARCH_SEGMENTS
        ):
            raise ValueError(
                "arch_segments must be an integer "
                f"of at least {cls.MIN_ARCH_SEGMENTS}"
            )

        half_width = width_mm / 2.0
        bottom_z = center_z - height_mm / 2.0
        top_z = center_z + height_mm / 2.0
        spring_z = bottom_z + spring_height_mm
        arch_rise = top_z - spring_z

        outline_xz = [
            (
                center_x - half_width,
                bottom_z,
            ),
            (
                center_x + half_width,
                bottom_z,
            ),
            (
                center_x + half_width,
                spring_z,
            ),
        ]

        for index in range(
            1,
            arch_segments,
        ):
            theta = (
                math.pi
                * index
                / arch_segments
            )

            outline_xz.append(
                (
                    center_x
                    + half_width
                    * math.cos(theta),
                    spring_z
                    + arch_rise
                    * math.sin(theta),
                )
            )

        outline_xz.append(
            (
                center_x - half_width,
                spring_z,
            )
        )

        outline_xz = tuple(outline_xz)

        triangles_2d = (
            AtlasPolygonTriangulator.triangulate(
                outline_xz
            )
        )

        if not triangles_2d:
            raise ValueError(
                "niche profile could not be triangulated"
            )

        back_y = front_y - recess_depth_mm

        front_triangles = []
        back_triangles = []

        for first, second, third in triangles_2d:
            front_triangles.append(
                (
                    (first[0], front_y, first[1]),
                    (second[0], front_y, second[1]),
                    (third[0], front_y, third[1]),
                )
            )

            back_triangles.append(
                (
                    (first[0], back_y, first[1]),
                    (third[0], back_y, third[1]),
                    (second[0], back_y, second[1]),
                )
            )

        side_triangles = []

        for index, first in enumerate(
            outline_xz
        ):
            second = outline_xz[
                (index + 1) % len(outline_xz)
            ]

            front_first = (
                first[0],
                front_y,
                first[1],
            )
            front_second = (
                second[0],
                front_y,
                second[1],
            )
            back_first = (
                first[0],
                back_y,
                first[1],
            )
            back_second = (
                second[0],
                back_y,
                second[1],
            )

            side_triangles.extend(
                (
                    (
                        front_first,
                        back_second,
                        back_first,
                    ),
                    (
                        front_first,
                        front_second,
                        back_second,
                    ),
                )
            )

        triangles = [
            *front_triangles,
            *back_triangles,
            *side_triangles,
        ]

        result = {
            "triangles": triangles,
            "front_profile": tuple(
                (
                    x,
                    front_y,
                    z,
                )
                for x, z in outline_xz
            ),
            "back_profile": tuple(
                (
                    x,
                    back_y,
                    z,
                )
                for x, z in outline_xz
            ),
            "width_mm": width_mm,
            "height_mm": height_mm,
            "spring_height_mm": spring_height_mm,
            "recess_depth_mm": recess_depth_mm,
            "arch_segments": arch_segments,
            "component_type": "recessed_arch_niche",
            "source_system": "recessed_arch_niche_mesher",
            "geometry_type": "recessed_arch_niche",
        }

        if metadata:
            result.update(
                dict(metadata)
            )

        return result
