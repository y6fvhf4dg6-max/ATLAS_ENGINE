from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_jaw_boundary_path_selector import (
    AtlasPortraitFlameJawBoundaryPathSelector,
)


def _projected_vertices() -> np.ndarray:
    """
    Intended jaw route:

        0 -- 1 -- 2 -- 3 -- 4 -- 5 -- 6

    Vertex 3 is the chin.

    Alternative routes deliberately model:

    - upper/ear detour:
      0 -- 7 -- 8 -- 9 -- 6

    - lower/neck detour:
      2 -- 10 -- 11 -- 12 -- 4
    """
    return np.array(
        [
            [100.0, 180.0],  # 0 left cheek endpoint
            [120.0, 220.0],  # 1
            [155.0, 250.0],  # 2
            [200.0, 270.0],  # 3 chin
            [245.0, 250.0],  # 4
            [280.0, 220.0],  # 5
            [300.0, 180.0],  # 6 right cheek endpoint

            [75.0, 130.0],   # 7 left ear / upper detour
            [200.0, 85.0],   # 8 skull top
            [325.0, 130.0],  # 9 right ear / upper detour

            [145.0, 315.0],  # 10 left neck
            [200.0, 350.0],  # 11 neck / bust bottom
            [255.0, 315.0],  # 12 right neck
        ],
        dtype=np.float64,
    )


def _boundary_edges() -> np.ndarray:
    return np.array(
        [
            # Correct jaw path.
            [0, 1],
            [1, 2],
            [2, 3],
            [3, 4],
            [4, 5],
            [5, 6],

            # Ear/skull path.
            [0, 7],
            [7, 8],
            [8, 9],
            [9, 6],

            # Neck/bust path.
            [2, 10],
            [10, 11],
            [11, 12],
            [12, 4],
        ],
        dtype=np.int64,
    )


def _jaw_targets() -> np.ndarray:
    return np.array(
        [
            [102.0, 182.0],
            [123.0, 221.0],
            [158.0, 248.0],
            [200.0, 268.0],
            [242.0, 248.0],
            [277.0, 221.0],
            [298.0, 182.0],
        ],
        dtype=np.float64,
    )


def _expected_ordered_edges() -> np.ndarray:
    return np.array(
        [
            [0, 1],
            [1, 2],
            [2, 3],
            [3, 4],
            [4, 5],
            [5, 6],
        ],
        dtype=np.int64,
    )


def _select(
    **overrides,
) -> np.ndarray:
    arguments = {
        "boundary_edge_vertex_indices": (
            _boundary_edges()
        ),
        "projected_vertices_2d": (
            _projected_vertices()
        ),
        "jaw_target_points_2d": (
            _jaw_targets()
        ),
        "chin_target_index": 3,
    }

    arguments.update(
        overrides
    )

    return (
        AtlasPortraitFlameJawBoundaryPathSelector.select(
            **arguments
        )
    )


def test_selector_returns_expected_jaw_path():
    result = _select()

    np.testing.assert_array_equal(
        result,
        _expected_ordered_edges(),
    )


def test_selector_returns_contiguous_oriented_chain():
    result = _select()

    np.testing.assert_array_equal(
        result[
            :-1,
            1,
        ],
        result[
            1:,
            0,
        ],
    )


def test_selector_starts_near_first_target():
    result = _select()
    vertices = _projected_vertices()

    start_point = vertices[
        result[
            0,
            0,
        ]
    ]

    np.testing.assert_allclose(
        start_point,
        vertices[
            0
        ],
    )


def test_selector_ends_near_last_target():
    result = _select()
    vertices = _projected_vertices()

    end_point = vertices[
        result[
            -1,
            1,
        ]
    ]

    np.testing.assert_allclose(
        end_point,
        vertices[
            6
        ],
    )


def test_selector_path_contains_chin_vertex():
    result = _select()

    chain_vertices = np.concatenate(
        (
            result[
                :1,
                0,
            ],
            result[
                :,
                1,
            ],
        )
    )

    assert 3 in set(
        chain_vertices.tolist()
    )


def test_selector_excludes_ear_and_skull_vertices():
    result = _select()

    used_vertices = set(
        result.reshape(
            -1
        ).tolist()
    )

    assert used_vertices.isdisjoint(
        {
            7,
            8,
            9,
        }
    )


