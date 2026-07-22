from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_visible_boundary_edge_extractor import (
    AtlasPortraitFlameVisibleBoundaryEdgeExtractor,
)


def _square_faces() -> np.ndarray:
    return np.array(
        [
            [0, 1, 2],
            [0, 2, 3],
        ],
        dtype=np.int64,
    )


def test_extractor_removes_shared_interior_edge():
    result = (
        AtlasPortraitFlameVisibleBoundaryEdgeExtractor.extract(
            triangle_faces=_square_faces(),
            visible_triangle_mask=np.array(
                [
                    True,
                    True,
                ],
                dtype=np.bool_,
            ),
            vertex_count=4,
        )
    )

    np.testing.assert_array_equal(
        result,
        np.array(
            [
                [0, 1],
                [0, 3],
                [1, 2],
                [2, 3],
            ],
            dtype=np.int64,
        ),
    )


def test_extractor_retains_edges_of_single_visible_triangle():
    result = (
        AtlasPortraitFlameVisibleBoundaryEdgeExtractor.extract(
            triangle_faces=_square_faces(),
            visible_triangle_mask=np.array(
                [
                    True,
                    False,
                ],
                dtype=np.bool_,
            ),
            vertex_count=4,
        )
    )

    np.testing.assert_array_equal(
        result,
        np.array(
            [
                [0, 1],
                [0, 2],
                [1, 2],
            ],
            dtype=np.int64,
        ),
    )


def test_extractor_ignores_hidden_triangles():
    faces = np.array(
        [
            [0, 1, 2],
            [3, 4, 5],
        ],
        dtype=np.int64,
    )

    result = (
        AtlasPortraitFlameVisibleBoundaryEdgeExtractor.extract(
            triangle_faces=faces,
            visible_triangle_mask=np.array(
                [
                    False,
                    True,
                ],
                dtype=np.bool_,
            ),
            vertex_count=6,
        )
    )

    np.testing.assert_array_equal(
        result,
        np.array(
            [
                [3, 4],
                [3, 5],
                [4, 5],
            ],
            dtype=np.int64,
        ),
    )


def test_extractor_returns_empty_array_when_no_triangle_is_visible():
    result = (
        AtlasPortraitFlameVisibleBoundaryEdgeExtractor.extract(
            triangle_faces=_square_faces(),
            visible_triangle_mask=np.array(
                [
                    False,
                    False,
                ],
                dtype=np.bool_,
            ),
            vertex_count=4,
        )
    )

    assert result.shape == (
        0,
        2,
    )
    assert result.dtype == np.int64


def test_extractor_normalizes_edge_orientation():
    faces = np.array(
        [
            [2, 1, 0],
        ],
        dtype=np.int64,
    )

    result = (
        AtlasPortraitFlameVisibleBoundaryEdgeExtractor.extract(
            triangle_faces=faces,
            visible_triangle_mask=np.array(
                [
                    True,
                ],
                dtype=np.bool_,
            ),
            vertex_count=3,
        )
    )

    np.testing.assert_array_equal(
        result,
        np.array(
            [
                [0, 1],
                [0, 2],
                [1, 2],
            ],
            dtype=np.int64,
        ),
    )


def test_extractor_sorts_edges_deterministically():
    faces = np.array(
        [
            [5, 3, 4],
            [2, 0, 1],
        ],
        dtype=np.int64,
    )

    result = (
        AtlasPortraitFlameVisibleBoundaryEdgeExtractor.extract(
            triangle_faces=faces,
            visible_triangle_mask=np.array(
                [
                    True,
                    True,
                ],
                dtype=np.bool_,
            ),
            vertex_count=6,
        )
    )

    expected = np.array(
        [
            [0, 1],
            [0, 2],
            [1, 2],
            [3, 4],
            [3, 5],
            [4, 5],
        ],
        dtype=np.int64,
    )

    np.testing.assert_array_equal(
        result,
        expected,
    )


def test_extractor_result_is_read_only():
    result = (
        AtlasPortraitFlameVisibleBoundaryEdgeExtractor.extract(
            triangle_faces=_square_faces(),
            visible_triangle_mask=np.array(
                [
                    True,
                    True,
                ],
                dtype=np.bool_,
            ),
            vertex_count=4,
        )
    )

    assert result.flags.writeable is False


def test_extractor_does_not_modify_inputs():
    faces = _square_faces()
    visible_mask = np.array(
        [
            True,
            True,
        ],
        dtype=np.bool_,
    )

    faces_before = faces.copy()
    mask_before = visible_mask.copy()

    AtlasPortraitFlameVisibleBoundaryEdgeExtractor.extract(
        triangle_faces=faces,
        visible_triangle_mask=visible_mask,
        vertex_count=4,
    )

    np.testing.assert_array_equal(
        faces,
        faces_before,
    )
    np.testing.assert_array_equal(
        visible_mask,
        mask_before,
    )


