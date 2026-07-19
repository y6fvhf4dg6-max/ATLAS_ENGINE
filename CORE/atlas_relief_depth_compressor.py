from __future__ import annotations

import math
from typing import Any

import numpy as np


class AtlasReliefDepthCompressor:
    """
    Compresses an unnormalized relief depth candidate into
    a deterministic 0.0..1.0 depth map.

    Percentile clipping reduces the influence of isolated
    extreme values before normalization. Gamma then shapes
    the normalized depth distribution.
    """

    @staticmethod
    def compress(
        values: Any,
        *,
        lower_percentile: float = 1.0,
        upper_percentile: float = 99.0,
        gamma: float = 1.0,
    ) -> dict[str, Any]:
        source = AtlasReliefDepthCompressor._as_valid_array(
            values
        )

        lower_percentile_value = (
            AtlasReliefDepthCompressor
            ._validate_percentile(
                lower_percentile,
                name="lower_percentile",
            )
        )

        upper_percentile_value = (
            AtlasReliefDepthCompressor
            ._validate_percentile(
                upper_percentile,
                name="upper_percentile",
            )
        )

        if (
            lower_percentile_value
            >= upper_percentile_value
        ):
            raise ValueError(
                "lower_percentile must be lower than "
                "upper_percentile."
            )

        gamma_value = (
            AtlasReliefDepthCompressor
            ._validate_positive_parameter(
                gamma,
                name="gamma",
            )
        )

        lower_bound = float(
            np.percentile(
                source,
                lower_percentile_value,
            )
        )

        upper_bound = float(
            np.percentile(
                source,
                upper_percentile_value,
            )
        )

        value_range = upper_bound - lower_bound

        if value_range <= 0.0:
            clipped = source.copy()
            normalized = np.zeros_like(
                source,
                dtype=np.float64,
            )
        else:
            clipped = np.clip(
                source,
                lower_bound,
                upper_bound,
            )

            normalized = (
                clipped - lower_bound
            ) / value_range

        compressed = np.power(
            normalized,
            gamma_value,
            dtype=np.float64,
        )

        compressed = np.clip(
            compressed,
            0.0,
            1.0,
        ).astype(
            np.float64,
            copy=True,
        )

        return {
            "type": "relief_depth_compression",
            "lower_percentile": (
                lower_percentile_value
            ),
            "upper_percentile": (
                upper_percentile_value
            ),
            "gamma": gamma_value,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "clipped_depth": clipped.astype(
                np.float64,
                copy=True,
            ),
            "compressed_depth": compressed,
        }

    @staticmethod
    def _validate_percentile(
        value: Any,
        *,
        name: str,
    ) -> float:
        numeric_value = (
            AtlasReliefDepthCompressor
            ._as_finite_number(
                value,
                name=name,
            )
        )

        if not 0.0 <= numeric_value <= 100.0:
            raise ValueError(
                f"{name} must be within the "
                "0.0..100.0 range."
            )

        return numeric_value

    @staticmethod
    def _validate_positive_parameter(
        value: Any,
        *,
        name: str,
    ) -> float:
        numeric_value = (
            AtlasReliefDepthCompressor
            ._as_finite_number(
                value,
                name=name,
            )
        )

        if numeric_value <= 0.0:
            raise ValueError(
                f"{name} must be greater than zero."
            )

        return numeric_value

    @staticmethod
    def _as_finite_number(
        value: Any,
        *,
        name: str,
    ) -> float:
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

        return numeric_value

    @staticmethod
    def _as_valid_array(
        values: Any,
    ) -> np.ndarray:
        try:
            source = np.asarray(
                values,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "Depth input must be numeric."
            ) from exc

        if source.ndim != 2:
            raise ValueError(
                "Depth input must be two-dimensional."
            )

        if source.size == 0:
            raise ValueError(
                "Depth input must not be empty."
            )

        if not np.isfinite(source).all():
            raise ValueError(
                "Depth input contains non-finite values."
            )

        return source.copy()
