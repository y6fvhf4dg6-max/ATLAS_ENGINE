from __future__ import annotations

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from CORE.atlas_portrait_weak_perspective_camera import (
    AtlasPortraitWeakPerspectiveCamera,
)
from CORE.providers.portrait.atlas_portrait_flame_dynamic_landmark_evaluator import (
    AtlasPortraitFlameDynamicLandmarkEvaluation,
)
from CORE.providers.portrait.atlas_portrait_flame_dynamic_landmark_pixel_projector import (
    AtlasPortraitFlameDynamicLandmarkPixelProjection,
    AtlasPortraitFlameDynamicLandmarkPixelProjector,
)


def _evaluation() -> (
    AtlasPortraitFlameDynamicLandmarkEvaluation
):
    return AtlasPortraitFlameDynamicLandmarkEvaluation(
        requested_yaw_degrees=-10.25,
        selected_yaw_degrees=-10.0,
        yaw_bin_index=49,
        landmark_points=np.array(
            [
                [1.0, 2.0, 3.0],
                [-1.0, 0.5, -4.0],
            ],
            dtype=np.float64,
        ),
    )


def _camera(
    *,
    coordinate_space: str = "pixel",
) -> AtlasPortraitWeakPerspectiveCamera:
    return AtlasPortraitWeakPerspectiveCamera(
        scale=10.0,
        translation_x=100.0,
        translation_y=200.0,
        projected_points_2d=np.array(
            [
                [100.0, 200.0],
            ],
            dtype=np.float64,
        ),
        weighted_root_mean_square_error=0.0,
        metadata={
            "coordinate_space": coordinate_space,
            "image_width": 1024,
            "image_height": 1024,
        },
    )


def _project(
    *,
    evaluation: object | None = None,
    camera: object | None = None,
) -> AtlasPortraitFlameDynamicLandmarkPixelProjection:
    return (
        AtlasPortraitFlameDynamicLandmarkPixelProjector.project(
            (
                _evaluation()
                if evaluation is None
                else evaluation
            ),
            camera=(
                _camera()
                if camera is None
                else camera
            ),
        )
    )


def test_projector_returns_projection():
    result = _project()

    assert isinstance(
        result,
        AtlasPortraitFlameDynamicLandmarkPixelProjection,
    )


def test_projector_applies_weak_perspective_camera():
    result = _project()

    np.testing.assert_allclose(
        result.projected_points_2d,
        np.array(
            [
                [110.0, 220.0],
                [90.0, 205.0],
            ],
            dtype=np.float64,
        ),
    )


def test_projector_ignores_landmark_depth():
    evaluation = (
        AtlasPortraitFlameDynamicLandmarkEvaluation(
            requested_yaw_degrees=0.0,
            selected_yaw_degrees=0.0,
            yaw_bin_index=0,
            landmark_points=np.array(
                [
                    [1.0, 2.0, -1000.0],
                    [1.0, 2.0, 1000.0],
                ],
                dtype=np.float64,
            ),
        )
    )

    result = _project(
        evaluation=evaluation,
    )

    np.testing.assert_allclose(
        result.projected_points_2d,
        np.array(
            [
                [110.0, 220.0],
                [110.0, 220.0],
            ],
            dtype=np.float64,
        ),
    )


def test_projection_preserves_evaluation_metadata():
    result = _project()

    assert result.requested_yaw_degrees == pytest.approx(
        -10.25
    )
    assert result.selected_yaw_degrees == pytest.approx(
        -10.0
    )
    assert result.yaw_bin_index == 49


def test_projection_preserves_camera_parameters():
    result = _project()

    assert result.scale == pytest.approx(
        10.0
    )
    assert result.translation_x == pytest.approx(
        100.0
    )
    assert result.translation_y == pytest.approx(
        200.0
    )


def test_projection_reports_landmark_count():
    result = _project()

    assert result.landmark_count == 2


def test_projection_points_are_read_only():
    result = _project()

    assert (
        result.projected_points_2d.flags.writeable
        is False
    )


def test_projection_is_frozen():
    result = _project()

    with pytest.raises(
        FrozenInstanceError,
    ):
        result.yaw_bin_index = 0


def test_projector_copies_output():
    evaluation = _evaluation()

    result = _project(
        evaluation=evaluation,
    )

    object.__setattr__(
        evaluation,
        "landmark_points",
        np.zeros(
            (
                2,
                3,
            ),
            dtype=np.float64,
        ),
    )

    np.testing.assert_allclose(
        result.projected_points_2d,
        np.array(
            [
                [110.0, 220.0],
                [90.0, 205.0],
            ],
            dtype=np.float64,
        ),
    )


