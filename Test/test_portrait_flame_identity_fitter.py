from __future__ import annotations

import math

import numpy as np
import pytest

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
from CORE.atlas_portrait_flame_identity_fitter import (
    AtlasPortraitFlameIdentityFitter,
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
from CORE.providers.portrait.atlas_flame_barycentric_landmark_evaluator import (
    AtlasFlameBarycentricLandmarkEvaluator,
)


KNOWN_ACTIVE_IDENTITY = np.array(
    [
        0.55,
        -0.35,
    ],
    dtype=np.float64,
)

REQUESTED_IDS = (
    10,
    20,
    30,
    40,
)


def _base_landmark_points() -> np.ndarray:
    return np.array(
        [
            [-0.40, 0.32, 0.08],
            [0.31, 0.27, 0.14],
            [-0.24, -0.35, 0.11],
            [0.38, -0.23, 0.04],
        ],
        dtype=np.float64,
    )


def _model_and_embedding():
    base_points = _base_landmark_points()

    vertices: list[np.ndarray] = []
    faces: list[list[int]] = []

    for point in base_points:
        start = len(
            vertices
        )

        vertices.extend(
            [
                point,
                point
                + np.array(
                    [
                        0.004,
                        0.0,
                        0.0,
                    ],
                    dtype=np.float64,
                ),
                point
                + np.array(
                    [
                        0.0,
                        0.004,
                        0.0,
                    ],
                    dtype=np.float64,
                ),
            ]
        )

        faces.append(
            [
                start,
                start + 1,
                start + 2,
            ]
        )

    template_vertices = np.asarray(
        vertices,
        dtype=np.float64,
    )
    triangle_faces = np.asarray(
        faces,
        dtype=np.int64,
    )

    vertex_count = int(
        template_vertices.shape[0]
    )

    identity_directions = np.zeros(
        (
            vertex_count,
            3,
            3,
        ),
        dtype=np.float64,
    )

    mode_zero_offsets = np.array(
        [
            [-0.060, 0.020, 0.010],
            [0.025, -0.010, 0.000],
            [0.010, 0.045, -0.005],
            [0.035, -0.030, 0.008],
        ],
        dtype=np.float64,
    )

    mode_one_offsets = np.array(
        [
            [0.010, -0.040, 0.005],
            [-0.045, 0.030, -0.006],
            [0.030, 0.015, 0.010],
            [0.005, -0.020, -0.004],
        ],
        dtype=np.float64,
    )

    mode_two_offsets = np.array(
        [
            [0.020, 0.010, 0.000],
            [-0.010, 0.020, 0.000],
            [0.015, -0.015, 0.000],
            [-0.020, -0.010, 0.000],
        ],
        dtype=np.float64,
    )

    for landmark_index in range(
        4
    ):
        vertex_start = (
            landmark_index
            * 3
        )

        for local_vertex_index in range(
            3
        ):
            vertex_index = (
                vertex_start
                + local_vertex_index
            )

            identity_directions[
                vertex_index,
                :,
                0,
            ] = mode_zero_offsets[
                landmark_index
            ]

            identity_directions[
                vertex_index,
                :,
                1,
            ] = mode_one_offsets[
                landmark_index
            ]

            identity_directions[
                vertex_index,
                :,
                2,
            ] = mode_two_offsets[
                landmark_index
            ]

    model = AtlasPortraitFlameCanonicalModel(
        template_vertices=template_vertices,
        triangle_faces=triangle_faces,
        identity_shape_directions=identity_directions,
        expression_shape_directions=np.zeros(
            (
                vertex_count,
                3,
                1,
            ),
            dtype=np.float64,
        ),
        pose_directions=np.zeros(
            (
                vertex_count,
                3,
                9,
            ),
            dtype=np.float64,
        ),
        pose_parameter_count=6,
        joint_regressor=np.vstack(
            [
                np.full(
                    vertex_count,
                    1.0 / float(
                        vertex_count
                    ),
                    dtype=np.float64,
                ),
                np.full(
                    vertex_count,
                    1.0 / float(
                        vertex_count
                    ),
                    dtype=np.float64,
                ),
            ]
        ),
        skinning_weights=np.column_stack(
            [
                np.ones(
                    vertex_count,
                    dtype=np.float64,
                ),
                np.zeros(
                    vertex_count,
                    dtype=np.float64,
                ),
            ]
        ),
        kinematic_tree=np.array(
            [
                -1,
                0,
            ],
            dtype=np.int64,
        ),
        metadata={
            "model_family": "flame",
            "model_version": "synthetic-identity-v1",
            "synthetic": True,
        },
    )

    landmark_indices = np.asarray(
        REQUESTED_IDS,
        dtype=np.int64,
    )

    landmark_face_indices = np.arange(
        len(
            REQUESTED_IDS
        ),
        dtype=np.int64,
    )

    landmark_barycentric_coordinates = np.tile(
        np.array(
            [
                1.0,
                0.0,
                0.0,
            ],
            dtype=np.float64,
        ),
        (
            len(
                REQUESTED_IDS
            ),
            1,
        ),
    )

    return (
        model,
        landmark_indices,
        landmark_face_indices,
        landmark_barycentric_coordinates,
    )


def _evaluate_image_landmarks(
    model: AtlasPortraitFlameCanonicalModel,
    *,
    identity_parameters: np.ndarray,
    root_pose_parameters: np.ndarray,
    landmark_indices: np.ndarray,
    landmark_face_indices: np.ndarray,
    landmark_barycentric_coordinates: np.ndarray,
) -> np.ndarray:
    pose_parameters = np.zeros(
        model.pose_parameter_count,
        dtype=np.float64,
    )
    pose_parameters[
        :3
    ] = root_pose_parameters

    parameters = AtlasPortraitFlameFittingParameters(
        identity_parameters=identity_parameters,
        expression_parameters=np.zeros(
            model.expression_parameter_count,
            dtype=np.float64,
        ),
        pose_parameters=pose_parameters,
        metadata={
            "fitting_stage": "synthetic_identity_target",
            "synthetic": True,
        },
    )

    shaped_vertices = (
        AtlasPortraitFlameBlendshapeEvaluator.evaluate(
            model,
            parameters=parameters,
        )
    )

    joint_positions = (
        AtlasPortraitFlameJointRegressorEvaluator.evaluate(
            model,
            shaped_vertices=shaped_vertices,
        )
    )

    pose_features = (
        AtlasPortraitFlamePoseFeatureEvaluator.evaluate(
            parameters
        )
    )

    corrective_offsets = (
        AtlasPortraitFlamePoseCorrectiveEvaluator.evaluate(
            model,
            pose_features=pose_features,
        )
    )

    posed_vertices = (
        AtlasPortraitFlamePosedVertexComposer.compose(
            model,
            shaped_vertices=shaped_vertices,
            pose_corrective_offsets=corrective_offsets,
        )
    )

    joint_transforms = (
        AtlasPortraitFlameKinematicTransformEvaluator.evaluate(
            model,
            joint_positions=joint_positions,
            pose_parameters=pose_parameters,
        )
    )

    skinned_vertices = (
        AtlasPortraitFlameLinearBlendSkinningEvaluator.evaluate(
            model,
            posed_vertices=posed_vertices,
            joint_transforms=joint_transforms,
        )
    )

    image_vertices = (
        AtlasPortraitFlameImageCoordinateNormalizer.normalize(
            skinned_vertices
        )
    )

    return AtlasFlameBarycentricLandmarkEvaluator.evaluate(
        vertices=image_vertices,
        triangle_faces=model.triangle_faces,
        landmark_indices=landmark_indices,
        landmark_face_indices=landmark_face_indices,
        landmark_barycentric_coordinates=(
            landmark_barycentric_coordinates
        ),
        requested_mediapipe_ids=REQUESTED_IDS,
    )


def _target_landmark_result() -> (
    AtlasPortraitIndexedLandmarkResult
):
    (
        model,
        landmark_indices,
        landmark_face_indices,
        landmark_barycentric_coordinates,
    ) = _model_and_embedding()

    identity_parameters = np.zeros(
        model.identity_parameter_count,
        dtype=np.float64,
    )
    identity_parameters[
        :2
    ] = KNOWN_ACTIVE_IDENTITY

    source_points = _evaluate_image_landmarks(
        model,
        identity_parameters=identity_parameters,
        root_pose_parameters=np.zeros(
            3,
            dtype=np.float64,
        ),
        landmark_indices=landmark_indices,
        landmark_face_indices=landmark_face_indices,
        landmark_barycentric_coordinates=(
            landmark_barycentric_coordinates
        ),
    )

    target_points_2d = (
        0.68
        * source_points[
            :,
            :2
        ]
        + np.array(
            [
                0.49,
                0.51,
            ],
            dtype=np.float64,
        )
    )

    landmarks_3d = np.column_stack(
        [
            target_points_2d,
            np.zeros(
                len(
                    REQUESTED_IDS
                ),
                dtype=np.float64,
            ),
        ]
    )

    return AtlasPortraitIndexedLandmarkResult(
        image_width=1024,
        image_height=1024,
        landmark_ids=REQUESTED_IDS,
        landmarks_3d=landmarks_3d,
        confidence=1.0,
        provider_id="synthetic-dense-identity",
        metadata={
            "image_sha256": "synthetic-identity-sha256",
            "synthetic": True,
            "view_type": "front",
        },
    )


def _fit(
    **overrides,
) -> AtlasPortraitFlameIdentityFitResult:
    (
        model,
        landmark_indices,
        landmark_face_indices,
        landmark_barycentric_coordinates,
    ) = _model_and_embedding()

    arguments = {
        "model": model,
        "landmark_result": _target_landmark_result(),
        "landmark_indices": landmark_indices,
        "landmark_face_indices": landmark_face_indices,
        "landmark_barycentric_coordinates": (
            landmark_barycentric_coordinates
        ),
        "requested_mediapipe_ids": REQUESTED_IDS,
        "root_pose_parameters": np.zeros(
            3,
            dtype=np.float64,
        ),
        "active_identity_count": 2,
        "regularization_weight": 0.0,
        "identity_parameter_limit": 3.0,
        "maximum_function_evaluations": 200,
    }
    arguments.update(
        overrides
    )

    return AtlasPortraitFlameIdentityFitter.fit(
        **arguments
    )


def test_fitter_returns_identity_fit_result():
    assert isinstance(
        _fit(),
        AtlasPortraitFlameIdentityFitResult,
    )


def test_fitter_recovers_known_active_identity_parameters():
    result = _fit()

    np.testing.assert_allclose(
        result.identity_parameters[
            :2
        ],
        KNOWN_ACTIVE_IDENTITY,
        rtol=0.0,
        atol=2.0e-5,
    )


def test_fitter_leaves_inactive_identity_parameters_at_zero():
    result = _fit()

    np.testing.assert_allclose(
        result.identity_parameters[
            2:
        ],
        0.0,
        rtol=0.0,
        atol=1.0e-12,
    )


def test_fitter_reduces_reprojection_error():
    result = _fit()

    assert (
        result.final_weighted_root_mean_square_error
        < result.initial_weighted_root_mean_square_error
    )


def test_fitter_reaches_near_zero_unregularized_error():
    result = _fit()

    assert (
        result.final_weighted_root_mean_square_error
        < 1.0e-8
    )


def test_fitter_reports_successful_optimizer():
    result = _fit()

    assert result.optimizer_success is True
    assert result.function_evaluation_count > 0


def test_fitter_records_deterministic_metadata():
    result = _fit()

    assert result.metadata == {
        "active_identity_count": 2,
        "fitting_stage": "dense_identity",
        "identity_parameter_limit": 3.0,
        "landmark_count": 4,
        "model_family": "flame",
        "model_version": "synthetic-identity-v1",
        "optimizer": "scipy_least_squares_trf",
        "synthetic": True,
    }


def test_fitter_preserves_regularization_weight():
    result = _fit(
        regularization_weight=1.0e-5
    )

    assert result.regularization_weight == pytest.approx(
        1.0e-5
    )


def test_fitter_is_deterministic():
    first = _fit()
    second = _fit()

    assert first.to_dict() == second.to_dict()


def test_fitter_does_not_modify_inputs():
    (
        model,
        landmark_indices,
        landmark_face_indices,
        landmark_barycentric_coordinates,
    ) = _model_and_embedding()

    landmark_result = _target_landmark_result()
    root_pose_parameters = np.zeros(
        3,
        dtype=np.float64,
    )

    model_before = model.to_dict()
    landmark_result_before = landmark_result.to_dict()
    landmark_indices_before = landmark_indices.copy()
    face_indices_before = landmark_face_indices.copy()
    barycentric_before = (
        landmark_barycentric_coordinates.copy()
    )
    root_pose_before = root_pose_parameters.copy()

    AtlasPortraitFlameIdentityFitter.fit(
        model,
        landmark_result=landmark_result,
        landmark_indices=landmark_indices,
        landmark_face_indices=landmark_face_indices,
        landmark_barycentric_coordinates=(
            landmark_barycentric_coordinates
        ),
        requested_mediapipe_ids=REQUESTED_IDS,
        root_pose_parameters=root_pose_parameters,
        active_identity_count=2,
        regularization_weight=0.0,
        identity_parameter_limit=3.0,
        maximum_function_evaluations=200,
    )

    assert model.to_dict() == model_before
    assert landmark_result.to_dict() == landmark_result_before
    assert np.array_equal(
        landmark_indices,
        landmark_indices_before,
    )
    assert np.array_equal(
        landmark_face_indices,
        face_indices_before,
    )
    assert np.array_equal(
        landmark_barycentric_coordinates,
        barycentric_before,
    )
    assert np.array_equal(
        root_pose_parameters,
        root_pose_before,
    )


def test_fitter_rejects_wrong_model_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameCanonicalModel",
    ):
        _fit(
            model=object()
        )


