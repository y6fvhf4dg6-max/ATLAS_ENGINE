from __future__ import annotations

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)


def _template_vertices() -> np.ndarray:
    return np.array(
        [
            [-1.0, 1.0, 0.0],
            [1.0, 1.0, 0.0],
            [-1.0, -1.0, 0.0],
            [1.0, -1.0, 0.0],
        ],
        dtype=np.float64,
    )


def _triangle_faces() -> np.ndarray:
    return np.array(
        [
            [0, 2, 1],
            [1, 2, 3],
        ],
        dtype=np.int64,
    )


def _identity_directions() -> np.ndarray:
    result = np.zeros(
        (
            4,
            3,
            2,
        ),
        dtype=np.float64,
    )

    result[
        :,
        0,
        0,
    ] = np.array(
        [
            -0.1,
            0.1,
            -0.1,
            0.1,
        ],
        dtype=np.float64,
    )

    result[
        :,
        1,
        1,
    ] = np.array(
        [
            0.1,
            0.1,
            -0.1,
            -0.1,
        ],
        dtype=np.float64,
    )

    return result


def _expression_directions() -> np.ndarray:
    result = np.zeros(
        (
            4,
            3,
            1,
        ),
        dtype=np.float64,
    )

    result[
        :,
        2,
        0,
    ] = np.array(
        [
            0.0,
            0.0,
            0.1,
            0.1,
        ],
        dtype=np.float64,
    )

    return result


def _pose_directions() -> np.ndarray:
    return np.zeros(
        (
            4,
            3,
            3,
        ),
        dtype=np.float64,
    )


def _joint_regressor() -> np.ndarray:
    return np.array(
        [
            [0.25, 0.25, 0.25, 0.25],
            [0.50, 0.50, 0.00, 0.00],
        ],
        dtype=np.float64,
    )


def _skinning_weights() -> np.ndarray:
    return np.array(
        [
            [1.0, 0.0],
            [1.0, 0.0],
            [0.5, 0.5],
            [0.5, 0.5],
        ],
        dtype=np.float64,
    )


def _kinematic_tree() -> np.ndarray:
    return np.array(
        [
            -1,
            0,
        ],
        dtype=np.int64,
    )


def _model(
    **overrides,
) -> AtlasPortraitFlameCanonicalModel:
    values = {
        "template_vertices": _template_vertices(),
        "triangle_faces": _triangle_faces(),
        "identity_shape_directions": (
            _identity_directions()
        ),
        "expression_shape_directions": (
            _expression_directions()
        ),
        "pose_directions": _pose_directions(),
        "pose_parameter_count": 6,
        "joint_regressor": _joint_regressor(),
        "skinning_weights": _skinning_weights(),
        "kinematic_tree": _kinematic_tree(),
        "metadata": {
            "model_family": "flame",
            "model_version": "synthetic-v1",
            "synthetic": True,
        },
    }

    values.update(
        overrides,
    )

    return AtlasPortraitFlameCanonicalModel(
        **values,
    )


def test_model_preserves_primary_dimensions():
    model = _model()

    assert model.vertex_count == 4
    assert model.triangle_count == 2
    assert model.identity_parameter_count == 2
    assert model.expression_parameter_count == 1
    assert model.pose_parameter_count == 6
    assert model.pose_feature_count == 3
    assert model.joint_count == 2


def test_model_normalizes_array_dtypes():
    model = _model()

    assert model.template_vertices.dtype == np.float64
    assert model.triangle_faces.dtype == np.int64
    assert (
        model.identity_shape_directions.dtype
        == np.float64
    )
    assert (
        model.expression_shape_directions.dtype
        == np.float64
    )
    assert model.pose_directions.dtype == np.float64
    assert model.joint_regressor.dtype == np.float64
    assert model.skinning_weights.dtype == np.float64
    assert model.kinematic_tree.dtype == np.int64


def test_model_arrays_are_read_only():
    model = _model()

    arrays = (
        model.template_vertices,
        model.triangle_faces,
        model.identity_shape_directions,
        model.expression_shape_directions,
        model.pose_directions,
        model.joint_regressor,
        model.skinning_weights,
        model.kinematic_tree,
    )

    for array in arrays:
        assert array.flags.writeable is False

        with pytest.raises(
            ValueError,
        ):
            array.flat[
                0
            ] = 99


def test_model_copies_input_arrays():
    template_vertices = _template_vertices()

    model = _model(
        template_vertices=template_vertices,
    )

    template_vertices[
        0,
        0,
    ] = 99.0

    assert model.template_vertices[
        0,
        0,
    ] != 99.0


