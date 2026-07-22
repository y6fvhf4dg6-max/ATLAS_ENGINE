from __future__ import annotations

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from CORE.providers.portrait.atlas_portrait_flame_dynamic_landmark_embedding_loader import (
    AtlasPortraitFlameDynamicLandmarkEmbedding,
)
from CORE.providers.portrait.atlas_portrait_flame_dynamic_landmark_selector import (
    AtlasPortraitFlameDynamicLandmarkSelection,
    AtlasPortraitFlameDynamicLandmarkSelector,
)


def _embedding(
    yaw_bin_count: int = 79,
) -> AtlasPortraitFlameDynamicLandmarkEmbedding:
    face_indices = np.arange(
        yaw_bin_count * 2,
        dtype=np.int64,
    ).reshape(
        yaw_bin_count,
        2,
    )

    barycentric_coordinates = np.zeros(
        (
            yaw_bin_count,
            2,
            3,
        ),
        dtype=np.float64,
    )
    barycentric_coordinates[
        :,
        :,
        0,
    ] = 1.0

    return AtlasPortraitFlameDynamicLandmarkEmbedding(
        landmark_face_indices=face_indices,
        landmark_barycentric_coordinates=(
            barycentric_coordinates
        ),
    )


def _select(
    yaw_degrees: float,
) -> AtlasPortraitFlameDynamicLandmarkSelection:
    return AtlasPortraitFlameDynamicLandmarkSelector.select(
        _embedding(),
        yaw_degrees=yaw_degrees,
    )


def test_selector_returns_selection():
    assert isinstance(
        _select(
            0.0
        ),
        AtlasPortraitFlameDynamicLandmarkSelection,
    )


@pytest.mark.parametrize(
    (
        "yaw_degrees",
        "expected_bin",
        "expected_selected_yaw",
    ),
    [
        (0.0, 0, 0.0),
        (0.49, 0, 0.0),
        (0.50, 0, 0.0),
        (0.51, 1, 1.0),
        (1.0, 1, 1.0),
        (10.0, 10, 10.0),
        (38.6, 39, 39.0),
        (39.0, 39, 39.0),
        (50.0, 39, 39.0),
        (200.0, 39, 39.0),
        (-0.49, 0, 0.0),
        (-0.50, 0, 0.0),
        (-0.51, 40, -1.0),
        (-1.0, 40, -1.0),
        (-2.0, 41, -2.0),
        (-10.0, 49, -10.0),
        (-38.6, 78, -39.0),
        (-39.0, 78, -39.0),
        (-50.0, 78, -39.0),
        (-200.0, 78, -39.0),
    ],
)
def test_selector_uses_official_flame_dynamic_index_layout(
    yaw_degrees: float,
    expected_bin: int,
    expected_selected_yaw: float,
):
    result = _select(
        yaw_degrees
    )

    assert result.yaw_bin_index == expected_bin
    assert result.selected_yaw_degrees == pytest.approx(
        expected_selected_yaw
    )


def test_zero_yaw_selects_first_embedding_row():
    result = _select(
        0.0
    )

    np.testing.assert_array_equal(
        result.landmark_face_indices,
        np.array(
            [
                0,
                1,
            ],
            dtype=np.int64,
        ),
    )


def test_positive_one_degree_selects_row_one():
    result = _select(
        1.0
    )

    np.testing.assert_array_equal(
        result.landmark_face_indices,
        np.array(
            [
                2,
                3,
            ],
            dtype=np.int64,
        ),
    )


def test_negative_one_degree_selects_row_forty():
    result = _select(
        -1.0
    )

    np.testing.assert_array_equal(
        result.landmark_face_indices,
        np.array(
            [
                80,
                81,
            ],
            dtype=np.int64,
        ),
    )


def test_negative_thirty_nine_degrees_selects_last_row():
    result = _select(
        -39.0
    )

    np.testing.assert_array_equal(
        result.landmark_face_indices,
        np.array(
            [
                156,
                157,
            ],
            dtype=np.int64,
        ),
    )


def test_selector_preserves_requested_yaw():
    result = _select(
        52.25
    )

    assert result.requested_yaw_degrees == pytest.approx(
        52.25
    )


def test_selection_reports_landmark_count():
    assert _select(
        0.0
    ).landmark_count == 2


def test_selection_arrays_are_read_only():
    result = _select(
        0.0
    )

    assert (
        result.landmark_face_indices.flags.writeable
        is False
    )
    assert (
        result
        .landmark_barycentric_coordinates
        .flags
        .writeable
        is False
    )


def test_selection_is_frozen():
    result = _select(
        0.0
    )

    with pytest.raises(
        FrozenInstanceError,
    ):
        result.yaw_bin_index = 1


def test_selector_does_not_modify_embedding():
    embedding = _embedding()

    faces_before = (
        embedding.landmark_face_indices.copy()
    )
    barycentric_before = (
        embedding
        .landmark_barycentric_coordinates
        .copy()
    )

    AtlasPortraitFlameDynamicLandmarkSelector.select(
        embedding,
        yaw_degrees=-17.0,
    )

    np.testing.assert_array_equal(
        embedding.landmark_face_indices,
        faces_before,
    )
    np.testing.assert_array_equal(
        embedding.landmark_barycentric_coordinates,
        barycentric_before,
    )


def test_selection_serialization_is_deterministic():
    first = _select(
        -17.0
    )
    second = _select(
        -17.0
    )

    assert first.to_dict() == second.to_dict()


@pytest.mark.parametrize(
    "yaw_degrees",
    [
        np.nan,
        np.inf,
        -np.inf,
        "invalid",
        None,
        True,
    ],
)
def test_selector_rejects_invalid_yaw(
    yaw_degrees,
):
    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
        match="yaw_degrees",
    ):
        AtlasPortraitFlameDynamicLandmarkSelector.select(
            _embedding(),
            yaw_degrees=yaw_degrees,
        )


def test_selector_rejects_invalid_embedding_type():
    with pytest.raises(
        TypeError,
        match="embedding",
    ):
        AtlasPortraitFlameDynamicLandmarkSelector.select(
            object(),
            yaw_degrees=0.0,
        )


@pytest.mark.parametrize(
    "yaw_bin_count",
    [
        1,
        5,
        78,
        81,
    ],
)
def test_selector_requires_official_79_bin_layout(
    yaw_bin_count: int,
):
    with pytest.raises(
        ValueError,
        match="79",
    ):
        AtlasPortraitFlameDynamicLandmarkSelector.select(
            _embedding(
                yaw_bin_count
            ),
            yaw_degrees=0.0,
        )
