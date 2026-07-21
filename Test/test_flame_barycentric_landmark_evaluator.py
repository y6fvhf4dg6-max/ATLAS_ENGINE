from __future__ import annotations

import numpy as np
import pytest

from CORE.providers.portrait.atlas_flame_barycentric_landmark_evaluator import (
    AtlasFlameBarycentricLandmarkEvaluator,
)


def _vertices() -> np.ndarray:
    return np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [1.0, 1.0, 1.0],
        ],
        dtype=np.float64,
    )


def _triangle_faces() -> np.ndarray:
    return np.array(
        [
            [0, 1, 2],
            [1, 3, 2],
        ],
        dtype=np.int64,
    )


def _landmark_indices() -> np.ndarray:
    return np.array(
        [
            4,
            17,
            263,
        ],
        dtype=np.int64,
    )


def _landmark_face_indices() -> np.ndarray:
    return np.array(
        [
            0,
            1,
            0,
        ],
        dtype=np.int64,
    )


def _landmark_barycentric_coordinates() -> np.ndarray:
    return np.array(
        [
            [1.0, 0.0, 0.0],
            [0.25, 0.50, 0.25],
            [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0],
        ],
        dtype=np.float64,
    )


def test_evaluator_returns_expected_shape():
    result = AtlasFlameBarycentricLandmarkEvaluator.evaluate(
        vertices=_vertices(),
        triangle_faces=_triangle_faces(),
        landmark_indices=_landmark_indices(),
        landmark_face_indices=_landmark_face_indices(),
        landmark_barycentric_coordinates=(
            _landmark_barycentric_coordinates()
        ),
        requested_mediapipe_ids=(
            4,
            17,
            263,
        ),
    )

    assert result.shape == (
        3,
        3,
    )


def test_evaluator_returns_float64_points():
    result = AtlasFlameBarycentricLandmarkEvaluator.evaluate(
        vertices=_vertices(),
        triangle_faces=_triangle_faces(),
        landmark_indices=_landmark_indices(),
        landmark_face_indices=_landmark_face_indices(),
        landmark_barycentric_coordinates=(
            _landmark_barycentric_coordinates()
        ),
        requested_mediapipe_ids=(
            4,
            17,
            263,
        ),
    )

    assert result.dtype == np.float64


def test_evaluator_computes_barycentric_positions():
    result = AtlasFlameBarycentricLandmarkEvaluator.evaluate(
        vertices=_vertices(),
        triangle_faces=_triangle_faces(),
        landmark_indices=_landmark_indices(),
        landmark_face_indices=_landmark_face_indices(),
        landmark_barycentric_coordinates=(
            _landmark_barycentric_coordinates()
        ),
        requested_mediapipe_ids=(
            4,
            17,
            263,
        ),
    )

    assert result[0] == pytest.approx(
        [
            0.0,
            0.0,
            0.0,
        ]
    )

    assert result[1] == pytest.approx(
        [
            0.75,
            0.75,
            0.50,
        ]
    )

    assert result[2] == pytest.approx(
        [
            1.0 / 3.0,
            1.0 / 3.0,
            0.0,
        ]
    )


def test_evaluator_preserves_requested_id_order():
    result = AtlasFlameBarycentricLandmarkEvaluator.evaluate(
        vertices=_vertices(),
        triangle_faces=_triangle_faces(),
        landmark_indices=_landmark_indices(),
        landmark_face_indices=_landmark_face_indices(),
        landmark_barycentric_coordinates=(
            _landmark_barycentric_coordinates()
        ),
        requested_mediapipe_ids=(
            263,
            4,
        ),
    )

    assert result[0] == pytest.approx(
        [
            1.0 / 3.0,
            1.0 / 3.0,
            0.0,
        ]
    )

    assert result[1] == pytest.approx(
        [
            0.0,
            0.0,
            0.0,
        ]
    )


def test_evaluator_returns_independent_read_only_array():
    result = AtlasFlameBarycentricLandmarkEvaluator.evaluate(
        vertices=_vertices(),
        triangle_faces=_triangle_faces(),
        landmark_indices=_landmark_indices(),
        landmark_face_indices=_landmark_face_indices(),
        landmark_barycentric_coordinates=(
            _landmark_barycentric_coordinates()
        ),
        requested_mediapipe_ids=(
            4,
            17,
        ),
    )

    assert result.flags.writeable is False

    with pytest.raises(
        ValueError,
    ):
        result[
            0,
            0,
        ] = 99.0


