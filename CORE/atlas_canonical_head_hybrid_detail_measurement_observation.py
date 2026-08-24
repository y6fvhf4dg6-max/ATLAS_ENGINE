from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Integral


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadHybridDetailMeasurementObservation:
    measurement_id: str
    source_view_id: str

    image_reference_span_px: float
    canonical_reference_span: float
    scale_factor: float

    mapped_vertex_count: int
    active_vertex_count: int
    clipped_vertex_count: int

    maximum_absolute_amplitude: float

    raw_absolute_max: float
    weighted_absolute_max: float
    bounded_absolute_max: float
    weighted_absolute_p95: float
    weighted_absolute_p99: float

    connectivity_signature: str

    def __post_init__(self) -> None:
        for field_name in (
            "measurement_id",
            "source_view_id",
            "connectivity_signature",
        ):
            value = getattr(
                self,
                field_name,
            )

            if not isinstance(
                value,
                str,
            ):
                raise TypeError(
                    f"{field_name} must be a string."
                )

            normalized = value.strip()

            if not normalized:
                raise ValueError(
                    f"{field_name} must not be blank."
                )

            object.__setattr__(
                self,
                field_name,
                normalized,
            )

        for field_name in (
            "image_reference_span_px",
            "canonical_reference_span",
            "scale_factor",
            "maximum_absolute_amplitude",
        ):
            value = self._normalize_positive_finite(
                getattr(
                    self,
                    field_name,
                ),
                name=field_name,
            )

            object.__setattr__(
                self,
                field_name,
                value,
            )

        for field_name in (
            "raw_absolute_max",
            "weighted_absolute_max",
            "bounded_absolute_max",
            "weighted_absolute_p95",
            "weighted_absolute_p99",
        ):
            value = self._normalize_nonnegative_finite(
                getattr(
                    self,
                    field_name,
                ),
                name=field_name,
            )

            object.__setattr__(
                self,
                field_name,
                value,
            )

        for field_name in (
            "mapped_vertex_count",
            "active_vertex_count",
            "clipped_vertex_count",
        ):
            value = self._normalize_nonnegative_integer(
                getattr(
                    self,
                    field_name,
                ),
                name=field_name,
            )

            object.__setattr__(
                self,
                field_name,
                value,
            )

        if self.active_vertex_count > self.mapped_vertex_count:
            raise ValueError(
                "active_vertex_count must not exceed "
                "mapped_vertex_count."
            )

        if self.clipped_vertex_count > self.active_vertex_count:
            raise ValueError(
                "clipped_vertex_count must not exceed "
                "active_vertex_count."
            )

        if (
            self.bounded_absolute_max
            > self.maximum_absolute_amplitude + 1e-12
        ):
            raise ValueError(
                "bounded_absolute_max must not exceed "
                "maximum_absolute_amplitude."
            )

        if self.weighted_absolute_p95 > self.weighted_absolute_p99:
            raise ValueError(
                "weighted_absolute_p95 must not exceed "
                "weighted_absolute_p99."
            )

        if self.weighted_absolute_p99 > self.weighted_absolute_max:
            raise ValueError(
                "weighted_absolute_p99 must not exceed "
                "weighted_absolute_max."
            )

        if self.weighted_absolute_max > self.raw_absolute_max + 1e-12:
            raise ValueError(
                "weighted_absolute_max must not exceed "
                "raw_absolute_max."
            )

    @property
    def clipped_vertex_fraction(
        self,
    ) -> float:
        if self.active_vertex_count == 0:
            return 0.0

        return (
            self.clipped_vertex_count
            / self.active_vertex_count
        )

    @staticmethod
    def _normalize_positive_finite(
        value: object,
        *,
        name: str,
    ) -> float:
        try:
            normalized = float(
                value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if (
            not math.isfinite(
                normalized
            )
            or normalized <= 0.0
        ):
            raise ValueError(
                f"{name} must be finite and positive."
            )

        return normalized

    @staticmethod
    def _normalize_nonnegative_finite(
        value: object,
        *,
        name: str,
    ) -> float:
        try:
            normalized = float(
                value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if (
            not math.isfinite(
                normalized
            )
            or normalized < 0.0
        ):
            raise ValueError(
                f"{name} must be finite and nonnegative."
            )

        return normalized

    @staticmethod
    def _normalize_nonnegative_integer(
        value: object,
        *,
        name: str,
    ) -> int:
        if (
            isinstance(
                value,
                bool,
            )
            or not isinstance(
                value,
                Integral,
            )
        ):
            raise TypeError(
                f"{name} must be an integer."
            )

        normalized = int(
            value
        )

        if normalized < 0:
            raise ValueError(
                f"{name} must be nonnegative."
            )

        return normalized
