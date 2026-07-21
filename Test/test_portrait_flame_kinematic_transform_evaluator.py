from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)
from CORE.atlas_portrait_flame_kinematic_transform_evaluator import (
    AtlasPortraitFlameKinematicTransformEvaluator,
)


def _canonical_model() -> AtlasPortraitFlameCanonicalModel:
    return AtlasPortraitFlameCanonicalModel(
        template_vertices=np.array(
            [
                [-1.0, 1.0, 0.0],
                [1.0, 1.0, 0.0],
                [-1.0, -1.0, 0.0],
                [1.0, -1.0, 0.0],
            ],
            dtype=np.float64,
        ),
        triangle_faces=np.array(
            [
                [0, 2, 1],
                [1, 2, 3],
            ],
            dtype=np.int64,
        ),
        identity_shape_directions=np.zeros(
            (
                4,
                3,
                2,
            ),
            dtype=np.float64,
        ),
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
                18,
            ),
            dtype=np.float64,
        ),
        pose_parameter_count=9,
        joint_regressor=np.array(
            [
                [0.25, 0.25, 0.25, 0.25],
                [0.50, 0.50, 0.00, 0.00],
                [0.00, 0.00, 0.50, 0.50],
            ],
            dtype=np.float64,
        ),
        skinning_weights=np.array(
            [
                [1.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.5, 0.5, 0.0],
                [0.5, 0.0, 0.5],
            ],
            dtype=np.float64,
        ),
        kinematic_tree=np.array(
            [
                -1,
                0,
                1,
            ],
            dtype=np.int64,
        ),
        metadata={
            "model_family": "flame",
            "model_version": "synthetic-v1",
            "synthetic": True,
        },
    )


def _joint_positions() -> np.ndarray:
    return np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [2.0, 0.0, 0.0],
        ],
        dtype=np.float64,
    )


def test_evaluator_returns_identity_transforms_for_zero_pose():
    result = AtlasPortraitFlameKinematicTransformEvaluator.evaluate(
        _canonical_model(),
        joint_positions=_joint_positions(),
        pose_parameters=np.zeros(
            9,
            dtype=np.float64,
        ),
    )

    expected = np.repeat(
        np.eye(
            4,
            dtype=np.float64,
        )[None, :, :],
        repeats=3,
        axis=0,
    )

    assert np.allclose(
        result,
        expected,
        rtol=0.0,
        atol=1.0e-12,
    )


