from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from CORE.atlas_relief_sampling_plan import (
    AtlasReliefSamplingPlan,
)


@dataclass(frozen=True, slots=True)
class AtlasArchitecturalReliefPhysicalProfile:
    name: str
    base_thickness_mm: float
    relief_height_mm: float
    target_sample_spacing_mm: float

    def __post_init__(self) -> None:
        if not isinstance(
            self.name,
            str,
        ):
            raise ValueError(
                "name must be a string"
            )

        normalized_name = self.name.strip()

        if not normalized_name:
            raise ValueError(
                "name must not be blank"
            )

        base_thickness_mm = (
            self._positive_finite(
                self.base_thickness_mm,
                name="base_thickness_mm",
            )
        )
        relief_height_mm = (
            self._positive_finite(
                self.relief_height_mm,
                name="relief_height_mm",
            )
        )
        target_sample_spacing_mm = (
            self._positive_finite(
                self.target_sample_spacing_mm,
                name="target_sample_spacing_mm",
            )
        )

        object.__setattr__(
            self,
            "name",
            normalized_name,
        )
        object.__setattr__(
            self,
            "base_thickness_mm",
            base_thickness_mm,
        )
        object.__setattr__(
            self,
            "relief_height_mm",
            relief_height_mm,
        )
        object.__setattr__(
            self,
            "target_sample_spacing_mm",
            target_sample_spacing_mm,
        )

    @property
    def total_height_mm(self) -> float:
        return (
            self.base_thickness_mm
            + self.relief_height_mm
        )

    def resolve(
        self,
        *,
        width_mm: float,
        depth_mm: float,
    ) -> dict[str, Any]:
        resolved_width_mm = (
            self._positive_finite(
                width_mm,
                name="width_mm",
            )
        )
        resolved_depth_mm = (
            self._positive_finite(
                depth_mm,
                name="depth_mm",
            )
        )

        sampling_plan = AtlasReliefSamplingPlan(
            width_mm=resolved_width_mm,
            depth_mm=resolved_depth_mm,
            target_sample_spacing_mm=(
                self.target_sample_spacing_mm
            ),
        )

        pipeline_kwargs = {
            "base_thickness_mm": (
                self.base_thickness_mm
            ),
            "relief_height_mm": (
                self.relief_height_mm
            ),
            **sampling_plan.to_pipeline_kwargs(),
        }

        mesh_kwargs = {
            "width_mm": resolved_width_mm,
            "depth_mm": resolved_depth_mm,
            "base_thickness_mm": (
                self.base_thickness_mm
            ),
            "relief_height_mm": (
                self.relief_height_mm
            ),
        }

        return {
            "type": (
                "architectural_relief_physical_plan"
            ),
            "profile": self,
            "width_mm": resolved_width_mm,
            "depth_mm": resolved_depth_mm,
            "base_thickness_mm": (
                self.base_thickness_mm
            ),
            "relief_height_mm": (
                self.relief_height_mm
            ),
            "total_height_mm": (
                self.total_height_mm
            ),
            "target_sample_spacing_mm": (
                self.target_sample_spacing_mm
            ),
            "effective_spacing_x_mm": (
                sampling_plan
                .effective_spacing_x_mm
            ),
            "effective_spacing_y_mm": (
                sampling_plan
                .effective_spacing_y_mm
            ),
            "triangle_count": (
                sampling_plan
                .total_triangle_count
            ),
            "sampling_plan": sampling_plan,
            "pipeline_kwargs": (
                pipeline_kwargs
            ),
            "mesh_kwargs": mesh_kwargs,
        }

    @staticmethod
    def _positive_finite(
        value: Any,
        *,
        name: str,
    ) -> float:
        try:
            numeric = float(value)
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric"
            ) from exc

        if (
            not math.isfinite(numeric)
            or numeric <= 0.0
        ):
            raise ValueError(
                f"{name} must be greater than zero"
            )

        return numeric
