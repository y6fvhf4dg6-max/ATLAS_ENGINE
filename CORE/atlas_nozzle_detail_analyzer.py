from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Iterable


def _normalize_component(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("component must be a string")

    normalized = value.strip().lower()

    if not normalized:
        raise ValueError("component must not be empty")

    return normalized


def _positive_finite(value, *, name: str) -> float:
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
class AtlasNozzleDetailMeasurement:
    component: str
    detail_size_mm: float
    nozzle_diameter_mm: float
    nozzle_ratio: float = field(init=False)

    def __post_init__(self) -> None:
        component = _normalize_component(
            self.component
        )
        detail_size_mm = _positive_finite(
            self.detail_size_mm,
            name="detail_size_mm",
        )
        nozzle_diameter_mm = _positive_finite(
            self.nozzle_diameter_mm,
            name="nozzle_diameter_mm",
        )

        object.__setattr__(
            self,
            "component",
            component,
        )
        object.__setattr__(
            self,
            "detail_size_mm",
            detail_size_mm,
        )
        object.__setattr__(
            self,
            "nozzle_diameter_mm",
            nozzle_diameter_mm,
        )
        object.__setattr__(
            self,
            "nozzle_ratio",
            detail_size_mm / nozzle_diameter_mm,
        )


@dataclass(frozen=True)
class AtlasNozzleDetailAnalysis:
    nozzle_diameter_mm: float
    measurements: tuple[AtlasNozzleDetailMeasurement, ...]
    minimum_observed_detail_mm: float
    below_nozzle_components: tuple[str, ...]
    has_below_nozzle_details: bool


class AtlasNozzleDetailAnalyzer:
    @classmethod
    def analyze(
        cls,
        *,
        measurements: Iterable[AtlasNozzleDetailMeasurement],
        nozzle_diameter_mm: float,
    ) -> AtlasNozzleDetailAnalysis:
        nozzle = _positive_finite(
            nozzle_diameter_mm,
            name="nozzle_diameter_mm",
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
                AtlasNozzleDetailMeasurement,
            )
            for measurement in normalized_measurements
        ):
            raise TypeError(
                "measurements must contain only "
                "AtlasNozzleDetailMeasurement values"
            )

        for measurement in normalized_measurements:
            if not math.isclose(
                measurement.nozzle_diameter_mm,
                nozzle,
                rel_tol=1e-12,
                abs_tol=1e-12,
            ):
                raise ValueError(
                    "measurement nozzle_diameter_mm must match "
                    "analysis nozzle_diameter_mm"
                )

        minimum_observed_detail_mm = min(
            measurement.detail_size_mm
            for measurement in normalized_measurements
        )

        below_nozzle_components = []
        seen = set()

        for measurement in normalized_measurements:
            if measurement.detail_size_mm >= nozzle:
                continue

            component = measurement.component

            if component in seen:
                continue

            seen.add(component)
            below_nozzle_components.append(component)

        components = tuple(
            below_nozzle_components
        )

        return AtlasNozzleDetailAnalysis(
            nozzle_diameter_mm=nozzle,
            measurements=normalized_measurements,
            minimum_observed_detail_mm=minimum_observed_detail_mm,
            below_nozzle_components=components,
            has_below_nozzle_details=bool(components),
        )