def test_evaluator_applies_root_rotation():
    result = AtlasPortraitFlameKinematicTransformEvaluator.evaluate(
        _canonical_model(),
        joint_positions=_joint_positions(),
        pose_parameters=np.array(
            [
                0.0,
                0.0,
                np.pi / 2.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ],
            dtype=np.float64,
        ),
    )

    expected_rotation = np.array(
        [
            [0.0, -1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )

    assert np.allclose(
        result[
            0,
            :3,
            :3,
        ],
        expected_rotation,
        rtol=0.0,
        atol=1.0e-12,
    )


def test_evaluator_accumulates_parent_and_child_rotations():
    result = AtlasPortraitFlameKinematicTransformEvaluator.evaluate(
        _canonical_model(),
        joint_positions=_joint_positions(),
        pose_parameters=np.array(
            [
                0.0,
                0.0,
                np.pi / 2.0,
                0.0,
                0.0,
                np.pi / 2.0,
                0.0,
                0.0,
                0.0,
            ],
            dtype=np.float64,
        ),
    )

    expected_child_rotation = np.array(
        [
            [-1.0, 0.0, 0.0],
            [0.0, -1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )

    assert np.allclose(
        result[
            1,
            :3,
            :3,
        ],
        expected_child_rotation,
        rtol=0.0,
        atol=1.0e-12,
    )


def test_evaluator_preserves_homogeneous_bottom_row():
    result = AtlasPortraitFlameKinematicTransformEvaluator.evaluate(
        _canonical_model(),
        joint_positions=_joint_positions(),
        pose_parameters=np.zeros(
            9,
            dtype=np.float64,
        ),
    )

    expected = np.array(
        [
            0.0,
            0.0,
            0.0,
            1.0,
        ],
        dtype=np.float64,
    )

    assert np.array_equal(
        result[
            :,
            3,
            :,
        ],
        np.repeat(
            expected[None, :],
            repeats=3,
            axis=0,
        ),
    )


def test_evaluator_uses_model_joint_count():
    result = AtlasPortraitFlameKinematicTransformEvaluator.evaluate(
        _canonical_model(),
        joint_positions=_joint_positions(),
        pose_parameters=np.zeros(
            9,
            dtype=np.float64,
        ),
    )

    assert result.shape == (
        3,
        4,
        4,
    )


def test_evaluator_result_is_float64():
    result = AtlasPortraitFlameKinematicTransformEvaluator.evaluate(
        _canonical_model(),
        joint_positions=_joint_positions(),
        pose_parameters=np.zeros(
            9,
            dtype=np.float64,
        ),
    )

    assert result.dtype == np.float64


def test_evaluator_result_is_read_only():
    result = AtlasPortraitFlameKinematicTransformEvaluator.evaluate(
        _canonical_model(),
        joint_positions=_joint_positions(),
        pose_parameters=np.zeros(
            9,
            dtype=np.float64,
        ),
    )

    assert result.flags.writeable is False

    with pytest.raises(
        ValueError,
    ):
        result[
            0,
            0,
            0,
        ] = 2.0


def test_evaluator_returns_independent_results():
    model = _canonical_model()
    joints = _joint_positions()
    pose = np.zeros(
        9,
        dtype=np.float64,
    )

    first = AtlasPortraitFlameKinematicTransformEvaluator.evaluate(
        model,
        joint_positions=joints,
        pose_parameters=pose,
    )

    second = AtlasPortraitFlameKinematicTransformEvaluator.evaluate(
        model,
        joint_positions=joints,
        pose_parameters=pose,
    )

    assert first is not second
    assert not np.shares_memory(
        first,
        second,
    )
    assert np.array_equal(
        first,
        second,
    )


def test_evaluator_does_not_modify_model_or_inputs():
    model = _canonical_model()
    joints = _joint_positions()
    pose = np.zeros(
        9,
        dtype=np.float64,
    )

    model_before = model.to_dict()
    joints_before = joints.copy()
    pose_before = pose.copy()

    AtlasPortraitFlameKinematicTransformEvaluator.evaluate(
        model,
        joint_positions=joints,
        pose_parameters=pose,
    )

    assert model.to_dict() == model_before
    assert np.array_equal(
        joints,
        joints_before,
    )
    assert np.array_equal(
        pose,
        pose_before,
    )


def test_evaluator_rejects_wrong_model_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameCanonicalModel",
    ):
        AtlasPortraitFlameKinematicTransformEvaluator.evaluate(
            object(),
            joint_positions=_joint_positions(),
            pose_parameters=np.zeros(
                9,
                dtype=np.float64,
            ),
        )


@pytest.mark.parametrize(
    "joint_positions",
    [
        np.zeros(
            (
                3,
                2,
            ),
            dtype=np.float64,
        ),
        np.zeros(
            (
                2,
                3,
            ),
            dtype=np.float64,
        ),
        np.zeros(
            (
                3,
                3,
                1,
            ),
            dtype=np.float64,
        ),
    ],
)
def test_evaluator_rejects_invalid_joint_position_shape(
    joint_positions,
):
    with pytest.raises(
        ValueError,
        match="joint_positions",
    ):
        AtlasPortraitFlameKinematicTransformEvaluator.evaluate(
            _canonical_model(),
            joint_positions=joint_positions,
            pose_parameters=np.zeros(
                9,
                dtype=np.float64,
            ),
        )


@pytest.mark.parametrize(
    "pose_parameters",
    [
        np.zeros(
            8,
            dtype=np.float64,
        ),
        np.zeros(
            10,
            dtype=np.float64,
        ),
        np.zeros(
            (
                3,
                3,
            ),
            dtype=np.float64,
        ),
    ],
)
def test_evaluator_rejects_invalid_pose_parameter_shape(
    pose_parameters,
):
    with pytest.raises(
        ValueError,
        match="pose_parameters",
    ):
        AtlasPortraitFlameKinematicTransformEvaluator.evaluate(
            _canonical_model(),
            joint_positions=_joint_positions(),
            pose_parameters=pose_parameters,
        )


@pytest.mark.parametrize(
    (
        "argument_name",
        "joint_positions",
        "pose_parameters",
    ),
    [
        (
            "joint_positions",
            [
                [
                    "invalid",
                    "invalid",
                    "invalid",
                ],
            ]
            * 3,
            np.zeros(
                9,
                dtype=np.float64,
            ),
        ),
        (
            "pose_parameters",
            _joint_positions(),
            [
                "invalid",
            ]
            * 9,
        ),
    ],
)
def test_evaluator_rejects_non_numeric_inputs(
    argument_name,
    joint_positions,
    pose_parameters,
):
    with pytest.raises(
        ValueError,
        match=argument_name,
    ):
        AtlasPortraitFlameKinematicTransformEvaluator.evaluate(
            _canonical_model(),
            joint_positions=joint_positions,
            pose_parameters=pose_parameters,
        )


@pytest.mark.parametrize(
    "argument_name",
    [
        "joint_positions",
        "pose_parameters",
    ],
)
def test_evaluator_rejects_non_finite_inputs(
    argument_name,
):
    joints = _joint_positions()
    pose = np.zeros(
        9,
        dtype=np.float64,
    )

    if argument_name == "joint_positions":
        joints[
            0,
            0,
        ] = np.nan
    else:
        pose[
            0,
        ] = np.inf

    with pytest.raises(
        ValueError,
        match=argument_name,
    ):
        AtlasPortraitFlameKinematicTransformEvaluator.evaluate(
            _canonical_model(),
            joint_positions=joints,
            pose_parameters=pose,
        )
