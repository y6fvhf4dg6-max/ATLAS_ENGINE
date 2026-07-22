from __future__ import annotations

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from CORE.atlas_portrait_flame_jaw_contour_correspondence import (
    AtlasPortraitFlameJawContourCorrespondence,
)


def _target_points() -> np.ndarray:
    return np.array(
        [
            [220.0, 480.0],
            [260.0, 610.0],
            [420.0, 720.0],
            [580.0, 610.0],
            [620.0, 480.0],
        ],
        dtype=np.float64,
    )


def _matched_points() -> np.ndarray:
    return np.array(
        [
            [226.0, 482.0],
            [267.0, 605.0],
            [418.0, 714.0],
            [573.0, 606.0],
            [614.0, 483.0],
        ],
        dtype=np.float64,
    )


def _edge_vertex_indices() -> np.ndarray:
    return np.array(
        [
            [100, 101],
            [120, 121],
            [150, 151],
            [180, 181],
            [200, 201],
        ],
        dtype=np.int64,
    )


def _visible_mask() -> np.ndarray:
    return np.array(
        [
            True,
            True,
            True,
            True,
            True,
        ],
        dtype=np.bool_,
    )


def _correspondence(
    **overrides,
) -> AtlasPortraitFlameJawContourCorrespondence:
    target_points = _target_points()
    matched_points = _matched_points()

    values = {
        "landmark_ids": (
            234,
            132,
            152,
            361,
            454,
        ),
        "target_points_2d": target_points,
        "matched_points_2d": matched_points,
        "matched_edge_vertex_indices": (
            _edge_vertex_indices()
        ),
        "visible_landmark_mask": _visible_mask(),
        "residuals": np.linalg.norm(
            matched_points - target_points,
            axis=1,
        ),
        "metadata": {
            "coordinate_space": "pixel",
            "correspondence_type": (
                "dynamic_jaw_contour"
            ),
            "model_family": "flame",
            "synthetic": True,
        },
    }

    values.update(
        overrides
    )

    return AtlasPortraitFlameJawContourCorrespondence(
        **values
    )


def test_correspondence_preserves_landmark_ids():
    result = _correspondence()

    assert result.landmark_ids == (
        234,
        132,
        152,
        361,
        454,
    )


def test_correspondence_preserves_target_points():
    result = _correspondence()

    np.testing.assert_allclose(
        result.target_points_2d,
        _target_points(),
    )


def test_correspondence_preserves_matched_points():
    result = _correspondence()

    np.testing.assert_allclose(
        result.matched_points_2d,
        _matched_points(),
    )


def test_correspondence_preserves_edge_vertex_indices():
    result = _correspondence()

    np.testing.assert_array_equal(
        result.matched_edge_vertex_indices,
        _edge_vertex_indices(),
    )


def test_correspondence_preserves_visibility():
    result = _correspondence()

    np.testing.assert_array_equal(
        result.visible_landmark_mask,
        _visible_mask(),
    )


def test_correspondence_preserves_residuals():
    result = _correspondence()

    expected = np.linalg.norm(
        _matched_points() - _target_points(),
        axis=1,
    )

    np.testing.assert_allclose(
        result.residuals,
        expected,
    )


def test_correspondence_reports_counts():
    result = _correspondence()

    assert result.landmark_count == 5
    assert result.visible_landmark_count == 5


def test_correspondence_reports_residual_statistics():
    result = _correspondence()

    assert result.mean_residual == pytest.approx(
        float(
            np.mean(
                result.residuals
            )
        )
    )
    assert result.median_residual == pytest.approx(
        float(
            np.median(
                result.residuals
            )
        )
    )
    assert result.maximum_residual == pytest.approx(
        float(
            np.max(
                result.residuals
            )
        )
    )


def test_correspondence_arrays_are_read_only():
    result = _correspondence()

    arrays = (
        result.target_points_2d,
        result.matched_points_2d,
        result.matched_edge_vertex_indices,
        result.visible_landmark_mask,
        result.residuals,
    )

    assert all(
        array.flags.writeable is False
        for array in arrays
    )


