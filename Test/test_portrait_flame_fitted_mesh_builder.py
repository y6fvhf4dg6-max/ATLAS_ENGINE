from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)
from CORE.atlas_portrait_flame_deformed_mesh_evaluator import (
    AtlasPortraitFlameDeformedMesh,
)
from CORE.atlas_portrait_flame_dense_identity_pipeline_result import (
    AtlasPortraitFlameDenseIdentityPipelineResult,
)
from CORE.atlas_portrait_flame_fitted_mesh_builder import (
    AtlasPortraitFlameFittedMeshBuilder,
)
from CORE.atlas_portrait_flame_identity_fit_result import (
    AtlasPortraitFlameIdentityFitResult,
)
from CORE.atlas_portrait_flame_root_pose_fit_result import (
    AtlasPortraitFlameRootPoseFitResult,
)
from CORE.atlas_portrait_weak_perspective_camera import (
    AtlasPortraitWeakPerspectiveCamera,
)


def _model() -> AtlasPortraitFlameCanonicalModel:
    template_vertices = np.array(
        [
            [-0.40, 0.30, 0.10],
            [0.35, 0.25, 0.12],
            [-0.20, -0.35, 0.08],
            [0.30, -0.25, 0.05],
        ],
        dtype=np.float64,
    )

    identity_directions = np.zeros(
        (
            4,
            3,
            2,
        ),
        dtype=np.float64,
    )

    identity_directions[
        :,
        :,
        0,
    ] = np.array(
        [
            [-0.05, 0.01, 0.00],
            [0.03, -0.01, 0.01],
            [0.01, 0.04, 0.00],
            [0.02, -0.02, -0.01],
        ],
        dtype=np.float64,
    )

    identity_directions[
        :,
        :,
        1,
    ] = np.array(
        [
            [0.01, -0.03, 0.01],
            [-0.04, 0.02, 0.00],
            [0.03, 0.01, 0.01],
            [0.00, -0.02, 0.00],
        ],
        dtype=np.float64,
    )

    return AtlasPortraitFlameCanonicalModel(
        template_vertices=template_vertices,
        triangle_faces=np.array(
            [
                [0, 2, 1],
                [1, 2, 3],
            ],
            dtype=np.int64,
        ),
        identity_shape_directions=identity_directions,
        expression_shape_directions=np.zeros(
            (
                4,
                3,
                1,
            ),
            dtype=np.float64,
        ),
        pose_directions=np.zeros(
            (
                4,
                3,
                9,
            ),
            dtype=np.float64,
        ),
        pose_parameter_count=6,
        joint_regressor=np.array(
            [
                [0.25, 0.25, 0.25, 0.25],
                [0.50, 0.50, 0.00, 0.00],
            ],
            dtype=np.float64,
        ),
        skinning_weights=np.array(
            [
                [1.0, 0.0],
                [1.0, 0.0],
                [1.0, 0.0],
                [1.0, 0.0],
            ],
            dtype=np.float64,
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
            "model_version": "synthetic-fitted-mesh-v1",
            "synthetic": True,
        },
    )


def _camera(
    *,
    error: float,
) -> AtlasPortraitWeakPerspectiveCamera:
    return AtlasPortraitWeakPerspectiveCamera(
        scale=2.5,
        translation_x=0.5,
        translation_y=0.5,
        projected_points_2d=np.array(
            [
                [0.30, 0.40],
                [0.70, 0.40],
                [0.50, 0.60],
            ],
            dtype=np.float64,
        ),
        weighted_root_mean_square_error=error,
        metadata={
            "camera_model": "weak_perspective",
            "synthetic": True,
        },
    )


