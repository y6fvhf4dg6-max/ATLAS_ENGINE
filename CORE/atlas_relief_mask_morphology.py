from __future__ import annotations

from typing import Any

import numpy as np


class AtlasReliefMaskMorphology:
    SUPPORTED_OPERATIONS = {
        "dilate",
        "erode",
        "open",
        "close",
    }

    @staticmethod
    def apply(
        mask: Any,
        *,
        operation: str,
        radius: int,
        threshold: float = 0.5,
    ) -> dict:
        source_mask = np.asarray(
            mask,
            dtype=np.float64,
        )

        AtlasReliefMaskMorphology._validate_mask(
            source_mask
        )

        validated_operation = (
            AtlasReliefMaskMorphology
            ._validate_operation(operation)
        )
        validated_radius = (
            AtlasReliefMaskMorphology
            ._validate_radius(radius)
        )
        validated_threshold = (
            AtlasReliefMaskMorphology
            ._validate_threshold(threshold)
        )

        binary_mask = (
            source_mask >= validated_threshold
        ).astype(
            np.float64,
            copy=False,
        )

        if validated_radius == 0:
            processed_mask = binary_mask.copy()
        elif validated_operation == "dilate":
            processed_mask = (
                AtlasReliefMaskMorphology
                ._dilate(
                    binary_mask,
                    radius=validated_radius,
                )
            )
        elif validated_operation == "erode":
            processed_mask = (
                AtlasReliefMaskMorphology
                ._erode(
                    binary_mask,
                    radius=validated_radius,
                )
            )
        elif validated_operation == "open":
            eroded = (
                AtlasReliefMaskMorphology
                ._erode(
                    binary_mask,
                    radius=validated_radius,
                )
            )
            processed_mask = (
                AtlasReliefMaskMorphology
                ._dilate(
                    eroded,
                    radius=validated_radius,
                )
            )
        else:
            dilated = (
                AtlasReliefMaskMorphology
                ._dilate(
                    binary_mask,
                    radius=validated_radius,
                )
            )
            processed_mask = (
                AtlasReliefMaskMorphology
                ._erode(
                    dilated,
                    radius=validated_radius,
                )
            )

        return {
            "type": (
                "relief_mask_morphology_result"
            ),
            "operation": validated_operation,
            "radius": validated_radius,
            "threshold": validated_threshold,
            "processed_mask": processed_mask,
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

        if (
            mask.min() < 0.0
            or mask.max() > 1.0
        ):
            raise ValueError(
                "mask values must be within "
                "[0.0, 1.0]."
            )

    @staticmethod
    def _validate_operation(
        operation: Any,
    ) -> str:
        if (
            not isinstance(operation, str)
            or operation
            not in (
                AtlasReliefMaskMorphology
                .SUPPORTED_OPERATIONS
            )
        ):
            raise ValueError(
                "operation must be one of: "
                "dilate, erode, open, close."
            )

        return operation

    @staticmethod
    def _validate_radius(
        radius: Any,
    ) -> int:
        if (
            isinstance(radius, bool)
            or not isinstance(
                radius,
                (int, np.integer),
            )
        ):
            raise ValueError(
                "radius must be a non-negative "
                "integer."
            )

        value = int(radius)

        if value < 0:
            raise ValueError(
                "radius must be a non-negative "
                "integer."
            )

        return value

    @staticmethod
    def _validate_threshold(
        threshold: Any,
    ) -> float:
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
    def _dilate(
        mask: np.ndarray,
        *,
        radius: int,
    ) -> np.ndarray:
        return (
            AtlasReliefMaskMorphology
            ._window_reduce(
                mask,
                radius=radius,
                reducer=np.max,
                padding_value=0.0,
            )
        )

    @staticmethod
    def _erode(
        mask: np.ndarray,
        *,
        radius: int,
    ) -> np.ndarray:
        return (
            AtlasReliefMaskMorphology
            ._window_reduce(
                mask,
                radius=radius,
                reducer=np.min,
                padding_value=0.0,
            )
        )

    @staticmethod
    def _window_reduce(
        mask: np.ndarray,
        *,
        radius: int,
        reducer: Any,
        padding_value: float,
    ) -> np.ndarray:
        kernel_size = 2 * radius + 1

        padded = np.pad(
            mask,
            (
                (radius, radius),
                (radius, radius),
            ),
            mode="constant",
            constant_values=padding_value,
        )

        windows = (
            np.lib.stride_tricks
            .sliding_window_view(
                padded,
                (
                    kernel_size,
                    kernel_size,
                ),
            )
        )

        processed = reducer(
            windows,
            axis=(-2, -1),
        )

        return np.asarray(
            processed,
            dtype=np.float64,
        )
