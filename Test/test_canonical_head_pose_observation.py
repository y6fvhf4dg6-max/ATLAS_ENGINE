from dataclasses import FrozenInstanceError

import math
import pytest

from CORE.atlas_canonical_head_pose_observation import (
    AtlasCanonicalHeadPoseObservation,
)


def test_preserves_observed_head_pose_angles():
    pose = AtlasCanonicalHeadPoseObservation(
        pose_id="  Fixture Pose A  ",
        yaw_deg=18.0,
        pitch_deg=-7.5,
        roll_deg=3.0,
    )

    assert pose.pose_id == "fixture_pose_a"
    assert pose.yaw_deg == pytest.approx(18.0)
    assert pose.pitch_deg == pytest.approx(-7.5)
    assert pose.roll_deg == pytest.approx(3.0)
    assert pose.is_canonical_neutral is False


def test_canonical_neutral_pose_is_zero_rotation():
    pose = AtlasCanonicalHeadPoseObservation(
        pose_id="neutral",
        yaw_deg=0.0,
        pitch_deg=0.0,
        roll_deg=0.0,
    )

    assert pose.is_canonical_neutral is True


def test_pose_is_immutable():
    pose = AtlasCanonicalHeadPoseObservation(
        pose_id="fixture",
        yaw_deg=1.0,
        pitch_deg=2.0,
        roll_deg=3.0,
    )

    with pytest.raises(FrozenInstanceError):
        pose.yaw_deg = 10.0


def test_rejects_blank_pose_id():
    with pytest.raises(
        ValueError,
        match="pose_id",
    ):
        AtlasCanonicalHeadPoseObservation(
            pose_id="   ",
            yaw_deg=0.0,
            pitch_deg=0.0,
            roll_deg=0.0,
        )


@pytest.mark.parametrize(
    "field_name,value",
    (
        ("yaw_deg", math.nan),
        ("yaw_deg", math.inf),
        ("pitch_deg", -math.inf),
        ("roll_deg", math.nan),
        ("yaw_deg", "invalid"),
    ),
)
def test_rejects_nonfinite_or_nonnumeric_angles(
    field_name,
    value,
):
    arguments = {
        "pose_id": "fixture",
        "yaw_deg": 0.0,
        "pitch_deg": 0.0,
        "roll_deg": 0.0,
    }
    arguments[field_name] = value

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        AtlasCanonicalHeadPoseObservation(
            **arguments
        )


def test_contract_does_not_claim_camera_identity_expression_or_provider():
    pose = AtlasCanonicalHeadPoseObservation(
        pose_id="fixture",
        yaw_deg=10.0,
        pitch_deg=5.0,
        roll_deg=-2.0,
    )

    assert not hasattr(pose, "camera")
    assert not hasattr(pose, "intrinsics")
    assert not hasattr(pose, "focal_length")
    assert not hasattr(pose, "identity_shape")
    assert not hasattr(pose, "expression")
    assert not hasattr(pose, "provider_id")
    assert not hasattr(pose, "confidence")
