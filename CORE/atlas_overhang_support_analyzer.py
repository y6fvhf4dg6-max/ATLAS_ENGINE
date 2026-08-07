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


def _overhang_degrees(value, *, name: str) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name} must be numeric") from exc

    if not math.isfinite(numeric):
        raise ValueError(f"{name} must be finite")

    if not 0.0 <= numeric <= 90.0:
        raise ValueError(
            f"{name} must be in the 0.0..90.0 range"
        )

    return numeric


def _support_threshold_degrees(value) -> float:
    numeric = _overhang_degrees(
        value,
        name="support_threshold_degrees",
    )

    if numeric <= 0.0:
        raise ValueError(
            "support_threshold_degrees must be greater than zero"
        )

    return numeric


@dataclass(frozen=True)
class AtlasOverhangMeasurement:
    component: str
    overhang_degrees: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "component",
            _normalize_component(self.component),
        )
        object.__setattr__(
            self,
            "overhang_degrees",
            _overhang_degrees(
                self.overhang_degrees,
                name="overhang_degrees",
            ),
        )


@dataclass(frozen=True)
class AtlasOverhangSupportAnalysis:
    support_threshold_degrees: float
    measurements: tuple[AtlasOverhangMeasurement, ...]
    maximum_overhang_degrees: float
    support_required_components: tuple[str, ...]
    support_required: bool


class AtlasOverhangSupportAnalyzer:
    @classmethod
    def analyze(
        cls,
        *,
        measurements: Iterable[AtlasOverhangMeasurement],
        support_threshold_degrees: float,
    ) -> AtlasOverhangSupportAnalysis:
        threshold = _support_threshold_degrees(
            support_threshold_degrees
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
                AtlasOverhangMeasurement,
            )
            for measurement in normalized_measurements
        ):
            raise TypeError(
                "measurements must contain only "
                "AtlasOverhangMeasurement values"
            )

        maximum_overhang = max(
            measurement.overhang_degrees
            for measurement in normalized_measurements
        )

        support_required_components = []
        seen = set()

        for measurement in normalized_measurements:
            if measurement.overhang_degrees < threshold:
                continue

            component = measurement.component

            if component in seen:
                continue

            seen.add(component)
            support_required_components.append(component)

        components = tuple(
            support_required_components
        )

        return AtlasOverhangSupportAnalysis(
            support_threshold_degrees=threshold,
            measurements=normalized_measurements,
            maximum_overhang_degrees=maximum_overhang,
            support_required_components=components,
            support_required=bool(components),
        )
