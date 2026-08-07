import dataclasses
import math

import pytest

from CORE.atlas_minimum_thickness_analyzer import (
    AtlasMinimumThicknessAnalysis,
    AtlasMinimumThicknessAnalyzer,
    AtlasThicknessMeasurement,
)


def test_thickness_measurement_normalizes_component_and_is_immutable():
    measurement = AtlasThicknessMeasurement(
        component="  MINARET ",
        thickness_mm=0.8,
    )

    assert measurement.component == "minaret"
    assert measurement.thickness_mm == pytest.approx(0.8)

    with pytest.raises(dataclasses.FrozenInstanceError):
        measurement.thickness_mm = 1.0


@pytest.mark.parametrize(
    ("component", "thickness_mm"),
    [
        ("", 0.8),
        ("   ", 0.8),
        ("wall", 0.0),
        ("wall", -0.1),
        ("wall", math.nan),
        ("wall", math.inf),
        ("wall", -math.inf),
    ],
)
def test_thickness_measurement_rejects_invalid_values(
    component,
    thickness_mm,
):
    with pytest.raises((TypeError, ValueError)):
        AtlasThicknessMeasurement(
            component=component,
            thickness_mm=thickness_mm,
        )


def test_analysis_marks_measurements_at_or_above_minimum_as_safe():
    result = AtlasMinimumThicknessAnalyzer.analyze(
        measurements=(
            AtlasThicknessMeasurement(
                component="wall",
                thickness_mm=0.8,
            ),
            AtlasThicknessMeasurement(
                component="tower",
                thickness_mm=1.2,
            ),
        ),
        minimum_thickness_mm=0.8,
    )

    assert isinstance(result, AtlasMinimumThicknessAnalysis)
    assert result.minimum_thickness_mm == pytest.approx(0.8)
    assert result.minimum_observed_thickness_mm == pytest.approx(0.8)
    assert result.violating_components == ()
    assert result.is_safe is True


def test_analysis_reports_components_below_minimum():
    result = AtlasMinimumThicknessAnalyzer.analyze(
        measurements=(
            AtlasThicknessMeasurement(
                component="wall",
                thickness_mm=0.75,
            ),
            AtlasThicknessMeasurement(
                component="minaret",
                thickness_mm=0.35,
            ),
            AtlasThicknessMeasurement(
                component="roof",
                thickness_mm=1.1,
            ),
        ),
        minimum_thickness_mm=0.8,
    )

    assert result.minimum_observed_thickness_mm == pytest.approx(0.35)
    assert result.violating_components == ("wall", "minaret")
    assert result.is_safe is False


def test_analysis_freezes_measurement_collection():
    measurements = [
        AtlasThicknessMeasurement(
            component="wall",
            thickness_mm=1.0,
        )
    ]

    result = AtlasMinimumThicknessAnalyzer.analyze(
        measurements=measurements,
        minimum_thickness_mm=0.8,
    )

    assert isinstance(result.measurements, tuple)
    assert result.measurements == tuple(measurements)

    measurements.append(
        AtlasThicknessMeasurement(
            component="roof",
            thickness_mm=0.5,
        )
    )

    assert len(result.measurements) == 1


def test_analysis_preserves_violation_order_without_duplicates():
    result = AtlasMinimumThicknessAnalyzer.analyze(
        measurements=(
            AtlasThicknessMeasurement(
                component="wall",
                thickness_mm=0.7,
            ),
            AtlasThicknessMeasurement(
                component="minaret",
                thickness_mm=0.4,
            ),
            AtlasThicknessMeasurement(
                component="wall",
                thickness_mm=0.6,
            ),
        ),
        minimum_thickness_mm=0.8,
    )

    assert result.violating_components == (
        "wall",
        "minaret",
    )


@pytest.mark.parametrize(
    "minimum_thickness_mm",
    [
        0.0,
        -0.1,
        math.nan,
        math.inf,
        -math.inf,
        None,
    ],
)
def test_analysis_rejects_invalid_minimum_thickness(
    minimum_thickness_mm,
):
    with pytest.raises((TypeError, ValueError)):
        AtlasMinimumThicknessAnalyzer.analyze(
            measurements=(
                AtlasThicknessMeasurement(
                    component="wall",
                    thickness_mm=1.0,
                ),
            ),
            minimum_thickness_mm=minimum_thickness_mm,
        )


def test_analysis_rejects_empty_measurements():
    with pytest.raises(ValueError):
        AtlasMinimumThicknessAnalyzer.analyze(
            measurements=(),
            minimum_thickness_mm=0.8,
        )


def test_analysis_rejects_invalid_measurement_items():
    with pytest.raises((TypeError, ValueError)):
        AtlasMinimumThicknessAnalyzer.analyze(
            measurements=("not-a-measurement",),
            minimum_thickness_mm=0.8,
        )
