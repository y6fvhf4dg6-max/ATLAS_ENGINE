from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_deformed_mesh_evaluator import (
    AtlasPortraitFlameDeformedMesh,
)
from CORE.atlas_portrait_flame_triangle_visibility_evaluator import (
    AtlasPortraitFlameTriangleVisibility,
    AtlasPortraitFlameTriangleVisibilityEvaluator,
)
from CORE.atlas_portrait_flame_weak_perspective_projection_evaluator import (
    AtlasPortraitFlameWeakPerspectiveProjection,
)


def _mesh() -> AtlasPortraitFlameDeformedMesh:
    return AtlasPortraitFlameDeformedMesh(
        vertices=np.array(
            [
                [0.0, 0.0, 1.0],
                [1.0, 0.0, 2.0],
                [0.0, 1.0, 3.0],
                [1.0, 1.0, 4.0],
            ],
            dtype=np.float64,
        ),
        triangle_faces=np.array(
            [
                [0, 1, 2],
                [1, 2, 3],
                [0, 2, 1],
            ],
            dtype=np.int64,
        ),
    )


def _projection() -> AtlasPortraitFlameWeakPerspectiveProjection:
    return AtlasPortraitFlameWeakPerspectiveProjection(
        scale=1.0,
        translation_x=0.0,
        translation_y=0.0,
        projected_vertices_2d=np.array(
            [
                [0.0, 0.0],
                [1.0, 0.0],
                [0.0, 1.0],
                [1.0, 1.0],
            ],
            dtype=np.float64,
        ),
        triangle_faces=np.array(
            [
                [0, 1, 2],
                [1, 2, 3],
                [0, 2, 1],
            ],
            dtype=np.int64,
        ),
    )


def test_evaluator_returns_visibility_contract():
    result = AtlasPortraitFlameTriangleVisibilityEvaluator.evaluate(
        _mesh(),
        projection=_projection(),
    )

    assert isinstance(
        result,
        AtlasPortraitFlameTriangleVisibility,
    )


def test_evaluator_classifies_front_and_back_facing_triangles():
    result = AtlasPortraitFlameTriangleVisibilityEvaluator.evaluate(
        _mesh(),
        projection=_projection(),
    )

    assert np.array_equal(
        result.visible_triangle_mask,
        np.array(
            [
                True,
                False,
                False,
            ],
            dtype=np.bool_,
        ),
    )

    assert np.array_equal(
        result.front_facing_triangle_mask,
        np.array(
            [
                True,
                False,
                False,
            ],
            dtype=np.bool_,
        ),
    )


def test_evaluator_reports_signed_projected_areas():
    result = AtlasPortraitFlameTriangleVisibilityEvaluator.evaluate(
        _mesh(),
        projection=_projection(),
    )

    assert np.allclose(
        result.signed_projected_areas,
        np.array(
            [
                0.5,
                -0.5,
                -0.5,
            ],
            dtype=np.float64,
        ),
        rtol=0.0,
        atol=1.0e-12,
    )


def test_evaluator_reports_mean_triangle_depths():
    result = AtlasPortraitFlameTriangleVisibilityEvaluator.evaluate(
        _mesh(),
        projection=_projection(),
    )

    assert np.allclose(
        result.mean_triangle_depths,
        np.array(
            [
                2.0,
                3.0,
                2.0,
            ],
            dtype=np.float64,
        ),
        rtol=0.0,
        atol=1.0e-12,
    )


def test_visibility_reports_counts():
    result = AtlasPortraitFlameTriangleVisibilityEvaluator.evaluate(
        _mesh(),
        projection=_projection(),
    )

    assert result.triangle_count == 3
    assert result.visible_triangle_count == 1
    assert result.hidden_triangle_count == 2


def test_visibility_arrays_use_expected_dtypes():
    result = AtlasPortraitFlameTriangleVisibilityEvaluator.evaluate(
        _mesh(),
        projection=_projection(),
    )

    assert (
        result.visible_triangle_mask.dtype
        == np.bool_
    )
    assert (
        result.front_facing_triangle_mask.dtype
        == np.bool_
    )
    assert (
        result.signed_projected_areas.dtype
        == np.float64
    )
    assert (
        result.mean_triangle_depths.dtype
        == np.float64
    )


