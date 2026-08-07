import dataclasses
import math

import pytest

from CORE.atlas_overhang_support_analyzer import (
    AtlasOverhangMeasurement,
    AtlasOverhangSupportAnalysis,
    AtlasOverhangSupportAnalyzer,
)


def test_overhang_measurement_normalizes_component_and_is_immutable():
    measurement = AtlasOverhangMeasurement(
        component="  ROOF ",
        overhang_degrees=45.0,
    )

    assert measurement.component == "roof"
    assert measurement.overhang_degrees == pytest.approx(45.0)

    with pytest.raises(dataclasses.FrozenInstanceError):
        measurement.overhang_degrees = 50.0


@pytest.mark.parametrize(
    ("component", "overhang_degrees"),
    [
        ("", 45.0),
        ("   ", 45.0),
        ("roof", -0.1),
        ("roof", 90.1),
        ("roof", math.nan),
        ("roof", math.inf),
        ("roof", -math.inf),
    ],
)
def test_overhang_measurement_rejects_invalid_values(
    component,
    overhang_degrees,
):
    with pytest.raises((TypeError, ValueError)):
        AtlasOverhangMeasurement(
            component=component,
            overhang_degrees=overhang_degrees,
        )


def test_analysis_marks_angles_below_threshold_as_support_free():
    result = AtlasOverhangSupportAnalyzer.analyze(
        measurements=(
            AtlasOverhangMeasurement(
                component="wall",
                overhang_degrees=0.0,
            ),
            AtlasOverhangMeasurement(
                component="roof",
                overhang_degrees=44.9,
            ),
        ),
        support_threshold_degrees=45.0,
    )

    assert isinstance(result, AtlasOverhangSupportAnalysis)
    assert result.support_threshold_degrees == pytest.approx(45.0)
    assert result.maximum_overhang_degrees == pytest.approx(44.9)
    assert result.support_required_components == ()
    assert result.support_required is False


def test_analysis_marks_threshold_and_above_as_support_required():
    result = AtlasOverhangSupportAnalyzer.analyze(
        measurements=(
            AtlasOverhangMeasurement(
                component="roof",
                overhang_degrees=45.0,
            ),
            AtlasOverhangMeasurement(
                component="balcony",
                overhang_degrees=70.0,
            ),
            AtlasOverhangMeasurement(
                component="wall",
                overhang_degrees=10.0,
            ),
        ),
        support_threshold_degrees=45.0,
    )

    assert result.maximum_overhang_degrees == pytest.approx(70.0)
    assert result.support_required_components == (
        "roof",
        "balcony",
    )
    assert result.support_required is True


def test_analysis_freezes_measurement_collection():
    measurements = [
        AtlasOverhangMeasurement(
            component="roof",
            overhang_degrees=30.0,
        )
    ]

    result = AtlasOverhangSupportAnalyzer.analyze(
        measurements=measurements,
        support_threshold_degrees=45.0,
    )

    assert isinstance(result.measurements, tuple)
    assert result.measurements == tuple(measurements)

    measurements.append(
        AtlasOverhangMeasurement(
            component="balcony",
            overhang_degrees=80.0,
        )
    )

    assert len(result.measurements) == 1


def test_analysis_preserves_component_order_without_duplicates():
    result = AtlasOverhangSupportAnalyzer.analyze(
        measurements=(
            AtlasOverhangMeasurement(
                component="roof",
                overhang_degrees=50.0,
            ),
            AtlasOverhangMeasurement(
                component="balcony",
                overhang_degrees=60.0,
            ),
            AtlasOverhangMeasurement(
                component="roof",
                overhang_degrees=75.0,
            ),
        ),
        support_threshold_degrees=45.0,
    )

    assert result.support_required_components == (
        "roof",
        "balcony",
    )


@pytest.mark.parametrize(
    "support_threshold_degrees",
    [
        0.0,
        -0.1,
        90.1,
        math.nan,
        math.inf,
        -math.inf,
        None,
    ],
)
def test_analysis_rejects_invalid_support_threshold(
    support_threshold_degrees,
):
    with pytest.raises((TypeError, ValueError)):
        AtlasOverhangSupportAnalyzer.analyze(
            measurements=(
                AtlasOverhangMeasurement(
                    component="roof",
                    overhang_degrees=30.0,
                ),
            ),
            support_threshold_degrees=support_threshold_degrees,
        )


def test_analysis_accepts_ninety_degree_support_threshold():
    result = AtlasOverhangSupportAnalyzer.analyze(
        measurements=(
            AtlasOverhangMeasurement(
                component="bridge_deck",
                overhang_degrees=90.0,
            ),
        ),
        support_threshold_degrees=90.0,
    )

    assert result.support_required_components == ("bridge_deck",)
    assert result.support_required is True


def test_analysis_rejects_empty_measurements():
    with pytest.raises(ValueError):
        AtlasOverhangSupportAnalyzer.analyze(
            measurements=(),
            support_threshold_degrees=45.0,
        )


def test_analysis_rejects_invalid_measurement_items():
    with pytest.raises((TypeError, ValueError)):
        AtlasOverhangSupportAnalyzer.analyze(
            measurements=("not-a-measurement",),
            support_threshold_degrees=45.0,
        )
