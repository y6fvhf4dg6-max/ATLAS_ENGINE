from __future__ import annotations

import math
from typing import Any

import numpy as np

from CORE.atlas_height_map_engine import (
    AtlasHeightMapEngine,
)


class AtlasReliefMultiscaleDecomposer:
    """
    Separates image-like numeric data into deterministic
    low-, mid- and high-frequency bands.

    Bands:
    - form: broad low-frequency structure
    - detail: medium-frequency structure
    - micro_detail: high-frequency residual

    The bands reconstruct the original input exactly
    within floating-point precision.
    """

    @staticmethod
    def decompose(
        values: Any,
        *,
        form_sigma: float,
        detail_sigma: float,
    ) -> dict[str, Any]:
        form_sigma_value = (
            AtlasReliefMultiscaleDecomposer
            ._validate_sigma(
                form_sigma,
                name="form_sigma",
            )
        )

        detail_sigma_value = (
            AtlasReliefMultiscaleDecomposer
            ._validate_sigma(
                detail_sigma,
                name="detail_sigma",
            )
        )

        if (
            detail_sigma_value
            >= form_sigma_value
        ):
            raise ValueError(
                "detail_sigma must be lower than "
                "form_sigma."
            )

        source = (
            AtlasReliefMultiscaleDecomposer
            ._as_valid_array(values)
        )

        form = AtlasHeightMapEngine.smooth_gaussian(
            source,
            sigma=form_sigma_value,
        )

        detail_scale = (
            AtlasHeightMapEngine.smooth_gaussian(
                source,
                sigma=detail_sigma_value,
            )
        )

        detail = detail_scale - form
        micro_detail = source - detail_scale

        return {
            "type": "relief_multiscale_decomposition",
            "form_sigma": form_sigma_value,
            "detail_sigma": detail_sigma_value,
            "form": form.astype(
                np.float64,
                copy=True,
            ),
            "detail": detail.astype(
                np.float64,
                copy=True,
            ),
            "micro_detail": micro_detail.astype(
                np.float64,
                copy=True,
            ),
        }

    @staticmethod
    def _validate_sigma(
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

        if numeric_value <= 0.0:
            raise ValueError(
                f"{name} must be greater than zero."
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
                "Multiscale input must be numeric."
            ) from exc

        if source.ndim != 2:
            raise ValueError(
                "Multiscale input must be "
                "two-dimensional."
            )

        if source.size == 0:
            raise ValueError(
                "Multiscale input must not be empty."
            )

        if not np.isfinite(source).all():
            raise ValueError(
                "Multiscale input contains "
                "non-finite values."
            )

        return source.copy()
