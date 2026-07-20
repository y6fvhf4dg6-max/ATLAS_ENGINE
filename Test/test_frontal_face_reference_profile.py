from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_frontal_face_reference_profile import (
    AtlasFrontalFaceReferenceProfile,
)


def _profile(
    **overrides,
) -> AtlasFrontalFaceReferenceProfile:
    values = {
        "name": "synthetic-neutral",
        "face_width_ratio": 0.7500,
        "eye_spacing_ratio": 0.3250,
        "nose_width_ratio": 0.1250,
        "nose_length_ratio": 0.1875,
        "mouth_width_ratio": 0.2250,
        "jaw_width_ratio": 0.5500,
        "forehead_height_ratio": 0.3750,
    }

    values.update(
        overrides,
    )

    return AtlasFrontalFaceReferenceProfile(
        **values,
    )


def test_profile_preserves_values():
    profile = _profile()

    assert profile.name == "synthetic-neutral"
    assert profile.face_width_ratio == pytest.approx(
        0.7500,
    )
    assert profile.eye_spacing_ratio == pytest.approx(
        0.3250,
    )
    assert profile.nose_width_ratio == pytest.approx(
        0.1250,
    )
    assert profile.nose_length_ratio == pytest.approx(
        0.1875,
    )
    assert profile.mouth_width_ratio == pytest.approx(
        0.2250,
    )
    assert profile.jaw_width_ratio == pytest.approx(
        0.5500,
    )
    assert profile.forehead_height_ratio == pytest.approx(
        0.3750,
    )


def test_profile_normalizes_numeric_values():
    profile = _profile(
        face_width_ratio="0.75",
        eye_spacing_ratio=1,
    )

    assert profile.face_width_ratio == 0.75
    assert isinstance(
        profile.face_width_ratio,
        float,
    )
    assert profile.eye_spacing_ratio == 1.0
    assert isinstance(
        profile.eye_spacing_ratio,
        float,
    )


def test_profile_strips_name():
    profile = _profile(
        name="  synthetic-neutral  ",
    )

    assert profile.name == "synthetic-neutral"


@pytest.mark.parametrize(
    "name",
    [
        "",
        "   ",
    ],
)
def test_profile_rejects_blank_name(
    name,
):
    with pytest.raises(
        ValueError,
        match="name must not be blank",
    ):
        _profile(
            name=name,
        )


def test_profile_rejects_non_string_name():
    with pytest.raises(
        ValueError,
        match="name must be a string",
    ):
        _profile(
            name=123,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "face_width_ratio",
        "eye_spacing_ratio",
        "nose_width_ratio",
        "nose_length_ratio",
        "mouth_width_ratio",
        "jaw_width_ratio",
        "forehead_height_ratio",
    ],
)
@pytest.mark.parametrize(
    "invalid_value",
    [
        0.0,
        -0.01,
    ],
)
def test_profile_rejects_non_positive_ratios(
    field_name,
    invalid_value,
):
    with pytest.raises(
        ValueError,
        match=(f"{field_name} must be greater than zero"),
    ):
        _profile(
            **{
                field_name: invalid_value,
            },
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "face_width_ratio",
        "eye_spacing_ratio",
        "nose_width_ratio",
        "nose_length_ratio",
        "mouth_width_ratio",
        "jaw_width_ratio",
        "forehead_height_ratio",
    ],
)
@pytest.mark.parametrize(
    "invalid_value",
    [
        float("inf"),
        float("-inf"),
        float("nan"),
    ],
)
def test_profile_rejects_non_finite_ratios(
    field_name,
    invalid_value,
):
    with pytest.raises(
        ValueError,
        match=(f"{field_name} must be finite"),
    ):
        _profile(
            **{
                field_name: invalid_value,
            },
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "face_width_ratio",
        "eye_spacing_ratio",
        "nose_width_ratio",
        "nose_length_ratio",
        "mouth_width_ratio",
        "jaw_width_ratio",
        "forehead_height_ratio",
    ],
)
def test_profile_rejects_non_numeric_ratios(
    field_name,
):
    with pytest.raises(
        ValueError,
        match=(f"{field_name} must be numeric"),
    ):
        _profile(
            **{
                field_name: object(),
            },
        )


def test_profile_is_immutable():
    profile = _profile()

    with pytest.raises(
        FrozenInstanceError,
    ):
        profile.name = "changed"


def test_profile_equality_is_value_based():
    assert _profile() == _profile()


def test_profile_instances_are_distinct():
    first = _profile()
    second = _profile()

    assert first is not second
