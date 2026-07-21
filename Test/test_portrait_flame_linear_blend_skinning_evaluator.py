from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)
from CORE.atlas_portrait_flame_linear_blend_skinning_evaluator import (
    AtlasPortraitFlameLinearBlendSkinningEvaluator,
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
                [0.0, 1.0, 0.0],
                [0.5, 0.5, 0.0],
                [0.25, 0.25, 0.50],
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


def _posed_vertices() -> np.ndarray:
    return np.array(
        [
            [-2.0, 2.0, 0.0],
            [2.0, 2.0, 0.0],
            [-1.0, -2.0, 1.0],
            [1.0, -2.0, 1.0],
        ],
        dtype=np.float64,
    )


def _identity_transforms() -> np.ndarray:
    return np.repeat(
        np.eye(
            4,
            dtype=np.float64,
        )[None, :, :],
        repeats=3,
        axis=0,
    )


def _translated_transforms() -> np.ndarray:
    transforms = _identity_transforms()

    transforms[
        0,
        :3,
        3,
    ] = np.array(
        [1.0, 0.0, 0.0],
        dtype=np.float64,
    )
    transforms[
        1,
        :3,
        3,
    ] = np.array(
        [0.0, 2.0, 0.0],
        dtype=np.float64,
    )
    transforms[
        2,
        :3,
        3,
    ] = np.array(
        [0.0, 0.0, 4.0],
        dtype=np.float64,
    )

    return transforms


def test_evaluator_returns_original_vertices_for_identity_transforms():
    result = AtlasPortraitFlameLinearBlendSkinningEvaluator.evaluate(
        _canonical_model(),
        posed_vertices=_posed_vertices(),
        joint_transforms=_identity_transforms(),
    )

    assert np.allclose(
        result,
        _posed_vertices(),
        rtol=0.0,
        atol=1.0e-12,
    )


def test_evaluator_applies_weighted_joint_translations():
    result = AtlasPortraitFlameLinearBlendSkinningEvaluator.evaluate(
        _canonical_model(),
        posed_vertices=_posed_vertices(),
        joint_transforms=_translated_transforms(),
    )

    expected = np.array(
        [
            [-1.0, 2.0, 0.0],
            [2.0, 4.0, 0.0],
            [-0.5, -1.0, 1.0],
            [1.25, -1.5, 3.0],
        ],
        dtype=np.float64,
    )

    assert np.allclose(
        result,
        expected,
        rtol=0.0,
        atol=1.0e-12,
    )


def test_evaluator_applies_rotation_transform():
    transforms = _identity_transforms()
    transforms[
        0,
        :3,
        :3,
    ] = np.array(
        [
            [0.0, -1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )

    result = AtlasPortraitFlameLinearBlendSkinningEvaluator.evaluate(
        _canonical_model(),
        posed_vertices=_posed_vertices(),
        joint_transforms=transforms,
    )

    assert np.allclose(
        result[
            0,
        ],
        np.array(
            [-2.0, -2.0, 0.0],
            dtype=np.float64,
        ),
        rtol=0.0,
        atol=1.0e-12,
    )


def test_evaluator_uses_model_vertex_count():
    result = AtlasPortraitFlameLinearBlendSkinningEvaluator.evaluate(
        _canonical_model(),
        posed_vertices=_posed_vertices(),
        joint_transforms=_identity_transforms(),
    )

    assert result.shape == (
        4,
        3,
    )


def test_evaluator_result_is_float64():
    result = AtlasPortraitFlameLinearBlendSkinningEvaluator.evaluate(
        _canonical_model(),
        posed_vertices=_posed_vertices(),
        joint_transforms=_identity_transforms(),
    )

    assert result.dtype == np.float64


def test_evaluator_result_is_read_only():
    result = AtlasPortraitFlameLinearBlendSkinningEvaluator.evaluate(
        _canonical_model(),
        posed_vertices=_posed_vertices(),
        joint_transforms=_identity_transforms(),
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
    vertices = _posed_vertices()
    transforms = _identity_transforms()

    first = AtlasPortraitFlameLinearBlendSkinningEvaluator.evaluate(
        model,
        posed_vertices=vertices,
        joint_transforms=transforms,
    )

    second = AtlasPortraitFlameLinearBlendSkinningEvaluator.evaluate(
        model,
        posed_vertices=vertices,
        joint_transforms=transforms,
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
    vertices = _posed_vertices()
    transforms = _translated_transforms()

    model_before = model.to_dict()
    vertices_before = vertices.copy()
    transforms_before = transforms.copy()

    AtlasPortraitFlameLinearBlendSkinningEvaluator.evaluate(
        model,
        posed_vertices=vertices,
        joint_transforms=transforms,
    )

    assert model.to_dict() == model_before
    assert np.array_equal(
        vertices,
        vertices_before,
    )
    assert np.array_equal(
        transforms,
        transforms_before,
    )


def test_evaluator_rejects_wrong_model_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameCanonicalModel",
    ):
        AtlasPortraitFlameLinearBlendSkinningEvaluator.evaluate(
            object(),
            posed_vertices=_posed_vertices(),
            joint_transforms=_identity_transforms(),
        )


@pytest.mark.parametrize(
    "posed_vertices",
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
    posed_vertices,
):
    with pytest.raises(
        ValueError,
        match="posed_vertices",
    ):
        AtlasPortraitFlameLinearBlendSkinningEvaluator.evaluate(
            _canonical_model(),
            posed_vertices=posed_vertices,
            joint_transforms=_identity_transforms(),
        )


@pytest.mark.parametrize(
    "joint_transforms",
    [
        np.zeros(
            (
                3,
                3,
                3,
            ),
            dtype=np.float64,
        ),
        np.zeros(
            (
                2,
                4,
                4,
            ),
            dtype=np.float64,
        ),
        np.zeros(
            (
                3,
                4,
            ),
            dtype=np.float64,
        ),
    ],
)
def test_evaluator_rejects_invalid_transform_shape(
    joint_transforms,
):
    with pytest.raises(
        ValueError,
        match="joint_transforms",
    ):
        AtlasPortraitFlameLinearBlendSkinningEvaluator.evaluate(
            _canonical_model(),
            posed_vertices=_posed_vertices(),
            joint_transforms=joint_transforms,
        )


@pytest.mark.parametrize(
    (
        "argument_name",
        "posed_vertices",
        "joint_transforms",
    ),
    [
        (
            "posed_vertices",
            [
                [
                    "invalid",
                    "invalid",
                    "invalid",
                ],
            ]
            * 4,
            _identity_transforms(),
        ),
        (
            "joint_transforms",
            _posed_vertices(),
            [
                [
                    [
                        "invalid",
                    ]
                    * 4,
                ]
                * 4,
            ]
            * 3,
        ),
    ],
)
def test_evaluator_rejects_non_numeric_inputs(
    argument_name,
    posed_vertices,
    joint_transforms,
):
    with pytest.raises(
        ValueError,
        match=argument_name,
    ):
        AtlasPortraitFlameLinearBlendSkinningEvaluator.evaluate(
            _canonical_model(),
            posed_vertices=posed_vertices,
            joint_transforms=joint_transforms,
        )


@pytest.mark.parametrize(
    "argument_name",
    [
        "posed_vertices",
        "joint_transforms",
    ],
)
def test_evaluator_rejects_non_finite_inputs(
    argument_name,
):
    vertices = _posed_vertices()
    transforms = _identity_transforms()

    if argument_name == "posed_vertices":
        vertices[
            0,
            0,
        ] = np.nan
    else:
        transforms[
            0,
            0,
            0,
        ] = np.inf

    with pytest.raises(
        ValueError,
        match=argument_name,
    ):
        AtlasPortraitFlameLinearBlendSkinningEvaluator.evaluate(
            _canonical_model(),
            posed_vertices=vertices,
            joint_transforms=transforms,
        )


def test_evaluator_rejects_invalid_homogeneous_bottom_rows():
    transforms = _identity_transforms()
    transforms[
        1,
        3,
        :,
    ] = np.array(
        [
            0.0,
            0.0,
            1.0,
            1.0,
        ],
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="joint_transforms",
    ):
        AtlasPortraitFlameLinearBlendSkinningEvaluator.evaluate(
            _canonical_model(),
            posed_vertices=_posed_vertices(),
            joint_transforms=transforms,
        )
