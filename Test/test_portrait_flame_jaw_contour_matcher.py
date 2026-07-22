from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_jaw_contour_correspondence import (
    AtlasPortraitFlameJawContourCorrespondence,
)
from CORE.atlas_portrait_flame_jaw_contour_matcher import (
    AtlasPortraitFlameJawContourMatcher,
)


def _projected_vertices() -> np.ndarray:
    """
    Ordered jaw chain:

        0 -- 1 -- 2 -- 3 -- 4 -- 5 -- 6

    Vertex 3 is the chin anchor.
    """
    return np.array(
        [
            [100.0, 180.0],
            [120.0, 220.0],
            [155.0, 250.0],
            [200.0, 265.0],
            [245.0, 250.0],
            [280.0, 220.0],
            [300.0, 180.0],

            # Deliberate non-jaw ear/neck geometry.
            [70.0, 145.0],
            [65.0, 220.0],
            [85.0, 300.0],
            [330.0, 145.0],
            [335.0, 220.0],
            [315.0, 300.0],
        ],
        dtype=np.float64,
    )


def _ordered_jaw_edges() -> np.ndarray:
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


def _target_points() -> np.ndarray:
    return np.array(
        [
            [103.0, 184.0],
            [126.0, 224.0],
            [160.0, 248.0],
            [201.0, 263.0],
            [240.0, 249.0],
            [274.0, 224.0],
            [297.0, 184.0],
        ],
        dtype=np.float64,
    )


def _landmark_ids() -> tuple[int, ...]:
    return (
        234,
        132,
        172,
        152,
        397,
        361,
        454,
    )


def _match(
    **overrides,
) -> AtlasPortraitFlameJawContourCorrespondence:
    arguments = {
        "landmark_ids": _landmark_ids(),
        "target_points_2d": _target_points(),
        "projected_vertices_2d": _projected_vertices(),
        "ordered_jaw_edge_vertex_indices": (
            _ordered_jaw_edges()
        ),
        "chin_landmark_id": 152,
        "metadata": {
            "coordinate_space": "pixel",
            "model_family": "flame",
            "synthetic": True,
        },
    }

    arguments.update(
        overrides
    )

    return AtlasPortraitFlameJawContourMatcher.match(
        **arguments
    )


def test_matcher_returns_correspondence():
    result = _match()

    assert isinstance(
        result,
        AtlasPortraitFlameJawContourCorrespondence,
    )


def test_matcher_preserves_landmark_order():
    result = _match()

    assert result.landmark_ids == _landmark_ids()


def test_matcher_preserves_target_points():
    result = _match()

    np.testing.assert_allclose(
        result.target_points_2d,
        _target_points(),
    )


def test_matcher_matches_only_supplied_jaw_edges():
    result = _match()

    allowed_edges = {
        tuple(
            edge
        )
        for edge in _ordered_jaw_edges()
    }

    assert all(
        tuple(
            edge
        )
        in allowed_edges
        for edge in result.matched_edge_vertex_indices
    )

    used_vertices = set(
        result.matched_edge_vertex_indices.reshape(
            -1
        ).tolist()
    )

    # Ear and neck vertices deliberately placed in the
    # projected mesh must never be selected.
    assert used_vertices.isdisjoint(
        {
            7,
            8,
            9,
            10,
            11,
            12,
        }
    )


def test_matcher_assignments_are_monotonic():
    result = _match()

    edge_lookup = {
        tuple(
            edge
        ): index
        for index, edge in enumerate(
            _ordered_jaw_edges()
        )
    }

    matched_positions = [
        edge_lookup[
            tuple(
                edge
            )
        ]
        for edge in result.matched_edge_vertex_indices
    ]

    assert matched_positions == sorted(
        matched_positions
    )


def test_matcher_anchors_chin_to_chin_vertex():
    result = _match()

    chin_index = result.landmark_ids.index(
        152
    )

    np.testing.assert_allclose(
        result.matched_points_2d[
            chin_index
        ],
        _projected_vertices()[
            3
        ],
    )

    assert 3 in set(
        result.matched_edge_vertex_indices[
            chin_index
        ].tolist()
    )


def test_matcher_matches_left_side_before_chin():
    result = _match()

    chin_index = result.landmark_ids.index(
        152
    )

    assert np.all(
        result.matched_points_2d[
            :chin_index,
            0,
        ]
        <= result.matched_points_2d[
            chin_index,
            0,
        ]
    )