def test_selector_excludes_neck_and_bust_vertices():
    result = _select()

    used_vertices = set(
        result.reshape(
            -1
        ).tolist()
    )

    assert used_vertices.isdisjoint(
        {
            10,
            11,
            12,
        }
    )


def test_selector_accepts_unsorted_undirected_input_edges():
    edges = _boundary_edges()[
        ::-1
    ].copy()

    edges[
        1::2
    ] = edges[
        1::2,
        ::-1
    ]

    result = _select(
        boundary_edge_vertex_indices=edges,
    )

    np.testing.assert_array_equal(
        result,
        _expected_ordered_edges(),
    )


def test_selector_result_is_read_only():
    result = _select()

    assert result.flags.writeable is False


def test_selector_does_not_modify_inputs():
    edges = _boundary_edges()
    vertices = _projected_vertices()
    targets = _jaw_targets()

    edges_before = edges.copy()
    vertices_before = vertices.copy()
    targets_before = targets.copy()

    _select(
        boundary_edge_vertex_indices=edges,
        projected_vertices_2d=vertices,
        jaw_target_points_2d=targets,
    )

    np.testing.assert_array_equal(
        edges,
        edges_before,
    )
    np.testing.assert_array_equal(
        vertices,
        vertices_before,
    )
    np.testing.assert_array_equal(
        targets,
        targets_before,
    )


def test_selector_is_deterministic():
    first = _select()
    second = _select()

    np.testing.assert_array_equal(
        first,
        second,
    )


def test_selector_rejects_missing_path():
    edges = np.array(
        [
            [0, 1],
            [1, 2],
            [4, 5],
            [5, 6],
        ],
        dtype=np.int64,
    )

    with pytest.raises(
        ValueError,
        match="boundary_edge_vertex_indices",
    ):
        _select(
            boundary_edge_vertex_indices=edges,
        )


def test_selector_rejects_path_without_chin_connection():
    edges = np.array(
        [
            [0, 1],
            [1, 2],
            [2, 10],
            [10, 11],
            [11, 12],
            [12, 4],
            [4, 5],
            [5, 6],
        ],
        dtype=np.int64,
    )

    with pytest.raises(
        ValueError,
        match="chin",
    ):
        _select(
            boundary_edge_vertex_indices=edges,
        )


@pytest.mark.parametrize(
    "edges",
    [
        np.zeros(
            (
                3,
                3,
            ),
            dtype=np.int64,
        ),
        np.zeros(
            6,
            dtype=np.int64,
        ),
        np.array(
            [
                [0.0, 1.5],
            ],
            dtype=np.float64,
        ),
        np.array(
            [
                [-1, 0],
            ],
            dtype=np.int64,
        ),
    ],
)
def test_selector_rejects_invalid_boundary_edges(
    edges,
):
    with pytest.raises(
        ValueError,
        match="boundary_edge_vertex_indices",
    ):
        _select(
            boundary_edge_vertex_indices=edges,
        )


def test_selector_rejects_boundary_index_outside_vertices():
    edges = _boundary_edges()
    edges[
        0,
        0,
    ] = 999

    with pytest.raises(
        ValueError,
        match="boundary_edge_vertex_indices",
    ):
        _select(
            boundary_edge_vertex_indices=edges,
        )


def test_selector_rejects_nonfinite_projected_vertices():
    vertices = _projected_vertices()
    vertices[
        0,
        0,
    ] = np.nan

    with pytest.raises(
        ValueError,
        match="projected_vertices_2d",
    ):
        _select(
            projected_vertices_2d=vertices,
        )


def test_selector_rejects_invalid_target_shape():
    with pytest.raises(
        ValueError,
        match="jaw_target_points_2d",
    ):
        _select(
            jaw_target_points_2d=np.zeros(
                (
                    7,
                    3,
                ),
                dtype=np.float64,
            ),
        )


def test_selector_rejects_nonfinite_targets():
    targets = _jaw_targets()
    targets[
        0,
        0,
    ] = np.inf

    with pytest.raises(
        ValueError,
        match="jaw_target_points_2d",
    ):
        _select(
            jaw_target_points_2d=targets,
        )


@pytest.mark.parametrize(
    "chin_target_index",
    [
        -1,
        0,
        6,
        7,
        3.5,
        True,
    ],
)
def test_selector_rejects_invalid_chin_target_index(
    chin_target_index,
):
    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
        match="chin_target_index",
    ):
        _select(
            chin_target_index=chin_target_index,
        )
