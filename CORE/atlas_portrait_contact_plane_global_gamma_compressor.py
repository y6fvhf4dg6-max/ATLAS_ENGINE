from __future__ import annotations

import math
from typing import Any

import numpy as np

from CORE.atlas_portrait_contact_plane_projection_result import (
    AtlasPortraitContactPlaneProjectionResult,
)
from CORE.atlas_relief_depth_compressor import (
    AtlasReliefDepthCompressor,
)


class AtlasPortraitContactPlaneGlobalGammaCompressor:
    """
    Applies deterministic global gamma shaping to a
    portrait contact-plane relief-height field.

    Processing:
    - invert contact-plane distance into source height
    - normalize through AtlasReliefDepthCompressor
    - apply global gamma shaping without percentile clipping
    - scale normalized output to a physical target height

    It performs no feature-sensitive weighting, local
    gradient preservation, semantic masking, rendering,
    validity analysis, triangulation, or mesh generation.
    """

    DEFAULT_GAMMA = 0.60

    LOWER_PERCENTILE = 0.0
    UPPER_PERCENTILE = 100.0

    COMPRESSION_MODE = (
        "global_gamma_target_maximum_height"
    )

    @classmethod
    def compress(
        cls,
        projection: AtlasPortraitContactPlaneProjectionResult,
        *,
        target_maximum_height: float,
        gamma: float = DEFAULT_GAMMA,
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

        target_height = cls._normalize_positive_float(
            target_maximum_height,
            name="target_maximum_height",
        )

        gamma_value = cls._normalize_positive_float(
            gamma,
            name="gamma",
        )

        source_maximum_height = float(
            projection.maximum_distance,
        )

        source_height = (
            source_maximum_height
            - projection.distance_to_plane
        ).astype(
            np.float64,
            copy=True,
        )

        source_height = np.clip(
            source_height,
            0.0,
            source_maximum_height,
        ).astype(
            np.float64,
            copy=False,
        )

        nonlinear = AtlasReliefDepthCompressor.compress(
            source_height,
            lower_percentile=cls.LOWER_PERCENTILE,
            upper_percentile=cls.UPPER_PERCENTILE,
            gamma=gamma_value,
        )

        compressed_height = (
            nonlinear["compressed_depth"]
            * target_height
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
                "portrait_contact_plane_global_gamma_compression"
            ),
            "compression_mode": cls.COMPRESSION_MODE,
            "source_shape": projection.source_shape,
            "source_maximum_height": (
                source_maximum_height
            ),
            "target_maximum_height": target_height,
            "gamma": gamma_value,
            "lower_percentile": cls.LOWER_PERCENTILE,
            "upper_percentile": cls.UPPER_PERCENTILE,
            "lower_bound": float(
                nonlinear["lower_bound"],
            ),
            "upper_bound": float(
                nonlinear["upper_bound"],
            ),
            "compressed_height": compressed_height,
        }

    @staticmethod
    def _normalize_positive_float(
        value: Any,
        *,
        name: str,
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
                f"{name} must be numeric."
            ) from exc

        if not math.isfinite(
            numeric_value,
        ):
            raise ValueError(
                f"{name} must be finite."
            )

        if numeric_value <= 0.0:
            raise ValueError(
                f"{name} must be greater than zero."
            )

        return numeric_value
