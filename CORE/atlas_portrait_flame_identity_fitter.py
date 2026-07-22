from __future__ import annotations

import math
from numbers import Integral
from typing import Any

import numpy as np
from scipy.optimize import least_squares

from CORE.atlas_portrait_dense_weak_perspective_fitting_input_builder import (
    AtlasPortraitDenseWeakPerspectiveFittingInputBuilder,
)
from CORE.atlas_portrait_flame_blendshape_evaluator import (
    AtlasPortraitFlameBlendshapeEvaluator,
)
from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)
from CORE.atlas_portrait_flame_fitting_parameters import (
    AtlasPortraitFlameFittingParameters,
)
from CORE.atlas_portrait_flame_identity_fit_result import (
    AtlasPortraitFlameIdentityFitResult,
)
from CORE.atlas_portrait_flame_image_coordinate_normalizer import (
    AtlasPortraitFlameImageCoordinateNormalizer,
)
from CORE.atlas_portrait_flame_joint_regressor_evaluator import (
    AtlasPortraitFlameJointRegressorEvaluator,
)
from CORE.atlas_portrait_flame_kinematic_transform_evaluator import (
    AtlasPortraitFlameKinematicTransformEvaluator,
)
from CORE.atlas_portrait_flame_linear_blend_skinning_evaluator import (
    AtlasPortraitFlameLinearBlendSkinningEvaluator,
)
from CORE.atlas_portrait_flame_pose_corrective_evaluator import (
    AtlasPortraitFlamePoseCorrectiveEvaluator,
)
from CORE.atlas_portrait_flame_pose_feature_evaluator import (
    AtlasPortraitFlamePoseFeatureEvaluator,
)
from CORE.atlas_portrait_flame_posed_vertex_composer import (
    AtlasPortraitFlamePosedVertexComposer,
)
from CORE.atlas_portrait_indexed_landmark_result import (
    AtlasPortraitIndexedLandmarkResult,
)
from CORE.atlas_portrait_weak_perspective_camera_initializer import (
    AtlasPortraitWeakPerspectiveCameraInitializer,
)
from CORE.providers.portrait.atlas_flame_barycentric_landmark_evaluator import (
    AtlasFlameBarycentricLandmarkEvaluator,
)