def test_visibility_arrays_are_read_only():
    result = AtlasPortraitFlameTriangleVisibilityEvaluator.evaluate(
        _mesh(),
        projection=_projection(),
    )

    assert result.visible_triangle_mask.flags.writeable is False
    assert (
        result.front_facing_triangle_mask.flags.writeable
        is False
    )
    assert result.signed_projected_areas.flags.writeable is False
    assert result.mean_triangle_depths.flags.writeable is False

    with pytest.raises(
        ValueError,
    ):
        result.visible_triangle_mask[
            0,
        ] = False

    with pytest.raises(
        ValueError,
    ):
        result.signed_projected_areas[
            0,
        ] = 0.0


def test_evaluator_returns_independent_results():
    mesh = _mesh()
    projection = _projection()

    first = AtlasPortraitFlameTriangleVisibilityEvaluator.evaluate(
        mesh,
        projection=projection,
    )
    second = AtlasPortraitFlameTriangleVisibilityEvaluator.evaluate(
        mesh,
        projection=projection,
    )

    assert first is not second

    assert not np.shares_memory(
        first.visible_triangle_mask,
        second.visible_triangle_mask,
    )
    assert not np.shares_memory(
        first.front_facing_triangle_mask,
        second.front_facing_triangle_mask,
    )
    assert not np.shares_memory(
        first.signed_projected_areas,
        second.signed_projected_areas,
    )
    assert not np.shares_memory(
        first.mean_triangle_depths,
        second.mean_triangle_depths,
    )


def test_evaluator_does_not_modify_inputs():
    mesh = _mesh()
    projection = _projection()

    mesh_vertices_before = mesh.vertices.copy()
    mesh_faces_before = mesh.triangle_faces.copy()
    projected_vertices_before = (
        projection.projected_vertices_2d.copy()
    )
    projected_faces_before = projection.triangle_faces.copy()

    AtlasPortraitFlameTriangleVisibilityEvaluator.evaluate(
        mesh,
        projection=projection,
    )

    assert np.array_equal(
        mesh.vertices,
        mesh_vertices_before,
    )
    assert np.array_equal(
        mesh.triangle_faces,
        mesh_faces_before,
    )
    assert np.array_equal(
        projection.projected_vertices_2d,
        projected_vertices_before,
    )
    assert np.array_equal(
        projection.triangle_faces,
        projected_faces_before,
    )


def test_visibility_to_dict_returns_plain_values():
    result = AtlasPortraitFlameTriangleVisibilityEvaluator.evaluate(
        _mesh(),
        projection=_projection(),
    )

    payload = result.to_dict()

    assert payload == {
        "triangle_count": 3,
        "visible_triangle_count": 1,
        "hidden_triangle_count": 2,
        "visible_triangle_mask": [
            True,
            False,
            False,
        ],
        "front_facing_triangle_mask": [
            True,
            False,
            False,
        ],
        "signed_projected_areas": [
            0.5,
            -0.5,
            -0.5,
        ],
        "mean_triangle_depths": [
            2.0,
            3.0,
            2.0,
        ],
    }


def test_evaluator_rejects_wrong_mesh_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameDeformedMesh",
    ):
        AtlasPortraitFlameTriangleVisibilityEvaluator.evaluate(
            object(),
            projection=_projection(),
        )


def test_evaluator_rejects_wrong_projection_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameWeakPerspectiveProjection",
    ):
        AtlasPortraitFlameTriangleVisibilityEvaluator.evaluate(
            _mesh(),
            projection=object(),
        )


def test_evaluator_rejects_mismatched_faces():
    projection = AtlasPortraitFlameWeakPerspectiveProjection(
        scale=1.0,
        translation_x=0.0,
        translation_y=0.0,
        projected_vertices_2d=_projection().projected_vertices_2d,
        triangle_faces=np.array(
            [
                [0, 2, 1],
                [1, 2, 3],
                [0, 1, 2],
            ],
            dtype=np.int64,
        ),
    )

    with pytest.raises(
        ValueError,
        match="triangle_faces",
    ):
        AtlasPortraitFlameTriangleVisibilityEvaluator.evaluate(
            _mesh(),
            projection=projection,
        )


def test_evaluator_rejects_degenerate_projected_triangle():
    projection = AtlasPortraitFlameWeakPerspectiveProjection(
        scale=1.0,
        translation_x=0.0,
        translation_y=0.0,
        projected_vertices_2d=np.array(
            [
                [0.0, 0.0],
                [1.0, 0.0],
                [2.0, 0.0],
                [1.0, 1.0],
            ],
            dtype=np.float64,
        ),
        triangle_faces=_mesh().triangle_faces,
    )

    with pytest.raises(
        ValueError,
        match="degenerate",
    ):
        AtlasPortraitFlameTriangleVisibilityEvaluator.evaluate(
            _mesh(),
            projection=projection,
        )
