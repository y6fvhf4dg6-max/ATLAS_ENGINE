from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AtlasReliefProductProfile:
    """
    Immutable image-to-relief product profile.

    The profile groups deterministic image-processing
    and physical relief parameters without owning any
    image, mesh, sampling, or print-risk logic.
    """

    name: str
    form_sigma: float
    detail_sigma: float
    form_weight: float = 1.0
    detail_weight: float = 0.35
    micro_detail_weight: float = 0.10
    micro_detail_limit: float = 0.05
    depth_lower_percentile: float = 1.0
    depth_upper_percentile: float = 99.0
    depth_gamma: float = 1.0
    background_depth_range: Any = (0.0, 0.40)
    foreground_depth_range: Any = (0.60, 1.0)
    relief_height_mm: float = 2.00
    smoothing_sigma: float | None = None
    smoothing_radius: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise ValueError(
                "name must be a string."
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

        positive_values = {
            "form_sigma": self.form_sigma,
            "depth_gamma": self.depth_gamma,
            "relief_height_mm": self.relief_height_mm,
        }

        non_negative_values = {
            "detail_sigma": self.detail_sigma,
            "form_weight": self.form_weight,
            "detail_weight": self.detail_weight,
            "micro_detail_weight": (
                self.micro_detail_weight
            ),
        }

        converted: dict[str, float] = {}

        for name, value in {
            **positive_values,
            **non_negative_values,
            "micro_detail_limit": (
                self.micro_detail_limit
            ),
            "depth_lower_percentile": (
                self.depth_lower_percentile
            ),
            "depth_upper_percentile": (
                self.depth_upper_percentile
            ),
        }.items():
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

            converted[name] = numeric_value

        for name in positive_values:
            if converted[name] <= 0.0:
                raise ValueError(
                    f"{name} must be greater than zero."
                )

        for name in non_negative_values:
            if converted[name] < 0.0:
                raise ValueError(
                    f"{name} must be zero or greater."
                )

        micro_detail_limit = converted[
            "micro_detail_limit"
        ]

        if not (
            0.0
            <= micro_detail_limit
            <= 1.0
        ):
            raise ValueError(
                "micro_detail_limit must be in the "
                "0.0..1.0 range."
            )

        depth_lower_percentile = converted[
            "depth_lower_percentile"
        ]
        depth_upper_percentile = converted[
            "depth_upper_percentile"
        ]

        if not (
            0.0
            <= depth_lower_percentile
            < depth_upper_percentile
            <= 100.0
        ):
            raise ValueError(
                "depth percentiles must satisfy "
                "0.0 <= lower < upper <= 100.0."
            )

        background_depth_range = (
            self._normalize_depth_range(
                self.background_depth_range,
                name="background_depth_range",
            )
        )
        foreground_depth_range = (
            self._normalize_depth_range(
                self.foreground_depth_range,
                name="foreground_depth_range",
            )
        )

        if (
            background_depth_range[1]
            > foreground_depth_range[0]
        ):
            raise ValueError(
                "background_depth_range must not "
                "overlap foreground_depth_range."
            )

        smoothing_sigma = self.smoothing_sigma

        if smoothing_sigma is not None:
            try:
                smoothing_sigma = float(
                    smoothing_sigma
                )
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise ValueError(
                    "smoothing_sigma must be numeric "
                    "or None."
                ) from exc

            if not math.isfinite(smoothing_sigma):
                raise ValueError(
                    "smoothing_sigma must be finite."
                )

            if smoothing_sigma <= 0.0:
                raise ValueError(
                    "smoothing_sigma must be greater "
                    "than zero."
                )

        smoothing_radius = self.smoothing_radius

        if smoothing_radius is not None:
            if smoothing_sigma is None:
                raise ValueError(
                    "smoothing_radius requires "
                    "smoothing_sigma."
                )

            try:
                numeric_radius = float(
                    smoothing_radius
                )
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise ValueError(
                    "smoothing_radius must be an "
                    "integer or None."
                ) from exc

            if not math.isfinite(numeric_radius):
                raise ValueError(
                    "smoothing_radius must be finite."
                )

            if not numeric_radius.is_integer():
                raise ValueError(
                    "smoothing_radius must be an "
                    "integer."
                )

            smoothing_radius = int(
                numeric_radius
            )

            if smoothing_radius <= 0:
                raise ValueError(
                    "smoothing_radius must be greater "
                    "than zero."
                )

        for name, value in converted.items():
            object.__setattr__(
                self,
                name,
                value,
            )

        object.__setattr__(
            self,
            "background_depth_range",
            background_depth_range,
        )
        object.__setattr__(
            self,
            "foreground_depth_range",
            foreground_depth_range,
        )
        object.__setattr__(
            self,
            "smoothing_sigma",
            smoothing_sigma,
        )
        object.__setattr__(
            self,
            "smoothing_radius",
            smoothing_radius,
        )

    @staticmethod
    def _normalize_depth_range(
        value: Any,
        *,
        name: str,
    ) -> tuple[float, float]:
        try:
            lower_raw, upper_raw = value
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must contain two values."
            ) from exc

        try:
            lower = float(lower_raw)
            upper = float(upper_raw)
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} values must be numeric."
            ) from exc

        if not (
            math.isfinite(lower)
            and math.isfinite(upper)
        ):
            raise ValueError(
                f"{name} values must be finite."
            )

        if not (
            0.0
            <= lower
            < upper
            <= 1.0
        ):
            raise ValueError(
                f"{name} must satisfy "
                "0.0 <= lower < upper <= 1.0."
            )

        return (
            lower,
            upper,
        )

    def to_pipeline_kwargs(self) -> dict[str, Any]:
        return {
            "form_sigma": self.form_sigma,
            "detail_sigma": self.detail_sigma,
            "form_weight": self.form_weight,
            "detail_weight": self.detail_weight,
            "micro_detail_weight": (
                self.micro_detail_weight
            ),
            "micro_detail_limit": (
                self.micro_detail_limit
            ),
            "depth_lower_percentile": (
                self.depth_lower_percentile
            ),
            "depth_upper_percentile": (
                self.depth_upper_percentile
            ),
            "depth_gamma": self.depth_gamma,
            "background_depth_range": (
                self.background_depth_range
            ),
            "foreground_depth_range": (
                self.foreground_depth_range
            ),
            "relief_height_mm": (
                self.relief_height_mm
            ),
            "smoothing_sigma": (
                self.smoothing_sigma
            ),
            "smoothing_radius": (
                self.smoothing_radius
            ),
        }