def _pipeline_result() -> (
    AtlasPortraitFlameDenseIdentityPipelineResult
):
    root_result = AtlasPortraitFlameRootPoseFitResult(
        root_pose_parameters=np.array(
            [
                -0.12,
                0.07,
                0.03,
            ],
            dtype=np.float64,
        ),
        camera=_camera(
            error=0.006
        ),
        initial_weighted_root_mean_square_error=(
            0.010
        ),
        final_weighted_root_mean_square_error=(
            0.006
        ),
        function_evaluation_count=12,
        optimizer_success=True,
        optimizer_status=2,
        optimizer_message="Root fit complete.",
        metadata={
            "fitting_stage": "root_pose",
            "synthetic": True,
        },
    )

    identity_result = AtlasPortraitFlameIdentityFitResult(
        identity_parameters=np.array(
            [
                0.55,
                -0.35,
            ],
            dtype=np.float64,
        ),
        camera=_camera(
            error=0.004
        ),
        initial_weighted_root_mean_square_error=(
            0.006
        ),
        final_weighted_root_mean_square_error=(
            0.004
        ),
        regularization_weight=1.0e-5,
        function_evaluation_count=9,
        optimizer_success=True,
        optimizer_status=2,
        optimizer_message="Identity fit complete.",
        metadata={
            "active_identity_count": 2,
            "fitting_stage": "dense_identity",
            "synthetic": True,
        },
    )

    return AtlasPortraitFlameDenseIdentityPipelineResult(
        root_pose_result=root_result,
        identity_fit_result=identity_result,
        metadata={
            "pipeline": "flame_dense_identity",
            "synthetic": True,
        },
    )


def _expected_image_mesh():
    model = _model()
    pipeline_result = _pipeline_result()

    identity_parameters = (
        pipeline_result.final_identity_parameters
    )

    shaped_vertices = (
        model.template_vertices
        + np.tensordot(
            model.identity_shape_directions,
            identity_parameters,
            axes=(
                2,
                0,
            ),
        )
    )

    root_pose = pipeline_result.final_root_pose_parameters

    angle = float(
        np.linalg.norm(
            root_pose
        )
    )
    axis = root_pose / angle

    skew = np.array(
        [
            [0.0, -axis[2], axis[1]],
            [axis[2], 0.0, -axis[0]],
            [-axis[1], axis[0], 0.0],
        ],
        dtype=np.float64,
    )

    rotation = (
        np.eye(
            3,
            dtype=np.float64,
        )
        + np.sin(
            angle
        )
        * skew
        + (
            1.0
            - np.cos(
                angle
            )
        )
        * (
            skew
            @ skew
        )
    )

    root_joint = (
        model.joint_regressor[
            0
        ]
        @ shaped_vertices
    )

    rotated_vertices = (
        rotation
        @ (
            shaped_vertices
            - root_joint
        ).T
    ).T + root_joint

    image_vertices = rotated_vertices.copy()
    image_vertices[
        :,
        1
    ] *= -1.0

    image_faces = model.triangle_faces[
        :,
        [
            0,
            2,
            1,
        ],
    ].copy()

    return (
        image_vertices,
        image_faces,
    )


def test_builder_returns_deformed_mesh():
    result = AtlasPortraitFlameFittedMeshBuilder.build(
        _model(),
        pipeline_result=_pipeline_result(),
    )

    assert isinstance(
        result,
        AtlasPortraitFlameDeformedMesh,
    )


def test_builder_applies_fitted_identity_and_root_pose():
    result = AtlasPortraitFlameFittedMeshBuilder.build(
        _model(),
        pipeline_result=_pipeline_result(),
    )

    expected_vertices, _ = _expected_image_mesh()

    np.testing.assert_allclose(
        result.vertices,
        expected_vertices,
        rtol=0.0,
        atol=1.0e-12,
    )


def test_builder_normalizes_mesh_to_image_coordinates():
    result = AtlasPortraitFlameFittedMeshBuilder.build(
        _model(),
        pipeline_result=_pipeline_result(),
    )

    _, expected_faces = _expected_image_mesh()

    np.testing.assert_array_equal(
        result.triangle_faces,
        expected_faces,
    )


def test_builder_preserves_model_topology_count():
    model = _model()

    result = AtlasPortraitFlameFittedMeshBuilder.build(
        model,
        pipeline_result=_pipeline_result(),
    )

    assert result.vertex_count == model.vertex_count
    assert result.face_count == model.triangle_count


