from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable


def _normalize_component(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("component must be a string")

    normalized = value.strip().lower()

    if not normalized:
        raise ValueError("component must not be empty")

    return normalized


def _positive_finite_mm(value, *, name: str) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name} must be numeric") from exc

    if not math.isfinite(numeric):
        raise ValueError(f"{name} must be finite")

    if numeric <= 0.0:
        raise ValueError(f"{name} must be positive")

    return numeric


@dataclass(frozen=True)
class AtlasThicknessMeasurement:
    component: str
    thickness_mm: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "component",
            _normalize_component(self.component),
        )
        object.__setattr__(
            self,
            "thickness_mm",
            _positive_finite_mm(
                self.thickness_mm,
                name="thickness_mm",
            ),
        )


@dataclass(frozen=True)
class AtlasMinimumThicknessAnalysis:
    minimum_thickness_mm: float
    measurements: tuple[AtlasThicknessMeasurement, ...]
    minimum_observed_thickness_mm: float
    violating_components: tuple[str, ...]
    is_safe: bool


class AtlasMinimumThicknessAnalyzer:
    @classmethod
    def analyze(
        cls,
        *,
        measurements: Iterable[AtlasThicknessMeasurement],
        minimum_thickness_mm: float,
    ) -> AtlasMinimumThicknessAnalysis:
        minimum = _positive_finite_mm(
            minimum_thickness_mm,
            name="minimum_thickness_mm",
        )

        try:
            normalized_measurements = tuple(measurements)
        except TypeError as exc:
            raise TypeError(
                "measurements must be an iterable"
            ) from exc

        if not normalized_measurements:
            raise ValueError(
                "measurements must not be empty"
            )

        if not all(
            isinstance(
                measurement,
                AtlasThicknessMeasurement,
            )
            for measurement in normalized_measurements
        ):
            raise TypeError(
                "measurements must contain only "
                "AtlasThicknessMeasurement values"
            )

        minimum_observed = min(
            measurement.thickness_mm
            for measurement in normalized_measurements
        )

        violating_components = []
        seen = set()

        for measurement in normalized_measurements:
            if measurement.thickness_mm >= minimum:
                continue

            component = measurement.component

            if component in seen:
                continue

            seen.add(component)
            violating_components.append(component)

        violations = tuple(violating_components)

        return AtlasMinimumThicknessAnalysis(
            minimum_thickness_mm=minimum,
            measurements=normalized_measurements,
            minimum_observed_thickness_mm=minimum_observed,
            violating_components=violations,
            is_safe=not violations,
        )
