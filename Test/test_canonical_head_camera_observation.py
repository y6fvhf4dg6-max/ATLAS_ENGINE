from dataclasses import FrozenInstanceError

import math
import pytest

from CORE.atlas_canonical_head_camera_observation import (
    AtlasCanonicalHeadCameraObservation,
)


def test_preserves_perspective_camera_observation():
    camera = AtlasCanonicalHeadCameraObservation(
        camera_id="  Fixture Camera A  ",
        projection_mode="perspective",
        image_width=1024,
        image_height=768,
        focal_length_px=900.0,
        principal_point_x_px=511.5,
        principal_point_y_px=383.5,
    )

    assert camera.camera_id == "fixture_camera_a"
    assert camera.projection_mode == "perspective"
    assert camera.image_width == 1024
    assert camera.image_height == 768
    assert camera.focal_length_px == pytest.approx(900.0)
    assert camera.principal_point_x_px == pytest.approx(511.5)
    assert camera.principal_point_y_px == pytest.approx(383.5)


def test_exposes_normalized_principal_point():
    camera = AtlasCanonicalHeadCameraObservation(
        camera_id="fixture",
        projection_mode="perspective",
        image_width=1001,
        image_height=801,
        focal_length_px=800.0,
        principal_point_x_px=500.0,
        principal_point_y_px=400.0,
    )

    assert camera.principal_point_normalized == pytest.approx(
        (0.5, 0.5)
    )


def test_camera_is_immutable():
    camera = AtlasCanonicalHeadCameraObservation(
        camera_id="fixture",
        projection_mode="perspective",
        image_width=640,
        image_height=480,
        focal_length_px=600.0,
        principal_point_x_px=319.5,
        principal_point_y_px=239.5,
    )

    with pytest.raises(FrozenInstanceError):
        camera.focal_length_px = 700.0


@pytest.mark.parametrize(
    "projection_mode",
    (
        "",
        "unsupported",
    ),
)
def test_rejects_invalid_projection_mode(
    projection_mode,
):
    with pytest.raises(
        ValueError,
        match="projection_mode",
    ):
        AtlasCanonicalHeadCameraObservation(
            camera_id="fixture",
            projection_mode=projection_mode,
            image_width=640,
            image_height=480,
            focal_length_px=600.0,
            principal_point_x_px=319.5,
            principal_point_y_px=239.5,
        )


@pytest.mark.parametrize(
    "field_name,value",
    (
        ("image_width", 0),
        ("image_height", -1),
        ("image_width", True),
        ("focal_length_px", 0.0),
        ("focal_length_px", math.nan),
        ("principal_point_x_px", math.inf),
        ("principal_point_y_px", math.nan),
    ),
)
def test_rejects_invalid_camera_values(
    field_name,
    value,
):
    arguments = {
        "camera_id": "fixture",
        "projection_mode": "perspective",
        "image_width": 640,
        "image_height": 480,
        "focal_length_px": 600.0,
        "principal_point_x_px": 319.5,
        "principal_point_y_px": 239.5,
    }
    arguments[field_name] = value

    with pytest.raises(
        (TypeError, ValueError),
        match=field_name,
    ):
        AtlasCanonicalHeadCameraObservation(
            **arguments
        )


def test_rejects_principal_point_outside_image_bounds():
    with pytest.raises(
        ValueError,
        match="principal_point",
    ):
        AtlasCanonicalHeadCameraObservation(
            camera_id="fixture",
            projection_mode="perspective",
            image_width=640,
            image_height=480,
            focal_length_px=600.0,
            principal_point_x_px=640.0,
            principal_point_y_px=239.5,
        )


def test_contract_does_not_claim_pose_identity_expression_or_provider():
    camera = AtlasCanonicalHeadCameraObservation(
        camera_id="fixture",
        projection_mode="perspective",
        image_width=640,
        image_height=480,
        focal_length_px=600.0,
        principal_point_x_px=319.5,
        principal_point_y_px=239.5,
    )

    assert not hasattr(camera, "yaw_deg")
    assert not hasattr(camera, "pitch_deg")
    assert not hasattr(camera, "roll_deg")
    assert not hasattr(camera, "identity_shape")
    assert not hasattr(camera, "expression")
    assert not hasattr(camera, "provider_id")
    assert not hasattr(camera, "confidence")
