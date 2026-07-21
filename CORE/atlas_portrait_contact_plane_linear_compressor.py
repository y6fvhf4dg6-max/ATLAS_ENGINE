from __future__ import annotations

import math
from typing import Any

import numpy as np

from CORE.atlas_portrait_contact_plane_projection_result import (
    AtlasPortraitContactPlaneProjectionResult,
)


class AtlasPortraitContactPlaneLinearCompressor:
    """
    Linearly compresses contact-plane depth into a target
    maximum relief height.

    Processing:

    - invert contact-plane distance into relief height
    - normalize by the source maximum distance
    - scale to the requested target maximum height

    It performs no nonlinear shaping, percentile clipping,
    gradient preservation, semantic weighting, rendering,
    triangulation, or mesh generation.
    """

    COMPRESSION_MODE = "linear_target_maximum_height"

    @classmethod
    def compress(
        cls,
        projection: AtlasPortraitContactPlaneProjectionResult,
        *,
        target_maximum_height: float,
    ) -> dict[str, object]:
        if not isinstance(
            projection,
            AtlasPortraitContactPlaneProjectionResult,
        ):
            raise TypeError(
                "projection must be an "
                "AtlasPortraitContactPlaneProjectionResult "
                "instance."
            )

        target_height = cls._normalize_target_height(
            target_maximum_height,
        )

        source_maximum_height = float(
            projection.maximum_distance,
        )

        if source_maximum_height <= 0.0:
            linear_scale = 0.0
            compressed_height = np.zeros(
                projection.source_shape,
                dtype=np.float64,
            )
        else:
            linear_scale = (
                target_height
                / source_maximum_height
            )

            full_height = (
                source_maximum_height
                - projection.distance_to_plane
            )

            compressed_height = (
                full_height
                * linear_scale
            ).astype(
                np.float64,
                copy=True,
            )

            compressed_height = np.clip(
                compressed_height,
                0.0,
                target_height,
            ).astype(
                np.float64,
                copy=False,
            )

        return {
            "type": (
                "portrait_contact_plane_linear_compression"
            ),
            "compression_mode": cls.COMPRESSION_MODE,
            "source_shape": projection.source_shape,
            "source_maximum_height": (
                source_maximum_height
            ),
            "target_maximum_height": target_height,
            "linear_scale": float(
                linear_scale,
            ),
            "compressed_height": compressed_height,
        }

    @staticmethod
    def _normalize_target_height(
        value: Any,
    ) -> float:
        try:
            numeric_value = float(
                value,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "target_maximum_height must be numeric."
            ) from exc

        if not math.isfinite(
            numeric_value,
        ):
            raise ValueError(
                "target_maximum_height must be finite."
            )

        if numeric_value <= 0.0:
            raise ValueError(
                "target_maximum_height must be "
                "greater than zero."
            )

        return numeric_value
