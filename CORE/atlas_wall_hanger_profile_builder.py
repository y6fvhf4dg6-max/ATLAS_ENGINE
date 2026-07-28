from __future__ import annotations

import math

from shapely.geometry import Polygon
from shapely.ops import unary_union

from CORE.atlas_wall_frame_spec import AtlasWallFrameSpec
from CORE.atlas_wall_hanger_spec import AtlasWallHangerSpec


class AtlasWallHangerProfileBuilder:
    CIRCLE_SEGMENTS = 32
    FRAME_CLEARANCE_MM = 0.25

    @classmethod
    def build(
        cls,
        *,
        frame_spec: AtlasWallFrameSpec,
        hanger_spec: AtlasWallHangerSpec,
        center_x_mm: float,
    ) -> dict:
        center_x_mm = float(center_x_mm)

        outer_half_x = frame_spec.outer_width_mm / 2.0
        outer_half_y = frame_spec.outer_height_mm / 2.0
        inner_half_y = frame_spec.inner_height_mm / 2.0

        head_radius_mm = hanger_spec.head_diameter_mm / 2.0
        neck_half_width_mm = hanger_spec.neck_width_mm / 2.0

        usable_bottom_y_mm = (
            inner_half_y
            + cls.FRAME_CLEARANCE_MM
        )
        usable_top_y_mm = (
            outer_half_y
            - cls.FRAME_CLEARANCE_MM
        )

        head_center_y_mm = (
            usable_bottom_y_mm
            + head_radius_mm
        )
        neck_top_y_mm = (
            head_center_y_mm
            + hanger_spec.locking_travel_mm
            + head_radius_mm
        )

        if neck_top_y_mm > usable_top_y_mm:
            raise ValueError(
                "hanger profile exceeds frame bounds"
            )

        head_ring = []

        for index in range(cls.CIRCLE_SEGMENTS):
            angle = (
                2.0
                * math.pi
                * index
                / cls.CIRCLE_SEGMENTS
            )
            head_ring.append(
                (
                    center_x_mm
                    + head_radius_mm * math.cos(angle),
                    head_center_y_mm
                    + head_radius_mm * math.sin(angle),
                )
            )

        head_polygon = Polygon(head_ring)

        neck_polygon = Polygon(
            (
                (
                    center_x_mm - neck_half_width_mm,
                    head_center_y_mm,
                ),
                (
                    center_x_mm + neck_half_width_mm,
                    head_center_y_mm,
                ),
                (
                    center_x_mm + neck_half_width_mm,
                    neck_top_y_mm,
                ),
                (
                    center_x_mm - neck_half_width_mm,
                    neck_top_y_mm,
                ),
            )
        )

        profile_polygon = unary_union(
            (head_polygon, neck_polygon)
        )

        if profile_polygon.geom_type != "Polygon":
            raise ValueError(
                "hanger profile could not be resolved as one polygon"
            )

        min_x, min_y, max_x, max_y = profile_polygon.bounds

        if (
            min_x < -outer_half_x
            or max_x > outer_half_x
            or min_y < inner_half_y
            or max_y > outer_half_y
        ):
            raise ValueError(
                "hanger profile exceeds frame bounds"
            )

        ring = [
            (float(x), float(y))
            for x, y in list(profile_polygon.exterior.coords)[:-1]
        ]

        closed_outer_wall_mm = (
            outer_half_y
            - max_y
        )

        return {
            "type": "wall_hanger_keyhole_profile",
            "center_x_mm": center_x_mm,
            "head_center_y_mm": head_center_y_mm,
            "neck_top_y_mm": neck_top_y_mm,
            "closed_outer_wall_mm": closed_outer_wall_mm,
            "ring": ring,
        }
