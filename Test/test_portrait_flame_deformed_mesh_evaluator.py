from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)
from CORE.atlas_portrait_flame_deformed_mesh_evaluator import (
    AtlasPortraitFlameDeformedMesh,
    AtlasPortraitFlameDeformedMeshEvaluator,
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


def _skinned_vertices() -> np.ndarray:
    return np.array(
        [
            [-1.9, 2.0, 0.2],
            [1.9, 2.0, 0.2],
            [-1.0, -1.7, 0.9],
            [1.0, -1.7, 0.9],
        ],
        dtype=np.float64,
    )


def test_evaluator_returns_deformed_mesh_contract():
    result = AtlasPortraitFlameDeformedMeshEvaluator.evaluate(
        _canonical_model(),
        skinned_vertices=_skinned_vertices(),
    )

    assert isinstance(
        result,
        AtlasPortraitFlameDeformedMesh,
    )


def test_evaluator_copies_skinned_vertices():
    source = _skinned_vertices()

    result = AtlasPortraitFlameDeformedMeshEvaluator.evaluate(
        _canonical_model(),
        skinned_vertices=source,
    )

    assert np.array_equal(
        result.vertices,
        source,
    )
    assert not np.shares_memory(
        result.vertices,
        source,
    )


def test_evaluator_uses_canonical_triangle_faces():
    model = _canonical_model()

    result = AtlasPortraitFlameDeformedMeshEvaluator.evaluate(
        model,
        skinned_vertices=_skinned_vertices(),
    )

    assert np.array_equal(
        result.triangle_faces,
        model.triangle_faces,
    )
    assert not np.shares_memory(
        result.triangle_faces,
        model.triangle_faces,
    )


def test_mesh_reports_vertex_and_face_counts():
    result = AtlasPortraitFlameDeformedMeshEvaluator.evaluate(
        _canonical_model(),
        skinned_vertices=_skinned_vertices(),
    )

    assert result.vertex_count == 4
    assert result.face_count == 2


def test_mesh_arrays_use_expected_dtypes():
    result = AtlasPortraitFlameDeformedMeshEvaluator.evaluate(
        _canonical_model(),
        skinned_vertices=_skinned_vertices(),
    )

    assert result.vertices.dtype == np.float64
    assert result.triangle_faces.dtype == np.int64


def test_mesh_arrays_are_read_only():
    result = AtlasPortraitFlameDeformedMeshEvaluator.evaluate(
        _canonical_model(),
        skinned_vertices=_skinned_vertices(),
    )

    assert result.vertices.flags.writeable is False
    assert result.triangle_faces.flags.writeable is False

    with pytest.raises(
        ValueError,
    ):
        result.vertices[
            0,
            0,
        ] = 0.0

    with pytest.raises(
        ValueError,
    ):
        result.triangle_faces[
            0,
            0,
        ] = 0


def test_evaluator_returns_independent_meshes():
    model = _canonical_model()
    vertices = _skinned_vertices()

    first = AtlasPortraitFlameDeformedMeshEvaluator.evaluate(
        model,
        skinned_vertices=vertices,
    )
    second = AtlasPortraitFlameDeformedMeshEvaluator.evaluate(
        model,
        skinned_vertices=vertices,
    )

    assert first is not second
    assert first.vertices is not second.vertices
    assert first.triangle_faces is not second.triangle_faces
    assert not np.shares_memory(
        first.vertices,
        second.vertices,
    )
    assert not np.shares_memory(
        first.triangle_faces,
        second.triangle_faces,
    )


def test_evaluator_does_not_modify_model_or_vertices():
    model = _canonical_model()
    vertices = _skinned_vertices()

    model_before = model.to_dict()
    vertices_before = vertices.copy()

    AtlasPortraitFlameDeformedMeshEvaluator.evaluate(
        model,
        skinned_vertices=vertices,
    )

    assert model.to_dict() == model_before
    assert np.array_equal(
        vertices,
        vertices_before,
    )


def test_mesh_to_dict_returns_independent_arrays():
    mesh = AtlasPortraitFlameDeformedMeshEvaluator.evaluate(
        _canonical_model(),
        skinned_vertices=_skinned_vertices(),
    )

    payload = mesh.to_dict()

    assert set(
        payload,
    ) == {
        "vertices",
        "triangle_faces",
        "vertex_count",
        "face_count",
    }
    assert np.array_equal(
        payload["vertices"],
        mesh.vertices,
    )
    assert np.array_equal(
        payload["triangle_faces"],
        mesh.triangle_faces,
    )
    assert not np.shares_memory(
        payload["vertices"],
        mesh.vertices,
    )
    assert not np.shares_memory(
        payload["triangle_faces"],
        mesh.triangle_faces,
    )
    assert payload["vertex_count"] == 4
    assert payload["face_count"] == 2


def test_evaluator_rejects_wrong_model_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameCanonicalModel",
    ):
        AtlasPortraitFlameDeformedMeshEvaluator.evaluate(
            object(),
            skinned_vertices=_skinned_vertices(),
        )


@pytest.mark.parametrize(
    "skinned_vertices",
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
    skinned_vertices,
):
    with pytest.raises(
        ValueError,
        match="skinned_vertices",
    ):
        AtlasPortraitFlameDeformedMeshEvaluator.evaluate(
            _canonical_model(),
            skinned_vertices=skinned_vertices,
        )


def test_evaluator_rejects_non_numeric_vertices():
    with pytest.raises(
        ValueError,
        match="skinned_vertices",
    ):
        AtlasPortraitFlameDeformedMeshEvaluator.evaluate(
            _canonical_model(),
            skinned_vertices=[
                [
                    "invalid",
                    "invalid",
                    "invalid",
                ],
            ]
            * 4,
        )


@pytest.mark.parametrize(
    "invalid_value",
    [
        np.nan,
        np.inf,
        -np.inf,
    ],
)
def test_evaluator_rejects_non_finite_vertices(
    invalid_value,
):
    vertices = _skinned_vertices()
    vertices[
        0,
        0,
    ] = invalid_value

    with pytest.raises(
        ValueError,
        match="skinned_vertices",
    ):
        AtlasPortraitFlameDeformedMeshEvaluator.evaluate(
            _canonical_model(),
            skinned_vertices=vertices,
        )
