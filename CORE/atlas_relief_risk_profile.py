from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class AtlasReliefRiskProfile:
    """
    Immutable relief print-risk policy.

    Measurement remains independent from this profile.
    The profile only carries thresholds used during
    print-risk classification.
    """

    warning_slope_degrees: float = 55.0
    critical_slope_degrees: float = 75.0
    warning_slope_area_percent: float = 0.0
    critical_slope_area_percent: float = 0.0
    name: str | None = None

    def __post_init__(self) -> None:
        if self.name is not None:
            if not isinstance(self.name, str):
                raise ValueError(
                    "name must be a string or None."
                )

            normalized_name = self.name.strip()

            if not normalized_name:
                raise ValueError(
                    "name must not be blank."
                )

            object.__setattr__(
                self,
                "name",
                normalized_name,
            )

        values = {
            "warning_slope_degrees": (
                self.warning_slope_degrees
            ),
            "critical_slope_degrees": (
                self.critical_slope_degrees
            ),
            "warning_slope_area_percent": (
                self.warning_slope_area_percent
            ),
            "critical_slope_area_percent": (
                self.critical_slope_area_percent
            ),
        }

        converted = {}

        for name, value in values.items():
            numeric_value = float(value)

            if not math.isfinite(numeric_value):
                raise ValueError(
                    f"{name} must be finite."
                )

            converted[name] = numeric_value

        warning_slope_degrees = converted[
            "warning_slope_degrees"
        ]
        critical_slope_degrees = converted[
            "critical_slope_degrees"
        ]
        warning_slope_area_percent = converted[
            "warning_slope_area_percent"
        ]
        critical_slope_area_percent = converted[
            "critical_slope_area_percent"
        ]

        if not (
            0.0
            <= warning_slope_degrees
            < 90.0
        ):
            raise ValueError(
                "warning_slope_degrees must be "
                "in the 0.0..<90.0 range."
            )

        if not (
            0.0
            < critical_slope_degrees
            < 90.0
        ):
            raise ValueError(
                "critical_slope_degrees must be "
                "in the 0.0..<90.0 range."
            )

        if (
            warning_slope_degrees
            >= critical_slope_degrees
        ):
            raise ValueError(
                "warning_slope_degrees must be "
                "lower than critical_slope_degrees."
            )

        if not (
            0.0
            <= warning_slope_area_percent
            <= 100.0
        ):
            raise ValueError(
                "warning_slope_area_percent must "
                "be in the 0.0..100.0 range."
            )

        if not (
            0.0
            <= critical_slope_area_percent
            <= 100.0
        ):
            raise ValueError(
                "critical_slope_area_percent must "
                "be in the 0.0..100.0 range."
            )

        for name, value in converted.items():
            object.__setattr__(
                self,
                name,
                value,
            )

    def to_pipeline_kwargs(self) -> dict[str, float]:
        return {
            "warning_slope_degrees": (
                self.warning_slope_degrees
            ),
            "critical_slope_degrees": (
                self.critical_slope_degrees
            ),
            "warning_slope_area_percent": (
                self.warning_slope_area_percent
            ),
            "critical_slope_area_percent": (
                self.critical_slope_area_percent
            ),
        }
