from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_fitting_parameters import (
    AtlasPortraitFlameFittingParameters,
)
from CORE.atlas_portrait_flame_pose_feature_evaluator import (
    AtlasPortraitFlamePoseFeatureEvaluator,
)


def _parameters(
    pose_parameters: np.ndarray,
) -> AtlasPortraitFlameFittingParameters:
    return AtlasPortraitFlameFittingParameters(
        identity_parameters=np.zeros(
            2,
            dtype=np.float64,
        ),
        expression_parameters=np.zeros(
            1,
            dtype=np.float64,
        ),
        pose_parameters=pose_parameters,
        metadata={
            "fitting_stage": "synthetic_test",
            "synthetic": True,
        },
    )


def test_evaluator_returns_zero_features_for_neutral_pose():
    parameters = _parameters(
        np.zeros(
            6,
            dtype=np.float64,
        ),
    )

    result = AtlasPortraitFlamePoseFeatureEvaluator.evaluate(
        parameters,
    )

    assert np.array_equal(
        result,
        np.zeros(
            9,
            dtype=np.float64,
        ),
    )


def test_evaluator_excludes_root_rotation():
    parameters = _parameters(
        np.array(
            [
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

    result = AtlasPortraitFlamePoseFeatureEvaluator.evaluate(
        parameters,
    )

    assert np.array_equal(
        result,
        np.zeros(
            9,
            dtype=np.float64,
        ),
    )


def test_evaluator_converts_child_axis_angle_to_pose_feature():
    parameters = _parameters(
        np.array(
            [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                np.pi / 2.0,
            ],
            dtype=np.float64,
        ),
    )

    result = AtlasPortraitFlamePoseFeatureEvaluator.evaluate(
        parameters,
    )

    expected_rotation = np.array(
        [
            [0.0, -1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )

    expected = (
        expected_rotation
        - np.eye(
            3,
            dtype=np.float64,
        )
    ).reshape(
        -1,
    )

    assert np.allclose(
        result,
        expected,
        rtol=0.0,
        atol=1.0e-12,
    )


def test_evaluator_preserves_joint_order():
    parameters = _parameters(
        np.array(
            [
                0.0,
                0.0,
                0.0,
                np.pi / 2.0,
                0.0,
                0.0,
                0.0,
                np.pi / 2.0,
                0.0,
            ],
            dtype=np.float64,
        ),
    )

    result = AtlasPortraitFlamePoseFeatureEvaluator.evaluate(
        parameters,
    )

    first_child_rotation = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 0.0, -1.0],
            [0.0, 1.0, 0.0],
        ],
        dtype=np.float64,
    )

    second_child_rotation = np.array(
        [
            [0.0, 0.0, 1.0],
            [0.0, 1.0, 0.0],
            [-1.0, 0.0, 0.0],
        ],
        dtype=np.float64,
    )

    expected = np.concatenate(
        [
            (
                first_child_rotation
                - np.eye(
                    3,
                    dtype=np.float64,
                )
            ).reshape(
                -1,
            ),
            (
                second_child_rotation
                - np.eye(
                    3,
                    dtype=np.float64,
                )
            ).reshape(
                -1,
            ),
        ]
    )

    assert np.allclose(
        result,
        expected,
        rtol=0.0,
        atol=1.0e-12,
    )


def test_evaluator_supports_small_axis_angles():
    angle = 1.0e-10

    parameters = _parameters(
        np.array(
            [
                0.0,
                0.0,
                0.0,
                angle,
                0.0,
                0.0,
            ],
            dtype=np.float64,
        ),
    )

    result = AtlasPortraitFlamePoseFeatureEvaluator.evaluate(
        parameters,
    )

    assert np.isfinite(
        result,
    ).all()

    assert result.shape == (
        9,
    )

    assert np.linalg.norm(
        result,
    ) > 0.0


def test_evaluator_result_is_float64_and_read_only():
    result = AtlasPortraitFlamePoseFeatureEvaluator.evaluate(
        _parameters(
            np.zeros(
                6,
                dtype=np.float64,
            ),
        ),
    )

    assert result.dtype == np.float64
    assert result.flags.writeable is False

    with pytest.raises(
        ValueError,
    ):
        result[
            0
        ] = 1.0


def test_evaluator_returns_independent_results():
    parameters = _parameters(
        np.zeros(
            6,
            dtype=np.float64,
        ),
    )

    first = AtlasPortraitFlamePoseFeatureEvaluator.evaluate(
        parameters,
    )

    second = AtlasPortraitFlamePoseFeatureEvaluator.evaluate(
        parameters,
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


def test_evaluator_does_not_modify_parameters():
    parameters = _parameters(
        np.array(
            [
                0.1,
                -0.2,
                0.3,
                0.4,
                -0.5,
                0.6,
            ],
            dtype=np.float64,
        ),
    )

    before = parameters.to_dict()

    AtlasPortraitFlamePoseFeatureEvaluator.evaluate(
        parameters,
    )

    assert parameters.to_dict() == before


def test_evaluator_rejects_wrong_parameter_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameFittingParameters",
    ):
        AtlasPortraitFlamePoseFeatureEvaluator.evaluate(
            object(),
        )


@pytest.mark.parametrize(
    "pose_parameter_count",
    [
        1,
        2,
        3,
        4,
        5,
        7,
    ],
)
def test_evaluator_rejects_invalid_pose_parameter_layout(
    pose_parameter_count,
):
    parameters = _parameters(
        np.zeros(
            pose_parameter_count,
            dtype=np.float64,
        ),
    )

    with pytest.raises(
        ValueError,
        match="pose parameter count",
    ):
        AtlasPortraitFlamePoseFeatureEvaluator.evaluate(
            parameters,
        )
