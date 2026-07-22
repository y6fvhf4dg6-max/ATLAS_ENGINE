from __future__ import annotations

import math
from numbers import Integral
from typing import Any

import numpy as np

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)
from CORE.atlas_portrait_flame_dense_identity_pipeline_result import (
    AtlasPortraitFlameDenseIdentityPipelineResult,
)
from CORE.atlas_portrait_flame_identity_fitter import (
    AtlasPortraitFlameIdentityFitter,
)
from CORE.atlas_portrait_flame_root_pose_fitter import (
    AtlasPortraitFlameRootPoseFitter,
)
from CORE.atlas_portrait_indexed_landmark_result import (
    AtlasPortraitIndexedLandmarkResult,
)
from CORE.atlas_portrait_landmark_result import (
    AtlasPortraitLandmarkResult,
)


class AtlasPortraitFlameDenseIdentityPipeline:
    """
    Orchestrates staged FLAME portrait fitting.

    The pipeline:

    1. fits the three-component root pose using the named
       landmark result,
    2. keeps that root pose fixed,
    3. fits a bounded prefix of FLAME identity parameters
       using the indexed dense landmark result,
    4. returns an immutable combined pipeline result.

    The class introduces no new deformation, projection,
    optimization, rendering, relief, or STL mathematics.
    """

    DEFAULT_ANGLE_LIMIT_DEGREES = (
        AtlasPortraitFlameRootPoseFitter
        .DEFAULT_ANGLE_LIMIT_DEGREES
    )
    DEFAULT_ROOT_MAXIMUM_FUNCTION_EVALUATIONS = (
        AtlasPortraitFlameRootPoseFitter
        .DEFAULT_MAXIMUM_FUNCTION_EVALUATIONS
    )
    DEFAULT_ACTIVE_IDENTITY_COUNT = (
        AtlasPortraitFlameIdentityFitter
        .DEFAULT_ACTIVE_IDENTITY_COUNT
    )
    DEFAULT_REGULARIZATION_WEIGHT = (
        AtlasPortraitFlameIdentityFitter
        .DEFAULT_REGULARIZATION_WEIGHT
    )
    DEFAULT_IDENTITY_PARAMETER_LIMIT = (
        AtlasPortraitFlameIdentityFitter
        .DEFAULT_IDENTITY_PARAMETER_LIMIT
    )
    DEFAULT_IDENTITY_MAXIMUM_FUNCTION_EVALUATIONS = (
        AtlasPortraitFlameIdentityFitter
        .DEFAULT_MAXIMUM_FUNCTION_EVALUATIONS
    )

    @classmethod
    def fit(
        cls,
        model: AtlasPortraitFlameCanonicalModel,
        *,
        named_landmark_result: AtlasPortraitLandmarkResult,
        indexed_landmark_result: (
            AtlasPortraitIndexedLandmarkResult
        ),
        landmark_indices: Any,
        landmark_face_indices: Any,
        landmark_barycentric_coordinates: Any,
        root_landmark_weights: Any = None,
        identity_landmark_weights: Any = None,
        angle_limit_degrees: Any = (
            DEFAULT_ANGLE_LIMIT_DEGREES
        ),
        root_maximum_function_evaluations: Any = (
            DEFAULT_ROOT_MAXIMUM_FUNCTION_EVALUATIONS
        ),
        active_identity_count: Any = (
            DEFAULT_ACTIVE_IDENTITY_COUNT
        ),
        regularization_weight: Any = (
            DEFAULT_REGULARIZATION_WEIGHT
        ),
        identity_parameter_limit: Any = (
            DEFAULT_IDENTITY_PARAMETER_LIMIT
        ),
        identity_maximum_function_evaluations: Any = (
            DEFAULT_IDENTITY_MAXIMUM_FUNCTION_EVALUATIONS
        ),
    ) -> AtlasPortraitFlameDenseIdentityPipelineResult:
        if not isinstance(
            model,
            AtlasPortraitFlameCanonicalModel,
        ):
            raise TypeError(
                "model must be an "
                "AtlasPortraitFlameCanonicalModel instance."
            )

        if not isinstance(
            named_landmark_result,
            AtlasPortraitLandmarkResult,
        ):
            raise TypeError(
                "named_landmark_result must be an "
                "AtlasPortraitLandmarkResult instance."
            )

        if not isinstance(
            indexed_landmark_result,
            AtlasPortraitIndexedLandmarkResult,
        ):
            raise TypeError(
                "indexed_landmark_result must be an "
                "AtlasPortraitIndexedLandmarkResult instance."
            )

        normalized_angle_limit = (
            cls._normalize_positive_float(
                angle_limit_degrees,
                name="angle_limit_degrees",
            )
        )

        normalized_root_maximum_evaluations = (
            cls._normalize_positive_integer(
                root_maximum_function_evaluations,
                name=(
                    "root_maximum_function_evaluations"
                ),
            )
        )

        normalized_active_identity_count = (
            cls._normalize_positive_integer(
                active_identity_count,
                name="active_identity_count",
            )
        )

        if (
            normalized_active_identity_count
            > model.identity_parameter_count
        ):
            raise ValueError(
                "active_identity_count must not exceed "
                "the model identity parameter count."
            )

        normalized_regularization_weight = (
            cls._normalize_nonnegative_float(
                regularization_weight,
                name="regularization_weight",
            )
        )

        normalized_identity_parameter_limit = (
            cls._normalize_positive_float(
                identity_parameter_limit,
                name="identity_parameter_limit",
            )
        )

        normalized_identity_maximum_evaluations = (
            cls._normalize_positive_integer(
                identity_maximum_function_evaluations,
                name=(
                    "identity_maximum_function_evaluations"
                ),
            )
        )

        embedding_landmark_indices = (
            cls._normalize_unique_nonnegative_integer_vector(
                landmark_indices,
                name="landmark_indices",
            )
        )

        embedding_face_indices = (
            cls._normalize_integer_vector(
                landmark_face_indices,
                name="landmark_face_indices",
            )
        )

        embedding_barycentric_coordinates = (
            cls._normalize_barycentric_coordinates(
                landmark_barycentric_coordinates
            )
        )

        embedding_count = int(
            embedding_landmark_indices.shape[0]
        )

        if (
            embedding_face_indices.shape[0]
            != embedding_count
            or embedding_barycentric_coordinates.shape[0]
            != embedding_count
        ):
            raise ValueError(
                "FLAME embedding arrays must have "
                "matching lengths."
            )

        requested_mediapipe_ids = tuple(
            int(
                value
            )
            for value in embedding_landmark_indices
        )

        root_pose_result = (
            AtlasPortraitFlameRootPoseFitter.fit(
                model,
                landmark_result=named_landmark_result,
                landmark_indices=(
                    embedding_landmark_indices.copy()
                ),
                landmark_face_indices=(
                    embedding_face_indices.copy()
                ),
                landmark_barycentric_coordinates=(
                    embedding_barycentric_coordinates.copy()
                ),
                landmark_weights=root_landmark_weights,
                angle_limit_degrees=(
                    normalized_angle_limit
                ),
                maximum_function_evaluations=(
                    normalized_root_maximum_evaluations
                ),
            )
        )

        identity_fit_result = (
            AtlasPortraitFlameIdentityFitter.fit(
                model,
                landmark_result=indexed_landmark_result,
                landmark_indices=(
                    embedding_landmark_indices.copy()
                ),
                landmark_face_indices=(
                    embedding_face_indices.copy()
                ),
                landmark_barycentric_coordinates=(
                    embedding_barycentric_coordinates.copy()
                ),
                requested_mediapipe_ids=(
                    requested_mediapipe_ids
                ),
                root_pose_parameters=(
                    root_pose_result
                    .root_pose_parameters
                    .copy()
                ),
                landmark_weights=(
                    identity_landmark_weights
                ),
                active_identity_count=(
                    normalized_active_identity_count
                ),
                regularization_weight=(
                    normalized_regularization_weight
                ),
                identity_parameter_limit=(
                    normalized_identity_parameter_limit
                ),
                maximum_function_evaluations=(
                    normalized_identity_maximum_evaluations
                ),
            )
        )

        return AtlasPortraitFlameDenseIdentityPipelineResult(
            root_pose_result=root_pose_result,
            identity_fit_result=identity_fit_result,
            metadata={
                "dense_landmark_count": (
                    indexed_landmark_result.landmark_count
                ),
                "model_family": "flame",
                "model_version": model.metadata.get(
                    "model_version"
                ),
                "pipeline": "flame_dense_identity",
                "root_landmark_count": len(
                    named_landmark_result.landmarks
                ),
                "synthetic": model.metadata.get(
                    "synthetic"
                ),
            },
        )

    @staticmethod
    def _normalize_nonnegative_float(
        value: Any,
        *,
        name: str,
    ) -> float:
        if isinstance(
            value,
            (
                bool,
                np.bool_,
            ),
        ):
            raise ValueError(
                f"{name} must be numeric."
            )

        try:
            normalized = float(
                value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if not math.isfinite(
            normalized
        ):
            raise ValueError(
                f"{name} must be finite."
            )

        if normalized < 0.0:
            raise ValueError(
                f"{name} must be nonnegative."
            )

        return normalized

    @classmethod
    def _normalize_positive_float(
        cls,
        value: Any,
        *,
        name: str,
    ) -> float:
        normalized = cls._normalize_nonnegative_float(
            value,
            name=name,
        )

        if normalized <= 0.0:
            raise ValueError(
                f"{name} must be greater than zero."
            )

        return normalized

    @staticmethod
    def _normalize_positive_integer(
        value: Any,
        *,
        name: str,
    ) -> int:
        if isinstance(
            value,
            (
                bool,
                np.bool_,
            ),
        ):
            raise ValueError(
                f"{name} must be an integer."
            )

        try:
            numeric_value = float(
                value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be an integer."
            ) from exc

        if (
            not math.isfinite(
                numeric_value
            )
            or not numeric_value.is_integer()
        ):
            raise ValueError(
                f"{name} must be an integer."
            )

        normalized = int(
            numeric_value
        )

        if normalized <= 0:
            raise ValueError(
                f"{name} must be greater than zero."
            )

        return normalized

    @classmethod
    def _normalize_unique_nonnegative_integer_vector(
        cls,
        value: Any,
        *,
        name: str,
    ) -> np.ndarray:
        result = cls._normalize_integer_vector(
            value,
            name=name,
        )

        if result.shape[0] < 1:
            raise ValueError(
                f"{name} must not be empty."
            )

        if np.any(
            result < 0
        ):
            raise ValueError(
                f"{name} must not contain negative values."
            )

        if len(
            set(
                result.tolist()
            )
        ) != result.shape[0]:
            raise ValueError(
                f"{name} must contain unique values."
            )

        return result

    @staticmethod
    def _normalize_integer_vector(
        value: Any,
        *,
        name: str,
    ) -> np.ndarray:
        try:
            numeric = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if numeric.ndim != 1:
            raise ValueError(
                f"{name} must be one-dimensional."
            )

        if not np.isfinite(
            numeric
        ).all():
            raise ValueError(
                f"{name} contains non-finite values."
            )

        if not np.equal(
            numeric,
            np.rint(
                numeric
            ),
        ).all():
            raise ValueError(
                f"{name} must contain integer values."
            )

        return numeric.astype(
            np.int64,
            copy=True,
        )

    @staticmethod
    def _normalize_barycentric_coordinates(
        value: Any,
    ) -> np.ndarray:
        try:
            result = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "landmark_barycentric_coordinates "
                "must be numeric."
            ) from exc

        if (
            result.ndim != 2
            or result.shape[1] != 3
        ):
            raise ValueError(
                "landmark_barycentric_coordinates "
                "must have shape (N, 3)."
            )

        if not np.isfinite(
            result
        ).all():
            raise ValueError(
                "landmark_barycentric_coordinates "
                "contains non-finite values."
            )

        if not np.allclose(
            np.sum(
                result,
                axis=1,
            ),
            1.0,
            rtol=0.0,
            atol=1.0e-10,
        ):
            raise ValueError(
                "Each landmark barycentric coordinate "
                "triplet must sum to 1.0."
            )

        return result.astype(
            np.float64,
            copy=True,
        )