def test_fitter_rejects_wrong_landmark_result_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitIndexedLandmarkResult",
    ):
        _fit(
            landmark_result=object()
        )


@pytest.mark.parametrize(
    (
        "overrides",
        "match",
    ),
    [
        (
            {
                "root_pose_parameters": [
                    0.0,
                    0.0,
                ],
            },
            "root_pose_parameters",
        ),
        (
            {
                "root_pose_parameters": [
                    0.0,
                    math.nan,
                    0.0,
                ],
            },
            "finite",
        ),
        (
            {
                "active_identity_count": 0,
            },
            "active_identity_count",
        ),
        (
            {
                "active_identity_count": 4,
            },
            "active_identity_count",
        ),
        (
            {
                "active_identity_count": True,
            },
            "active_identity_count",
        ),
        (
            {
                "regularization_weight": -1.0,
            },
            "regularization_weight",
        ),
        (
            {
                "regularization_weight": math.nan,
            },
            "regularization_weight",
        ),
        (
            {
                "identity_parameter_limit": 0.0,
            },
            "identity_parameter_limit",
        ),
        (
            {
                "identity_parameter_limit": math.inf,
            },
            "identity_parameter_limit",
        ),
        (
            {
                "maximum_function_evaluations": 0,
            },
            "maximum_function_evaluations",
        ),
        (
            {
                "maximum_function_evaluations": 2.5,
            },
            "maximum_function_evaluations",
        ),
        (
            {
                "requested_mediapipe_ids": (
                    10,
                    20,
                    20,
                    40,
                ),
            },
            "unique",
        ),
    ],
)
def test_fitter_rejects_invalid_configuration(
    overrides,
    match,
):
    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
        match=match,
    ):
        _fit(
            **overrides
        )