def test_projector_does_not_modify_inputs():
    evaluation = _evaluation()
    camera = _camera()

    landmarks_before = (
        evaluation.landmark_points.copy()
    )
    camera_points_before = (
        camera.projected_points_2d.copy()
    )

    AtlasPortraitFlameDynamicLandmarkPixelProjector.project(
        evaluation,
        camera=camera,
    )

    np.testing.assert_array_equal(
        evaluation.landmark_points,
        landmarks_before,
    )
    np.testing.assert_array_equal(
        camera.projected_points_2d,
        camera_points_before,
    )


def test_projection_serialization_is_deterministic():
    first = _project()
    second = _project()

    assert first.to_dict() == second.to_dict()


def test_projector_rejects_invalid_evaluation_type():
    with pytest.raises(
        TypeError,
        match="evaluation",
    ):
        _project(
            evaluation=object(),
        )


def test_projector_rejects_invalid_camera_type():
    with pytest.raises(
        TypeError,
        match="camera",
    ):
        _project(
            camera=object(),
        )


def test_projector_requires_pixel_coordinate_camera():
    with pytest.raises(
        ValueError,
        match="coordinate_space",
    ):
        _project(
            camera=_camera(
                coordinate_space="normalized",
            ),
        )


def test_projector_accepts_additional_camera_metadata():
    camera = AtlasPortraitWeakPerspectiveCamera(
        scale=10.0,
        translation_x=100.0,
        translation_y=200.0,
        projected_points_2d=np.array(
            [
                [100.0, 200.0],
            ],
            dtype=np.float64,
        ),
        weighted_root_mean_square_error=0.0,
        metadata={
            "coordinate_space": "pixel",
            "image_width": 1024,
            "image_height": 1024,
            "source_coordinate_space": "normalized",
            "pixel_scale": 1023.0,
        },
    )

    result = _project(
        camera=camera,
    )

    assert result.landmark_count == 2


def test_projection_result_rejects_invalid_point_shape():
    with pytest.raises(
        ValueError,
        match="projected_points_2d",
    ):
        AtlasPortraitFlameDynamicLandmarkPixelProjection(
            requested_yaw_degrees=0.0,
            selected_yaw_degrees=0.0,
            yaw_bin_index=0,
            scale=1.0,
            translation_x=0.0,
            translation_y=0.0,
            projected_points_2d=np.zeros(
                (
                    2,
                    3,
                ),
                dtype=np.float64,
            ),
        )


def test_projection_result_rejects_nonfinite_points():
    with pytest.raises(
        ValueError,
        match="projected_points_2d",
    ):
        AtlasPortraitFlameDynamicLandmarkPixelProjection(
            requested_yaw_degrees=0.0,
            selected_yaw_degrees=0.0,
            yaw_bin_index=0,
            scale=1.0,
            translation_x=0.0,
            translation_y=0.0,
            projected_points_2d=np.array(
                [
                    [0.0, np.nan],
                ],
                dtype=np.float64,
            ),
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "field_value",
    ),
    [
        (
            "requested_yaw_degrees",
            np.nan,
        ),
        (
            "selected_yaw_degrees",
            np.inf,
        ),
        (
            "scale",
            0.0,
        ),
        (
            "scale",
            -1.0,
        ),
        (
            "translation_x",
            np.nan,
        ),
        (
            "translation_y",
            np.inf,
        ),
    ],
)
def test_projection_result_rejects_invalid_scalar(
    field_name: str,
    field_value: float,
):
    values = {
        "requested_yaw_degrees": 0.0,
        "selected_yaw_degrees": 0.0,
        "yaw_bin_index": 0,
        "scale": 1.0,
        "translation_x": 0.0,
        "translation_y": 0.0,
        "projected_points_2d": np.array(
            [
                [0.0, 0.0],
            ],
            dtype=np.float64,
        ),
    }
    values[
        field_name
    ] = field_value

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        AtlasPortraitFlameDynamicLandmarkPixelProjection(
            **values,
        )


@pytest.mark.parametrize(
    "yaw_bin_index",
    [
        -1,
        79,
    ],
)
def test_projection_result_rejects_invalid_yaw_bin(
    yaw_bin_index: int,
):
    with pytest.raises(
        ValueError,
        match="yaw_bin_index",
    ):
        AtlasPortraitFlameDynamicLandmarkPixelProjection(
            requested_yaw_degrees=0.0,
            selected_yaw_degrees=0.0,
            yaw_bin_index=yaw_bin_index,
            scale=1.0,
            translation_x=0.0,
            translation_y=0.0,
            projected_points_2d=np.array(
                [
                    [0.0, 0.0],
                ],
                dtype=np.float64,
            ),
        )
