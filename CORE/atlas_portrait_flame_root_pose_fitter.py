from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy.optimize import least_squares

from CORE.atlas_portrait_flame_blendshape_evaluator import (
    AtlasPortraitFlameBlendshapeEvaluator,
)
from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)
from CORE.atlas_portrait_flame_fitting_parameters import (
    AtlasPortraitFlameFittingParameters,
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
from CORE.atlas_portrait_flame_root_pose_fit_result import (
    AtlasPortraitFlameRootPoseFitResult,
)
from CORE.atlas_portrait_landmark_result import (
    AtlasPortraitLandmarkResult,
)
from CORE.atlas_portrait_weak_perspective_camera_initializer import (
    AtlasPortraitWeakPerspectiveCameraInitializer,
)
from CORE.atlas_portrait_weak_perspective_fitting_input_builder import (
    AtlasPortraitWeakPerspectiveFittingInputBuilder,
)
from CORE.providers.portrait.atlas_flame_barycentric_landmark_evaluator import (
    AtlasFlameBarycentricLandmarkEvaluator,
)
from CORE.providers.portrait.atlas_flame_mediapipe_landmark_correspondence import (
    AtlasFlameMediaPipeLandmarkCorrespondence,
)


class AtlasPortraitFlameRootPoseFitter:
    """
    Fits the three-component FLAME root axis-angle pose.

    Identity and expression parameters remain neutral.
    For every root-pose candidate the fitter runs the
    deterministic FLAME deformation chain, evaluates the
    configured barycentric landmarks, and analytically
    reinitializes the weak-perspective camera.

    Optimization is bounded and deterministic. It performs
    no identity fitting, expression fitting, non-root joint
    fitting, rendering, relief compression, or STL export.
    """

    DEFAULT_ANGLE_LIMIT_DEGREES = 30.0
    DEFAULT_MAXIMUM_FUNCTION_EVALUATIONS = 300

    _STARTS_DEGREES = (
        (
            0.0,
            0.0,
            0.0,
        ),
        (
            0.0,
            10.0,
            0.0,
        ),
        (
            0.0,
            -10.0,
            0.0,
        ),
        (
            5.0,
            0.0,
            0.0,
        ),
        (
            -5.0,
            0.0,
            0.0,
        ),
    )

    @classmethod
    def fit(
        cls,
        model: AtlasPortraitFlameCanonicalModel,
        *,
        landmark_result: AtlasPortraitLandmarkResult,
        landmark_indices: Any,
        landmark_face_indices: Any,
        landmark_barycentric_coordinates: Any,
        landmark_weights: Any = None,
        angle_limit_degrees: Any = (
            DEFAULT_ANGLE_LIMIT_DEGREES
        ),
        maximum_function_evaluations: Any = (
            DEFAULT_MAXIMUM_FUNCTION_EVALUATIONS
        ),
    ) -> AtlasPortraitFlameRootPoseFitResult:
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
            AtlasPortraitLandmarkResult,
        ):
            raise TypeError(
                "landmark_result must be an "
                "AtlasPortraitLandmarkResult instance."
            )

        if model.pose_parameter_count < 3:
            raise ValueError(
                "model must contain at least three pose "
                "parameters for root-pose fitting."
            )

        normalized_angle_limit = (
            cls._normalize_positive_float(
                angle_limit_degrees,
                name="angle_limit_degrees",
            )
        )

        normalized_maximum_evaluations = (
            cls._normalize_positive_integer(
                maximum_function_evaluations,
                name="maximum_function_evaluations",
            )
        )

        embedding_landmark_indices = np.asarray(
            landmark_indices,
        ).copy()
        embedding_face_indices = np.asarray(
            landmark_face_indices,
        ).copy()
        embedding_barycentric = np.asarray(
            landmark_barycentric_coordinates,
        ).copy()

        requested_ids = (
            AtlasFlameMediaPipeLandmarkCorrespondence
            .validate_embedding_indices(
                embedding_landmark_indices
            )
        )

        neutral_identity = np.zeros(
            model.identity_parameter_count,
            dtype=np.float64,
        )
        neutral_expression = np.zeros(
            model.expression_parameter_count,
            dtype=np.float64,
        )

        neutral_parameters = (
            AtlasPortraitFlameFittingParameters(
                identity_parameters=neutral_identity,
                expression_parameters=neutral_expression,
                pose_parameters=np.zeros(
                    model.pose_parameter_count,
                    dtype=np.float64,
                ),
                metadata={
                    "fitting_stage": "root_pose",
                    "model_family": "flame",
                    "synthetic": model.metadata.get(
                        "synthetic",
                    ),
                },
            )
        )

        shaped_vertices = (
            AtlasPortraitFlameBlendshapeEvaluator.evaluate(
                model,
                parameters=neutral_parameters,
            )
        )

        joint_positions = (
            AtlasPortraitFlameJointRegressorEvaluator
            .evaluate(
                model,
                shaped_vertices=shaped_vertices,
            )
        )

        def evaluate_candidate(
            root_pose_parameters: np.ndarray,
        ):
            pose_parameters = np.zeros(
                model.pose_parameter_count,
                dtype=np.float64,
            )

            pose_parameters[
                :3
            ] = root_pose_parameters

            parameters = (
                AtlasPortraitFlameFittingParameters(
                    identity_parameters=neutral_identity,
                    expression_parameters=neutral_expression,
                    pose_parameters=pose_parameters,
                    metadata={
                        "fitting_stage": "root_pose",
                        "model_family": "flame",
                        "synthetic": model.metadata.get(
                            "synthetic",
                        ),
                    },
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
                AtlasPortraitFlamePosedVertexComposer
                .compose(
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

            image_coordinates = (
                AtlasPortraitFlameImageCoordinateNormalizer
                .normalize(
                    skinned_vertices
                )
            )

            source_points_3d = (
                AtlasFlameBarycentricLandmarkEvaluator
                .evaluate(
                    vertices=image_coordinates,
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
                    requested_mediapipe_ids=(
                        requested_ids
                    ),
                )
            )

            fitting_input = (
                AtlasPortraitWeakPerspectiveFittingInputBuilder
                .build(
                    landmark_result=landmark_result,
                    source_points_3d=source_points_3d,
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
            )

            return (
                weighted_residuals.reshape(
                    -1
                ),
                camera,
                fitting_input,
            )

        initial_root_pose = np.zeros(
            3,
            dtype=np.float64,
        )

        (
            _,
            initial_camera,
            initial_fitting_input,
        ) = evaluate_candidate(
            initial_root_pose
        )

        angle_limit_radians = math.radians(
            normalized_angle_limit
        )

        lower_bounds = np.full(
            3,
            -angle_limit_radians,
            dtype=np.float64,
        )
        upper_bounds = np.full(
            3,
            angle_limit_radians,
            dtype=np.float64,
        )

        solutions = []

        for start_degrees in cls._STARTS_DEGREES:
            start = np.radians(
                np.asarray(
                    start_degrees,
                    dtype=np.float64,
                )
            )

            start = np.clip(
                start,
                lower_bounds,
                upper_bounds,
            )

            solution = least_squares(
                lambda root_pose: evaluate_candidate(
                    root_pose
                )[
                    0
                ],
                x0=start,
                bounds=(
                    lower_bounds,
                    upper_bounds,
                ),
                method="trf",
                ftol=1.0e-12,
                xtol=1.0e-12,
                gtol=1.0e-12,
                max_nfev=(
                    normalized_maximum_evaluations
                ),
            )

            solutions.append(
                solution
            )

        best_solution = min(
            solutions,
            key=lambda solution: float(
                np.dot(
                    solution.fun,
                    solution.fun,
                )
            ),
        )

        (
            _,
            final_camera,
            final_fitting_input,
        ) = evaluate_candidate(
            np.asarray(
                best_solution.x,
                dtype=np.float64,
            )
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
                "Root-pose optimization increased the "
                "weighted reprojection error."
            )

        return AtlasPortraitFlameRootPoseFitResult(
            root_pose_parameters=np.asarray(
                best_solution.x,
                dtype=np.float64,
            ),
            camera=final_camera,
            initial_weighted_root_mean_square_error=(
                initial_error
            ),
            final_weighted_root_mean_square_error=(
                final_error
            ),
            function_evaluation_count=int(
                best_solution.nfev
            ),
            optimizer_success=bool(
                best_solution.success
            ),
            optimizer_status=int(
                best_solution.status
            ),
            optimizer_message=str(
                best_solution.message
            ),
            metadata={
                "angle_limit_degrees": (
                    normalized_angle_limit
                ),
                "fitting_stage": "root_pose",
                "landmark_count": (
                    final_fitting_input.landmark_count
                ),
                "model_family": "flame",
                "model_version": model.metadata.get(
                    "model_version",
                ),
                "optimizer": (
                    "scipy_least_squares_trf"
                ),
                "synthetic": model.metadata.get(
                    "synthetic",
                ),
            },
        )

    @staticmethod
    def _normalize_positive_float(
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
