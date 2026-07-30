from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy.ndimage import gaussian_filter


class AtlasRockReliefIlluminationNormalizer:
    @staticmethod
    def normalize(
        values: Any,
        *,
        illumination_sigma: float = 12.0,
        detail_strength: float = 0.70,
    ) -> np.ndarray:
        image = np.asarray(
            values,
            dtype=np.float64,
        )

        if image.ndim != 2:
            raise ValueError(
                "values must be a two-dimensional array."
            )

        if image.size == 0:
            raise ValueError(
                "values must not be empty."
            )

        if not np.all(np.isfinite(image)):
            raise ValueError(
                "values must contain only finite values."
            )

        try:
            sigma = float(illumination_sigma)
            strength = float(detail_strength)
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "illumination_sigma and detail_strength "
                "must be numeric."
            ) from exc

        if not math.isfinite(sigma) or sigma <= 0.0:
            raise ValueError(
                "illumination_sigma must be greater "
                "than zero."
            )

        if not math.isfinite(strength):
            raise ValueError(
                "detail_strength must be finite."
            )

        if not 0.0 <= strength <= 1.0:
            raise ValueError(
                "detail_strength must be in the "
                "0.0..1.0 range."
            )

        minimum = float(np.min(image))
        maximum = float(np.max(image))

        if maximum <= minimum:
            return np.full_like(
                image,
                0.5,
                dtype=np.float64,
            )

        normalized = (
            image - minimum
        ) / (
            maximum - minimum
        )

        illumination = gaussian_filter(
            normalized,
            sigma=sigma,
            mode="reflect",
        )

        residual = normalized - illumination

        result = (
            0.5
            + strength * residual
        )

        return np.clip(
            result,
            0.0,
            1.0,
        ).astype(
            np.float64,
            copy=False,
        )
