from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class AtlasWallCollectionTieredCornerSupportSpec:
    frame_width_mm: float
    frame_depth_mm: float
    scene_max_height_mm: float

    corner_engagement_mm: float = 8.0
    xy_fit_clearance_mm: float = 0.35
    vertical_clearance_mm: float = 2.0
    wall_thickness_mm: float = 2.0
    shelf_thickness_mm: float = 1.2
    print_height_increment_mm: float = 0.2
    plate_slot_clearance_mm: float = 0.4

    product_capacity_mm: float | None = None
    module_product_clearance_mm: float = 2.0
    connector_engagement_mm: float = 1.6
    connector_recess_depth_mm: float = 1.8
    connector_clearance_per_side_mm: float = 0.25

    @classmethod
    def for_scene(
        cls,
        *,
        frame_width_mm: float,
        frame_depth_mm: float,
        scene_max_height_mm: float,
    ) -> "AtlasWallCollectionTieredCornerSupportSpec":
        spec = cls(
            frame_width_mm=float(frame_width_mm),
            frame_depth_mm=float(frame_depth_mm),
            scene_max_height_mm=float(scene_max_height_mm),
        )
        spec._validate()
        return spec

    @classmethod
    def for_module(
        cls,
        *,
        product_capacity_mm: float,
    ) -> "AtlasWallCollectionTieredCornerSupportSpec":
        product_capacity_mm = float(product_capacity_mm)

        if (
            not math.isfinite(product_capacity_mm)
            or product_capacity_mm not in (25.0, 50.0)
        ):
            raise ValueError(
                "product_capacity_mm must be "
                "25.0 mm or 50.0 mm"
            )

        spec = cls(
            frame_width_mm=10.0,
            frame_depth_mm=6.0,
            scene_max_height_mm=product_capacity_mm,
            product_capacity_mm=product_capacity_mm,
        )
        spec._validate()
        return spec

    def _validate(self) -> None:
        values = {
            "frame_width_mm": self.frame_width_mm,
            "frame_depth_mm": self.frame_depth_mm,
            "scene_max_height_mm": self.scene_max_height_mm,
            "corner_engagement_mm": self.corner_engagement_mm,
            "xy_fit_clearance_mm": self.xy_fit_clearance_mm,
            "vertical_clearance_mm": self.vertical_clearance_mm,
            "wall_thickness_mm": self.wall_thickness_mm,
            "shelf_thickness_mm": self.shelf_thickness_mm,
            "print_height_increment_mm": self.print_height_increment_mm,
            "plate_slot_clearance_mm": self.plate_slot_clearance_mm,
            "module_product_clearance_mm": (
                self.module_product_clearance_mm
            ),
            "connector_engagement_mm": (
                self.connector_engagement_mm
            ),
            "connector_recess_depth_mm": (
                self.connector_recess_depth_mm
            ),
            "connector_clearance_per_side_mm": (
                self.connector_clearance_per_side_mm
            ),
        }

        for name, value in values.items():
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and positive")

        if (
            self.product_capacity_mm is not None
            and self.product_capacity_mm not in (25.0, 50.0)
        ):
            raise ValueError(
                "product_capacity_mm must be "
                "25.0 mm or 50.0 mm"
            )

        if self.corner_engagement_mm > self.frame_width_mm:
            raise ValueError(
                "corner_engagement_mm must not exceed frame_width_mm"
            )

    @property
    def next_plate_base_z_mm(self) -> float:
        if self.product_capacity_mm is not None:
            return (
                self.product_capacity_mm
                + self.module_product_clearance_mm
            )

        raw_height = self.scene_max_height_mm + self.vertical_clearance_mm
        increment = self.print_height_increment_mm
        steps = math.ceil((raw_height - 1e-12) / increment)
        return steps * increment

    @property
    def plate_slot_height_mm(self) -> float:
        return self.frame_depth_mm + self.plate_slot_clearance_mm

    @property
    def total_height_mm(self) -> float:
        return self.next_plate_base_z_mm + self.plate_slot_height_mm

    @property
    def bottom_connector(self) -> str:
        return "female"

    @property
    def top_connector(self) -> str:
        return "male"
