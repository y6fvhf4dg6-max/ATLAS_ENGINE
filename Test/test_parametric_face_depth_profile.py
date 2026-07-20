from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_parametric_face_depth_profile import (
    AtlasParametricFaceDepthProfile,
)


def _profile(
    **overrides,
) -> AtlasParametricFaceDepthProfile:
    values = {
        "name": "neutral-anatomical",
        "brow_projection": 0.040,
        "eye_socket_depth": 0.055,
        "cheek_projection": 0.060,
        "nose_bridge_projection": 0.110,
        "nose_tip_projection": 0.160,
        "nose_wing_projection": 0.045,
        "upper_lip_projection": 0.035,
        "lower_lip_projection": 0.045,
        "philtrum_depth": 0.018,
        "labiomental_fold_depth": 0.022,
        "chin_projection": 0.070,
    }

    values.update(
        overrides,
    )

    return AtlasParametricFaceDepthProfile(
        **values,
    )


def test_profile_preserves_expected_values():
    profile = _profile()

    assert profile.name == "neutral-anatomical"
    assert profile.brow_projection == 0.040
    assert profile.eye_socket_depth == 0.055
    assert profile.cheek_projection == 0.060
    assert profile.nose_bridge_projection == 0.110
    assert profile.nose_tip_projection == 0.160
    assert profile.nose_wing_projection == 0.045
    assert profile.upper_lip_projection == 0.035
    assert profile.lower_lip_projection == 0.045
    assert profile.philtrum_depth == 0.018
    assert profile.labiomental_fold_depth == 0.022
    assert profile.chin_projection == 0.070


def test_profile_normalizes_name():
    profile = _profile(
        name="  neutral-anatomical  ",
    )

    assert profile.name == "neutral-anatomical"


def test_profile_converts_numeric_values_to_float():
    profile = _profile(
        brow_projection=1,
        eye_socket_depth="0.05",
    )

    assert profile.brow_projection == 1.0
    assert profile.eye_socket_depth == 0.05
    assert isinstance(
        profile.brow_projection,
        float,
    )
    assert isinstance(
        profile.eye_socket_depth,
        float,
    )


def test_profile_is_immutable():
    profile = _profile()

    with pytest.raises(
        FrozenInstanceError,
    ):
        profile.nose_tip_projection = 0.20


@pytest.mark.parametrize(
    "invalid_name",
    (
        "",
        "   ",
        None,
        123,
    ),
)
def test_profile_rejects_invalid_name(
    invalid_name,
):
    with pytest.raises(
        ValueError,
    ):
        _profile(
            name=invalid_name,
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "brow_projection",
        "eye_socket_depth",
        "cheek_projection",
        "nose_bridge_projection",
        "nose_tip_projection",
        "nose_wing_projection",
        "upper_lip_projection",
        "lower_lip_projection",
        "philtrum_depth",
        "labiomental_fold_depth",
        "chin_projection",
    ),
)
def test_profile_accepts_zero_depth(
    field_name,
):
    profile = _profile(
        **{
            field_name: 0.0,
        },
    )

    assert getattr(
        profile,
        field_name,
    ) == 0.0


@pytest.mark.parametrize(
    "field_name",
    (
        "brow_projection",
        "eye_socket_depth",
        "cheek_projection",
        "nose_bridge_projection",
        "nose_tip_projection",
        "nose_wing_projection",
        "upper_lip_projection",
        "lower_lip_projection",
        "philtrum_depth",
        "labiomental_fold_depth",
        "chin_projection",
    ),
)
def test_profile_rejects_negative_depth(
    field_name,
):
    with pytest.raises(
        ValueError,
        match=f"{field_name} must be nonnegative",
    ):
        _profile(
            **{
                field_name: -0.01,
            },
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "brow_projection",
        "eye_socket_depth",
        "cheek_projection",
        "nose_bridge_projection",
        "nose_tip_projection",
        "nose_wing_projection",
        "upper_lip_projection",
        "lower_lip_projection",
        "philtrum_depth",
        "labiomental_fold_depth",
        "chin_projection",
    ),
)
@pytest.mark.parametrize(
    "invalid_value",
    (
        float("nan"),
        float("inf"),
        float("-inf"),
        "invalid",
        None,
    ),
)
def test_profile_rejects_invalid_depth(
    field_name,
    invalid_value,
):
    with pytest.raises(
        ValueError,
    ):
        _profile(
            **{
                field_name: invalid_value,
            },
        )


def test_profile_has_deterministic_field_order():
    profile = _profile()

    assert tuple(
        profile.__dataclass_fields__,
    ) == (
        "name",
        "brow_projection",
        "eye_socket_depth",
        "cheek_projection",
        "nose_bridge_projection",
        "nose_tip_projection",
        "nose_wing_projection",
        "upper_lip_projection",
        "lower_lip_projection",
        "philtrum_depth",
        "labiomental_fold_depth",
        "chin_projection",
    )
