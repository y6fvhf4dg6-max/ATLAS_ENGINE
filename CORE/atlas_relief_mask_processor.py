from __future__ import annotations

from typing import Any

import numpy as np


class AtlasReliefMaskProcessor:
    @staticmethod
    def process(
        mask: Any,
        *,
        threshold: float | None = None,
        feather_sigma: float = 0.0,
    ) -> dict:
        source_mask = np.asarray(
            mask,
            dtype=np.float64,
        )

        AtlasReliefMaskProcessor._validate_mask(
            source_mask
        )

        validated_threshold = (
            AtlasReliefMaskProcessor
            ._validate_threshold(threshold)
        )
        validated_sigma = (
            AtlasReliefMaskProcessor
            ._validate_feather_sigma(
                feather_sigma
            )
        )

        processed_mask = np.clip(
            source_mask,
            0.0,
            1.0,
        ).copy()

        if validated_threshold is not None:
            processed_mask = (
                processed_mask
                >= validated_threshold
            ).astype(
                np.float64,
                copy=False,
            )

        if validated_sigma > 0.0:
            processed_mask = (
                AtlasReliefMaskProcessor
                ._gaussian_blur(
                    processed_mask,
                    sigma=validated_sigma,
                )
            )

        processed_mask = np.clip(
            processed_mask,
            0.0,
            1.0,
        )

        return {
            "type": (
                "relief_mask_processing_result"
            ),
            "processed_mask": processed_mask,
            "threshold": validated_threshold,
            "feather_sigma": validated_sigma,
        }

    @staticmethod
    def _validate_mask(
        mask: np.ndarray,
    ) -> None:
        if mask.ndim != 2:
            raise ValueError(
                "mask must be a two-dimensional "
                "array."
            )

        if mask.size == 0:
            raise ValueError(
                "mask cannot be empty."
            )

        if not np.all(np.isfinite(mask)):
            raise ValueError(
                "mask must contain only finite "
                "values."
            )

    @staticmethod
    def _validate_threshold(
        threshold: float | None,
    ) -> float | None:
        if threshold is None:
            return None

        value = float(threshold)

        if (
            not np.isfinite(value)
            or value < 0.0
            or value > 1.0
        ):
            raise ValueError(
                "threshold must be finite and "
                "within [0.0, 1.0]."
            )

        return value

    @staticmethod
    def _validate_feather_sigma(
        feather_sigma: float,
    ) -> float:
        value = float(feather_sigma)

        if (
            not np.isfinite(value)
            or value < 0.0
        ):
            raise ValueError(
                "feather_sigma must be finite "
                "and non-negative."
            )

        return value

    @staticmethod
    def _gaussian_blur(
        mask: np.ndarray,
        *,
        sigma: float,
    ) -> np.ndarray:
        radius = max(
            1,
            int(np.ceil(3.0 * sigma)),
        )

        coordinates = np.arange(
            -radius,
            radius + 1,
            dtype=np.float64,
        )

        kernel = np.exp(
            -0.5
            * np.square(
                coordinates / sigma
            )
        )
        kernel /= np.sum(kernel)

        horizontal = (
            AtlasReliefMaskProcessor
            ._convolve_axis(
                mask,
                kernel=kernel,
                axis=1,
            )
        )

        return (
            AtlasReliefMaskProcessor
            ._convolve_axis(
                horizontal,
                kernel=kernel,
                axis=0,
            )
        )

    @staticmethod
    def _convolve_axis(
        values: np.ndarray,
        *,
        kernel: np.ndarray,
        axis: int,
    ) -> np.ndarray:
        radius = kernel.size // 2

        padding = (
            ((0, 0), (radius, radius))
            if axis == 1
            else ((radius, radius), (0, 0))
        )

        padded = np.pad(
            values,
            padding,
            mode="edge",
        )

        result = np.empty_like(
            values,
            dtype=np.float64,
        )

        if axis == 1:
            for row_index in range(
                values.shape[0]
            ):
                result[row_index, :] = (
                    np.convolve(
                        padded[row_index, :],
                        kernel,
                        mode="valid",
                    )
                )
        else:
            for column_index in range(
                values.shape[1]
            ):
                result[:, column_index] = (
                    np.convolve(
                        padded[:, column_index],
                        kernel,
                        mode="valid",
                    )
                )

        return result
