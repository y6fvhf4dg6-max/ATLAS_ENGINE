from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AtlasWallHangerSpec:
    hanger_count: int
    center_x_positions_mm: tuple[float, ...]
    head_diameter_mm: float
    neck_width_mm: float
    locking_travel_mm: float
    recess_depth_mm: float
    front_wall_thickness_mm: float

    SUPPORTED_PRODUCT_SIZES_MM = (150.0, 170.0, 200.0, 260.0)

    HEAD_DIAMETER_MM = 5.0
    NECK_WIDTH_MM = 3.0
    LOCKING_TRAVEL_MM = 1.0
    RECESS_DEPTH_MM = 3.0
    MIN_FRONT_WALL_THICKNESS_MM = 3.0
    MIN_FRAME_WIDTH_MM = 8.0

    @classmethod
    def for_product_size(
        cls,
        *,
        outer_width_mm: float,
        outer_height_mm: float,
        frame_width_mm: float,
        frame_depth_mm: float,
    ) -> "AtlasWallHangerSpec":
        outer_width_mm = float(outer_width_mm)
        outer_height_mm = float(outer_height_mm)
        frame_width_mm = float(frame_width_mm)
        frame_depth_mm = float(frame_depth_mm)

        if (
            outer_width_mm not in cls.SUPPORTED_PRODUCT_SIZES_MM
            or outer_height_mm != outer_width_mm
        ):
            raise ValueError(
                "unsupported Wall Collection product size"
            )

        if frame_width_mm < cls.MIN_FRAME_WIDTH_MM:
            raise ValueError(
                "frame width is too narrow for keyhole hanger"
            )

        front_wall_thickness_mm = (
            frame_depth_mm - cls.RECESS_DEPTH_MM
        )

        if (
            front_wall_thickness_mm
            < cls.MIN_FRONT_WALL_THICKNESS_MM
        ):
            raise ValueError(
                "frame depth is too shallow for hanger recess"
            )

        if outer_width_mm < 260.0:
            center_x_positions_mm = (0.0,)
        else:
            quarter_width_mm = outer_width_mm / 4.0
            center_x_positions_mm = (
                -quarter_width_mm,
                0.0,
                quarter_width_mm,
            )

        return cls(
            hanger_count=len(center_x_positions_mm),
            center_x_positions_mm=center_x_positions_mm,
            head_diameter_mm=cls.HEAD_DIAMETER_MM,
            neck_width_mm=cls.NECK_WIDTH_MM,
            locking_travel_mm=cls.LOCKING_TRAVEL_MM,
            recess_depth_mm=cls.RECESS_DEPTH_MM,
            front_wall_thickness_mm=front_wall_thickness_mm,
        )