def test_evaluator_is_deterministic():
    arguments = {
        "vertices": _vertices(),
        "triangle_faces": _triangle_faces(),
        "landmark_indices": _landmark_indices(),
        "landmark_face_indices": _landmark_face_indices(),
        "landmark_barycentric_coordinates": (
            _landmark_barycentric_coordinates()
        ),
        "requested_mediapipe_ids": (
            4,
            17,
            263,
        ),
    }

    first = AtlasFlameBarycentricLandmarkEvaluator.evaluate(
        **arguments,
    )

    second = AtlasFlameBarycentricLandmarkEvaluator.evaluate(
        **arguments,
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
        np.array(
            [
                [0.0, 0.0, np.nan],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ],
            dtype=np.float64,
        ),
    ],
)
def test_evaluator_rejects_invalid_vertices(
    vertices,
):
    with pytest.raises(
        ValueError,
        match="vertices",
    ):
        AtlasFlameBarycentricLandmarkEvaluator.evaluate(
            vertices=vertices,
            triangle_faces=_triangle_faces(),
            landmark_indices=_landmark_indices(),
            landmark_face_indices=_landmark_face_indices(),
            landmark_barycentric_coordinates=(
                _landmark_barycentric_coordinates()
            ),
            requested_mediapipe_ids=(
                4,
            ),
        )


def test_evaluator_rejects_invalid_triangle_shape():
    with pytest.raises(
        ValueError,
        match="triangle_faces",
    ):
        AtlasFlameBarycentricLandmarkEvaluator.evaluate(
            vertices=_vertices(),
            triangle_faces=np.zeros(
                (
                    2,
                    4,
                ),
                dtype=np.int64,
            ),
            landmark_indices=_landmark_indices(),
            landmark_face_indices=_landmark_face_indices(),
            landmark_barycentric_coordinates=(
                _landmark_barycentric_coordinates()
            ),
            requested_mediapipe_ids=(
                4,
            ),
        )


def test_evaluator_rejects_triangle_vertex_out_of_range():
    triangle_faces = _triangle_faces()
    triangle_faces[
        0,
        0,
    ] = 99

    with pytest.raises(
        ValueError,
        match="triangle",
    ):
        AtlasFlameBarycentricLandmarkEvaluator.evaluate(
            vertices=_vertices(),
            triangle_faces=triangle_faces,
            landmark_indices=_landmark_indices(),
            landmark_face_indices=_landmark_face_indices(),
            landmark_barycentric_coordinates=(
                _landmark_barycentric_coordinates()
            ),
            requested_mediapipe_ids=(
                4,
            ),
        )


def test_evaluator_rejects_embedding_length_mismatch():
    with pytest.raises(
        ValueError,
        match="embedding",
    ):
        AtlasFlameBarycentricLandmarkEvaluator.evaluate(
            vertices=_vertices(),
            triangle_faces=_triangle_faces(),
            landmark_indices=np.array(
                [
                    4,
                    17,
                ],
                dtype=np.int64,
            ),
            landmark_face_indices=_landmark_face_indices(),
            landmark_barycentric_coordinates=(
                _landmark_barycentric_coordinates()
            ),
            requested_mediapipe_ids=(
                4,
            ),
        )


def test_evaluator_rejects_embedding_face_out_of_range():
    landmark_face_indices = _landmark_face_indices()
    landmark_face_indices[
        0
    ] = 99

    with pytest.raises(
        ValueError,
        match="face",
    ):
        AtlasFlameBarycentricLandmarkEvaluator.evaluate(
            vertices=_vertices(),
            triangle_faces=_triangle_faces(),
            landmark_indices=_landmark_indices(),
            landmark_face_indices=landmark_face_indices,
            landmark_barycentric_coordinates=(
                _landmark_barycentric_coordinates()
            ),
            requested_mediapipe_ids=(
                4,
            ),
        )


