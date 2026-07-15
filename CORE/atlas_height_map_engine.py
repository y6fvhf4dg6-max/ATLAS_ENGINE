from __future__ import annotations

from typing import Any

import numpy as np


class AtlasHeightMapEngine:
    """
    ATLAS Height Map Engine v0.2

    Converts numeric image-like input into a deterministic,
    normalized height field suitable for relief geometry.

    Supported operations:
    - two-dimensional numeric arrays
    - finite-value validation
    - normalization to 0.0..1.0
    - optional inversion
    - dependency-free Gaussian smoothing
    - deterministic float64 output
    """

    @staticmethod
    def normalize(
        values: Any,
        *,
        invert: bool = False,
    ) -> np.ndarray:
        height_map = AtlasHeightMapEngine._as_valid_array(
            values
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

    @staticmethod
    def smooth_gaussian(
        values: Any,
        *,
        sigma: float = 1.0,
        radius: int | None = None,
    ) -> np.ndarray:
        """
        Applies deterministic separable Gaussian smoothing.

        Edge handling uses reflected padding so the outer
        relief border is not artificially pulled toward zero.
        """

        height_map = AtlasHeightMapEngine._as_valid_array(
            values
        )

        if not np.isfinite(sigma):
            raise ValueError(
                "sigma must be finite."
            )

        if sigma <= 0.0:
            raise ValueError(
                "sigma must be greater than zero."
            )

        if radius is None:
            radius = max(
                1,
                int(np.ceil(3.0 * sigma)),
            )

        if isinstance(radius, bool):
            raise ValueError(
                "radius must be an integer."
            )

        try:
            radius_integer = int(radius)
        except (TypeError, ValueError) as error:
            raise ValueError(
                "radius must be an integer."
            ) from error

        if radius_integer != radius:
            raise ValueError(
                "radius must be an integer."
            )

        if radius_integer < 1:
            raise ValueError(
                "radius must be at least one."
            )

        coordinates = np.arange(
            -radius_integer,
            radius_integer + 1,
            dtype=np.float64,
        )

        kernel = np.exp(
            -0.5
            * (
                coordinates
                / float(sigma)
            )
            ** 2
        )

        kernel_sum = float(kernel.sum())

        if kernel_sum <= 0.0:
            raise ValueError(
                "Gaussian kernel could not be created."
            )

        kernel /= kernel_sum

        smoothed_x = (
            AtlasHeightMapEngine
            ._convolve_axis(
                height_map,
                kernel=kernel,
                axis=1,
                radius=radius_integer,
            )
        )

        smoothed_xy = (
            AtlasHeightMapEngine
            ._convolve_axis(
                smoothed_x,
                kernel=kernel,
                axis=0,
                radius=radius_integer,
            )
        )

        return smoothed_xy.astype(
            np.float64,
            copy=False,
        )

    @staticmethod
    def _as_valid_array(
        values: Any,
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

        return height_map

    @staticmethod
    def _convolve_axis(
        values: np.ndarray,
        *,
        kernel: np.ndarray,
        axis: int,
        radius: int,
    ) -> np.ndarray:
        padding = [
            (0, 0),
            (0, 0),
        ]

        padding[axis] = (
            radius,
            radius,
        )

        padded = np.pad(
            values,
            padding,
            mode="reflect",
        )

        result = np.empty_like(
            values,
            dtype=np.float64,
        )

        if axis == 1:
            for row in range(values.shape[0]):
                for column in range(
                    values.shape[1]
                ):
                    window = padded[
                        row,
                        column:
                        column + len(kernel),
                    ]

                    result[row, column] = float(
                        np.dot(
                            window,
                            kernel,
                        )
                    )
        elif axis == 0:
            for row in range(values.shape[0]):
                for column in range(
                    values.shape[1]
                ):
                    window = padded[
                        row:
                        row + len(kernel),
                        column,
                    ]

                    result[row, column] = float(
                        np.dot(
                            window,
                            kernel,
                        )
                    )
        else:
            raise ValueError(
                "Only axis 0 and axis 1 are supported."
            )

        return result
