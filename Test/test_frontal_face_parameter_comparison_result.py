from dataclasses import FrozenInstanceError
from types import MappingProxyType

import pytest

from CORE.atlas_frontal_face_measurements import (
    AtlasFrontalFaceMeasurements,
)
from CORE.atlas_frontal_face_parameter_comparison_result import (
    AtlasFrontalFaceParameterComparisonResult,
)
from CORE.atlas_parametric_face_parameters import (
    AtlasParametricFaceParameters,
)


def _measurements() -> AtlasFrontalFaceMeasurements:
    return AtlasFrontalFaceMeasurements(
        center_x=0.50,
        center_y=0.50,
        reference_scale=0.80,
        face_width=0.60,
        face_height=0.80,
        eye_spacing=0.26,
        eye_line_angle_degrees=0.0,
        nose_width=0.10,
        nose_length=0.15,
        mouth_width=0.18,
        jaw_width=0.44,
        forehead_height=0.30,
    )


def _parameters() -> AtlasParametricFaceParameters:
    return AtlasParametricFaceParameters(
        scale=0.80,
        translation_x=0.0,
        translation_y=0.0,
        rotation_degrees=0.0,
        face_width=1.10,
        face_height=1.0,
        eye_spacing=0.95,
        eye_height=1.0,
        nose_width=1.20,
        nose_length=0.90,
        mouth_width=1.05,
        chin_width=1.0,
        chin_length=1.0,
        jaw_width=1.15,
        forehead_height=0.85,
    )


def _result(
    **overrides,
) -> AtlasFrontalFaceParameterComparisonResult:
    values = {
        "reference_profile_name": "synthetic-neutral",
        "measurements": _measurements(),
        "parameters": _parameters(),
        "ratio_deviations": {
            "face_width": 0.10,
            "eye_spacing": -0.05,
            "nose_width": 0.20,
            "nose_length": -0.10,
            "mouth_width": 0.05,
            "jaw_width": 0.15,
            "forehead_height": -0.15,
        },
    }

    values.update(
        overrides,
    )

    return AtlasFrontalFaceParameterComparisonResult(
        **values,
    )


def test_result_preserves_contract_values():
    result = _result()

    assert result.reference_profile_name == ("synthetic-neutral")
    assert result.measurements == _measurements()
    assert result.parameters == _parameters()
    assert result.ratio_deviations == {
        "face_width": 0.10,
        "eye_spacing": -0.05,
        "nose_width": 0.20,
        "nose_length": -0.10,
        "mouth_width": 0.05,
        "jaw_width": 0.15,
        "forehead_height": -0.15,
    }


def test_result_strips_reference_profile_name():
    result = _result(
        reference_profile_name=("  synthetic-neutral  "),
    )

    assert result.reference_profile_name == ("synthetic-neutral")


@pytest.mark.parametrize(
    "invalid_name",
    [
        "",
        "   ",
    ],
)
def test_result_rejects_blank_reference_profile_name(
    invalid_name,
):
    with pytest.raises(
        ValueError,
        match=("reference_profile_name must not be blank"),
    ):
        _result(
            reference_profile_name=invalid_name,
        )


def test_result_rejects_non_string_reference_profile_name():
    with pytest.raises(
        ValueError,
        match=("reference_profile_name must be a string"),
    ):
        _result(
            reference_profile_name=123,
        )


def test_result_rejects_wrong_measurements_type():
    with pytest.raises(
        TypeError,
        match="AtlasFrontalFaceMeasurements",
    ):
        _result(
            measurements=object(),
        )


def test_result_rejects_wrong_parameters_type():
    with pytest.raises(
        TypeError,
        match="AtlasParametricFaceParameters",
    ):
        _result(
            parameters=object(),
        )


def test_result_converts_deviation_values_to_float():
    result = _result(
        ratio_deviations={
            "face_width": "0.10",
            "eye_spacing": 1,
        },
    )

    assert result.ratio_deviations == {
        "face_width": 0.10,
        "eye_spacing": 1.0,
    }
    assert isinstance(
        result.ratio_deviations["face_width"],
        float,
    )
    assert isinstance(
        result.ratio_deviations["eye_spacing"],
        float,
    )


def test_ratio_deviations_are_immutable():
    result = _result()

    assert isinstance(
        result.ratio_deviations,
        MappingProxyType,
    )

    with pytest.raises(
        TypeError,
    ):
        result.ratio_deviations["face_width"] = 0.0


def test_ratio_deviations_are_copied():
    source = {
        "face_width": 0.10,
    }

    result = _result(
        ratio_deviations=source,
    )

    source["face_width"] = 0.90

    assert result.ratio_deviations["face_width"] == pytest.approx(
        0.10,
    )


def test_result_rejects_non_mapping_deviations():
    with pytest.raises(
        ValueError,
        match="ratio_deviations must be a mapping",
    ):
        _result(
            ratio_deviations=[],
        )


def test_result_rejects_empty_deviations():
    with pytest.raises(
        ValueError,
        match=("ratio_deviations must not be empty"),
    ):
        _result(
            ratio_deviations={},
        )


def test_result_rejects_non_string_deviation_name():
    with pytest.raises(
        ValueError,
        match=("ratio deviation names must be strings"),
    ):
        _result(
            ratio_deviations={
                123: 0.10,
            },
        )


def test_result_rejects_blank_deviation_name():
    with pytest.raises(
        ValueError,
        match=("ratio deviation names must not be blank"),
    ):
        _result(
            ratio_deviations={
                "   ": 0.10,
            },
        )


def test_result_rejects_duplicate_normalized_names():
    with pytest.raises(
        ValueError,
        match=("ratio deviation names must be unique"),
    ):
        _result(
            ratio_deviations={
                "face_width": 0.10,
                " face_width ": 0.20,
            },
        )


@pytest.mark.parametrize(
    "invalid_value",
    [
        float("inf"),
        float("-inf"),
        float("nan"),
    ],
)
def test_result_rejects_non_finite_deviation(
    invalid_value,
):
    with pytest.raises(
        ValueError,
        match=("face_width deviation must be finite"),
    ):
        _result(
            ratio_deviations={
                "face_width": invalid_value,
            },
        )


def test_result_rejects_non_numeric_deviation():
    with pytest.raises(
        ValueError,
        match=("face_width deviation must be numeric"),
    ):
        _result(
            ratio_deviations={
                "face_width": object(),
            },
        )


def test_result_is_immutable():
    result = _result()

    with pytest.raises(
        FrozenInstanceError,
    ):
        result.reference_profile_name = "changed"


def test_result_equality_is_value_based():
    assert _result() == _result()


def test_result_instances_are_distinct():
    first = _result()
    second = _result()

    assert first is not second
