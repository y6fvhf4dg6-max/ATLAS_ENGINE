from __future__ import annotations

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
from CORE.atlas_portrait_flame_root_pose_fitter import (
    AtlasPortraitFlameRootPoseFitter,
)
from CORE.atlas_portrait_landmark_result import (
    AtlasPortraitLandmarkResult,
)
from CORE.providers.portrait.atlas_flame_barycentric_landmark_evaluator import (
    AtlasFlameBarycentricLandmarkEvaluator,
)
from CORE.providers.portrait.atlas_flame_mediapipe_landmark_correspondence import (
    AtlasFlameMediaPipeLandmarkCorrespondence,
)


KNOWN_ROOT_POSE = np.array(
    [
        -0.16,
        0.09,
        0.05,
    ],
    dtype=np.float64,
)


def _landmark_points() -> np.ndarray:
    return np.array(
        [
            [-0.34, 0.22, 0.06],
            [-0.19, 0.25, 0.13],
            [0.18, 0.24, 0.12],
            [0.35, 0.20, 0.04],
            [-0.28, 0.38, 0.02],
            [-0.12, 0.41, 0.09],
            [0.13, 0.40, 0.08],
            [0.29, 0.35, 0.01],
            [0.00, 0.27, 0.17],
            [0.01, 0.10, 0.24],
            [0.00, -0.02, 0.31],
            [-0.10, -0.08, 0.18],
            [0.11, -0.07, 0.17],
            [-0.23, -0.22, 0.09],
            [0.00, -0.19, 0.16],
            [0.01, -0.28, 0.13],
            [0.24, -0.21, 0.08],
        ],
        dtype=np.float64,
    )


