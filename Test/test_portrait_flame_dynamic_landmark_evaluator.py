from __future__ import annotations

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from CORE.providers.portrait.atlas_portrait_flame_dynamic_landmark_evaluator import (
    AtlasPortraitFlameDynamicLandmarkEvaluation,
    AtlasPortraitFlameDynamicLandmarkEvaluator,
)
from CORE.providers.portrait.atlas_portrait_flame_dynamic_landmark_selector import (
    AtlasPortraitFlameDynamicLandmarkSelection,
)


def _selection() -> AtlasPortraitFlameDynamicLandmarkSelection:
    return AtlasPortraitFlameDynamicLandmarkSelection(
        requested_yaw_degrees=0.0,
        selected_yaw_degrees=0.0,
        yaw_bin_index=0,
        landmark_face_indices=np.array(
            [
                0,
                1,
            ],
            dtype=np.int64,
        ),
        landmark_barycentric_coordinates=np.array(
            [
                [0.5, 0.25, 0.25],
                [0.0, 0.5, 0.5],
            ],
            dtype=np.float64,
        ),
    )


def _vertices() -> np.ndarray:
    return np.array(
        [
            [0.0, 0.0, 0.0],
            [2.0, 0.0, 0.0],
            [0.0, 2.0, 0.0],
            [0.0, 0.0, 2.0],
        ],
        dtype=np.float64,
    )


def _triangles() -> np.ndarray:
    return np.array(
        [
            [0, 1, 2],
            [0, 2, 3],
        ],
        dtype=np.int64,
    )


def _evaluate(
    *,
    selection: object | None = None,
    vertices: object | None = None,
    triangles: object | None = None,
) -> AtlasPortraitFlameDynamicLandmarkEvaluation:
    return AtlasPortraitFlameDynamicLandmarkEvaluator.evaluate(
        _selection() if selection is None else selection,
        vertices=_vertices() if vertices is None else vertices,
        triangles=_triangles() if triangles is None else triangles,
    )


def test_evaluator_returns_evaluation():
    result = _evaluate()

    assert isinstance(
        result,
        AtlasPortraitFlameDynamicLandmarkEvaluation,
    )


def test_evaluator_computes_barycentric_points():
    result = _evaluate()

    np.testing.assert_allclose(
        result.landmark_points,
        np.array(
            [
                [0.5, 0.5, 0.0],
                [0.0, 1.0, 1.0],
            ],
            dtype=np.float64,
        ),
    )


def test_evaluation_preserves_selection_metadata():
    result = _evaluate()

    assert result.requested_yaw_degrees == pytest.approx(
        0.0
    )
    assert result.selected_yaw_degrees == pytest.approx(
        0.0
    )
    assert result.yaw_bin_index == 0


def test_evaluation_reports_landmark_count():
    result = _evaluate()

    assert result.landmark_count == 2


def test_evaluation_points_are_read_only():
    result = _evaluate()

    assert result.landmark_points.flags.writeable is False


def test_evaluation_is_frozen():
    result = _evaluate()

    with pytest.raises(
        FrozenInstanceError,
    ):
        result.yaw_bin_index = 1


def test_evaluator_copies_output_data():
    vertices = _vertices()

    result = _evaluate(
        vertices=vertices,
    )

    vertices[
        :,
        :,
    ] = 99.0

    np.testing.assert_allclose(
        result.landmark_points,
        np.array(
            [
                [0.5, 0.5, 0.0],
                [0.0, 1.0, 1.0],
            ],
            dtype=np.float64,
        ),
    )


def test_evaluator_does_not_modify_inputs():
    selection = _selection()
    vertices = _vertices()
    triangles = _triangles()

    vertices_before = vertices.copy()
    triangles_before = triangles.copy()
    face_indices_before = (
        selection.landmark_face_indices.copy()
    )
    barycentric_before = (
        selection
        .landmark_barycentric_coordinates
        .copy()
    )

    AtlasPortraitFlameDynamicLandmarkEvaluator.evaluate(
        selection,
        vertices=vertices,
        triangles=triangles,
    )

    np.testing.assert_array_equal(
        vertices,
        vertices_before,
    )
    np.testing.assert_array_equal(
        triangles,
        triangles_before,
    )
    np.testing.assert_array_equal(
        selection.landmark_face_indices,
        face_indices_before,
    )
    np.testing.assert_array_equal(
        selection.landmark_barycentric_coordinates,
        barycentric_before,
    )


