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

    middle_module_capacities_mm: tuple = (25.0, 50.0)
    module_product_clearance_mm: float = 2.0
    connector_engagement_mm: float = 1.6
    connector_recess_depth_mm: float = 1.8
    connector_clearance_per_side_mm: float = 0.25

    personalization_plate_thickness_mm: float = 1.2
    personalization_recess_depth_mm: float = 0.8
    personalization_fit_clearance_per_side_mm: float = 0.20
    personalization_text_depth_mm: float = 0.6
    personalization_max_lines: int = 2

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
            "personalization_plate_thickness_mm": (
                self.personalization_plate_thickness_mm
            ),
            "personalization_recess_depth_mm": (
                self.personalization_recess_depth_mm
            ),
            "personalization_fit_clearance_per_side_mm": (
                self.personalization_fit_clearance_per_side_mm
            ),
            "personalization_text_depth_mm": (
                self.personalization_text_depth_mm
            ),
        }

        for name, value in values.items():
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and positive")

    def validate_middle_module_capacity(
        self,
        product_capacity_mm: float,
    ) -> float:
        product_capacity_mm = float(product_capacity_mm)

        if (
            not math.isfinite(product_capacity_mm)
            or product_capacity_mm
            not in self.middle_module_capacities_mm
        ):
            raise ValueError(
                "middle module capacity must be "
                "25.0 mm or 50.0 mm"
            )

        return product_capacity_mm

    def middle_module_usable_height_mm(
        self,
        product_capacity_mm: float,
    ) -> float:
        product_capacity_mm = (
            self.validate_middle_module_capacity(
                product_capacity_mm
            )
        )

        return (
            product_capacity_mm
            + self.module_product_clearance_mm
        )

    def compose_middle_module_capacities(
        self,
        required_capacity_mm: float,
    ) -> tuple:
        required_capacity_mm = float(required_capacity_mm)

        if (
            not math.isfinite(required_capacity_mm)
            or required_capacity_mm <= 0.0
            or abs(
                required_capacity_mm / 25.0
                - round(required_capacity_mm / 25.0)
            )
            > 1e-9
        ):
            raise ValueError(
                "required middle module capacity must be "
                "a positive multiple of 25.0 mm"
            )

        remaining = int(round(required_capacity_mm))
        capacities = []

        while remaining >= 50:
            capacities.append(50.0)
            remaining -= 50

        if remaining == 25:
            capacities.append(25.0)
            remaining = 0

        if remaining != 0:
            raise ValueError(
                "required middle module capacity cannot "
                "be composed from 25.0 mm and 50.0 mm"
            )

        return tuple(capacities)

    @property
    def personalization_plate_size_mm(self) -> tuple:
        maximum_product_side = max(
            self.product_width_mm,
            self.product_height_mm,
        )

        if maximum_product_side <= 120.0 + 1e-9:
            return (80.0, 24.0)

        if maximum_product_side <= 170.0 + 1e-9:
            return (110.0, 28.0)

        return (140.0, 32.0)

    @property
    def personalization_recess_size_mm(self) -> tuple:
        plate_width_mm, plate_height_mm = (
            self.personalization_plate_size_mm
        )
        total_clearance_mm = (
            2.0
            * self.personalization_fit_clearance_per_side_mm
        )

        return (
            plate_width_mm + total_clearance_mm,
            plate_height_mm + total_clearance_mm,
        )

    def validate_personalization_lines(
        self,
        lines,
    ) -> tuple:
        if isinstance(lines, str):
            lines = (lines,)

        resolved_lines = tuple(
            str(line).strip()
            for line in lines
        )

        if not resolved_lines:
            raise ValueError(
                "personalization requires at least one line"
            )

        if len(resolved_lines) > self.personalization_max_lines:
            raise ValueError(
                "personalization supports at most 2 lines"
            )

        if any(not line for line in resolved_lines):
            raise ValueError(
                "personalization lines must not be empty"
            )

        return resolved_lines

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