def _model_and_embedding():
    landmark_points = _landmark_points()

    vertices = []
    faces = []

    for point in landmark_points:
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

    model = AtlasPortraitFlameCanonicalModel(
        template_vertices=template_vertices,
        triangle_faces=triangle_faces,
        identity_shape_directions=np.zeros(
            (
                vertex_count,
                3,
                1,
            ),
            dtype=np.float64,
        ),
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
            "model_version": "synthetic-root-pose-v1",
            "synthetic": True,
        },
    )

    landmark_indices = np.asarray(
        AtlasFlameMediaPipeLandmarkCorrespondence
        .mediapipe_ids(),
        dtype=np.int64,
    )

    landmark_face_indices = np.arange(
        len(
            landmark_indices
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
                landmark_indices
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


def _skinned_vertices(
    model,
    *,
    root_pose,
):
    parameters = AtlasPortraitFlameFittingParameters(
        identity_parameters=np.zeros(
            model.identity_parameter_count,
            dtype=np.float64,
        ),
        expression_parameters=np.zeros(
            model.expression_parameter_count,
            dtype=np.float64,
        ),
        pose_parameters=np.concatenate(
            [
                np.asarray(
                    root_pose,
                    dtype=np.float64,
                ),
                np.zeros(
                    model.pose_parameter_count - 3,
                    dtype=np.float64,
                ),
            ]
        ),
        metadata={
            "fitting_stage": "synthetic_target",
            "synthetic": True,
        },
    )

    shaped_vertices = (
        AtlasPortraitFlameBlendshapeEvaluator
        .evaluate(
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
        AtlasPortraitFlamePosedVertexComposer
        .compose(
            model,
            shaped_vertices=shaped_vertices,
            pose_corrective_offsets=corrective_offsets,
        )
    )

    transforms = (
        AtlasPortraitFlameKinematicTransformEvaluator
        .evaluate(
            model,
            joint_positions=joint_positions,
            pose_parameters=parameters.pose_parameters,
        )
    )

    return (
        AtlasPortraitFlameLinearBlendSkinningEvaluator
        .evaluate(
            model,
            posed_vertices=posed_vertices,
            joint_transforms=transforms,
        )
    )


def _target_landmark_result():
    (
        model,
        landmark_indices,
        landmark_face_indices,
        landmark_barycentric_coordinates,
    ) = _model_and_embedding()

    skinned_vertices = _skinned_vertices(
        model,
        root_pose=KNOWN_ROOT_POSE,
    )

    normalized_vertices = (
        AtlasPortraitFlameImageCoordinateNormalizer
        .normalize(
            skinned_vertices
        )
    )

    points = (
        AtlasFlameBarycentricLandmarkEvaluator
        .evaluate(
            vertices=normalized_vertices,
            triangle_faces=model.triangle_faces,
            landmark_indices=landmark_indices,
            landmark_face_indices=landmark_face_indices,
            landmark_barycentric_coordinates=(
                landmark_barycentric_coordinates
            ),
            requested_mediapipe_ids=(
                AtlasFlameMediaPipeLandmarkCorrespondence
                .mediapipe_ids()
            ),
        )
    )

    target_points = (
        0.72
        * points[
            :,
            :2,
        ]
        + np.array(
            [
                0.50,
                0.48,
            ],
            dtype=np.float64,
        )
    )

    landmarks = {
        name: tuple(
            target_points[
                index
            ]
        )
        for index, name in enumerate(
            AtlasFlameMediaPipeLandmarkCorrespondence
            .landmark_names()
        )
    }

    return AtlasPortraitLandmarkResult(
        image_width=1024,
        image_height=1024,
        landmarks=landmarks,
        confidence=1.0,
        provider_id="synthetic-root-pose",
        metadata={
            "fixture_name": "synthetic-root-pose-v1",
            "image_sha256": "synthetic-root-pose-sha256",
            "synthetic": True,
            "view_type": "front",
        },
    )


def _fit():
    (
        model,
        landmark_indices,
        landmark_face_indices,
        landmark_barycentric_coordinates,
    ) = _model_and_embedding()

    result = AtlasPortraitFlameRootPoseFitter.fit(
        model,
        landmark_result=_target_landmark_result(),
        landmark_indices=landmark_indices,
        landmark_face_indices=landmark_face_indices,
        landmark_barycentric_coordinates=(
            landmark_barycentric_coordinates
        ),
    )

    return result


def test_fitter_returns_root_pose_fit_result():
    assert isinstance(
        _fit(),
        AtlasPortraitFlameRootPoseFitResult,
    )


def test_fitter_recovers_known_root_pose():
    result = _fit()

    np.testing.assert_allclose(
        result.root_pose_parameters,
        KNOWN_ROOT_POSE,
        rtol=0.0,
        atol=2.0e-5,
    )


def test_fitter_reduces_reprojection_error():
    result = _fit()

    assert (
        result.final_weighted_root_mean_square_error
        < result.initial_weighted_root_mean_square_error
    )


def test_fitter_reaches_near_zero_synthetic_error():
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
        "angle_limit_degrees": 30.0,
        "fitting_stage": "root_pose",
        "landmark_count": 17,
        "model_family": "flame",
        "model_version": "synthetic-root-pose-v1",
        "optimizer": "scipy_least_squares_trf",
        "synthetic": True,
    }


def test_fitter_is_deterministic():
    first = _fit()
    second = _fit()

    assert first.to_dict() == second.to_dict()


def test_fitter_rejects_wrong_model_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameCanonicalModel",
    ):
        AtlasPortraitFlameRootPoseFitter.fit(
            object(),
            landmark_result=_target_landmark_result(),
            landmark_indices=np.arange(
                17,
                dtype=np.int64,
            ),
            landmark_face_indices=np.arange(
                17,
                dtype=np.int64,
            ),
            landmark_barycentric_coordinates=np.tile(
                np.array(
                    [
                        1.0,
                        0.0,
                        0.0,
                    ],
                    dtype=np.float64,
                ),
                (
                    17,
                    1,
                ),
            ),
        )
