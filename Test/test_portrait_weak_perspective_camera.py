from __future__ import annotations

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from CORE.atlas_portrait_weak_perspective_camera import (
    AtlasPortraitWeakPerspectiveCamera,
)


def _projected_points() -> np.ndarray:
    return np.array(
        [
            [0.30, 0.25],
            [0.40, 0.35],
            [0.50, 0.45],
            [0.60, 0.55],
        ],
        dtype=np.float64,
    )


def _camera(
    **overrides,
) -> AtlasPortraitWeakPerspectiveCamera:
    values = {
        "scale": 4.25,
        "translation_x": 0.51,
        "translation_y": 0.42,
        "projected_points_2d": _projected_points(),
        "weighted_root_mean_square_error": 0.0125,
        "metadata": {
            "camera_model": "weak_perspective",
            "initialization_method": (
                "weighted_similarity_no_rotation"
            ),
            "landmark_count": 4,
        },
    }

    values.update(
        overrides,
    )

    return AtlasPortraitWeakPerspectiveCamera(
        **values,
    )


def test_camera_preserves_scale():
    camera = _camera()

    assert camera.scale == pytest.approx(
        4.25,
    )


def test_camera_preserves_translation():
    camera = _camera()

    assert camera.translation_x == pytest.approx(
        0.51,
    )

    assert camera.translation_y == pytest.approx(
        0.42,
    )


def test_camera_preserves_projected_points():
    camera = _camera()

    assert camera.projected_points_2d.shape == (
        4,
        2,
    )

    assert camera.projected_points_2d.dtype == (
        np.float64
    )

    assert np.array_equal(
        camera.projected_points_2d,
        _projected_points(),
    )


def test_camera_reports_projected_point_count():
    camera = _camera()

    assert camera.projected_point_count == 4


def test_camera_preserves_weighted_error():
    camera = _camera()

    assert (
        camera.weighted_root_mean_square_error
        == pytest.approx(
            0.0125,
        )
    )


def test_camera_is_frozen():
    camera = _camera()

    with pytest.raises(
        FrozenInstanceError,
    ):
        camera.scale = 5.0


def test_camera_projected_points_are_read_only():
    camera = _camera()

    assert (
        camera.projected_points_2d.flags.writeable
        is False
    )

    with pytest.raises(
        ValueError,
    ):
        camera.projected_points_2d[
            0,
            0,
        ] = 99.0


def test_camera_copies_projected_points():
    projected_points = _projected_points()

    camera = _camera(
        projected_points_2d=projected_points,
    )

    projected_points[
        0,
        0,
    ] = 99.0

    assert camera.projected_points_2d[
        0,
        0,
    ] != 99.0


def test_camera_metadata_is_deterministic():
    camera = _camera()

    assert tuple(
        camera.metadata,
    ) == tuple(
        sorted(
            camera.metadata,
        )
    )

    assert camera.metadata == {
        "camera_model": "weak_perspective",
        "initialization_method": (
            "weighted_similarity_no_rotation"
        ),
        "landmark_count": 4,
    }


def test_camera_serialization_is_deterministic():
    first = _camera()
    second = _camera()

    assert first.to_dict() == second.to_dict()


def test_camera_to_dict_contains_plain_values():
    camera = _camera()

    assert camera.to_dict() == {
        "scale": 4.25,
        "translation_x": 0.51,
        "translation_y": 0.42,
        "projected_point_count": 4,
        "projected_points_2d": (
            _projected_points().tolist()
        ),
        "weighted_root_mean_square_error": (
            0.0125
        ),
        "metadata": {
            "camera_model": "weak_perspective",
            "initialization_method": (
                "weighted_similarity_no_rotation"
            ),
            "landmark_count": 4,
        },
    }


@pytest.mark.parametrize(
    "scale",
    [
        0.0,
        -1.0,
        np.nan,
        np.inf,
        None,
        "invalid",
    ],
)
def test_camera_rejects_invalid_scale(
    scale,
):
    with pytest.raises(
        ValueError,
        match="scale",
    ):
        _camera(
            scale=scale,
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "value",
    ),
    [
        (
            "translation_x",
            np.nan,
        ),
        (
            "translation_x",
            np.inf,
        ),
        (
            "translation_x",
            None,
        ),
        (
            "translation_y",
            np.nan,
        ),
        (
            "translation_y",
            -np.inf,
        ),
        (
            "translation_y",
            "invalid",
        ),
    ],
)
def test_camera_rejects_invalid_translation(
    field_name,
    value,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _camera(
            **{
                field_name: value,
            }
        )


@pytest.mark.parametrize(
    "projected_points",
    [
        np.zeros(
            (
                4,
                3,
            ),
            dtype=np.float64,
        ),
        np.zeros(
            (
                0,
                2,
            ),
            dtype=np.float64,
        ),
        np.full(
            (
                4,
                2,
            ),
            np.nan,
            dtype=np.float64,
        ),
    ],
)
def test_camera_rejects_invalid_projected_points(
    projected_points,
):
    with pytest.raises(
        ValueError,
        match="projected_points_2d",
    ):
        _camera(
            projected_points_2d=projected_points,
        )


@pytest.mark.parametrize(
    "error",
    [
        -0.001,
        np.nan,
        np.inf,
        None,
        "invalid",
    ],
)
def test_camera_rejects_invalid_weighted_error(
    error,
):
    with pytest.raises(
        ValueError,
        match=(
            "weighted_root_mean_square_error"
        ),
    ):
        _camera(
            weighted_root_mean_square_error=error,
        )


def test_camera_rejects_non_mapping_metadata():
    with pytest.raises(
        TypeError,
        match="metadata",
    ):
        _camera(
            metadata=[
                "invalid",
            ],
        )
