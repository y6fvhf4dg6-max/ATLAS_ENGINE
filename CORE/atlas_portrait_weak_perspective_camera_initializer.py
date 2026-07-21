from __future__ import annotations

import math

import numpy as np

from CORE.atlas_portrait_weak_perspective_camera import (
    AtlasPortraitWeakPerspectiveCamera,
)
from CORE.atlas_portrait_weak_perspective_fitting_input import (
    AtlasPortraitWeakPerspectiveFittingInput,
)


class AtlasPortraitWeakPerspectiveCameraInitializer:
    """
    Initializes a deterministic no-rotation
    weak-perspective portrait camera.

    The initializer solves the weighted model:

        u = scale * x + translation_x
        v = scale * y + translation_y

    using canonical source landmark X/Y coordinates and
    normalized target image coordinates.

    It performs no rotation or pose fitting, nonlinear
    optimization, FLAME parameter fitting, mesh
    deformation, frontal normalization, rendering,
    relief compression, or STL generation.
    """

    _MINIMUM_SOURCE_SPREAD = 1.0e-15

    @classmethod
    def initialize(
        cls,
        fitting_input: (
            AtlasPortraitWeakPerspectiveFittingInput
        ),
    ) -> AtlasPortraitWeakPerspectiveCamera:
        if not isinstance(
            fitting_input,
            AtlasPortraitWeakPerspectiveFittingInput,
        ):
            raise TypeError(
                "fitting_input must be an "
                "AtlasPortraitWeakPerspectiveFittingInput "
                "instance."
            )

        source_points_2d = (
            fitting_input.source_points_3d[
                :,
                :2,
            ]
        )

        target_points_2d = (
            fitting_input.target_points_2d
        )

        weights = fitting_input.landmark_weights

        weight_sum = float(
            np.sum(
                weights,
                dtype=np.float64,
            )
        )

        source_centroid = cls._weighted_centroid(
            source_points_2d,
            weights=weights,
            weight_sum=weight_sum,
        )

        target_centroid = cls._weighted_centroid(
            target_points_2d,
            weights=weights,
            weight_sum=weight_sum,
        )

        centered_source = (
            source_points_2d
            - source_centroid
        )

        centered_target = (
            target_points_2d
            - target_centroid
        )

        source_spread = float(
            np.sum(
                weights[
                    :,
                    np.newaxis,
                ]
                * centered_source
                * centered_source,
                dtype=np.float64,
            )
        )

        if (
            not math.isfinite(
                source_spread,
            )
            or source_spread
            <= cls._MINIMUM_SOURCE_SPREAD
        ):
            raise ValueError(
                "Cannot initialize weak-perspective "
                "camera because source spread is "
                "degenerate."
            )

        weighted_covariance = float(
            np.sum(
                weights[
                    :,
                    np.newaxis,
                ]
                * centered_source
                * centered_target,
                dtype=np.float64,
            )
        )

        scale = (
            weighted_covariance
            / source_spread
        )

        if (
            not math.isfinite(
                scale,
            )
            or scale <= 0.0
        ):
            raise ValueError(
                "Weak-perspective initialization must "
                "produce a positive scale."
            )

        translation = (
            target_centroid
            - scale * source_centroid
        )

        projected_points_2d = (
            scale * source_points_2d
            + translation
        )

        residuals = (
            projected_points_2d
            - target_points_2d
        )

        weighted_squared_error = float(
            np.sum(
                weights[
                    :,
                    np.newaxis,
                ]
                * residuals
                * residuals,
                dtype=np.float64,
            )
        )

        weighted_root_mean_square_error = math.sqrt(
            weighted_squared_error
            / weight_sum
        )

        return AtlasPortraitWeakPerspectiveCamera(
            scale=scale,
            translation_x=float(
                translation[
                    0
                ]
            ),
            translation_y=float(
                translation[
                    1
                ]
            ),
            projected_points_2d=projected_points_2d,
            weighted_root_mean_square_error=(
                weighted_root_mean_square_error
            ),
            metadata=cls._build_metadata(
                fitting_input,
            ),
        )

    @staticmethod
    def _weighted_centroid(
        points: np.ndarray,
        *,
        weights: np.ndarray,
        weight_sum: float,
    ) -> np.ndarray:
        return (
            np.sum(
                weights[
                    :,
                    np.newaxis,
                ]
                * points,
                axis=0,
                dtype=np.float64,
            )
            / weight_sum
        )

    @staticmethod
    def _build_metadata(
        fitting_input: (
            AtlasPortraitWeakPerspectiveFittingInput
        ),
    ) -> dict[str, object]:
        source_metadata = fitting_input.metadata

        return {
            "camera_model": "weak_perspective",
            "initialization_method": (
                "weighted_similarity_no_rotation"
            ),
            "input_view": source_metadata.get(
                "input_view",
            ),
            "landmark_count": (
                fitting_input.landmark_count
            ),
            "model_family": source_metadata.get(
                "model_family",
            ),
            "portrait_fixture": source_metadata.get(
                "portrait_fixture",
            ),
            "synthetic": source_metadata.get(
                "synthetic",
            ),
        }
