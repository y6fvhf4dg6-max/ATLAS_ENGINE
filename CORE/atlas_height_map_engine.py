from __future__ import annotations

from typing import Any

import numpy as np


class AtlasHeightMapEngine:
    """
    ATLAS Height Map Engine v0.1

    Converts numeric image-like input into a deterministic,
    normalized height field suitable for relief geometry.

    Initial scope:
    - two-dimensional numeric arrays
    - finite-value validation
    - normalization to 0.0..1.0
    - optional inversion
    - deterministic float64 output
    """

    @staticmethod
    def normalize(
        values: Any,
        *,
        invert: bool = False,
    ) -> np.ndarray:
        height_map = np.asarray(
            values,
            dtype=np.float64,
        )

        if height_map.ndim != 2:
            raise ValueError(
                "Height-map input must be a "
                "two-dimensional array."
            )

        if height_map.size == 0:
            raise ValueError(
                "Height-map input must not be empty."
            )

        if not np.isfinite(height_map).all():
            raise ValueError(
                "Height-map input contains "
                "non-finite values."
            )

        minimum = float(height_map.min())
        maximum = float(height_map.max())
        value_range = maximum - minimum

        if value_range <= 0.0:
            normalized = np.zeros_like(
                height_map,
                dtype=np.float64,
            )
        else:
            normalized = (
                height_map - minimum
            ) / value_range

        if invert:
            normalized = 1.0 - normalized

        return normalized.astype(
            np.float64,
            copy=False,
        )
