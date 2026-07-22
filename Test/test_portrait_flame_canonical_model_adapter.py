from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)
from CORE.providers.portrait.atlas_portrait_flame_canonical_model_adapter import (
    AtlasPortraitFlameCanonicalModelAdapter,
)


def _source_mapping(
    *,
    use_faces_alias: bool = False,
    use_parents: bool = False,
) -> dict:
    vertex_count = 4
    joint_count = 2

    shapedirs = np.zeros(
        (
            vertex_count,
            3,
            3,
        ),
        dtype=np.float64,
    )
    shapedirs[
        :,
        0,
        0,
    ] = (
        -0.10,
        0.10,
        -0.10,
        0.10,
    )
    shapedirs[
        :,
        1,
        1,
    ] = (
        0.10,
        0.10,
        -0.10,
        -0.10,
    )
    shapedirs[
        :,
        2,
        2,
    ] = (
        0.00,
        0.00,
        0.10,
        0.10,
    )

    source = {
        "v_template": np.array(
            [
                [-1.0, 1.0, 0.0],
                [1.0, 1.0, 0.0],
                [-1.0, -1.0, 0.0],
                [1.0, -1.0, 0.0],
            ],
            dtype=np.float64,
        ),
        "shapedirs": shapedirs,
        "posedirs": np.zeros(
            (
                vertex_count * 3,
                3,
            ),
            dtype=np.float64,
        ),
        "J_regressor": np.array(
            [
                [0.25, 0.25, 0.25, 0.25],
                [0.50, 0.50, 0.00, 0.00],
            ],
            dtype=np.float64,
        ),
        "weights": np.array(
            [
                [1.0, 0.0],
                [1.0, 0.0],
                [0.5, 0.5],
                [0.5, 0.5],
            ],
            dtype=np.float64,
        ),
    }

    faces = np.array(
        [
            [0, 2, 1],
            [1, 2, 3],
        ],
        dtype=np.int64,
    )

    if use_faces_alias:
        source[
            "faces"
        ] = faces
    else:
        source[
            "f"
        ] = faces

    if use_parents:
        source[
            "parents"
        ] = np.array(
            [
                -1,
                0,
            ],
            dtype=np.int64,
        )
    else:
        source[
            "kintree_table"
        ] = np.array(
            [
                [
                    -1,
                    0,
                ],
                [
                    0,
                    1,
                ],
            ],
            dtype=np.int64,
        )

    assert source[
        "weights"
    ].shape == (
        vertex_count,
        joint_count,
    )

    return source


def _adapt(
    source=None,
    **overrides,
):
    arguments = {
        "source": (
            _source_mapping()
            if source is None
            else source
        ),
        "identity_parameter_count": 2,
        "expression_parameter_count": 1,
        "model_version": "synthetic-flame-v1",
        "source_format": "mapping",
    }
    arguments.update(
        overrides
    )

    return (
        AtlasPortraitFlameCanonicalModelAdapter
        .adapt(
            **arguments
        )
    )


def test_adapter_returns_canonical_model():
    model = _adapt()

    assert isinstance(
        model,
        AtlasPortraitFlameCanonicalModel,
    )


def test_adapter_maps_primary_geometry():
    source = _source_mapping()

    model = _adapt(
        source=source
    )

    np.testing.assert_allclose(
        model.template_vertices,
        source[
            "v_template"
        ],
    )
    np.testing.assert_array_equal(
        model.triangle_faces,
        source[
            "f"
        ],
    )


def test_adapter_accepts_faces_alias():
    source = _source_mapping(
        use_faces_alias=True,
    )

    model = _adapt(
        source=source
    )

    np.testing.assert_array_equal(
        model.triangle_faces,
        source[
            "faces"
        ],
    )


def test_adapter_splits_shape_directions():
    source = _source_mapping()

    model = _adapt(
        source=source
    )

    assert (
        model.identity_shape_directions.shape
        == (
            4,
            3,
            2,
        )
    )
    assert (
        model.expression_shape_directions.shape
        == (
            4,
            3,
            1,
        )
    )

    np.testing.assert_allclose(
        model.identity_shape_directions,
        source[
            "shapedirs"
        ][
            :,
            :,
            :2,
        ],
    )
    np.testing.assert_allclose(
        model.expression_shape_directions,
        source[
            "shapedirs"
        ][
            :,
            :,
            2:3,
        ],
    )


def test_adapter_normalizes_flat_pose_directions():
    source = _source_mapping()

    model = _adapt(
        source=source
    )

    assert model.pose_directions.shape == (
        4,
        3,
        3,
    )


