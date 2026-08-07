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


def _ratio(value, *, name: str) -> float:
    numeric = _positive_finite(
        value,
        name=name,
    )

    if numeric > 1.0:
        raise ValueError(
            f"{name} must be in the 0.0..1.0 range"
        )

    return numeric


@dataclass(frozen=True)
class AtlasConnectionMeasurement:
    component: str
    connection_width_mm: float
    component_span_mm: float
    connection_ratio: float = field(init=False)

    def __post_init__(self) -> None:
        component = _normalize_component(
            self.component
        )
        connection_width_mm = _positive_finite(
            self.connection_width_mm,
            name="connection_width_mm",
        )
        component_span_mm = _positive_finite(
            self.component_span_mm,
            name="component_span_mm",
        )

        if connection_width_mm > component_span_mm:
            raise ValueError(
                "connection_width_mm must not exceed "
                "component_span_mm"
            )

        object.__setattr__(
            self,
            "component",
            component,
        )
        object.__setattr__(
            self,
            "connection_width_mm",
            connection_width_mm,
        )
        object.__setattr__(
            self,
            "component_span_mm",
            component_span_mm,
        )
        object.__setattr__(
            self,
            "connection_ratio",
            connection_width_mm / component_span_mm,
        )


@dataclass(frozen=True)
class AtlasFragileConnectionAnalysis:
    minimum_connection_ratio: float
    measurements: tuple[AtlasConnectionMeasurement, ...]
    minimum_observed_ratio: float
    fragile_components: tuple[str, ...]
    has_fragile_connections: bool


class AtlasFragileConnectionAnalyzer:
    @classmethod
    def analyze(
        cls,
        *,
        measurements: Iterable[AtlasConnectionMeasurement],
        minimum_connection_ratio: float,
    ) -> AtlasFragileConnectionAnalysis:
        minimum_ratio = _ratio(
            minimum_connection_ratio,
            name="minimum_connection_ratio",
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
                AtlasConnectionMeasurement,
            )
            for measurement in normalized_measurements
        ):
            raise TypeError(
                "measurements must contain only "
                "AtlasConnectionMeasurement values"
            )

        minimum_observed_ratio = min(
            measurement.connection_ratio
            for measurement in normalized_measurements
        )

        fragile_components = []
        seen = set()

        for measurement in normalized_measurements:
            if measurement.connection_ratio >= minimum_ratio:
                continue

            component = measurement.component

            if component in seen:
                continue

            seen.add(component)
            fragile_components.append(component)

        components = tuple(fragile_components)

        return AtlasFragileConnectionAnalysis(
            minimum_connection_ratio=minimum_ratio,
            measurements=normalized_measurements,
            minimum_observed_ratio=minimum_observed_ratio,
            fragile_components=components,
            has_fragile_connections=bool(components),
        )
