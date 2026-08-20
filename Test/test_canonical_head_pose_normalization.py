from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_camera_observation import (
    AtlasCanonicalHeadCameraObservation,
)
from CORE.atlas_canonical_head_pose_normalization import (
    AtlasCanonicalHeadPoseNormalization,
)
from CORE.atlas_canonical_head_pose_observation import (
    AtlasCanonicalHeadPoseObservation,
)


def _pose():
    return AtlasCanonicalHeadPoseObservation(
        pose_id="fixture-pose",
        yaw_deg=18.0,
        pitch_deg=-7.5,
        roll_deg=3.0,
    )


def _camera():
    return AtlasCanonicalHeadCameraObservation(
        camera_id="fixture-camera",
        projection_mode="perspective",
        image_width=1024,
        image_height=768,
        focal_length_px=900.0,
        principal_point_x_px=511.5,
        principal_point_y_px=383.5,
    )


def test_builds_inverse_rotation_to_canonical_neutral_pose():
    normalization = AtlasCanonicalHeadPoseNormalization(
        normalization_id="  Fixture Normalize A  ",
        observed_pose=_pose(),
        camera_observation=_camera(),
    )

    assert normalization.normalization_id == "fixture_normalize_a"

    assert normalization.inverse_yaw_deg == pytest.approx(-18.0)
    assert normalization.inverse_pitch_deg == pytest.approx(7.5)
    assert normalization.inverse_roll_deg == pytest.approx(-3.0)

    assert normalization.target_yaw_deg == pytest.approx(0.0)
    assert normalization.target_pitch_deg == pytest.approx(0.0)
    assert normalization.target_roll_deg == pytest.approx(0.0)

    assert normalization.normalizes_to_canonical_neutral is True


def test_neutral_pose_requires_zero_inverse_rotation():
    pose = AtlasCanonicalHeadPoseObservation(
        pose_id="neutral",
        yaw_deg=0.0,
        pitch_deg=0.0,
        roll_deg=0.0,
    )

    normalization = AtlasCanonicalHeadPoseNormalization(
        normalization_id="neutral-normalization",
        observed_pose=pose,
        camera_observation=_camera(),
    )

    assert normalization.inverse_rotation_deg == pytest.approx(
        (0.0, 0.0, 0.0)
    )


def test_preserves_observation_contract_references():
    pose = _pose()
    camera = _camera()

    normalization = AtlasCanonicalHeadPoseNormalization(
        normalization_id="fixture",
        observed_pose=pose,
        camera_observation=camera,
    )

    assert normalization.observed_pose is pose
    assert normalization.camera_observation is camera


def test_normalization_is_immutable():
    normalization = AtlasCanonicalHeadPoseNormalization(
        normalization_id="fixture",
        observed_pose=_pose(),
        camera_observation=_camera(),
    )

    with pytest.raises(FrozenInstanceError):
        normalization.normalization_id = "changed"


def test_rejects_blank_normalization_id():
    with pytest.raises(
        ValueError,
        match="normalization_id",
    ):
        AtlasCanonicalHeadPoseNormalization(
            normalization_id="   ",
            observed_pose=_pose(),
            camera_observation=_camera(),
        )


def test_rejects_non_pose_observation():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadPoseObservation",
    ):
        AtlasCanonicalHeadPoseNormalization(
            normalization_id="fixture",
            observed_pose={},
            camera_observation=_camera(),
        )


def test_rejects_non_camera_observation():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadCameraObservation",
    ):
        AtlasCanonicalHeadPoseNormalization(
            normalization_id="fixture",
            observed_pose=_pose(),
            camera_observation={},
        )


def test_contract_does_not_modify_identity_expression_or_provider_state():
    normalization = AtlasCanonicalHeadPoseNormalization(
        normalization_id="fixture",
        observed_pose=_pose(),
        camera_observation=_camera(),
    )

    assert not hasattr(normalization, "identity_shape")
    assert not hasattr(normalization, "identity_displacement")
    assert not hasattr(normalization, "expression")
    assert not hasattr(normalization, "provider_id")
    assert not hasattr(normalization, "confidence")
    assert not hasattr(normalization, "likeness_score")
