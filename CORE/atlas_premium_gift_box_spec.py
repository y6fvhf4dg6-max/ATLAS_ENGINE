from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class AtlasPremiumGiftBoxSpec:
    product_width_mm: float
    product_height_mm: float
    product_depth_mm: float

    xy_clearance_per_side_mm: float = 1.0
    vertical_clearance_mm: float = 3.0

    wall_thickness_mm: float = 2.4
    floor_thickness_mm: float = 2.4

    lid_clearance_per_side_mm: float = 0.40
    lid_wall_thickness_mm: float = 2.0
    lid_overlap_mm: float = 8.0
    lid_top_thickness_mm: float = 2.0

    @classmethod
    def for_wall_collection(
        cls,
        *,
        product_width_mm: float,
        product_height_mm: float,
        product_depth_mm: float,
    ) -> "AtlasPremiumGiftBoxSpec":
        spec = cls(
            product_width_mm=float(product_width_mm),
            product_height_mm=float(product_height_mm),
            product_depth_mm=float(product_depth_mm),
        )
        spec._validate()
        return spec

    @classmethod
    def for_mini_wall_collection_v1(
        cls,
    ) -> "AtlasPremiumGiftBoxSpec":
        return cls.for_wall_collection(
            product_width_mm=120.0,
            product_height_mm=120.0,
            product_depth_mm=20.0,
        )

    @classmethod
    def for_original_wall_collection_v1(
        cls,
    ) -> "AtlasPremiumGiftBoxSpec":
        return cls.for_wall_collection(
            product_width_mm=170.0,
            product_height_mm=170.0,
            product_depth_mm=30.0,
        )

    def _validate(self) -> None:
        values = {
            "product_width_mm": self.product_width_mm,
            "product_height_mm": self.product_height_mm,
            "product_depth_mm": self.product_depth_mm,
            "xy_clearance_per_side_mm": self.xy_clearance_per_side_mm,
            "vertical_clearance_mm": self.vertical_clearance_mm,
            "wall_thickness_mm": self.wall_thickness_mm,
            "floor_thickness_mm": self.floor_thickness_mm,
            "lid_clearance_per_side_mm": self.lid_clearance_per_side_mm,
            "lid_wall_thickness_mm": self.lid_wall_thickness_mm,
            "lid_overlap_mm": self.lid_overlap_mm,
            "lid_top_thickness_mm": self.lid_top_thickness_mm,
        }

        for name, value in values.items():
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and positive")

    @property
    def inner_width_mm(self) -> float:
        return self.product_width_mm + 2.0 * self.xy_clearance_per_side_mm

    @property
    def inner_height_mm(self) -> float:
        return self.product_height_mm + 2.0 * self.xy_clearance_per_side_mm

    @property
    def inner_depth_mm(self) -> float:
        return self.product_depth_mm + self.vertical_clearance_mm

    @property
    def outer_width_mm(self) -> float:
        return self.inner_width_mm + 2.0 * self.wall_thickness_mm

    @property
    def outer_height_mm(self) -> float:
        return self.inner_height_mm + 2.0 * self.wall_thickness_mm

    @property
    def base_total_depth_mm(self) -> float:
        return self.inner_depth_mm + self.floor_thickness_mm

    @property
    def lid_inner_width_mm(self) -> float:
        return self.outer_width_mm + 2.0 * self.lid_clearance_per_side_mm

    @property
    def lid_inner_height_mm(self) -> float:
        return self.outer_height_mm + 2.0 * self.lid_clearance_per_side_mm

    @property
    def lid_outer_width_mm(self) -> float:
        return self.lid_inner_width_mm + 2.0 * self.lid_wall_thickness_mm

    @property
    def lid_outer_height_mm(self) -> float:
        return self.lid_inner_height_mm + 2.0 * self.lid_wall_thickness_mm

    @property
    def lid_total_depth_mm(self) -> float:
        return self.lid_overlap_mm + self.lid_top_thickness_mm
