from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_deformed_mesh_evaluator import (
    AtlasPortraitFlameDeformedMesh,
)
from CORE.atlas_portrait_flame_vertex_normal_evaluator import (
    AtlasPortraitFlameNormalField,
    AtlasPortraitFlameVertexNormalEvaluator,
)


def _flat_mesh() -> AtlasPortraitFlameDeformedMesh:
    return AtlasPortraitFlameDeformedMesh(
        vertices=np.array(
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
    )


def _bent_mesh() -> AtlasPortraitFlameDeformedMesh:
    return AtlasPortraitFlameDeformedMesh(
        vertices=np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            dtype=np.float64,
        ),
        triangle_faces=np.array(
            [
                [0, 1, 2],
                [0, 3, 1],
            ],
            dtype=np.int64,
        ),
    )


def test_evaluator_returns_normal_field_contract():
    result = AtlasPortraitFlameVertexNormalEvaluator.evaluate(
        _flat_mesh(),
    )

    assert isinstance(
        result,
        AtlasPortraitFlameNormalField,
    )


def test_evaluator_returns_expected_flat_face_normals():
    result = AtlasPortraitFlameVertexNormalEvaluator.evaluate(
        _flat_mesh(),
    )

    expected = np.array(
        [
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )

    assert np.allclose(
        result.face_normals,
        expected,
        rtol=0.0,
        atol=1.0e-12,
    )


def test_evaluator_returns_expected_flat_vertex_normals():
    result = AtlasPortraitFlameVertexNormalEvaluator.evaluate(
        _flat_mesh(),
    )

    expected = np.repeat(
        np.array(
            [
                [
                    0.0,
                    0.0,
                    1.0,
                ],
            ],
            dtype=np.float64,
        ),
        repeats=4,
        axis=0,
    )

    assert np.allclose(
        result.vertex_normals,
        expected,
        rtol=0.0,
        atol=1.0e-12,
    )


def test_evaluator_area_weights_shared_vertex_normals():
    result = AtlasPortraitFlameVertexNormalEvaluator.evaluate(
        _bent_mesh(),
    )

    expected_shared = np.array(
        [
            0.0,
            1.0,
            1.0,
        ],
        dtype=np.float64,
    )
    expected_shared /= np.linalg.norm(
        expected_shared,
    )

    assert np.allclose(
        result.vertex_normals[
            0,
        ],
        expected_shared,
        rtol=0.0,
        atol=1.0e-12,
    )
    assert np.allclose(
        result.vertex_normals[
            1,
        ],
        expected_shared,
        rtol=0.0,
        atol=1.0e-12,
    )


def test_evaluator_preserves_unique_face_normals():
    result = AtlasPortraitFlameVertexNormalEvaluator.evaluate(
        _bent_mesh(),
    )

    assert np.allclose(
        result.vertex_normals[
            2,
        ],
        np.array(
            [
                0.0,
                0.0,
                1.0,
            ],
            dtype=np.float64,
        ),
        rtol=0.0,
        atol=1.0e-12,
    )
    assert np.allclose(
        result.vertex_normals[
            3,
        ],
        np.array(
            [
                0.0,
                1.0,
                0.0,
            ],
            dtype=np.float64,
        ),
        rtol=0.0,
        atol=1.0e-12,
    )


def test_normal_field_reports_counts():
    result = AtlasPortraitFlameVertexNormalEvaluator.evaluate(
        _flat_mesh(),
    )

    assert result.face_count == 2
    assert result.vertex_count == 4


def test_normal_field_arrays_use_float64():
    result = AtlasPortraitFlameVertexNormalEvaluator.evaluate(
        _flat_mesh(),
    )

    assert result.face_normals.dtype == np.float64
    assert result.vertex_normals.dtype == np.float64


def test_normal_field_arrays_are_unit_length():
    result = AtlasPortraitFlameVertexNormalEvaluator.evaluate(
        _bent_mesh(),
    )

    assert np.allclose(
        np.linalg.norm(
            result.face_normals,
            axis=1,
        ),
        np.ones(
            result.face_count,
            dtype=np.float64,
        ),
        rtol=0.0,
        atol=1.0e-12,
    )
    assert np.allclose(
        np.linalg.norm(
            result.vertex_normals,
            axis=1,
        ),
        np.ones(
            result.vertex_count,
            dtype=np.float64,
        ),
        rtol=0.0,
        atol=1.0e-12,
    )


def test_normal_field_arrays_are_read_only():
    result = AtlasPortraitFlameVertexNormalEvaluator.evaluate(
        _flat_mesh(),
    )

    assert result.face_normals.flags.writeable is False
    assert result.vertex_normals.flags.writeable is False

    with pytest.raises(
        ValueError,
    ):
        result.face_normals[
            0,
            0,
        ] = 1.0

    with pytest.raises(
        ValueError,
    ):
        result.vertex_normals[
            0,
            0,
        ] = 1.0


def test_evaluator_returns_independent_results():
    mesh = _flat_mesh()

    first = AtlasPortraitFlameVertexNormalEvaluator.evaluate(
        mesh,
    )
    second = AtlasPortraitFlameVertexNormalEvaluator.evaluate(
        mesh,
    )

    assert first is not second
    assert not np.shares_memory(
        first.face_normals,
        second.face_normals,
    )
    assert not np.shares_memory(
        first.vertex_normals,
        second.vertex_normals,
    )


def test_evaluator_does_not_modify_mesh():
    mesh = _flat_mesh()

    vertices_before = mesh.vertices.copy()
    faces_before = mesh.triangle_faces.copy()

    AtlasPortraitFlameVertexNormalEvaluator.evaluate(
        mesh,
    )

    assert np.array_equal(
        mesh.vertices,
        vertices_before,
    )
    assert np.array_equal(
        mesh.triangle_faces,
        faces_before,
    )


def test_normal_field_to_dict_returns_independent_arrays():
    result = AtlasPortraitFlameVertexNormalEvaluator.evaluate(
        _flat_mesh(),
    )

    payload = result.to_dict()

    assert set(
        payload,
    ) == {
        "face_normals",
        "vertex_normals",
        "face_count",
        "vertex_count",
    }
    assert np.array_equal(
        payload["face_normals"],
        result.face_normals,
    )
    assert np.array_equal(
        payload["vertex_normals"],
        result.vertex_normals,
    )
    assert not np.shares_memory(
        payload["face_normals"],
        result.face_normals,
    )
    assert not np.shares_memory(
        payload["vertex_normals"],
        result.vertex_normals,
    )
    assert payload["face_count"] == 2
    assert payload["vertex_count"] == 4


def test_evaluator_rejects_wrong_mesh_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameDeformedMesh",
    ):
        AtlasPortraitFlameVertexNormalEvaluator.evaluate(
            object(),
        )


def test_evaluator_rejects_degenerate_triangle():
    mesh = AtlasPortraitFlameDeformedMesh(
        vertices=np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [2.0, 0.0, 0.0],
            ],
            dtype=np.float64,
        ),
        triangle_faces=np.array(
            [
                [0, 1, 2],
            ],
            dtype=np.int64,
        ),
    )

    with pytest.raises(
        ValueError,
        match="degenerate",
    ):
        AtlasPortraitFlameVertexNormalEvaluator.evaluate(
            mesh,
        )


def test_evaluator_rejects_unreferenced_vertex():
    mesh = AtlasPortraitFlameDeformedMesh(
        vertices=np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            dtype=np.float64,
        ),
        triangle_faces=np.array(
            [
                [0, 1, 2],
            ],
            dtype=np.int64,
        ),
    )

    with pytest.raises(
        ValueError,
        match="unreferenced",
    ):
        AtlasPortraitFlameVertexNormalEvaluator.evaluate(
            mesh,
        )
