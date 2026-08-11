from __future__ import annotations

import math

from CORE.atlas_castle_shell_triangulator import (
    AtlasCastleShellTriangulator,
)
from CORE.atlas_label_plate_spec import AtlasLabelPlateSpec


class AtlasLabelPlateMesher:
    ROUNDED_CORNER_SEGMENTS = 6

    @classmethod
    def _rounded_outline(
        cls,
        *,
        width_mm: float,
        height_mm: float,
        corner_radius_mm: float,
    ):
        half_width = width_mm / 2.0
        half_height = height_mm / 2.0
        radius = float(corner_radius_mm)

        if radius <= 0.0:
            return (
                (-half_width, -half_height),
                (half_width, -half_height),
                (half_width, half_height),
                (-half_width, half_height),
            )

        centers_and_angles = (
            (
                half_width - radius,
                -half_height + radius,
                -90.0,
                0.0,
            ),
            (
                half_width - radius,
                half_height - radius,
                0.0,
                90.0,
            ),
            (
                -half_width + radius,
                half_height - radius,
                90.0,
                180.0,
            ),
            (
                -half_width + radius,
                -half_height + radius,
                180.0,
                270.0,
            ),
        )

        outline = []

        for (
            center_x,
            center_y,
            start_degrees,
            end_degrees,
        ) in centers_and_angles:
            for segment in range(
                cls.ROUNDED_CORNER_SEGMENTS + 1
            ):
                if outline and segment == 0:
                    continue

                ratio = (
                    segment
                    / cls.ROUNDED_CORNER_SEGMENTS
                )
                angle_degrees = (
                    start_degrees
                    + (
                        end_degrees
                        - start_degrees
                    )
                    * ratio
                )
                angle_radians = math.radians(
                    angle_degrees
                )

                outline.append(
                    (
                        center_x
                        + radius
                        * math.cos(angle_radians),
                        center_y
                        + radius
                        * math.sin(angle_radians),
                    )
                )

        return tuple(outline)

    @staticmethod
    def _lift_triangles(
        triangles_2d,
        *,
        z_mm: float,
        reverse: bool = False,
    ):
        result = []

        for triangle in triangles_2d:
            lifted = tuple(
                (
                    float(x),
                    float(y),
                    float(z_mm),
                )
                for x, y in triangle
            )

            if reverse:
                lifted = (
                    lifted[0],
                    lifted[2],
                    lifted[1],
                )

            result.append(lifted)

        return result

    @classmethod
    def build(
        cls,
        *,
        spec: AtlasLabelPlateSpec,
    ) -> dict:
        outline = cls._rounded_outline(
            width_mm=spec.width_mm,
            height_mm=spec.height_mm,
            corner_radius_mm=spec.corner_radius_mm,
        )

        surface_triangles = (
            AtlasCastleShellTriangulator.triangulate(
                outer_ring=outline,
            )
        )

        if not surface_triangles:
            raise ValueError(
                "label plate surface triangulation failed"
            )

        depth = spec.depth_mm
        triangles = []

        triangles.extend(
            cls._lift_triangles(
                surface_triangles,
                z_mm=0.0,
                reverse=True,
            )
        )
        triangles.extend(
            cls._lift_triangles(
                surface_triangles,
                z_mm=depth,
            )
        )

        for index in range(len(outline)):
            next_index = (index + 1) % len(outline)

            x1, y1 = outline[index]
            x2, y2 = outline[next_index]

            bottom_1 = (x1, y1, 0.0)
            bottom_2 = (x2, y2, 0.0)
            top_1 = (x1, y1, depth)
            top_2 = (x2, y2, depth)

            triangles.extend(
                (
                    (
                        bottom_1,
                        bottom_2,
                        top_2,
                    ),
                    (
                        bottom_1,
                        top_2,
                        top_1,
                    ),
                )
            )

        return {
            "type": "label_plate",
            "width_mm": spec.width_mm,
            "height_mm": spec.height_mm,
            "depth_mm": spec.depth_mm,
            "corner_radius_mm": spec.corner_radius_mm,
            "outline": outline,
            "triangles": triangles,
        }
