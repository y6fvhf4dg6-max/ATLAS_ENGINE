from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_parametric_face_parameters import (
    AtlasParametricFaceParameters,
)


def _parameters(
    **overrides,
) -> AtlasParametricFaceParameters:
    values = {
        "scale": 1.0,
        "translation_x": 0.0,
        "translation_y": 0.0,
        "rotation_degrees": 0.0,
        "face_width": 1.0,
        "face_height": 1.0,
        "eye_spacing": 1.0,
        "eye_height": 1.0,
        "nose_width": 1.0,
        "nose_length": 1.0,
        "mouth_width": 1.0,
        "chin_width": 1.0,
        "chin_length": 1.0,
        "jaw_width": 1.0,
        "forehead_height": 1.0,
    }

    values.update(
        overrides,
    )

    return AtlasParametricFaceParameters(
        **values,
    )


def test_parameters_preserve_expected_values():
    parameters = _parameters(
        scale=1.25,
        translation_x=-0.10,
        translation_y=0.20,
        rotation_degrees=3.5,
        face_width=1.10,
        face_height=0.95,
        eye_spacing=1.05,
        eye_height=0.98,
        nose_width=0.90,
        nose_length=1.08,
        mouth_width=1.02,
        chin_width=0.94,
        chin_length=1.06,
        jaw_width=1.12,
        forehead_height=0.97,
    )

    assert parameters.scale == 1.25
    assert parameters.translation_x == -0.10
    assert parameters.translation_y == 0.20
    assert parameters.rotation_degrees == 3.5
    assert parameters.face_width == 1.10
    assert parameters.face_height == 0.95
    assert parameters.eye_spacing == 1.05
    assert parameters.eye_height == 0.98
    assert parameters.nose_width == 0.90
    assert parameters.nose_length == 1.08
    assert parameters.mouth_width == 1.02
    assert parameters.chin_width == 0.94
    assert parameters.chin_length == 1.06
    assert parameters.jaw_width == 1.12
    assert parameters.forehead_height == 0.97


def test_parameters_convert_numeric_values_to_float():
    parameters = _parameters(
        scale=2,
        translation_x="-0.1",
        translation_y="0.2",
        rotation_degrees="3",
        face_width="1.1",
    )

    assert parameters.scale == 2.0
    assert parameters.translation_x == -0.1
    assert parameters.translation_y == 0.2
    assert parameters.rotation_degrees == 3.0
    assert parameters.face_width == 1.1

    assert isinstance(
        parameters.scale,
        float,
    )
    assert isinstance(
        parameters.translation_x,
        float,
    )


def test_parameters_are_immutable():
    parameters = _parameters()

    with pytest.raises(
        FrozenInstanceError,
    ):
        parameters.face_width = 1.2


@pytest.mark.parametrize(
    "name",
    (
        "scale",
        "face_width",
        "face_height",
        "eye_spacing",
        "eye_height",
        "nose_width",
        "nose_length",
        "mouth_width",
        "chin_width",
        "chin_length",
        "jaw_width",
        "forehead_height",
    ),
)
def test_positive_parameters_reject_zero(
    name,
):
    with pytest.raises(
        ValueError,
        match=f"{name} must be greater than zero",
    ):
        _parameters(
            **{
                name: 0.0,
            },
        )


@pytest.mark.parametrize(
    "name",
    (
        "scale",
        "face_width",
        "face_height",
        "eye_spacing",
        "eye_height",
        "nose_width",
        "nose_length",
        "mouth_width",
        "chin_width",
        "chin_length",
        "jaw_width",
        "forehead_height",
    ),
)
def test_positive_parameters_reject_negative_values(
    name,
):
    with pytest.raises(
        ValueError,
        match=f"{name} must be greater than zero",
    ):
        _parameters(
            **{
                name: -0.1,
            },
        )


@pytest.mark.parametrize(
    "name",
    (
        "translation_x",
        "translation_y",
        "rotation_degrees",
    ),
)
def test_signed_parameters_accept_negative_values(
    name,
):
    parameters = _parameters(
        **{
            name: -2.5,
        },
    )

    assert (
        getattr(
            parameters,
            name,
        )
        == -2.5
    )


@pytest.mark.parametrize(
    "name",
    (
        "scale",
        "translation_x",
        "translation_y",
        "rotation_degrees",
        "face_width",
        "face_height",
        "eye_spacing",
        "eye_height",
        "nose_width",
        "nose_length",
        "mouth_width",
        "chin_width",
        "chin_length",
        "jaw_width",
        "forehead_height",
    ),
)
@pytest.mark.parametrize(
    "value",
    (
        float("nan"),
        float("inf"),
        float("-inf"),
    ),
)
def test_parameters_reject_non_finite_values(
    name,
    value,
):
    with pytest.raises(
        ValueError,
        match=f"{name} must be finite",
    ):
        _parameters(
            **{
                name: value,
            },
        )


@pytest.mark.parametrize(
    "name",
    (
        "scale",
        "translation_x",
        "translation_y",
        "rotation_degrees",
        "face_width",
        "face_height",
        "eye_spacing",
        "eye_height",
        "nose_width",
        "nose_length",
        "mouth_width",
        "chin_width",
        "chin_length",
        "jaw_width",
        "forehead_height",
    ),
)
def test_parameters_reject_non_numeric_values(
    name,
):
    with pytest.raises(
        ValueError,
        match=f"{name} must be numeric",
    ):
        _parameters(
            **{
                name: "invalid",
            },
        )


def test_parameters_have_deterministic_field_order():
    parameters = _parameters()

    assert tuple(
        parameters.__dataclass_fields__,
    ) == (
        "scale",
        "translation_x",
        "translation_y",
        "rotation_degrees",
        "face_width",
        "face_height",
        "eye_spacing",
        "eye_height",
        "nose_width",
        "nose_length",
        "mouth_width",
        "chin_width",
        "chin_length",
        "jaw_width",
        "forehead_height",
    )
