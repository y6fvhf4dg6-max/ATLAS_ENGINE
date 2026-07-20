import pytest

from CORE.atlas_frontal_face_measurements import (
    AtlasFrontalFaceMeasurements,
)
from CORE.atlas_frontal_face_parameter_comparator import (
    AtlasFrontalFaceParameterComparator,
)
from CORE.atlas_frontal_face_parameter_comparison_result import (
    AtlasFrontalFaceParameterComparisonResult,
)
from CORE.atlas_frontal_face_reference_profile import (
    AtlasFrontalFaceReferenceProfile,
)


def _measurements(
    **overrides,
) -> AtlasFrontalFaceMeasurements:
    values = {
        "center_x": 0.50,
        "center_y": 0.50,
        "reference_scale": 0.80,
        "face_width": 0.60,
        "face_height": 0.80,
        "eye_spacing": 0.26,
        "eye_line_angle_degrees": 0.0,
        "nose_width": 0.10,
        "nose_length": 0.15,
        "mouth_width": 0.18,
        "jaw_width": 0.44,
        "forehead_height": 0.30,
    }

    values.update(
        overrides,
    )

    return AtlasFrontalFaceMeasurements(
        **values,
    )


def _reference_profile(
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


def test_comparator_returns_comparison_result():
    result = AtlasFrontalFaceParameterComparator.compare(
        _measurements(),
        reference_profile=_reference_profile(),
    )

    assert isinstance(
        result,
        AtlasFrontalFaceParameterComparisonResult,
    )


def test_comparator_preserves_measurements_and_profile_name():
    measurements = _measurements()
    profile = _reference_profile()

    result = AtlasFrontalFaceParameterComparator.compare(
        measurements,
        reference_profile=profile,
    )

    assert result.measurements is measurements
    assert result.reference_profile_name == ("synthetic-neutral")


def test_neutral_measurements_produce_zero_deviations():
    result = AtlasFrontalFaceParameterComparator.compare(
        _measurements(),
        reference_profile=_reference_profile(),
    )

    assert result.ratio_deviations == {
        "face_width": 0.0,
        "eye_spacing": 0.0,
        "nose_width": 0.0,
        "nose_length": 0.0,
        "mouth_width": 0.0,
        "jaw_width": 0.0,
        "forehead_height": 0.0,
    }


def test_comparator_reports_parameter_minus_neutral():
    result = AtlasFrontalFaceParameterComparator.compare(
        _measurements(
            face_width=0.66,
            eye_spacing=0.234,
            nose_width=0.11,
            nose_length=0.135,
            mouth_width=0.198,
            jaw_width=0.484,
            forehead_height=0.27,
        ),
        reference_profile=_reference_profile(),
    )

    assert result.ratio_deviations == pytest.approx(
        {
            "face_width": 0.10,
            "eye_spacing": -0.10,
            "nose_width": 0.10,
            "nose_length": -0.10,
            "mouth_width": 0.10,
            "jaw_width": 0.10,
            "forehead_height": -0.10,
        }
    )


def test_comparator_parameters_match_initializer_output():
    measurements = _measurements(
        center_x=0.53,
        face_width=0.63,
        nose_length=0.16,
    )
    profile = _reference_profile()

    result = AtlasFrontalFaceParameterComparator.compare(
        measurements,
        reference_profile=profile,
    )

    assert result.parameters.scale == pytest.approx(
        0.80,
    )
    assert result.parameters.translation_x == pytest.approx(
        0.03,
    )
    assert result.parameters.face_width == pytest.approx(
        1.05,
    )
    assert result.parameters.nose_length == pytest.approx(
        1.0666666666666667,
    )


def test_comparator_rejects_wrong_measurements_type():
    with pytest.raises(
        TypeError,
        match="AtlasFrontalFaceMeasurements",
    ):
        AtlasFrontalFaceParameterComparator.compare(
            object(),
            reference_profile=_reference_profile(),
        )


def test_comparator_rejects_wrong_reference_profile_type():
    with pytest.raises(
        TypeError,
        match="AtlasFrontalFaceReferenceProfile",
    ):
        AtlasFrontalFaceParameterComparator.compare(
            _measurements(),
            reference_profile=object(),
        )


def test_comparator_is_deterministic():
    measurements = _measurements(
        face_width=0.63,
        jaw_width=0.46,
    )
    profile = _reference_profile()

    first = AtlasFrontalFaceParameterComparator.compare(
        measurements,
        reference_profile=profile,
    )
    second = AtlasFrontalFaceParameterComparator.compare(
        measurements,
        reference_profile=profile,
    )

    assert first == second
    assert first is not second