class AtlasPortraitFlameIdentityFitter:
    """
    Fits a bounded prefix of FLAME identity parameters.

    Root pose remains fixed. Expression and all non-root pose
    parameters remain neutral. For every identity candidate the
    fitter runs the deterministic FLAME deformation chain,
    evaluates dense barycentric landmarks, and analytically
    resolves the weak-perspective camera.

    L2 regularization is applied only to active identity
    parameters. Inactive identity parameters remain zero.

    The fitter performs no root-pose optimization, expression
    fitting, rendering, relief conversion, or STL export.
    """

    DEFAULT_ACTIVE_IDENTITY_COUNT = 20
    DEFAULT_REGULARIZATION_WEIGHT = 1.0e-5
    DEFAULT_IDENTITY_PARAMETER_LIMIT = 3.0
    DEFAULT_MAXIMUM_FUNCTION_EVALUATIONS = 250

    @classmethod
    def fit(
        cls,
        model: AtlasPortraitFlameCanonicalModel,
        *,
        landmark_result: AtlasPortraitIndexedLandmarkResult,
        landmark_indices: Any,
        landmark_face_indices: Any,
        landmark_barycentric_coordinates: Any,
        requested_mediapipe_ids: Any,
        root_pose_parameters: Any,
        landmark_weights: Any = None,
        active_identity_count: Any = (
            DEFAULT_ACTIVE_IDENTITY_COUNT
        ),
        regularization_weight: Any = (
            DEFAULT_REGULARIZATION_WEIGHT
        ),
        identity_parameter_limit: Any = (
            DEFAULT_IDENTITY_PARAMETER_LIMIT
        ),
        maximum_function_evaluations: Any = (
            DEFAULT_MAXIMUM_FUNCTION_EVALUATIONS
        ),
    ) -> AtlasPortraitFlameIdentityFitResult:
        if not isinstance(
            model,
            AtlasPortraitFlameCanonicalModel,
        ):
            raise TypeError(
                "model must be an "
                "AtlasPortraitFlameCanonicalModel instance."
            )

        if not isinstance(
            landmark_result,
            AtlasPortraitIndexedLandmarkResult,
        ):
            raise TypeError(
                "landmark_result must be an "
                "AtlasPortraitIndexedLandmarkResult instance."
            )

        normalized_root_pose = cls._normalize_root_pose(
            root_pose_parameters
        )

        normalized_active_count = (
            cls._normalize_positive_integer(
                active_identity_count,
                name="active_identity_count",
            )
        )

        if (
            normalized_active_count
            > model.identity_parameter_count
        ):
            raise ValueError(
                "active_identity_count must not exceed "
                "the model identity parameter count."
            )

        normalized_regularization = (
            cls._normalize_nonnegative_float(
                regularization_weight,
                name="regularization_weight",
            )
        )

        normalized_parameter_limit = (
            cls._normalize_positive_float(
                identity_parameter_limit,
                name="identity_parameter_limit",
            )
        )

        normalized_maximum_evaluations = (
            cls._normalize_positive_integer(
                maximum_function_evaluations,
                name="maximum_function_evaluations",
            )
        )

        embedding_landmark_indices = np.asarray(
            landmark_indices
        ).copy()
        embedding_face_indices = np.asarray(
            landmark_face_indices
        ).copy()
        embedding_barycentric = np.asarray(
            landmark_barycentric_coordinates
        ).copy()

        requested_ids = cls._normalize_requested_ids(
            requested_mediapipe_ids
        )

        neutral_expression = np.zeros(
            model.expression_parameter_count,
            dtype=np.float64,
        )

        pose_parameters = np.zeros(
            model.pose_parameter_count,
            dtype=np.float64,
        )

        if model.pose_parameter_count < 3:
            raise ValueError(
                "model must contain at least three pose "
                "parameters."
            )

        pose_parameters[
            :3
        ] = normalized_root_pose

        def evaluate_candidate(
            active_parameters: np.ndarray,
            *,
            include_regularization: bool,
        ):
            identity_parameters = np.zeros(
                model.identity_parameter_count,
                dtype=np.float64,
            )

            identity_parameters[
                :normalized_active_count
            ] = active_parameters

            parameters = AtlasPortraitFlameFittingParameters(
                identity_parameters=identity_parameters,
                expression_parameters=neutral_expression,
                pose_parameters=pose_parameters,
                metadata={
                    "fitting_stage": "dense_identity",
                    "model_family": "flame",
                    "synthetic": model.metadata.get(
                        "synthetic"
                    ),
                },
            )

            shaped_vertices = (
                AtlasPortraitFlameBlendshapeEvaluator.evaluate(
                    model,
                    parameters=parameters,
                )
            )

            joint_positions = (
                AtlasPortraitFlameJointRegressorEvaluator
                .evaluate(
                    model,
                    shaped_vertices=shaped_vertices,
                )
            )

            pose_features = (
                AtlasPortraitFlamePoseFeatureEvaluator
                .evaluate(
                    parameters
                )
            )

            corrective_offsets = (
                AtlasPortraitFlamePoseCorrectiveEvaluator
                .evaluate(
                    model,
                    pose_features=pose_features,
                )
            )

            posed_vertices = (
                AtlasPortraitFlamePosedVertexComposer.compose(
                    model,
                    shaped_vertices=shaped_vertices,
                    pose_corrective_offsets=(
                        corrective_offsets
                    ),
                )
            )

            joint_transforms = (
                AtlasPortraitFlameKinematicTransformEvaluator
                .evaluate(
                    model,
                    joint_positions=joint_positions,
                    pose_parameters=pose_parameters,
                )
            )

            skinned_vertices = (
                AtlasPortraitFlameLinearBlendSkinningEvaluator
                .evaluate(
                    model,
                    posed_vertices=posed_vertices,
                    joint_transforms=joint_transforms,
                )
            )

            image_vertices = (
                AtlasPortraitFlameImageCoordinateNormalizer
                .normalize(
                    skinned_vertices
                )
            )

            source_points_3d = (
                AtlasFlameBarycentricLandmarkEvaluator
                .evaluate(
                    vertices=image_vertices,
                    triangle_faces=model.triangle_faces,
                    landmark_indices=(
                        embedding_landmark_indices
                    ),
                    landmark_face_indices=(
                        embedding_face_indices
                    ),
                    landmark_barycentric_coordinates=(
                        embedding_barycentric
                    ),
                    requested_mediapipe_ids=requested_ids,
                )
            )

            fitting_input = (
                AtlasPortraitDenseWeakPerspectiveFittingInputBuilder
                .build(
                    landmark_result=landmark_result,
                    source_points_3d=source_points_3d,
                    requested_mediapipe_ids=requested_ids,
                    landmark_weights=landmark_weights,
                )
            )

            camera = (
                AtlasPortraitWeakPerspectiveCameraInitializer
                .initialize(
                    fitting_input
                )
            )

            residuals = (
                camera.projected_points_2d
                - fitting_input.target_points_2d
            )

            weighted_residuals = (
                residuals
                * np.sqrt(
                    fitting_input.landmark_weights
                )[
                    :,
                    np.newaxis,
                ]
            ).reshape(
                -1
            )

            if (
                include_regularization
                and normalized_regularization > 0.0
            ):
                optimizer_residuals = np.concatenate(
                    [
                        weighted_residuals,
                        math.sqrt(
                            normalized_regularization
                        )
                        * active_parameters,
                    ]
                )
            else:
                optimizer_residuals = weighted_residuals

            return (
                optimizer_residuals,
                camera,
                fitting_input,
                identity_parameters,
            )

        initial_active_parameters = np.zeros(
            normalized_active_count,
            dtype=np.float64,
        )

        (
            _,
            initial_camera,
            _,
            _,
        ) = evaluate_candidate(
            initial_active_parameters,
            include_regularization=False,
        )

        lower_bounds = np.full(
            normalized_active_count,
            -normalized_parameter_limit,
            dtype=np.float64,
        )
        upper_bounds = np.full(
            normalized_active_count,
            normalized_parameter_limit,
            dtype=np.float64,
        )

        solution = least_squares(
            lambda active_parameters: evaluate_candidate(
                active_parameters,
                include_regularization=True,
            )[
                0
            ],
            x0=initial_active_parameters,
            bounds=(
                lower_bounds,
                upper_bounds,
            ),
            method="trf",
            ftol=1.0e-12,
            xtol=1.0e-12,
            gtol=1.0e-12,
            max_nfev=normalized_maximum_evaluations,
        )

        (
            _,
            final_camera,
            final_fitting_input,
            final_identity_parameters,
        ) = evaluate_candidate(
            np.asarray(
                solution.x,
                dtype=np.float64,
            ),
            include_regularization=False,
        )

        initial_error = (
            initial_camera
            .weighted_root_mean_square_error
        )
        final_error = (
            final_camera
            .weighted_root_mean_square_error
        )

        if final_error > initial_error:
            raise RuntimeError(
                "Identity optimization increased the "
                "weighted reprojection error."
            )

        return AtlasPortraitFlameIdentityFitResult(
            identity_parameters=final_identity_parameters,
            camera=final_camera,
            initial_weighted_root_mean_square_error=(
                initial_error
            ),
            final_weighted_root_mean_square_error=(
                final_error
            ),
            regularization_weight=(
                normalized_regularization
            ),
            function_evaluation_count=int(
                solution.nfev
            ),
            optimizer_success=bool(
                solution.success
            ),
            optimizer_status=int(
                solution.status
            ),
            optimizer_message=str(
                solution.message
            ),
            metadata={
                "active_identity_count": (
                    normalized_active_count
                ),
                "fitting_stage": "dense_identity",
                "identity_parameter_limit": (
                    normalized_parameter_limit
                ),
                "landmark_count": (
                    final_fitting_input.landmark_count
                ),
                "model_family": "flame",
                "model_version": model.metadata.get(
                    "model_version"
                ),
                "optimizer": (
                    "scipy_least_squares_trf"
                ),
                "synthetic": model.metadata.get(
                    "synthetic"
                ),
            },
        )

    @staticmethod
    def _normalize_root_pose(
        value: Any,
    ) -> np.ndarray:
        try:
            root_pose = np.asarray(
                value,
                dtype=np.float64,
            ).copy()
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "root_pose_parameters must be numeric."
            ) from exc

        if root_pose.shape != (
            3,
        ):
            raise ValueError(
                "root_pose_parameters must have shape (3,)."
            )

        if not np.isfinite(
            root_pose
        ).all():
            raise ValueError(
                "root_pose_parameters must contain only "
                "finite values."
            )

        return root_pose

    @staticmethod
    def _normalize_requested_ids(
        value: Any,
    ) -> tuple[int, ...]:
        if (
            value is None
            or isinstance(
                value,
                (
                    str,
                    bytes,
                ),
            )
        ):
            raise TypeError(
                "requested_mediapipe_ids must be a "
                "non-empty iterable of integers."
            )

        try:
            raw_ids = tuple(
                value
            )
        except TypeError as exc:
            raise TypeError(
                "requested_mediapipe_ids must be a "
                "non-empty iterable of integers."
            ) from exc

        if not raw_ids:
            raise ValueError(
                "requested_mediapipe_ids must not be empty."
            )

        normalized: list[int] = []

        for raw_id in raw_ids:
            if (
                isinstance(
                    raw_id,
                    (
                        bool,
                        np.bool_,
                    ),
                )
                or not isinstance(
                    raw_id,
                    Integral,
                )
            ):
                raise TypeError(
                    "requested_mediapipe_ids must contain "
                    "integer values."
                )

            landmark_id = int(
                raw_id
            )

            if landmark_id < 0:
                raise ValueError(
                    "requested_mediapipe_ids must not "
                    "contain negative values."
                )

            normalized.append(
                landmark_id
            )

        if len(
            normalized
        ) != len(
            set(
                normalized
            )
        ):
            raise ValueError(
                "requested_mediapipe_ids must contain "
                "unique values."
            )

        return tuple(
            normalized
        )

    @staticmethod
    def _normalize_nonnegative_float(
        value: Any,
        *,
        name: str,
    ) -> float:
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

    @staticmethod
    def _normalize_positive_float(
        value: Any,
        *,
        name: str,
    ) -> float:
        normalized = (
            AtlasPortraitFlameIdentityFitter
            ._normalize_nonnegative_float(
                value,
                name=name,
            )
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
