from __future__ import annotations

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from CORE.providers.portrait.atlas_portrait_flame_dynamic_jaw_correspondence_builder import (
    AtlasPortraitFlameDynamicJawCorrespondence,
    AtlasPortraitFlameDynamicJawCorrespondenceBuilder,
)


def _flame_points() -> np.ndarray:
    return np.array(
        [
            [4.0, 0.0],
            [3.0, 1.0],
            [2.0, 1.5],
            [1.0, 1.0],
            [0.0, 0.0],
        ],
        dtype=np.float64,
    )


def _mediapipe_points() -> np.ndarray:
    # Opposite direction and non-uniform sampling.
    return np.array(
        [
            [0.0, 0.0],
            [0.4, 0.4],
            [1.0, 1.0],
            [1.5, 1.25],
            [2.0, 1.5],
            [3.0, 1.0],
            [3.7, 0.3],
            [4.0, 0.0],
        ],
        dtype=np.float64,
    )


def _build(
    *,
    flame_points: object | None = None,
    mediapipe_points: object | None = None,
) -> AtlasPortraitFlameDynamicJawCorrespondence:
    return (
        AtlasPortraitFlameDynamicJawCorrespondenceBuilder.build(
            flame_contour_points_2d=(
                _flame_points()
                if flame_points is None
                else flame_points
            ),
            mediapipe_jaw_points_2d=(
                _mediapipe_points()
                if mediapipe_points is None
                else mediapipe_points
            ),
        )
    )


def test_builder_returns_correspondence():
    result = _build()

    assert isinstance(
        result,
        AtlasPortraitFlameDynamicJawCorrespondence,
    )


def test_builder_preserves_flame_points():
    result = _build()

    np.testing.assert_allclose(
        result.flame_contour_points_2d,
        _flame_points(),
    )


def test_builder_resamples_target_to_flame_count():
    result = _build()

    assert result.landmark_count == 5
    assert result.target_jaw_points_2d.shape == (
        5,
        2,
    )


def test_builder_selects_reverse_orientation():
    result = _build()

    assert result.target_orientation == "reversed"


def test_resampled_target_endpoints_match_flame_orientation():
    result = _build()

    np.testing.assert_allclose(
        result.target_jaw_points_2d[
            0
        ],
        np.array(
            [
                4.0,
                0.0,
            ]
        ),
    )
    np.testing.assert_allclose(
        result.target_jaw_points_2d[
            -1
        ],
        np.array(
            [
                0.0,
                0.0,
            ]
        ),
    )


def test_builder_reports_residual_vectors():
    result = _build()

    np.testing.assert_allclose(
        result.residual_vectors_2d,
        (
            result.flame_contour_points_2d
            - result.target_jaw_points_2d
        ),
    )


def test_builder_reports_distances():
    result = _build()

    expected = np.linalg.norm(
        result.residual_vectors_2d,
        axis=1,
    )

    np.testing.assert_allclose(
        result.distances,
        expected,
    )


def test_builder_reports_error_statistics():
    result = _build()

    assert result.mean_distance == pytest.approx(
        float(
            np.mean(
                result.distances
            )
        )
    )
    assert result.maximum_distance == pytest.approx(
        float(
            np.max(
                result.distances
            )
        )
    )


def test_correspondence_arrays_are_read_only():
    result = _build()

    assert (
        result.flame_contour_points_2d.flags.writeable
        is False
    )
    assert (
        result.target_jaw_points_2d.flags.writeable
        is False
    )
    assert (
        result.residual_vectors_2d.flags.writeable
        is False
    )
    assert result.distances.flags.writeable is False


def test_correspondence_is_frozen():
    result = _build()

    with pytest.raises(
        FrozenInstanceError,
    ):
        result.target_orientation = "forward"


def test_builder_does_not_modify_inputs():
    flame = _flame_points()
    mediapipe = _mediapipe_points()

    flame_before = flame.copy()
    mediapipe_before = mediapipe.copy()

    AtlasPortraitFlameDynamicJawCorrespondenceBuilder.build(
        flame_contour_points_2d=flame,
        mediapipe_jaw_points_2d=mediapipe,
    )

    np.testing.assert_array_equal(
        flame,
        flame_before,
    )
    np.testing.assert_array_equal(
        mediapipe,
        mediapipe_before,
    )


def test_serialization_is_deterministic():
    first = _build()
    second = _build()

    assert first.to_dict() == second.to_dict()


def test_builder_accepts_equal_point_counts():
    result = _build(
        mediapipe_points=_flame_points()[
            ::-1
        ],
    )

    assert result.landmark_count == 5


@pytest.mark.parametrize(
    "points",
    [
        np.zeros(
            (
                5,
                3,
            ),
            dtype=np.float64,
        ),
        np.zeros(
            (
                1,
                2,
            ),
            dtype=np.float64,
        ),
        np.zeros(
            10,
            dtype=np.float64,
        ),
        np.zeros(
            (
                0,
                2,
            ),
            dtype=np.float64,
        ),
    ],
)
def test_builder_rejects_invalid_flame_shape(
    points: np.ndarray,
):
    with pytest.raises(
        ValueError,
        match="flame_contour_points_2d",
    ):
        _build(
            flame_points=points,
        )


@pytest.mark.parametrize(
    "points",
    [
        np.zeros(
            (
                5,
                3,
            ),
            dtype=np.float64,
        ),
        np.zeros(
            (
                1,
                2,
            ),
            dtype=np.float64,
        ),
        np.zeros(
            10,
            dtype=np.float64,
        ),
        np.zeros(
            (
                0,
                2,
            ),
            dtype=np.float64,
        ),
    ],
)
def test_builder_rejects_invalid_mediapipe_shape(
    points: np.ndarray,
):
    with pytest.raises(
        ValueError,
        match="mediapipe_jaw_points_2d",
    ):
        _build(
            mediapipe_points=points,
        )


def test_builder_rejects_nonfinite_flame_points():
    points = _flame_points()
    points[
        0,
        0,
    ] = np.nan

    with pytest.raises(
        ValueError,
        match="flame_contour_points_2d",
    ):
        _build(
            flame_points=points,
        )


def test_builder_rejects_nonfinite_mediapipe_points():
    points = _mediapipe_points()
    points[
        0,
        0,
    ] = np.inf

    with pytest.raises(
        ValueError,
        match="mediapipe_jaw_points_2d",
    ):
        _build(
            mediapipe_points=points,
        )


def test_builder_rejects_zero_length_mediapipe_polyline():
    points = np.repeat(
        np.array(
            [
                [
                    2.0,
                    3.0,
                ]
            ],
            dtype=np.float64,
        ),
        repeats=5,
        axis=0,
    )

    with pytest.raises(
        ValueError,
        match="length",
    ):
        _build(
            mediapipe_points=points,
        )


def test_builder_handles_duplicate_adjacent_target_points():
    points = np.array(
        [
            [0.0, 0.0],
            [1.0, 1.0],
            [1.0, 1.0],
            [2.0, 1.5],
            [4.0, 0.0],
        ],
        dtype=np.float64,
    )

    result = _build(
        mediapipe_points=points,
    )

    assert result.landmark_count == 5
    assert np.isfinite(
        result.target_jaw_points_2d
    ).all()
