from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)
from CORE.atlas_portrait_flame_joint_regressor_evaluator import (
    AtlasPortraitFlameJointRegressorEvaluator,
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
                9,
            ),
            dtype=np.float64,
        ),
        pose_parameter_count=6,
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
                0,
            ],
            dtype=np.int64,
        ),
        metadata={
            "model_family": "flame",
            "model_version": "synthetic-v1",
            "synthetic": True,
        },
    )


def _shaped_vertices() -> np.ndarray:
    return np.array(
        [
            [-2.0, 2.0, 0.0],
            [2.0, 2.0, 0.0],
            [-1.0, -2.0, 1.0],
            [1.0, -2.0, 1.0],
        ],
        dtype=np.float64,
    )


def test_evaluator_returns_expected_joint_positions():
    result = AtlasPortraitFlameJointRegressorEvaluator.evaluate(
        _canonical_model(),
        shaped_vertices=_shaped_vertices(),
    )

    expected = np.array(
        [
            [0.0, 0.0, 0.5],
            [0.0, 2.0, 0.0],
            [0.0, -2.0, 1.0],
        ],
        dtype=np.float64,
    )

    assert np.allclose(
        result,
        expected,
        rtol=0.0,
        atol=1.0e-12,
    )


def test_evaluator_uses_model_joint_count():
    result = AtlasPortraitFlameJointRegressorEvaluator.evaluate(
        _canonical_model(),
        shaped_vertices=_shaped_vertices(),
    )

    assert result.shape == (
        3,
        3,
    )


def test_evaluator_result_is_float64():
    result = AtlasPortraitFlameJointRegressorEvaluator.evaluate(
        _canonical_model(),
        shaped_vertices=_shaped_vertices(),
    )

    assert result.dtype == np.float64


def test_evaluator_result_is_read_only():
    result = AtlasPortraitFlameJointRegressorEvaluator.evaluate(
        _canonical_model(),
        shaped_vertices=_shaped_vertices(),
    )

    assert result.flags.writeable is False

    with pytest.raises(
        ValueError,
    ):
        result[
            0,
            0,
        ] = 1.0


def test_evaluator_returns_independent_results():
    model = _canonical_model()
    vertices = _shaped_vertices()

    first = AtlasPortraitFlameJointRegressorEvaluator.evaluate(
        model,
        shaped_vertices=vertices,
    )

    second = AtlasPortraitFlameJointRegressorEvaluator.evaluate(
        model,
        shaped_vertices=vertices,
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


def test_evaluator_does_not_modify_model_or_vertices():
    model = _canonical_model()
    vertices = _shaped_vertices()

    model_before = model.to_dict()
    vertices_before = vertices.copy()

    AtlasPortraitFlameJointRegressorEvaluator.evaluate(
        model,
        shaped_vertices=vertices,
    )

    assert model.to_dict() == model_before
    assert np.array_equal(
        vertices,
        vertices_before,
    )


def test_evaluator_rejects_wrong_model_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameCanonicalModel",
    ):
        AtlasPortraitFlameJointRegressorEvaluator.evaluate(
            object(),
            shaped_vertices=_shaped_vertices(),
        )


@pytest.mark.parametrize(
    "shaped_vertices",
    [
        np.zeros(
            (
                4,
                2,
            ),
            dtype=np.float64,
        ),
        np.zeros(
            (
                3,
                3,
            ),
            dtype=np.float64,
        ),
        np.zeros(
            (
                4,
                3,
                1,
            ),
            dtype=np.float64,
        ),
    ],
)
def test_evaluator_rejects_invalid_vertex_shape(
    shaped_vertices,
):
    with pytest.raises(
        ValueError,
        match="shaped_vertices",
    ):
        AtlasPortraitFlameJointRegressorEvaluator.evaluate(
            _canonical_model(),
            shaped_vertices=shaped_vertices,
        )


def test_evaluator_rejects_non_numeric_vertices():
    with pytest.raises(
        ValueError,
        match="shaped_vertices",
    ):
        AtlasPortraitFlameJointRegressorEvaluator.evaluate(
            _canonical_model(),
            shaped_vertices=[
                [
                    "invalid",
                    "invalid",
                    "invalid",
                ],
            ]
            * 4,
        )


def test_evaluator_rejects_non_finite_vertices():
    vertices = _shaped_vertices()

    vertices[
        0,
        0,
    ] = np.nan

    with pytest.raises(
        ValueError,
        match="shaped_vertices",
    ):
        AtlasPortraitFlameJointRegressorEvaluator.evaluate(
            _canonical_model(),
            shaped_vertices=vertices,
        )