def test_correspondence_copies_input_arrays():
    target_points = _target_points()
    matched_points = _matched_points()
    edge_indices = _edge_vertex_indices()
    visible_mask = _visible_mask()
    residuals = np.linalg.norm(
        matched_points - target_points,
        axis=1,
    )

    result = _correspondence(
        target_points_2d=target_points,
        matched_points_2d=matched_points,
        matched_edge_vertex_indices=edge_indices,
        visible_landmark_mask=visible_mask,
        residuals=residuals,
    )

    target_points[
        0,
        0,
    ] = 999.0
    matched_points[
        0,
        0,
    ] = 999.0
    edge_indices[
        0,
        0,
    ] = 999
    visible_mask[
        0
    ] = False
    residuals[
        0
    ] = 999.0

    assert result.target_points_2d[
        0,
        0,
    ] != 999.0
    assert result.matched_points_2d[
        0,
        0,
    ] != 999.0
    assert result.matched_edge_vertex_indices[
        0,
        0,
    ] != 999
    assert bool(
        result.visible_landmark_mask[
            0
        ]
    )
    assert result.residuals[
        0
    ] != 999.0


def test_correspondence_is_frozen():
    result = _correspondence()

    with pytest.raises(
        FrozenInstanceError,
    ):
        result.landmark_ids = (
            1,
            2,
            3,
        )


def test_correspondence_metadata_is_deterministic():
    result = _correspondence()

    assert tuple(
        result.metadata
    ) == tuple(
        sorted(
            result.metadata
        )
    )

    assert result.metadata == {
        "coordinate_space": "pixel",
        "correspondence_type": (
            "dynamic_jaw_contour"
        ),
        "model_family": "flame",
        "synthetic": True,
    }


def test_correspondence_serialization_is_deterministic():
    first = _correspondence()
    second = _correspondence()

    assert first.to_dict() == second.to_dict()


@pytest.mark.parametrize(
    "landmark_ids",
    [
        (),
        (
            234,
            132,
            132,
        ),
        (
            234,
            -1,
            454,
        ),
        (
            234,
            152.5,
            454,
        ),
    ],
)
def test_correspondence_rejects_invalid_landmark_ids(
    landmark_ids,
):
    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
        match="landmark_ids",
    ):
        _correspondence(
            landmark_ids=landmark_ids,
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "value",
    ),
    [
        (
            "target_points_2d",
            np.zeros(
                (
                    5,
                    3,
                ),
                dtype=np.float64,
            ),
        ),
        (
            "matched_points_2d",
            np.zeros(
                (
                    4,
                    2,
                ),
                dtype=np.float64,
            ),
        ),
        (
            "matched_edge_vertex_indices",
            np.zeros(
                (
                    5,
                    3,
                ),
                dtype=np.int64,
            ),
        ),
        (
            "visible_landmark_mask",
            np.ones(
                4,
                dtype=np.bool_,
            ),
        ),
        (
            "residuals",
            np.ones(
                4,
                dtype=np.float64,
            ),
        ),
    ],
)
def test_correspondence_rejects_invalid_array_shapes(
    field_name,
    value,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _correspondence(
            **{
                field_name: value,
            }
        )


def test_correspondence_rejects_nonfinite_points():
    points = _target_points()
    points[
        0,
        0,
    ] = np.nan

    with pytest.raises(
        ValueError,
        match="target_points_2d",
    ):
        _correspondence(
            target_points_2d=points,
        )


def test_correspondence_rejects_negative_edge_indices():
    indices = _edge_vertex_indices()
    indices[
        0,
        0,
    ] = -1

    with pytest.raises(
        ValueError,
        match="matched_edge_vertex_indices",
    ):
        _correspondence(
            matched_edge_vertex_indices=indices,
        )


def test_correspondence_rejects_negative_residuals():
    residuals = np.ones(
        5,
        dtype=np.float64,
    )
    residuals[
        0
    ] = -0.1

    with pytest.raises(
        ValueError,
        match="residuals",
    ):
        _correspondence(
            residuals=residuals,
        )


def test_correspondence_rejects_non_mapping_metadata():
    with pytest.raises(
        TypeError,
        match="metadata",
    ):
        _correspondence(
            metadata=[
                "invalid",
            ],
        )
