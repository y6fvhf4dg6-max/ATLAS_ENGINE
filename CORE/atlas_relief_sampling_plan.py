from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class AtlasReliefSamplingPlan:
    """
    Immutable physical sampling plan for relief meshes.

    The plan converts physical product dimensions and
    a maximum target sample spacing into deterministic
    grid dimensions and expected mesh complexity.
    """

    width_mm: float
    depth_mm: float
    target_sample_spacing_mm: float

    def __post_init__(self) -> None:
        values = {
            "width_mm": self.width_mm,
            "depth_mm": self.depth_mm,
            "target_sample_spacing_mm": (
                self.target_sample_spacing_mm
            ),
        }

        converted = {}

        for name, value in values.items():
            try:
                numeric_value = float(value)
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise ValueError(
                    f"{name} must be numeric."
                ) from exc

            if not math.isfinite(numeric_value):
                raise ValueError(
                    f"{name} must be finite."
                )

            if numeric_value <= 0.0:
                raise ValueError(
                    f"{name} must be greater than zero."
                )

            converted[name] = numeric_value

        for name, value in converted.items():
            object.__setattr__(
                self,
                name,
                value,
            )

    @property
    def column_count(self) -> int:
        interval_count = math.ceil(
            self.width_mm
            / self.target_sample_spacing_mm
        )

        return max(
            2,
            interval_count + 1,
        )

    @property
    def row_count(self) -> int:
        interval_count = math.ceil(
            self.depth_mm
            / self.target_sample_spacing_mm
        )

        return max(
            2,
            interval_count + 1,
        )

    @property
    def sample_count(self) -> int:
        return (
            self.row_count
            * self.column_count
        )

    @property
    def effective_spacing_x_mm(self) -> float:
        return (
            self.width_mm
            / (self.column_count - 1)
        )

    @property
    def effective_spacing_y_mm(self) -> float:
        return (
            self.depth_mm
            / (self.row_count - 1)
        )

    @property
    def top_triangle_count(self) -> int:
        return (
            2
            * (self.row_count - 1)
            * (self.column_count - 1)
        )

    @property
    def bottom_triangle_count(self) -> int:
        return self.top_triangle_count

    @property
    def perimeter_triangle_count(self) -> int:
        perimeter_segment_count = (
            2 * (self.column_count - 1)
            + 2 * (self.row_count - 1)
        )

        return 2 * perimeter_segment_count

    @property
    def total_triangle_count(self) -> int:
        return (
            self.top_triangle_count
            + self.bottom_triangle_count
            + self.perimeter_triangle_count
        )

    def to_pipeline_kwargs(self) -> dict[str, int]:
        return {
            "target_rows": self.row_count,
            "target_columns": self.column_count,
        }