def test_adapter_accepts_tensor_pose_directions():
    source = _source_mapping()
    source[
        "posedirs"
    ] = np.zeros(
        (
            4,
            3,
            3,
        ),
        dtype=np.float64,
    )

    model = _adapt(
        source=source
    )

    assert model.pose_directions.shape == (
        4,
        3,
        3,
    )


def test_adapter_maps_joint_regressor_and_weights():
    source = _source_mapping()

    model = _adapt(
        source=source
    )

    np.testing.assert_allclose(
        model.joint_regressor,
        source[
            "J_regressor"
        ],
    )
    np.testing.assert_allclose(
        model.skinning_weights,
        source[
            "weights"
        ],
    )


def test_adapter_converts_kintree_table_to_parents():
    model = _adapt()

    np.testing.assert_array_equal(
        model.kinematic_tree,
        np.array(
            [
                -1,
                0,
            ],
            dtype=np.int64,
        ),
    )


def test_adapter_accepts_parent_vector():
    source = _source_mapping(
        use_parents=True,
    )

    model = _adapt(
        source=source
    )

    np.testing.assert_array_equal(
        model.kinematic_tree,
        source[
            "parents"
        ],
    )


def test_adapter_derives_pose_parameter_count():
    model = _adapt()

    assert model.joint_count == 2
    assert model.pose_parameter_count == 6


def test_adapter_builds_deterministic_metadata():
    model = _adapt()

    assert model.metadata == {
        "expression_parameter_count": 1,
        "identity_parameter_count": 2,
        "model_family": "flame",
        "model_version": "synthetic-flame-v1",
        "source_format": "mapping",
        "synthetic": False,
    }


def test_adapter_converts_sparse_joint_regressor():
    scipy_sparse = pytest.importorskip(
        "scipy.sparse"
    )

    source = _source_mapping()
    source[
        "J_regressor"
    ] = scipy_sparse.csr_matrix(
        source[
            "J_regressor"
        ]
    )

    model = _adapt(
        source=source
    )

    assert isinstance(
        model.joint_regressor,
        np.ndarray,
    )
    assert model.joint_regressor.shape == (
        2,
        4,
    )


@pytest.mark.parametrize(
    "missing_field",
    [
        "v_template",
        "shapedirs",
        "posedirs",
        "J_regressor",
        "weights",
    ],
)
def test_adapter_rejects_missing_required_fields(
    missing_field,
):
    source = _source_mapping()
    del source[
        missing_field
    ]

    with pytest.raises(
        ValueError,
        match=missing_field,
    ):
        _adapt(
            source=source
        )


def test_adapter_rejects_missing_face_field():
    source = _source_mapping()
    del source[
        "f"
    ]

    with pytest.raises(
        ValueError,
        match="faces",
    ):
        _adapt(
            source=source
        )


def test_adapter_rejects_missing_kinematic_hierarchy():
    source = _source_mapping()
    del source[
        "kintree_table"
    ]

    with pytest.raises(
        ValueError,
        match="kinematic",
    ):
        _adapt(
            source=source
        )


@pytest.mark.parametrize(
    (
        "identity_count",
        "expression_count",
    ),
    [
        (
            0,
            1,
        ),
        (
            2,
            0,
        ),
        (
            3,
            1,
        ),
    ],
)
def test_adapter_rejects_invalid_shape_direction_split(
    identity_count,
    expression_count,
):
    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
        match="parameter_count",
    ):
        _adapt(
            identity_parameter_count=(
                identity_count
            ),
            expression_parameter_count=(
                expression_count
            ),
        )


def test_adapter_rejects_invalid_flat_pose_direction_shape():
    source = _source_mapping()
    source[
        "posedirs"
    ] = np.zeros(
        (
            11,
            3,
        ),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="posedirs",
    ):
        _adapt(
            source=source
        )


def test_adapter_rejects_non_mapping_source():
    with pytest.raises(
        TypeError,
        match="source",
    ):
        _adapt(
            source=[
                "invalid",
            ]
        )


def test_adapter_normalizes_unsigned_kintree_root_sentinel():
    source = _source_mapping()

    source[
        "kintree_table"
    ] = np.array(
        [
            [
                np.iinfo(
                    np.uint32
                ).max,
                0,
            ],
            [
                0,
                1,
            ],
        ],
        dtype=np.uint32,
    )

    model = _adapt(
        source=source
    )

    np.testing.assert_array_equal(
        model.kinematic_tree,
        np.array(
            [
                -1,
                0,
            ],
            dtype=np.int64,
        ),
    )