def test_matcher_matches_right_side_after_chin():
    result = _match()

    chin_index = result.landmark_ids.index(
        152
    )

    assert np.all(
        result.matched_points_2d[
            chin_index + 1:,
            0,
        ]
        >= result.matched_points_2d[
            chin_index,
            0,
        ]
    )


def test_matcher_computes_residuals():
    result = _match()

    expected = np.linalg.norm(
        result.matched_points_2d
        - result.target_points_2d,
        axis=1,
    )

    np.testing.assert_allclose(
        result.residuals,
        expected,
    )


def test_matcher_marks_all_matched_landmarks_visible():
    result = _match()

    np.testing.assert_array_equal(
        result.visible_landmark_mask,
        np.ones(
            len(
                _landmark_ids()
            ),
            dtype=np.bool_,
        ),
    )


def test_matcher_builds_deterministic_metadata():
    result = _match()

    assert result.metadata == {
        "chin_landmark_id": 152,
        "coordinate_space": "pixel",
        "correspondence_type": (
            "ordered_dynamic_jaw_contour"
        ),
        "jaw_edge_count": 6,
        "landmark_count": 7,
        "matching_method": (
            "split_monotonic_point_to_segment"
        ),
        "model_family": "flame",
        "synthetic": True,
    }


def test_matcher_is_deterministic():
    first = _match()
    second = _match()

    assert first.to_dict() == second.to_dict()


def test_matcher_does_not_modify_inputs():
    target_points = _target_points()
    projected_vertices = _projected_vertices()
    jaw_edges = _ordered_jaw_edges()

    target_before = target_points.copy()
    projected_before = projected_vertices.copy()
    edges_before = jaw_edges.copy()

    _match(
        target_points_2d=target_points,
        projected_vertices_2d=projected_vertices,
        ordered_jaw_edge_vertex_indices=jaw_edges,
    )

    np.testing.assert_array_equal(
        target_points,
        target_before,
    )
    np.testing.assert_array_equal(
        projected_vertices,
        projected_before,
    )
    np.testing.assert_array_equal(
        jaw_edges,
        edges_before,
    )


def test_matcher_rejects_missing_chin_landmark():
    with pytest.raises(
        ValueError,
        match="chin_landmark_id",
    ):
        _match(
            chin_landmark_id=999,
        )


def test_matcher_rejects_chin_at_chain_endpoint():
    with pytest.raises(
        ValueError,
        match="chin_landmark_id",
    ):
        _match(
            chin_landmark_id=234,
        )


@pytest.mark.parametrize(
    "edges",
    [
        np.array(
            [
                [0, 1],
                [2, 3],
            ],
            dtype=np.int64,
        ),
        np.array(
            [
                [0, 1],
                [1, 2],
                [3, 4],
            ],
            dtype=np.int64,
        ),
        np.array(
            [
                [0, 1],
                [1, 0],
            ],
            dtype=np.int64,
        ),
    ],
)
def test_matcher_rejects_disconnected_or_reversed_edge_chain(
    edges,
):
    with pytest.raises(
        ValueError,
        match="ordered_jaw_edge_vertex_indices",
    ):
        _match(
            ordered_jaw_edge_vertex_indices=edges,
        )


def test_matcher_rejects_edge_indices_outside_vertices():
    edges = _ordered_jaw_edges()
    edges[
        -1,
        1,
    ] = 999

    with pytest.raises(
        ValueError,
        match="ordered_jaw_edge_vertex_indices",
    ):
        _match(
            ordered_jaw_edge_vertex_indices=edges,
        )


def test_matcher_rejects_nonfinite_projected_vertices():
    vertices = _projected_vertices()
    vertices[
        0,
        0,
    ] = np.nan

    with pytest.raises(
        ValueError,
        match="projected_vertices_2d",
    ):
        _match(
            projected_vertices_2d=vertices,
        )


def test_matcher_rejects_target_count_mismatch():
    with pytest.raises(
        ValueError,
        match="target_points_2d",
    ):
        _match(
            target_points_2d=_target_points()[
                :-1
            ],
        )


def test_matcher_rejects_non_mapping_metadata():
    with pytest.raises(
        TypeError,
        match="metadata",
    ):
        _match(
            metadata=[
                "invalid",
            ],
        )
