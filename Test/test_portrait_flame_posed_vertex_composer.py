from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)
from CORE.atlas_portrait_flame_posed_vertex_composer import (
    AtlasPortraitFlamePosedVertexComposer,
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


def _pose_corrective_offsets() -> np.ndarray:
    return np.array(
        [
            [0.1, 0.0, 0.2],
            [-0.1, 0.0, 0.2],
            [0.0, 0.3, -0.1],
            [0.0, 0.3, -0.1],
        ],
        dtype=np.float64,
    )


def test_composer_returns_expected_posed_vertices():
    result = AtlasPortraitFlamePosedVertexComposer.compose(
        _canonical_model(),
        shaped_vertices=_shaped_vertices(),
        pose_corrective_offsets=_pose_corrective_offsets(),
    )

    expected = np.array(
        [
            [-1.9, 2.0, 0.2],
            [1.9, 2.0, 0.2],
            [-1.0, -1.7, 0.9],
            [1.0, -1.7, 0.9],
        ],
        dtype=np.float64,
    )

    assert np.allclose(
        result,
        expected,
        rtol=0.0,
        atol=1.0e-12,
    )


def test_composer_uses_model_vertex_count():
    result = AtlasPortraitFlamePosedVertexComposer.compose(
        _canonical_model(),
        shaped_vertices=_shaped_vertices(),
        pose_corrective_offsets=_pose_corrective_offsets(),
    )

    assert result.shape == (
        4,
        3,
    )


def test_composer_result_is_float64():
    result = AtlasPortraitFlamePosedVertexComposer.compose(
        _canonical_model(),
        shaped_vertices=_shaped_vertices(),
        pose_corrective_offsets=_pose_corrective_offsets(),
    )

    assert result.dtype == np.float64


def test_composer_result_is_read_only():
    result = AtlasPortraitFlamePosedVertexComposer.compose(
        _canonical_model(),
        shaped_vertices=_shaped_vertices(),
        pose_corrective_offsets=_pose_corrective_offsets(),
    )

    assert result.flags.writeable is False

    with pytest.raises(
        ValueError,
    ):
        result[
            0,
            0,
        ] = 1.0


def test_composer_returns_independent_results():
    model = _canonical_model()
    shaped_vertices = _shaped_vertices()
    offsets = _pose_corrective_offsets()

    first = AtlasPortraitFlamePosedVertexComposer.compose(
        model,
        shaped_vertices=shaped_vertices,
        pose_corrective_offsets=offsets,
    )

    second = AtlasPortraitFlamePosedVertexComposer.compose(
        model,
        shaped_vertices=shaped_vertices,
        pose_corrective_offsets=offsets,
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


def test_composer_does_not_modify_model_or_inputs():
    model = _canonical_model()
    shaped_vertices = _shaped_vertices()
    offsets = _pose_corrective_offsets()

    model_before = model.to_dict()
    shaped_before = shaped_vertices.copy()
    offsets_before = offsets.copy()

    AtlasPortraitFlamePosedVertexComposer.compose(
        model,
        shaped_vertices=shaped_vertices,
        pose_corrective_offsets=offsets,
    )

    assert model.to_dict() == model_before
    assert np.array_equal(
        shaped_vertices,
        shaped_before,
    )
    assert np.array_equal(
        offsets,
        offsets_before,
    )


def test_composer_rejects_wrong_model_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameCanonicalModel",
    ):
        AtlasPortraitFlamePosedVertexComposer.compose(
            object(),
            shaped_vertices=_shaped_vertices(),
            pose_corrective_offsets=_pose_corrective_offsets(),
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
def test_composer_rejects_invalid_shaped_vertex_shape(
    shaped_vertices,
):
    with pytest.raises(
        ValueError,
        match="shaped_vertices",
    ):
        AtlasPortraitFlamePosedVertexComposer.compose(
            _canonical_model(),
            shaped_vertices=shaped_vertices,
            pose_corrective_offsets=_pose_corrective_offsets(),
        )


@pytest.mark.parametrize(
    "pose_corrective_offsets",
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
def test_composer_rejects_invalid_offset_shape(
    pose_corrective_offsets,
):
    with pytest.raises(
        ValueError,
        match="pose_corrective_offsets",
    ):
        AtlasPortraitFlamePosedVertexComposer.compose(
            _canonical_model(),
            shaped_vertices=_shaped_vertices(),
            pose_corrective_offsets=pose_corrective_offsets,
        )


@pytest.mark.parametrize(
    (
        "argument_name",
        "shaped_vertices",
        "pose_corrective_offsets",
    ),
    [
        (
            "shaped_vertices",
            [
                [
                    "invalid",
                    "invalid",
                    "invalid",
                ],
            ]
            * 4,
            _pose_corrective_offsets(),
        ),
        (
            "pose_corrective_offsets",
            _shaped_vertices(),
            [
                [
                    "invalid",
                    "invalid",
                    "invalid",
                ],
            ]
            * 4,
        ),
    ],
)
def test_composer_rejects_non_numeric_inputs(
    argument_name,
    shaped_vertices,
    pose_corrective_offsets,
):
    with pytest.raises(
        ValueError,
        match=argument_name,
    ):
        AtlasPortraitFlamePosedVertexComposer.compose(
            _canonical_model(),
            shaped_vertices=shaped_vertices,
            pose_corrective_offsets=pose_corrective_offsets,
        )


@pytest.mark.parametrize(
    "argument_name",
    [
        "shaped_vertices",
        "pose_corrective_offsets",
    ],
)
def test_composer_rejects_non_finite_inputs(
    argument_name,
):
    shaped_vertices = _shaped_vertices()
    offsets = _pose_corrective_offsets()

    if argument_name == "shaped_vertices":
        shaped_vertices[
            0,
            0,
        ] = np.nan
    else:
        offsets[
            0,
            0,
        ] = np.inf

    with pytest.raises(
        ValueError,
        match=argument_name,
    ):
        AtlasPortraitFlamePosedVertexComposer.compose(
            _canonical_model(),
            shaped_vertices=shaped_vertices,
            pose_corrective_offsets=offsets,
        )