def test_builder_returns_immutable_independent_arrays():
    model = _model()

    result = AtlasPortraitFlameFittedMeshBuilder.build(
        model,
        pipeline_result=_pipeline_result(),
    )

    assert result.vertices.flags.writeable is False
    assert result.triangle_faces.flags.writeable is False
    assert not np.shares_memory(
        result.vertices,
        model.template_vertices,
    )
    assert not np.shares_memory(
        result.triangle_faces,
        model.triangle_faces,
    )


def test_builder_does_not_modify_inputs():
    model = _model()
    pipeline_result = _pipeline_result()

    model_before = model.to_dict()
    pipeline_before = pipeline_result.to_dict()

    AtlasPortraitFlameFittedMeshBuilder.build(
        model,
        pipeline_result=pipeline_result,
    )

    assert model.to_dict() == model_before
    assert pipeline_result.to_dict() == pipeline_before


def test_builder_is_deterministic():
    first = AtlasPortraitFlameFittedMeshBuilder.build(
        _model(),
        pipeline_result=_pipeline_result(),
    )
    second = AtlasPortraitFlameFittedMeshBuilder.build(
        _model(),
        pipeline_result=_pipeline_result(),
    )

    np.testing.assert_array_equal(
        first.vertices,
        second.vertices,
    )
    np.testing.assert_array_equal(
        first.triangle_faces,
        second.triangle_faces,
    )


def test_builder_rejects_wrong_model_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameCanonicalModel",
    ):
        AtlasPortraitFlameFittedMeshBuilder.build(
            object(),
            pipeline_result=_pipeline_result(),
        )


def test_builder_rejects_wrong_pipeline_result_type():
    with pytest.raises(
        TypeError,
        match=(
            "AtlasPortraitFlameDenseIdentityPipelineResult"
        ),
    ):
        AtlasPortraitFlameFittedMeshBuilder.build(
            _model(),
            pipeline_result=object(),
        )


def test_builder_rejects_identity_parameter_count_mismatch():
    model = _model()
    pipeline_result = _pipeline_result()

    incompatible_model = AtlasPortraitFlameCanonicalModel(
        template_vertices=model.template_vertices,
        triangle_faces=model.triangle_faces,
        identity_shape_directions=np.zeros(
            (
                model.vertex_count,
                3,
                3,
            ),
            dtype=np.float64,
        ),
        expression_shape_directions=(
            model.expression_shape_directions
        ),
        pose_directions=model.pose_directions,
        pose_parameter_count=model.pose_parameter_count,
        joint_regressor=model.joint_regressor,
        skinning_weights=model.skinning_weights,
        kinematic_tree=model.kinematic_tree,
        metadata=model.metadata,
    )

    with pytest.raises(
        ValueError,
        match="identity parameter count",
    ):
        AtlasPortraitFlameFittedMeshBuilder.build(
            incompatible_model,
            pipeline_result=pipeline_result,
        )


def test_builder_rejects_model_without_root_pose_capacity():
    model = _model()

    invalid_model = AtlasPortraitFlameCanonicalModel(
        template_vertices=model.template_vertices,
        triangle_faces=model.triangle_faces,
        identity_shape_directions=(
            model.identity_shape_directions
        ),
        expression_shape_directions=(
            model.expression_shape_directions
        ),
        pose_directions=np.zeros(
            (
                model.vertex_count,
                3,
                3,
            ),
            dtype=np.float64,
        ),
        pose_parameter_count=3,
        joint_regressor=np.array(
            [
                [0.25, 0.25, 0.25, 0.25],
            ],
            dtype=np.float64,
        ),
        skinning_weights=np.ones(
            (
                model.vertex_count,
                1,
            ),
            dtype=np.float64,
        ),
        kinematic_tree=np.array(
            [
                -1,
            ],
            dtype=np.int64,
        ),
        metadata=model.metadata,
    )

    with pytest.raises(
        ValueError,
        match="at least two",
    ):
        AtlasPortraitFlameFittedMeshBuilder.build(
            invalid_model,
            pipeline_result=_pipeline_result(),
        )