def test_model_is_frozen():
    model = _model()

    with pytest.raises(
        FrozenInstanceError,
    ):
        model.template_vertices = np.zeros(
            (
                4,
                3,
            ),
            dtype=np.float64,
        )


def test_model_metadata_is_deterministic():
    model = _model()

    assert tuple(
        model.metadata,
    ) == tuple(
        sorted(
            model.metadata,
        )
    )

    assert model.metadata == {
        "model_family": "flame",
        "model_version": "synthetic-v1",
        "synthetic": True,
    }


def test_model_serialization_is_deterministic():
    first = _model()
    second = _model()

    assert first.to_dict() == second.to_dict()


def test_model_to_dict_reports_dimensions():
    model = _model()

    serialized = model.to_dict()

    assert serialized[
        "vertex_count"
    ] == 4
    assert serialized[
        "triangle_count"
    ] == 2
    assert serialized[
        "identity_parameter_count"
    ] == 2
    assert serialized[
        "expression_parameter_count"
    ] == 1
    assert serialized[
        "pose_parameter_count"
    ] == 6
    assert serialized[
        "pose_feature_count"
    ] == 3
    assert serialized[
        "joint_count"
    ] == 2


@pytest.mark.parametrize(
    (
        "field_name",
        "value",
    ),
    [
        (
            "template_vertices",
            np.zeros(
                (
                    4,
                    2,
                ),
                dtype=np.float64,
            ),
        ),
        (
            "triangle_faces",
            np.zeros(
                (
                    2,
                    2,
                ),
                dtype=np.int64,
            ),
        ),
        (
            "identity_shape_directions",
            np.zeros(
                (
                    4,
                    2,
                    2,
                ),
                dtype=np.float64,
            ),
        ),
        (
            "expression_shape_directions",
            np.zeros(
                (
                    3,
                    3,
                    1,
                ),
                dtype=np.float64,
            ),
        ),
        (
            "pose_directions",
            np.zeros(
                (
                    4,
                    3,
                    0,
                ),
                dtype=np.float64,
            ),
        ),
        (
            "joint_regressor",
            np.zeros(
                (
                    2,
                    3,
                ),
                dtype=np.float64,
            ),
        ),
        (
            "skinning_weights",
            np.zeros(
                (
                    4,
                    3,
                ),
                dtype=np.float64,
            ),
        ),
        (
            "kinematic_tree",
            np.zeros(
                (
                    2,
                    1,
                ),
                dtype=np.int64,
            ),
        ),
    ],
)
def test_model_rejects_invalid_shapes(
    field_name,
    value,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _model(
            **{
                field_name: value,
            }
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "template_vertices",
        "identity_shape_directions",
        "expression_shape_directions",
        "pose_directions",
        "joint_regressor",
        "skinning_weights",
    ],
)
def test_model_rejects_non_finite_values(
    field_name,
):
    model = _model()

    value = np.array(
        getattr(
            model,
            field_name,
        ),
        copy=True,
    )

    value.flat[
        0
    ] = np.nan

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _model(
            **{
                field_name: value,
            }
        )


def test_model_rejects_out_of_range_triangle_index():
    faces = _triangle_faces()

    faces[
        0,
        0,
    ] = 4

    with pytest.raises(
        ValueError,
        match="triangle_faces",
    ):
        _model(
            triangle_faces=faces,
        )


def test_model_rejects_invalid_skinning_weight_sum():
    weights = _skinning_weights()

    weights[
        0,
    ] = np.array(
        [
            0.25,
            0.25,
        ],
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="skinning_weights",
    ):
        _model(
            skinning_weights=weights,
        )


def test_model_rejects_invalid_kinematic_root():
    tree = _kinematic_tree()

    tree[
        0
    ] = 0

    with pytest.raises(
        ValueError,
        match="kinematic_tree",
    ):
        _model(
            kinematic_tree=tree,
        )


@pytest.mark.parametrize(
    "value",
    [
        0,
        -1,
        1.5,
        True,
        "6",
    ],
)
def test_model_rejects_invalid_pose_parameter_count(
    value,
):
    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
        match="pose_parameter_count",
    ):
        _model(
            pose_parameter_count=value,
        )


def test_pose_parameter_and_feature_counts_are_independent():
    model = _model(
        pose_parameter_count=9,
    )

    assert model.pose_parameter_count == 9
    assert model.pose_feature_count == 3


def test_model_rejects_non_mapping_metadata():
    with pytest.raises(
        TypeError,
        match="metadata",
    ):
        _model(
            metadata=[
                "invalid",
            ],
        )
