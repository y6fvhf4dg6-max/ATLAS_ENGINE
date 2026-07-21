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


def _canonical_model() -> AtlasPortraitFlameCanonicalModel:
    template_vertices = np.array(
        [
            [-1.0, 1.0, 0.0],
            [1.0, 1.0, 0.0],
            [-1.0, -1.0, 0.0],
            [1.0, -1.0, 0.0],
        ],
        dtype=np.float64,
    )

    triangle_faces = np.array(
        [
            [0, 2, 1],
            [1, 2, 3],
        ],
        dtype=np.int64,
    )

    identity_shape_directions = np.zeros(
        (
            4,
            3,
            2,
        ),
        dtype=np.float64,
    )

    identity_shape_directions[
        :,
        0,
        0,
    ] = np.array(
        [
            -0.10,
            0.10,
            -0.10,
            0.10,
        ],
        dtype=np.float64,
    )

    identity_shape_directions[
        :,
        1,
        1,
    ] = np.array(
        [
            0.20,
            0.20,
            -0.20,
            -0.20,
        ],
        dtype=np.float64,
    )

    expression_shape_directions = np.zeros(
        (
            4,
            3,
            1,
        ),
        dtype=np.float64,
    )

    expression_shape_directions[
        :,
        2,
        0,
    ] = np.array(
        [
            0.00,
            0.00,
            0.30,
            0.30,
        ],
        dtype=np.float64,
    )

    pose_directions = np.zeros(
        (
            4,
            3,
            3,
        ),
        dtype=np.float64,
    )

    joint_regressor = np.array(
        [
            [0.25, 0.25, 0.25, 0.25],
            [0.50, 0.50, 0.00, 0.00],
        ],
        dtype=np.float64,
    )

    skinning_weights = np.array(
        [
            [1.0, 0.0],
            [1.0, 0.0],
            [0.5, 0.5],
            [0.5, 0.5],
        ],
        dtype=np.float64,
    )

    kinematic_tree = np.array(
        [
            -1,
            0,
        ],
        dtype=np.int64,
    )

    return AtlasPortraitFlameCanonicalModel(
        template_vertices=template_vertices,
        triangle_faces=triangle_faces,
        identity_shape_directions=(
            identity_shape_directions
        ),
        expression_shape_directions=(
            expression_shape_directions
        ),
        pose_directions=pose_directions,
        joint_regressor=joint_regressor,
        skinning_weights=skinning_weights,
        kinematic_tree=kinematic_tree,
        metadata={
            "model_family": "flame",
            "model_version": "synthetic-v1",
            "synthetic": True,
        },
    )


def _parameters(
    *,
    identity_parameters=None,
    expression_parameters=None,
    pose_parameters=None,
) -> AtlasPortraitFlameFittingParameters:
    if identity_parameters is None:
        identity_parameters = np.array(
            [
                0.0,
                0.0,
            ],
            dtype=np.float64,
        )

    if expression_parameters is None:
        expression_parameters = np.array(
            [
                0.0,
            ],
            dtype=np.float64,
        )

    if pose_parameters is None:
        pose_parameters = np.array(
            [
                0.0,
                0.0,
                0.0,
            ],
            dtype=np.float64,
        )

    return AtlasPortraitFlameFittingParameters(
        identity_parameters=identity_parameters,
        expression_parameters=expression_parameters,
        pose_parameters=pose_parameters,
        metadata={
            "fitting_stage": "synthetic_test",
            "synthetic": True,
        },
    )


def test_evaluator_returns_template_for_zero_parameters():
    model = _canonical_model()

    result = AtlasPortraitFlameBlendshapeEvaluator.evaluate(
        model,
        parameters=_parameters(),
    )

    assert np.array_equal(
        result,
        model.template_vertices,
    )


def test_evaluator_applies_identity_parameters():
    model = _canonical_model()

    result = AtlasPortraitFlameBlendshapeEvaluator.evaluate(
        model,
        parameters=_parameters(
            identity_parameters=np.array(
                [
                    2.0,
                    -0.5,
                ],
                dtype=np.float64,
            ),
        ),
    )

    expected = np.array(
        [
            [-1.20, 0.90, 0.00],
            [1.20, 0.90, 0.00],
            [-1.20, -0.90, 0.00],
            [1.20, -0.90, 0.00],
        ],
        dtype=np.float64,
    )

    assert np.allclose(
        result,
        expected,
        rtol=0.0,
        atol=1.0e-12,
    )


def test_evaluator_applies_expression_parameters():
    model = _canonical_model()

    result = AtlasPortraitFlameBlendshapeEvaluator.evaluate(
        model,
        parameters=_parameters(
            expression_parameters=np.array(
                [
                    0.5,
                ],
                dtype=np.float64,
            ),
        ),
    )

    expected = np.array(
        [
            [-1.0, 1.0, 0.00],
            [1.0, 1.0, 0.00],
            [-1.0, -1.0, 0.15],
            [1.0, -1.0, 0.15],
        ],
        dtype=np.float64,
    )

    assert np.allclose(
        result,
        expected,
        rtol=0.0,
        atol=1.0e-12,
    )


