from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_frontal_face_measurements import (
    AtlasFrontalFaceMeasurements,
)


def _measurements(
    **overrides,
) -> AtlasFrontalFaceMeasurements:
    values = {
        "center_x": 0.50,
        "center_y": 0.52,
        "reference_scale": 0.60,
        "face_width": 0.58,
        "face_height": 0.72,
        "eye_spacing": 0.24,
        "eye_line_angle_degrees": 0.0,
        "nose_width": 0.10,
        "nose_length": 0.18,
        "mouth_width": 0.20,
        "jaw_width": 0.46,
        "forehead_height": 0.16,
    }

    values.update(
        overrides,
    )

    return AtlasFrontalFaceMeasurements(
        **values,
    )


def test_measurements_preserve_expected_values():
    measurements = _measurements(
        center_x=0.48,
        center_y=0.51,
        reference_scale=0.64,
        face_width=0.61,
        face_height=0.75,
        eye_spacing=0.26,
        eye_line_angle_degrees=-2.5,
        nose_width=0.11,
        nose_length=0.19,
        mouth_width=0.21,
        jaw_width=0.49,
        forehead_height=0.17,
    )

    assert measurements.center_x == 0.48
    assert measurements.center_y == 0.51
    assert measurements.reference_scale == 0.64
    assert measurements.face_width == 0.61
    assert measurements.face_height == 0.75
    assert measurements.eye_spacing == 0.26
    assert measurements.eye_line_angle_degrees == -2.5
    assert measurements.nose_width == 0.11
    assert measurements.nose_length == 0.19
    assert measurements.mouth_width == 0.21
    assert measurements.jaw_width == 0.49
    assert measurements.forehead_height == 0.17


def test_measurements_convert_numeric_values_to_float():
    measurements = _measurements(
        center_x="0.48",
        center_y="0.51",
        reference_scale="0.64",
        eye_line_angle_degrees="-2.5",
    )

    assert measurements.center_x == 0.48
    assert measurements.center_y == 0.51
    assert measurements.reference_scale == 0.64
    assert measurements.eye_line_angle_degrees == -2.5

    assert isinstance(
        measurements.center_x,
        float,
    )
    assert isinstance(
        measurements.reference_scale,
        float,
    )


def test_measurements_are_immutable():
    measurements = _measurements()

    with pytest.raises(
        FrozenInstanceError,
    ):
        measurements.face_width = 0.70


@pytest.mark.parametrize(
    "name",
    (
        "center_x",
        "center_y",
    ),
)
@pytest.mark.parametrize(
    "value",
    (
        -0.01,
        1.01,
    ),
)
def test_normalized_centers_reject_values_outside_range(
    name,
    value,
):
    with pytest.raises(
        ValueError,
        match=f"{name} must be in the 0.0..1.0 range",
    ):
        _measurements(
            **{
                name: value,
            },
        )


@pytest.mark.parametrize(
    "name",
    (
        "reference_scale",
        "face_width",
        "face_height",
        "eye_spacing",
        "nose_width",
        "nose_length",
        "mouth_width",
        "jaw_width",
        "forehead_height",
    ),
)
def test_positive_measurements_reject_zero(
    name,
):
    with pytest.raises(
        ValueError,
        match=f"{name} must be greater than zero",
    ):
        _measurements(
            **{
                name: 0.0,
            },
        )


@pytest.mark.parametrize(
    "name",
    (
        "reference_scale",
        "face_width",
        "face_height",
        "eye_spacing",
        "nose_width",
        "nose_length",
        "mouth_width",
        "jaw_width",
        "forehead_height",
    ),
)
def test_positive_measurements_reject_negative_values(
    name,
):
    with pytest.raises(
        ValueError,
        match=f"{name} must be greater than zero",
    ):
        _measurements(
            **{
                name: -0.1,
            },
        )


def test_eye_line_angle_accepts_negative_value():
    measurements = _measurements(
        eye_line_angle_degrees=-7.5,
    )

    assert measurements.eye_line_angle_degrees == -7.5


@pytest.mark.parametrize(
    "name",
    (
        "center_x",
        "center_y",
        "reference_scale",
        "face_width",
        "face_height",
        "eye_spacing",
        "eye_line_angle_degrees",
        "nose_width",
        "nose_length",
        "mouth_width",
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
def test_measurements_reject_non_finite_values(
    name,
    value,
):
    with pytest.raises(
        ValueError,
        match=f"{name} must be finite",
    ):
        _measurements(
            **{
                name: value,
            },
        )


@pytest.mark.parametrize(
    "name",
    (
        "center_x",
        "center_y",
        "reference_scale",
        "face_width",
        "face_height",
        "eye_spacing",
        "eye_line_angle_degrees",
        "nose_width",
        "nose_length",
        "mouth_width",
        "jaw_width",
        "forehead_height",
    ),
)
def test_measurements_reject_non_numeric_values(
    name,
):
    with pytest.raises(
        ValueError,
        match=f"{name} must be numeric",
    ):
        _measurements(
            **{
                name: "invalid",
            },
        )


def test_measurements_have_deterministic_field_order():
    measurements = _measurements()

    assert tuple(
        measurements.__dataclass_fields__,
    ) == (
        "center_x",
        "center_y",
        "reference_scale",
        "face_width",
        "face_height",
        "eye_spacing",
        "eye_line_angle_degrees",
        "nose_width",
        "nose_length",
        "mouth_width",
        "jaw_width",
        "forehead_height",
    )
