from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_weak_perspective_camera import (
    AtlasPortraitWeakPerspectiveCamera,
)
from CORE.atlas_portrait_weak_perspective_camera_initializer import (
    AtlasPortraitWeakPerspectiveCameraInitializer,
)
from CORE.atlas_portrait_weak_perspective_fitting_input import (
    AtlasPortraitWeakPerspectiveFittingInput,
)


LANDMARK_NAMES = (
    "point_0",
    "point_1",
    "point_2",
    "point_3",
)


def _source_points() -> np.ndarray:
    return np.array(
        [
            [-1.0, -1.0, 0.20],
            [1.0, -1.0, 0.30],
            [1.0, 1.0, 0.40],
            [-1.0, 1.0, 0.50],
        ],
        dtype=np.float64,
    )


def _exact_target_points() -> np.ndarray:
    scale = 0.20
    translation = np.array(
        [
            0.50,
            0.40,
        ],
        dtype=np.float64,
    )

    return (
        scale * _source_points()[:, :2]
        + translation
    )


def _fitting_input(
    **overrides,
) -> AtlasPortraitWeakPerspectiveFittingInput:
    values = {
        "landmark_names": LANDMARK_NAMES,
        "source_points_3d": _source_points(),
        "target_points_2d": _exact_target_points(),
        "landmark_weights": np.array(
            [
                1.0,
                1.0,
                1.0,
                1.0,
            ],
            dtype=np.float64,
        ),
        "image_width": 1122,
        "image_height": 1402,
        "metadata": {
            "correspondence_version": (
                "synthetic-camera-initializer-v1"
            ),
            "input_view": "front",
            "landmark_provider_id": "synthetic",
            "model_family": "flame",
            "portrait_fixture": (
                "synthetic_camera_initializer"
            ),
            "source_image_sha256": "synthetic-sha256",
            "synthetic": True,
        },
    }

    values.update(
        overrides,
    )

    return AtlasPortraitWeakPerspectiveFittingInput(
        **values,
    )


def test_initializer_returns_camera():
    camera = (
        AtlasPortraitWeakPerspectiveCameraInitializer
        .initialize(
            _fitting_input(),
        )
    )

    assert isinstance(
        camera,
        AtlasPortraitWeakPerspectiveCamera,
    )


def test_initializer_recovers_exact_scale():
    camera = (
        AtlasPortraitWeakPerspectiveCameraInitializer
        .initialize(
            _fitting_input(),
        )
    )

    assert camera.scale == pytest.approx(
        0.20,
    )


def test_initializer_recovers_exact_translation():
    camera = (
        AtlasPortraitWeakPerspectiveCameraInitializer
        .initialize(
            _fitting_input(),
        )
    )

    assert camera.translation_x == pytest.approx(
        0.50,
    )
    assert camera.translation_y == pytest.approx(
        0.40,
    )


def test_initializer_projects_source_xy_coordinates():
    camera = (
        AtlasPortraitWeakPerspectiveCameraInitializer
        .initialize(
            _fitting_input(),
        )
    )

    assert np.allclose(
        camera.projected_points_2d,
        _exact_target_points(),
    )


def test_initializer_reports_zero_error_for_exact_fit():
    camera = (
        AtlasPortraitWeakPerspectiveCameraInitializer
        .initialize(
            _fitting_input(),
        )
    )

    assert (
        camera.weighted_root_mean_square_error
        == pytest.approx(
            0.0,
            abs=1.0e-15,
        )
    )


def test_initializer_uses_landmark_weights():
    target_points = _exact_target_points()

    target_points[
        3,
    ] += np.array(
        [
            0.20,
            -0.10,
        ],
        dtype=np.float64,
    )

    uniform = (
        AtlasPortraitWeakPerspectiveCameraInitializer
        .initialize(
            _fitting_input(
                target_points_2d=target_points,
            ),
        )
    )

    weighted = (
        AtlasPortraitWeakPerspectiveCameraInitializer
        .initialize(
            _fitting_input(
                target_points_2d=target_points,
                landmark_weights=np.array(
                    [
                        1.0,
                        1.0,
                        1.0,
                        0.01,
                    ],
                    dtype=np.float64,
                ),
            ),
        )
    )

    assert (
        weighted.weighted_root_mean_square_error
        < uniform.weighted_root_mean_square_error
    )

    assert abs(
        weighted.scale - 0.20,
    ) < abs(
        uniform.scale - 0.20,
    )


def test_initializer_metadata_is_deterministic():
    camera = (
        AtlasPortraitWeakPerspectiveCameraInitializer
        .initialize(
            _fitting_input(),
        )
    )

    assert camera.metadata == {
        "camera_model": "weak_perspective",
        "initialization_method": (
            "weighted_similarity_no_rotation"
        ),
        "input_view": "front",
        "landmark_count": 4,
        "model_family": "flame",
        "portrait_fixture": (
            "synthetic_camera_initializer"
        ),
        "synthetic": True,
    }


def test_initializer_is_deterministic():
    fitting_input = _fitting_input()

    first = (
        AtlasPortraitWeakPerspectiveCameraInitializer
        .initialize(
            fitting_input,
        )
    )

    second = (
        AtlasPortraitWeakPerspectiveCameraInitializer
        .initialize(
            fitting_input,
        )
    )

    assert first.to_dict() == second.to_dict()
    assert first is not second


def test_initializer_does_not_modify_fitting_input():
    fitting_input = _fitting_input()

    before = fitting_input.to_dict()

    AtlasPortraitWeakPerspectiveCameraInitializer.initialize(
        fitting_input,
    )

    assert fitting_input.to_dict() == before


def test_initializer_rejects_wrong_input_type():
    with pytest.raises(
        TypeError,
        match=(
            "AtlasPortraitWeakPerspectiveFittingInput"
        ),
    ):
        AtlasPortraitWeakPerspectiveCameraInitializer.initialize(
            object(),
        )


def test_initializer_rejects_degenerate_source_spread():
    source_points = np.array(
        [
            [0.25, 0.40, 0.10],
            [0.25, 0.40, 0.20],
            [0.25, 0.40, 0.30],
            [0.25, 0.40, 0.40],
        ],
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="source spread",
    ):
        AtlasPortraitWeakPerspectiveCameraInitializer.initialize(
            _fitting_input(
                source_points_3d=source_points,
            ),
        )


def test_initializer_rejects_non_positive_solution_scale():
    target_points = (
        -0.20 * _source_points()[:, :2]
        + np.array(
            [
                0.50,
                0.40,
            ],
            dtype=np.float64,
        )
    )

    with pytest.raises(
        ValueError,
        match="positive scale",
    ):
        AtlasPortraitWeakPerspectiveCameraInitializer.initialize(
            _fitting_input(
                target_points_2d=target_points,
            ),
        )
