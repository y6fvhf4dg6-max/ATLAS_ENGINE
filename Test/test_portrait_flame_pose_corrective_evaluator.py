from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)
from CORE.atlas_portrait_flame_pose_corrective_evaluator import (
    AtlasPortraitFlamePoseCorrectiveEvaluator,
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

    expression_shape_directions = np.zeros(
        (
            4,
            3,
            1,
        ),
        dtype=np.float64,
    )

    pose_directions = np.zeros(
        (
            4,
            3,
            9,
        ),
        dtype=np.float64,
    )

    pose_directions[
        0,
        0,
        0,
    ] = 0.10

    pose_directions[
        1,
        1,
        1,
    ] = -0.20

    pose_directions[
        2,
        2,
        2,
    ] = 0.30

    pose_directions[
        3,
        0,
        3,
    ] = 0.40

    pose_directions[
        3,
        2,
        8,
    ] = -0.50

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
        pose_parameter_count=6,
        joint_regressor=joint_regressor,
        skinning_weights=skinning_weights,
        kinematic_tree=kinematic_tree,
        metadata={
            "model_family": "flame",
            "model_version": "synthetic-v1",
            "synthetic": True,
        },
    )


def test_evaluator_returns_zero_offsets_for_zero_features():
    model = _canonical_model()

    result = AtlasPortraitFlamePoseCorrectiveEvaluator.evaluate(
        model,
        pose_features=np.zeros(
            9,
            dtype=np.float64,
        ),
    )

    assert np.array_equal(
        result,
        np.zeros(
            (
                4,
                3,
            ),
            dtype=np.float64,
        ),
    )


def test_evaluator_applies_pose_features():
    model = _canonical_model()

    pose_features = np.array(
        [
            2.0,
            -3.0,
            4.0,
            0.5,
            0.0,
            0.0,
            0.0,
            0.0,
            -2.0,
        ],
        dtype=np.float64,
    )

    result = AtlasPortraitFlamePoseCorrectiveEvaluator.evaluate(
        model,
        pose_features=pose_features,
    )

    expected = np.array(
        [
            [0.20, 0.00, 0.00],
            [0.00, 0.60, 0.00],
            [0.00, 0.00, 1.20],
            [0.20, 0.00, 1.00],
        ],
        dtype=np.float64,
    )

    assert np.allclose(
        result,
        expected,
        rtol=0.0,
        atol=1.0e-12,
    )


def test_evaluator_combines_multiple_features_per_vertex():
    model = _canonical_model()

    pose_directions = np.array(
        model.pose_directions,
        copy=True,
    )

    pose_directions[
        0,
        0,
        1,
    ] = 0.25

    model = AtlasPortraitFlameCanonicalModel(
        template_vertices=model.template_vertices,
        triangle_faces=model.triangle_faces,
        identity_shape_directions=(
            model.identity_shape_directions
        ),
        expression_shape_directions=(
            model.expression_shape_directions
        ),
        pose_directions=pose_directions,
        pose_parameter_count=model.pose_parameter_count,
        joint_regressor=model.joint_regressor,
        skinning_weights=model.skinning_weights,
        kinematic_tree=model.kinematic_tree,
        metadata=model.metadata,
    )

    pose_features = np.zeros(
        9,
        dtype=np.float64,
    )

    pose_features[
        0
    ] = 2.0

    pose_features[
        1
    ] = 4.0

    result = AtlasPortraitFlamePoseCorrectiveEvaluator.evaluate(
        model,
        pose_features=pose_features,
    )

    assert np.isclose(
        result[
            0,
            0,
        ],
        1.20,
        rtol=0.0,
        atol=1.0e-12,
    )


def test_evaluator_result_has_expected_shape_and_dtype():
    result = AtlasPortraitFlamePoseCorrectiveEvaluator.evaluate(
        _canonical_model(),
        pose_features=np.zeros(
            9,
            dtype=np.float64,
        ),
    )

    assert result.shape == (
        4,
        3,
    )
    assert result.dtype == np.float64


def test_evaluator_result_is_read_only():
    result = AtlasPortraitFlamePoseCorrectiveEvaluator.evaluate(
        _canonical_model(),
        pose_features=np.zeros(
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
        ] = 1.0


def test_evaluator_returns_independent_results():
    model = _canonical_model()

    pose_features = np.zeros(
        9,
        dtype=np.float64,
    )

    first = AtlasPortraitFlamePoseCorrectiveEvaluator.evaluate(
        model,
        pose_features=pose_features,
    )

    second = AtlasPortraitFlamePoseCorrectiveEvaluator.evaluate(
        model,
        pose_features=pose_features,
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


def test_evaluator_does_not_modify_model_or_features():
    model = _canonical_model()

    pose_features = np.arange(
        9,
        dtype=np.float64,
    )

    model_before = model.to_dict()
    features_before = pose_features.copy()

    AtlasPortraitFlamePoseCorrectiveEvaluator.evaluate(
        model,
        pose_features=pose_features,
    )

    assert model.to_dict() == model_before

    assert np.array_equal(
        pose_features,
        features_before,
    )


def test_evaluator_rejects_wrong_model_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameCanonicalModel",
    ):
        AtlasPortraitFlamePoseCorrectiveEvaluator.evaluate(
            object(),
            pose_features=np.zeros(
                9,
                dtype=np.float64,
            ),
        )


@pytest.mark.parametrize(
    "pose_features",
    [
        np.zeros(
            (
                3,
                3,
            ),
            dtype=np.float64,
        ),
        np.zeros(
            8,
            dtype=np.float64,
        ),
        np.zeros(
            10,
            dtype=np.float64,
        ),
    ],
)
def test_evaluator_rejects_invalid_pose_feature_shape(
    pose_features,
):
    with pytest.raises(
        ValueError,
        match="pose_features",
    ):
        AtlasPortraitFlamePoseCorrectiveEvaluator.evaluate(
            _canonical_model(),
            pose_features=pose_features,
        )


def test_evaluator_rejects_non_numeric_pose_features():
    with pytest.raises(
        ValueError,
        match="pose_features",
    ):
        AtlasPortraitFlamePoseCorrectiveEvaluator.evaluate(
            _canonical_model(),
            pose_features=[
                "invalid",
            ]
            * 9,
        )


def test_evaluator_rejects_non_finite_pose_features():
    pose_features = np.zeros(
        9,
        dtype=np.float64,
    )

    pose_features[
        0
    ] = np.nan

    with pytest.raises(
        ValueError,
        match="pose_features",
    ):
        AtlasPortraitFlamePoseCorrectiveEvaluator.evaluate(
            _canonical_model(),
            pose_features=pose_features,
        )