def test_evaluator_rejects_invalid_barycentric_shape():
    with pytest.raises(
        ValueError,
        match="barycentric",
    ):
        AtlasFlameBarycentricLandmarkEvaluator.evaluate(
            vertices=_vertices(),
            triangle_faces=_triangle_faces(),
            landmark_indices=_landmark_indices(),
            landmark_face_indices=_landmark_face_indices(),
            landmark_barycentric_coordinates=np.zeros(
                (
                    3,
                    2,
                ),
                dtype=np.float64,
            ),
            requested_mediapipe_ids=(
                4,
            ),
        )


def test_evaluator_rejects_non_finite_barycentric_values():
    barycentric = (
        _landmark_barycentric_coordinates()
    )

    barycentric[
        0,
        0,
    ] = np.nan

    with pytest.raises(
        ValueError,
        match="barycentric",
    ):
        AtlasFlameBarycentricLandmarkEvaluator.evaluate(
            vertices=_vertices(),
            triangle_faces=_triangle_faces(),
            landmark_indices=_landmark_indices(),
            landmark_face_indices=_landmark_face_indices(),
            landmark_barycentric_coordinates=barycentric,
            requested_mediapipe_ids=(
                4,
            ),
        )


def test_evaluator_rejects_barycentric_sum_mismatch():
    barycentric = (
        _landmark_barycentric_coordinates()
    )

    barycentric[
        0
    ] = [
        0.5,
        0.5,
        0.5,
    ]

    with pytest.raises(
        ValueError,
        match="sum",
    ):
        AtlasFlameBarycentricLandmarkEvaluator.evaluate(
            vertices=_vertices(),
            triangle_faces=_triangle_faces(),
            landmark_indices=_landmark_indices(),
            landmark_face_indices=_landmark_face_indices(),
            landmark_barycentric_coordinates=barycentric,
            requested_mediapipe_ids=(
                4,
            ),
        )


def test_evaluator_rejects_duplicate_embedding_ids():
    landmark_indices = _landmark_indices()

    landmark_indices[
        1
    ] = 4

    with pytest.raises(
        ValueError,
        match="unique",
    ):
        AtlasFlameBarycentricLandmarkEvaluator.evaluate(
            vertices=_vertices(),
            triangle_faces=_triangle_faces(),
            landmark_indices=landmark_indices,
            landmark_face_indices=_landmark_face_indices(),
            landmark_barycentric_coordinates=(
                _landmark_barycentric_coordinates()
            ),
            requested_mediapipe_ids=(
                4,
            ),
        )


def test_evaluator_rejects_missing_requested_id():
    with pytest.raises(
        ValueError,
        match="999",
    ):
        AtlasFlameBarycentricLandmarkEvaluator.evaluate(
            vertices=_vertices(),
            triangle_faces=_triangle_faces(),
            landmark_indices=_landmark_indices(),
            landmark_face_indices=_landmark_face_indices(),
            landmark_barycentric_coordinates=(
                _landmark_barycentric_coordinates()
            ),
            requested_mediapipe_ids=(
                999,
            ),
        )


@pytest.mark.parametrize(
    "requested_mediapipe_ids",
    [
        (),
        None,
        "4,17",
        (
            4,
            4,
        ),
    ],
)
def test_evaluator_rejects_invalid_requested_ids(
    requested_mediapipe_ids,
):
    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
    ):
        AtlasFlameBarycentricLandmarkEvaluator.evaluate(
            vertices=_vertices(),
            triangle_faces=_triangle_faces(),
            landmark_indices=_landmark_indices(),
            landmark_face_indices=_landmark_face_indices(),
            landmark_barycentric_coordinates=(
                _landmark_barycentric_coordinates()
            ),
            requested_mediapipe_ids=requested_mediapipe_ids,
        )


def test_evaluator_accepts_numpy_integer_ids():
    result = AtlasFlameBarycentricLandmarkEvaluator.evaluate(
        vertices=_vertices(),
        triangle_faces=_triangle_faces(),
        landmark_indices=_landmark_indices(),
        landmark_face_indices=_landmark_face_indices(),
        landmark_barycentric_coordinates=(
            _landmark_barycentric_coordinates()
        ),
        requested_mediapipe_ids=np.array(
            [
                4,
                17,
            ],
            dtype=np.int64,
        ),
    )

    assert result.shape == (
        2,
        3,
    )