def test_extractor_is_deterministic():
    arguments = {
        "triangle_faces": _square_faces(),
        "visible_triangle_mask": np.array(
            [
                True,
                True,
            ],
            dtype=np.bool_,
        ),
        "vertex_count": 4,
    }

    first = (
        AtlasPortraitFlameVisibleBoundaryEdgeExtractor.extract(
            **arguments
        )
    )
    second = (
        AtlasPortraitFlameVisibleBoundaryEdgeExtractor.extract(
            **arguments
        )
    )

    np.testing.assert_array_equal(
        first,
        second,
    )


@pytest.mark.parametrize(
    "triangle_faces",
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
            6,
            dtype=np.int64,
        ),
    ],
)
def test_extractor_rejects_invalid_triangle_face_shape(
    triangle_faces,
):
    with pytest.raises(
        ValueError,
        match="triangle_faces",
    ):
        AtlasPortraitFlameVisibleBoundaryEdgeExtractor.extract(
            triangle_faces=triangle_faces,
            visible_triangle_mask=np.ones(
                2,
                dtype=np.bool_,
            ),
            vertex_count=4,
        )


def test_extractor_rejects_noninteger_triangle_indices():
    with pytest.raises(
        ValueError,
        match="triangle_faces",
    ):
        AtlasPortraitFlameVisibleBoundaryEdgeExtractor.extract(
            triangle_faces=np.array(
                [
                    [0.0, 1.5, 2.0],
                ],
                dtype=np.float64,
            ),
            visible_triangle_mask=np.array(
                [
                    True,
                ],
                dtype=np.bool_,
            ),
            vertex_count=3,
        )


def test_extractor_rejects_negative_triangle_indices():
    with pytest.raises(
        ValueError,
        match="triangle_faces",
    ):
        AtlasPortraitFlameVisibleBoundaryEdgeExtractor.extract(
            triangle_faces=np.array(
                [
                    [0, 1, -1],
                ],
                dtype=np.int64,
            ),
            visible_triangle_mask=np.array(
                [
                    True,
                ],
                dtype=np.bool_,
            ),
            vertex_count=3,
        )


def test_extractor_rejects_indices_outside_vertex_count():
    with pytest.raises(
        ValueError,
        match="triangle_faces",
    ):
        AtlasPortraitFlameVisibleBoundaryEdgeExtractor.extract(
            triangle_faces=np.array(
                [
                    [0, 1, 4],
                ],
                dtype=np.int64,
            ),
            visible_triangle_mask=np.array(
                [
                    True,
                ],
                dtype=np.bool_,
            ),
            vertex_count=4,
        )


def test_extractor_rejects_degenerate_triangle():
    with pytest.raises(
        ValueError,
        match="triangle_faces",
    ):
        AtlasPortraitFlameVisibleBoundaryEdgeExtractor.extract(
            triangle_faces=np.array(
                [
                    [0, 1, 1],
                ],
                dtype=np.int64,
            ),
            visible_triangle_mask=np.array(
                [
                    True,
                ],
                dtype=np.bool_,
            ),
            vertex_count=3,
        )


def test_extractor_rejects_visibility_count_mismatch():
    with pytest.raises(
        ValueError,
        match="visible_triangle_mask",
    ):
        AtlasPortraitFlameVisibleBoundaryEdgeExtractor.extract(
            triangle_faces=_square_faces(),
            visible_triangle_mask=np.array(
                [
                    True,
                ],
                dtype=np.bool_,
            ),
            vertex_count=4,
        )


def test_extractor_rejects_nonboolean_visibility_mask():
    with pytest.raises(
        ValueError,
        match="visible_triangle_mask",
    ):
        AtlasPortraitFlameVisibleBoundaryEdgeExtractor.extract(
            triangle_faces=_square_faces(),
            visible_triangle_mask=np.array(
                [
                    1,
                    0,
                ],
                dtype=np.int64,
            ),
            vertex_count=4,
        )


@pytest.mark.parametrize(
    "vertex_count",
    [
        0,
        -1,
        3.5,
        True,
    ],
)
def test_extractor_rejects_invalid_vertex_count(
    vertex_count,
):
    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
        match="vertex_count",
    ):
        AtlasPortraitFlameVisibleBoundaryEdgeExtractor.extract(
            triangle_faces=_square_faces(),
            visible_triangle_mask=np.array(
                [
                    True,
                    True,
                ],
                dtype=np.bool_,
            ),
            vertex_count=vertex_count,
        )
