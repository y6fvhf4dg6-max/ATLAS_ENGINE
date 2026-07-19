from __future__ import annotations

import math
from typing import Any

import numpy as np


class AtlasReliefLayerSeparator:
    """
    Maps one normalized depth field into separate
    foreground and background depth ranges.

    The subject mask may be binary or soft. Soft mask
    values blend between the two mapped layer depths.
    """

    DEFAULT_BACKGROUND_RANGE = (
        0.0,
        0.40,
    )
    DEFAULT_FOREGROUND_RANGE = (
        0.60,
        1.0,
    )

    @staticmethod
    def separate(
        depth: Any,
        subject_mask: Any,
        *,
        background_range: Any = (
            DEFAULT_BACKGROUND_RANGE
        ),
        foreground_range: Any = (
            DEFAULT_FOREGROUND_RANGE
        ),
    ) -> dict[str, Any]:
        depth_array = (
            AtlasReliefLayerSeparator
            ._as_valid_array(
                depth,
                name="depth",
            )
        )

        mask_array = (
            AtlasReliefLayerSeparator
            ._as_valid_array(
                subject_mask,
                name="subject_mask",
            )
        )

        if depth_array.shape != mask_array.shape:
            raise ValueError(
                "depth and subject_mask must have "
                "the same shape."
            )

        if (
            depth_array.min() < 0.0
            or depth_array.max() > 1.0
        ):
            raise ValueError(
                "depth values must be within the "
                "0.0..1.0 range."
            )

        if (
            mask_array.min() < 0.0
            or mask_array.max() > 1.0
        ):
            raise ValueError(
                "subject_mask values must be within "
                "the 0.0..1.0 range."
            )

        background = (
            AtlasReliefLayerSeparator
            ._validate_range(
                background_range,
                name="background_range",
            )
        )

        foreground = (
            AtlasReliefLayerSeparator
            ._validate_range(
                foreground_range,
                name="foreground_range",
            )
        )

        if background[1] >= foreground[0]:
            raise ValueError(
                "background_range must end below "
                "foreground_range."
            )

        background_depth = (
            background[0]
            + depth_array
            * (
                background[1]
                - background[0]
            )
        )

        foreground_depth = (
            foreground[0]
            + depth_array
            * (
                foreground[1]
                - foreground[0]
            )
        )

        separated_depth = (
            background_depth
            * (1.0 - mask_array)
            + foreground_depth
            * mask_array
        )

        separated_depth = np.clip(
            separated_depth,
            0.0,
            1.0,
        ).astype(
            np.float64,
            copy=True,
        )

        return {
            "type": "relief_layer_separation",
            "background_range": background,
            "foreground_range": foreground,
            "background_depth": (
                background_depth.astype(
                    np.float64,
                    copy=True,
                )
            ),
            "foreground_depth": (
                foreground_depth.astype(
                    np.float64,
                    copy=True,
                )
            ),
            "subject_mask": mask_array.copy(),
            "separated_depth": separated_depth,
        }

    @staticmethod
    def _validate_range(
        value: Any,
        *,
        name: str,
    ) -> tuple[float, float]:
        if (
            not isinstance(
                value,
                (
                    tuple,
                    list,
                ),
            )
            or len(value) != 2
        ):
            raise ValueError(
                f"{name} must contain exactly "
                "two numeric values."
            )

        lower = (
            AtlasReliefLayerSeparator
            ._as_finite_number(
                value[0],
                name=f"{name}[0]",
            )
        )

        upper = (
            AtlasReliefLayerSeparator
            ._as_finite_number(
                value[1],
                name=f"{name}[1]",
            )
        )

        if (
            lower < 0.0
            or upper > 1.0
        ):
            raise ValueError(
                f"{name} values must be within "
                "the 0.0..1.0 range."
            )

        if lower >= upper:
            raise ValueError(
                f"{name} lower bound must be "
                "lower than its upper bound."
            )

        return (
            lower,
            upper,
        )

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
        *,
        name: str,
    ) -> np.ndarray:
        try:
            array = np.asarray(
                values,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if array.ndim != 2:
            raise ValueError(
                f"{name} must be two-dimensional."
            )

        if array.size == 0:
            raise ValueError(
                f"{name} must not be empty."
            )

        if not np.isfinite(array).all():
            raise ValueError(
                f"{name} contains non-finite values."
            )

        return array.copy()
