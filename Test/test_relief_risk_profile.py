import pytest

from CORE.atlas_relief_risk_profile import (
    AtlasReliefRiskProfile,
)


def test_default_profile_matches_current_risk_defaults():
    profile = AtlasReliefRiskProfile()

    assert profile.warning_slope_degrees == 55.0
    assert profile.critical_slope_degrees == 75.0
    assert profile.warning_slope_area_percent == 0.0
    assert profile.critical_slope_area_percent == 0.0


def test_profile_converts_values_to_float():
    profile = AtlasReliefRiskProfile(
        warning_slope_degrees=50,
        critical_slope_degrees=70,
        warning_slope_area_percent=2,
        critical_slope_area_percent=1,
    )

    assert profile.warning_slope_degrees == 50.0
    assert profile.critical_slope_degrees == 70.0
    assert profile.warning_slope_area_percent == 2.0
    assert profile.critical_slope_area_percent == 1.0


def test_profile_produces_pipeline_arguments():
    profile = AtlasReliefRiskProfile(
        warning_slope_degrees=48.0,
        critical_slope_degrees=72.0,
        warning_slope_area_percent=3.0,
        critical_slope_area_percent=1.0,
    )

    assert profile.to_pipeline_kwargs() == {
        "warning_slope_degrees": 48.0,
        "critical_slope_degrees": 72.0,
        "warning_slope_area_percent": 3.0,
        "critical_slope_area_percent": 1.0,
    }


def test_profile_is_immutable():
    profile = AtlasReliefRiskProfile()

    with pytest.raises(
        AttributeError,
    ):
        profile.warning_slope_degrees = 40.0


@pytest.mark.parametrize(
    "arguments",
    [
        {
            "warning_slope_degrees": -0.1,
        },
        {
            "warning_slope_degrees": 75.0,
            "critical_slope_degrees": 75.0,
        },
        {
            "critical_slope_degrees": 90.0,
        },
        {
            "warning_slope_area_percent": -0.1,
        },
        {
            "warning_slope_area_percent": 100.1,
        },
        {
            "critical_slope_area_percent": -0.1,
        },
        {
            "critical_slope_area_percent": 100.1,
        },
        {
            "warning_slope_degrees": float("nan"),
        },
        {
            "critical_slope_degrees": float("inf"),
        },
        {
            "warning_slope_area_percent": float("nan"),
        },
        {
            "critical_slope_area_percent": float("inf"),
        },
    ],
)
def test_profile_rejects_invalid_values(arguments):
    with pytest.raises(ValueError):
        AtlasReliefRiskProfile(**arguments)


def test_profile_accepts_optional_name():
    profile = AtlasReliefRiskProfile(
        name="prototype-safe",
    )

    assert profile.name == "prototype-safe"


def test_profile_strips_name_whitespace():
    profile = AtlasReliefRiskProfile(
        name="  prototype-safe  ",
    )

    assert profile.name == "prototype-safe"


@pytest.mark.parametrize(
    "name",
    [
        "",
        "   ",
    ],
)
def test_profile_rejects_blank_name(name):
    with pytest.raises(ValueError):
        AtlasReliefRiskProfile(
            name=name,
        )


def test_profile_pipeline_kwargs_exclude_name():
    profile = AtlasReliefRiskProfile(
        name="prototype-safe",
    )

    assert "name" not in profile.to_pipeline_kwargs()
