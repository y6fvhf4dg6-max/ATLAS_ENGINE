from __future__ import annotations

import math
from typing import Any

import numpy as np

from CORE.atlas_portrait_contact_plane_global_gamma_compressor import (
    AtlasPortraitContactPlaneGlobalGammaCompressor,
)
from CORE.atlas_portrait_contact_plane_linear_compressor import (
    AtlasPortraitContactPlaneLinearCompressor,
)
from CORE.atlas_portrait_contact_plane_projection_result import (
    AtlasPortraitContactPlaneProjectionResult,
)


class AtlasPortraitContactPlaneGradientLimitedCompressor:
    """
    Blends global-gamma and linear contact-plane relief
    heights according to local gradient magnitude.

    Low-gradient regions retain the global-gamma surface.
    High-gradient regions move toward the more conservative
    linear surface.

    This limits local gamma amplification without Gaussian
    smoothing, contact-peak renormalization, semantic
    masking, rendering, validity analysis, triangulation,
    or mesh generation.
    """

    DEFAULT_GAMMA = 0.60
    DEFAULT_GRADIENT_PERCENTILE = 70.0
    DEFAULT_BLEND_STRENGTH = 0.60

    COMPRESSION_MODE = (
        "global_gamma_gradient_limited_linear_blend"
    )

    @classmethod
    def compress(
        cls,
        projection: AtlasPortraitContactPlaneProjectionResult,
        *,
        target_maximum_height: float,
        gamma: float = DEFAULT_GAMMA,
        gradient_percentile: float = (
            DEFAULT_GRADIENT_PERCENTILE
        ),
        blend_strength: float = DEFAULT_BLEND_STRENGTH,
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

        percentile_value = cls._normalize_range_float(
            gradient_percentile,
            name="gradient_percentile",
            minimum=0.0,
            maximum=100.0,
        )

        blend_value = cls._normalize_range_float(
            blend_strength,
            name="blend_strength",
            minimum=0.0,
            maximum=1.0,
        )

        linear = (
            AtlasPortraitContactPlaneLinearCompressor
            .compress(
                projection,
                target_maximum_height=target_height,
            )
        )

        global_gamma = (
            AtlasPortraitContactPlaneGlobalGammaCompressor
            .compress(
                projection,
                target_maximum_height=target_height,
                gamma=gamma_value,
            )
        )

        linear_height = np.asarray(
            linear["compressed_height"],
            dtype=np.float64,
        )

        gamma_height = np.asarray(
            global_gamma["compressed_height"],
            dtype=np.float64,
        )

        row_gradient, column_gradient = np.gradient(
            gamma_height,
        )

        gradient_magnitude = np.hypot(
            row_gradient,
            column_gradient,
        ).astype(
            np.float64,
            copy=False,
        )

        gradient_threshold = float(
            np.percentile(
                gradient_magnitude,
                percentile_value,
            )
        )

        maximum_gradient = float(
            gradient_magnitude.max(),
        )

        denominator = (
            maximum_gradient
            - gradient_threshold
        )

        if denominator <= 0.0:
            base_weight = np.zeros_like(
                gradient_magnitude,
                dtype=np.float64,
            )
        else:
            base_weight = np.clip(
                (
                    gradient_magnitude
                    - gradient_threshold
                )
                / denominator,
                0.0,
                1.0,
            ).astype(
                np.float64,
                copy=False,
            )

        gradient_weight = np.clip(
            base_weight * blend_value,
            0.0,
            1.0,
        ).astype(
            np.float64,
            copy=True,
        )

        compressed_height = (
            gamma_height
            * (
                1.0
                - gradient_weight
            )
            + linear_height
            * gradient_weight
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
                "portrait_contact_plane_"
                "gradient_limited_compression"
            ),
            "compression_mode": cls.COMPRESSION_MODE,
            "source_shape": projection.source_shape,
            "source_maximum_height": float(
                projection.maximum_distance,
            ),
            "target_maximum_height": target_height,
            "gamma": gamma_value,
            "gradient_percentile": percentile_value,
            "blend_strength": blend_value,
            "gradient_threshold": (
                gradient_threshold
            ),
            "maximum_gradient": maximum_gradient,
            "gradient_weight": gradient_weight,
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

    @staticmethod
    def _normalize_range_float(
        value: Any,
        *,
        name: str,
        minimum: float,
        maximum: float,
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

        if not (
            minimum
            <= numeric_value
            <= maximum
        ):
            raise ValueError(
                f"{name} must be in the "
                f"{minimum}..{maximum} range."
            )

        return numeric_value
