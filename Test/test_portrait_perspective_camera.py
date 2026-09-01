import numpy as np
import pytest

from CORE.atlas_portrait_perspective_camera import (
    AtlasPortraitPerspectiveCamera,
)


def test_projection_matches_pinhole_equation():
    camera = AtlasPortraitPerspectiveCamera(
        fx=1000.0,
        fy=800.0,
        cx=640.0,
        cy=480.0,
    )

    points = np.array(
        [
            [1.0, 2.0, 10.0],
            [-2.0, -1.0, 20.0],
        ],
        dtype=np.float64,
    )

    projected = camera.project(points)

    np.testing.assert_allclose(
        projected,
        np.array(
            [
                [740.0, 640.0],
                [540.0, 440.0],
            ]
        ),
    )


def test_depth_changes_apparent_scale():
    camera = AtlasPortraitPerspectiveCamera(
        fx=1000.0,
        fy=1000.0,
        cx=0.0,
        cy=0.0,
    )

    projected = camera.project(
        np.array(
            [
                [1.0, 0.0, 5.0],
                [1.0, 0.0, 10.0],
            ]
        )
    )

    assert projected[0, 0] == pytest.approx(200.0)
    assert projected[1, 0] == pytest.approx(100.0)


def test_optical_axis_projects_to_principal_point():
    camera = AtlasPortraitPerspectiveCamera(
        fx=900.0,
        fy=900.0,
        cx=512.0,
        cy=384.0,
    )

    projected = camera.project(
        np.array(
            [
                [0.0, 0.0, 1.0],
                [0.0, 0.0, 100.0],
            ]
        )
    )

    np.testing.assert_array_equal(
        projected,
        np.array(
            [
                [512.0, 384.0],
                [512.0, 384.0],
            ]
        ),
    )


def test_normalized_coordinates_are_inverse_intrinsic_transform():
    camera = AtlasPortraitPerspectiveCamera(
        fx=1000.0,
        fy=500.0,
        cx=600.0,
        cy=400.0,
    )

    normalized = camera.normalized_image_coordinates(
        np.array(
            [
                [700.0, 450.0],
                [400.0, 300.0],
            ]
        )
    )

    np.testing.assert_allclose(
        normalized,
        np.array(
            [
                [0.1, 0.1],
                [-0.2, -0.2],
            ]
        ),
    )


def test_intrinsic_matrix_is_correct_and_read_only():
    camera = AtlasPortraitPerspectiveCamera(
        fx=1000.0,
        fy=900.0,
        cx=640.0,
        cy=480.0,
    )

    np.testing.assert_array_equal(
        camera.intrinsic_matrix,
        np.array(
            [
                [1000.0, 0.0, 640.0],
                [0.0, 900.0, 480.0],
                [0.0, 0.0, 1.0],
            ]
        ),
    )

    assert camera.intrinsic_matrix.flags.writeable is False


@pytest.mark.parametrize(
    "kwargs",
    [
        {"fx": 0.0},
        {"fx": -1.0},
        {"fy": 0.0},
        {"fy": -1.0},
        {"near_z": 0.0},
        {"near_z": -1.0},
        {"fx": np.nan},
        {"cy": np.inf},
    ],
)
def test_invalid_camera_parameters_are_rejected(kwargs):
    values = dict(
        fx=1000.0,
        fy=1000.0,
        cx=640.0,
        cy=480.0,
    )
    values.update(kwargs)

    with pytest.raises(ValueError):
        AtlasPortraitPerspectiveCamera(**values)


@pytest.mark.parametrize(
    "points",
    [
        np.array([]),
        np.zeros((2, 2)),
        np.array([[0.0, 0.0, np.nan]]),
        np.array([[0.0, 0.0, 0.0]]),
        np.array([[0.0, 0.0, -1.0]]),
    ],
)
def test_invalid_projection_input_is_rejected(points):
    camera = AtlasPortraitPerspectiveCamera(
        fx=1000.0,
        fy=1000.0,
        cx=640.0,
        cy=480.0,
    )

    with pytest.raises(ValueError):
        camera.project(points)


def test_projection_result_is_read_only():
    camera = AtlasPortraitPerspectiveCamera(
        fx=1000.0,
        fy=1000.0,
        cx=640.0,
        cy=480.0,
    )

    projected = camera.project(
        np.array([[0.0, 0.0, 10.0]])
    )

    assert projected.flags.writeable is False