def test_evaluation_serialization_is_deterministic():
    first = _evaluate()
    second = _evaluate()

    assert first.to_dict() == second.to_dict()


def test_evaluator_accepts_float32_vertices():
    result = _evaluate(
        vertices=_vertices().astype(
            np.float32
        ),
    )

    assert result.landmark_points.dtype == np.float64


def test_evaluator_accepts_unsigned_triangles():
    result = _evaluate(
        triangles=_triangles().astype(
            np.uint32
        ),
    )

    assert result.landmark_count == 2


def test_evaluator_rejects_invalid_selection_type():
    with pytest.raises(
        TypeError,
        match="selection",
    ):
        _evaluate(
            selection=object(),
        )


@pytest.mark.parametrize(
    "vertices",
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
                4,
                4,
            ),
            dtype=np.float64,
        ),
        np.zeros(
            (
                0,
                3,
            ),
            dtype=np.float64,
        ),
        np.zeros(
            12,
            dtype=np.float64,
        ),
    ],
)
def test_evaluator_rejects_invalid_vertex_shape(
    vertices: np.ndarray,
):
    with pytest.raises(
        ValueError,
        match="vertices",
    ):
        _evaluate(
            vertices=vertices,
        )


def test_evaluator_rejects_nonfinite_vertices():
    vertices = _vertices()
    vertices[
        0,
        0,
    ] = np.nan

    with pytest.raises(
        ValueError,
        match="vertices",
    ):
        _evaluate(
            vertices=vertices,
        )


@pytest.mark.parametrize(
    "triangles",
    [
        np.zeros(
            (
                2,
                2,
            ),
            dtype=np.int64,
        ),
        np.zeros(
            (
                2,
                4,
            ),
            dtype=np.int64,
        ),
        np.zeros(
            (
                0,
                3,
            ),
            dtype=np.int64,
        ),
        np.zeros(
            6,
            dtype=np.int64,
        ),
    ],
)
def test_evaluator_rejects_invalid_triangle_shape(
    triangles: np.ndarray,
):
    with pytest.raises(
        ValueError,
        match="triangles",
    ):
        _evaluate(
            triangles=triangles,
        )


def test_evaluator_rejects_noninteger_triangles():
    triangles = np.array(
        [
            [0.0, 1.0, 2.5],
            [0.0, 2.0, 3.0],
        ],
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="triangles",
    ):
        _evaluate(
            triangles=triangles,
        )


def test_evaluator_rejects_negative_triangle_vertex_index():
    triangles = _triangles()
    triangles[
        0,
        0,
    ] = -1

    with pytest.raises(
        ValueError,
        match="triangles",
    ):
        _evaluate(
            triangles=triangles,
        )


def test_evaluator_rejects_triangle_vertex_index_outside_vertices():
    triangles = _triangles()
    triangles[
        1,
        2,
    ] = 4

    with pytest.raises(
        ValueError,
        match="vertices",
    ):
        _evaluate(
            triangles=triangles,
        )


def test_evaluator_rejects_landmark_face_index_outside_triangles():
    selection = AtlasPortraitFlameDynamicLandmarkSelection(
        requested_yaw_degrees=0.0,
        selected_yaw_degrees=0.0,
        yaw_bin_index=0,
        landmark_face_indices=np.array(
            [
                0,
                2,
            ],
            dtype=np.int64,
        ),
        landmark_barycentric_coordinates=np.array(
            [
                [1.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
            ],
            dtype=np.float64,
        ),
    )

    with pytest.raises(
        ValueError,
        match="landmark_face_indices",
    ):
        _evaluate(
            selection=selection,
        )


def test_evaluator_supports_repeated_landmark_faces():
    selection = AtlasPortraitFlameDynamicLandmarkSelection(
        requested_yaw_degrees=0.0,
        selected_yaw_degrees=0.0,
        yaw_bin_index=0,
        landmark_face_indices=np.array(
            [
                0,
                0,
            ],
            dtype=np.int64,
        ),
        landmark_barycentric_coordinates=np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ],
            dtype=np.float64,
        ),
    )

    result = _evaluate(
        selection=selection,
    )

    np.testing.assert_allclose(
        result.landmark_points,
        np.array(
            [
                [0.0, 0.0, 0.0],
                [2.0, 0.0, 0.0],
            ],
            dtype=np.float64,
        ),
    )