def test_evaluator_combines_identity_and_expression():
    model = _canonical_model()

    result = AtlasPortraitFlameBlendshapeEvaluator.evaluate(
        model,
        parameters=_parameters(
            identity_parameters=np.array(
                [
                    1.0,
                    0.5,
                ],
                dtype=np.float64,
            ),
            expression_parameters=np.array(
                [
                    -1.0,
                ],
                dtype=np.float64,
            ),
        ),
    )

    expected = np.array(
        [
            [-1.10, 1.10, 0.00],
            [1.10, 1.10, 0.00],
            [-1.10, -1.10, -0.30],
            [1.10, -1.10, -0.30],
        ],
        dtype=np.float64,
    )

    assert np.allclose(
        result,
        expected,
        rtol=0.0,
        atol=1.0e-12,
    )


def test_evaluator_does_not_apply_pose_parameters():
    model = _canonical_model()

    neutral = AtlasPortraitFlameBlendshapeEvaluator.evaluate(
        model,
        parameters=_parameters(),
    )

    posed = AtlasPortraitFlameBlendshapeEvaluator.evaluate(
        model,
        parameters=_parameters(
            pose_parameters=np.array(
                [
                    10.0,
                    -5.0,
                    2.0,
                ],
                dtype=np.float64,
            ),
        ),
    )

    assert np.array_equal(
        neutral,
        posed,
    )


def test_evaluator_result_has_expected_shape_and_dtype():
    result = AtlasPortraitFlameBlendshapeEvaluator.evaluate(
        _canonical_model(),
        parameters=_parameters(),
    )

    assert result.shape == (
        4,
        3,
    )
    assert result.dtype == np.float64


def test_evaluator_result_is_read_only():
    result = AtlasPortraitFlameBlendshapeEvaluator.evaluate(
        _canonical_model(),
        parameters=_parameters(),
    )

    assert result.flags.writeable is False

    with pytest.raises(
        ValueError,
    ):
        result[
            0,
            0,
        ] = 99.0


def test_evaluator_returns_independent_results():
    model = _canonical_model()
    parameters = _parameters()

    first = AtlasPortraitFlameBlendshapeEvaluator.evaluate(
        model,
        parameters=parameters,
    )

    second = AtlasPortraitFlameBlendshapeEvaluator.evaluate(
        model,
        parameters=parameters,
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


def test_evaluator_does_not_modify_model_or_parameters():
    model = _canonical_model()
    parameters = _parameters(
        identity_parameters=np.array(
            [
                0.5,
                -0.25,
            ],
            dtype=np.float64,
        ),
        expression_parameters=np.array(
            [
                0.75,
            ],
            dtype=np.float64,
        ),
    )

    model_before = model.to_dict()
    parameters_before = parameters.to_dict()

    AtlasPortraitFlameBlendshapeEvaluator.evaluate(
        model,
        parameters=parameters,
    )

    assert model.to_dict() == model_before
    assert parameters.to_dict() == parameters_before


def test_evaluator_rejects_wrong_model_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameCanonicalModel",
    ):
        AtlasPortraitFlameBlendshapeEvaluator.evaluate(
            object(),
            parameters=_parameters(),
        )


def test_evaluator_rejects_wrong_parameters_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameFittingParameters",
    ):
        AtlasPortraitFlameBlendshapeEvaluator.evaluate(
            _canonical_model(),
            parameters=object(),
        )


def test_evaluator_rejects_identity_parameter_count_mismatch():
    with pytest.raises(
        ValueError,
        match="identity parameter count",
    ):
        AtlasPortraitFlameBlendshapeEvaluator.evaluate(
            _canonical_model(),
            parameters=_parameters(
                identity_parameters=np.zeros(
                    3,
                    dtype=np.float64,
                ),
            ),
        )


def test_evaluator_rejects_expression_parameter_count_mismatch():
    with pytest.raises(
        ValueError,
        match="expression parameter count",
    ):
        AtlasPortraitFlameBlendshapeEvaluator.evaluate(
            _canonical_model(),
            parameters=_parameters(
                expression_parameters=np.zeros(
                    2,
                    dtype=np.float64,
                ),
            ),
        )


def test_evaluator_rejects_pose_parameter_count_mismatch():
    with pytest.raises(
        ValueError,
        match="pose parameter count",
    ):
        AtlasPortraitFlameBlendshapeEvaluator.evaluate(
            _canonical_model(),
            parameters=_parameters(
                pose_parameters=np.zeros(
                    4,
                    dtype=np.float64,
                ),
            ),
        )
