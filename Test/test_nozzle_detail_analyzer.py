import dataclasses
import math

import pytest

from CORE.atlas_nozzle_detail_analyzer import (
    AtlasNozzleDetailAnalysis,
    AtlasNozzleDetailAnalyzer,
    AtlasNozzleDetailMeasurement,
)


def test_measurement_normalizes_component_and_is_immutable():
    measurement = AtlasNozzleDetailMeasurement(
        component="  WINDOW ",
        detail_size_mm=0.3,
        nozzle_diameter_mm=0.4,
    )

    assert measurement.component == "window"
    assert measurement.detail_size_mm == pytest.approx(0.3)
    assert measurement.nozzle_diameter_mm == pytest.approx(0.4)
    assert measurement.nozzle_ratio == pytest.approx(0.75)

    with pytest.raises(dataclasses.FrozenInstanceError):
        measurement.detail_size_mm = 0.5


def test_nozzle_ratio_is_derived_and_not_constructor_input():
    with pytest.raises(TypeError):
        AtlasNozzleDetailMeasurement(
            component="window",
            detail_size_mm=0.3,
            nozzle_diameter_mm=0.4,
            nozzle_ratio=0.9,
        )


@pytest.mark.parametrize(
    ("component", "detail_size_mm", "nozzle_diameter_mm"),
    [
        ("", 0.3, 0.4),
        ("   ", 0.3, 0.4),
        ("window", 0.0, 0.4),
        ("window", -0.1, 0.4),
        ("window", math.nan, 0.4),
        ("window", math.inf, 0.4),
        ("window", 0.3, 0.0),
        ("window", 0.3, -0.4),
        ("window", 0.3, math.nan),
        ("window", 0.3, math.inf),
    ],
)
def test_measurement_rejects_invalid_values(
    component,
    detail_size_mm,
    nozzle_diameter_mm,
):
    with pytest.raises((TypeError, ValueError)):
        AtlasNozzleDetailMeasurement(
            component=component,
            detail_size_mm=detail_size_mm,
            nozzle_diameter_mm=nozzle_diameter_mm,
        )


def test_analysis_marks_detail_equal_to_or_above_nozzle_as_safe():
    result = AtlasNozzleDetailAnalyzer.analyze(
        measurements=(
            AtlasNozzleDetailMeasurement(
                component="window",
                detail_size_mm=0.4,
                nozzle_diameter_mm=0.4,
            ),
            AtlasNozzleDetailMeasurement(
                component="cornice",
                detail_size_mm=0.8,
                nozzle_diameter_mm=0.4,
            ),
        ),
        nozzle_diameter_mm=0.4,
    )

    assert isinstance(result, AtlasNozzleDetailAnalysis)
    assert result.nozzle_diameter_mm == pytest.approx(0.4)
    assert result.minimum_observed_detail_mm == pytest.approx(0.4)
    assert result.below_nozzle_components == ()
    assert result.has_below_nozzle_details is False


def test_analysis_reports_details_below_nozzle():
    result = AtlasNozzleDetailAnalyzer.analyze(
        measurements=(
            AtlasNozzleDetailMeasurement(
                component="window",
                detail_size_mm=0.3,
                nozzle_diameter_mm=0.4,
            ),
            AtlasNozzleDetailMeasurement(
                component="ornament",
                detail_size_mm=0.1,
                nozzle_diameter_mm=0.4,
            ),
            AtlasNozzleDetailMeasurement(
                component="buttress",
                detail_size_mm=0.6,
                nozzle_diameter_mm=0.4,
            ),
        ),
        nozzle_diameter_mm=0.4,
    )

    assert result.minimum_observed_detail_mm == pytest.approx(0.1)
    assert result.below_nozzle_components == (
        "window",
        "ornament",
    )
    assert result.has_below_nozzle_details is True


def test_analysis_requires_measurements_to_match_analysis_nozzle():
    with pytest.raises(ValueError):
        AtlasNozzleDetailAnalyzer.analyze(
            measurements=(
                AtlasNozzleDetailMeasurement(
                    component="window",
                    detail_size_mm=0.3,
                    nozzle_diameter_mm=0.6,
                ),
            ),
            nozzle_diameter_mm=0.4,
        )


def test_analysis_freezes_measurement_collection():
    measurements = [
        AtlasNozzleDetailMeasurement(
            component="window",
            detail_size_mm=0.5,
            nozzle_diameter_mm=0.4,
        )
    ]

    result = AtlasNozzleDetailAnalyzer.analyze(
        measurements=measurements,
        nozzle_diameter_mm=0.4,
    )

    assert isinstance(result.measurements, tuple)
    assert result.measurements == tuple(measurements)

    measurements.append(
        AtlasNozzleDetailMeasurement(
            component="ornament",
            detail_size_mm=0.1,
            nozzle_diameter_mm=0.4,
        )
    )

    assert len(result.measurements) == 1


def test_analysis_preserves_below_nozzle_component_order_without_duplicates():
    result = AtlasNozzleDetailAnalyzer.analyze(
        measurements=(
            AtlasNozzleDetailMeasurement(
                component="window",
                detail_size_mm=0.3,
                nozzle_diameter_mm=0.4,
            ),
            AtlasNozzleDetailMeasurement(
                component="ornament",
                detail_size_mm=0.2,
                nozzle_diameter_mm=0.4,
            ),
            AtlasNozzleDetailMeasurement(
                component="window",
                detail_size_mm=0.1,
                nozzle_diameter_mm=0.4,
            ),
        ),
        nozzle_diameter_mm=0.4,
    )

    assert result.below_nozzle_components == (
        "window",
        "ornament",
    )


@pytest.mark.parametrize(
    "nozzle_diameter_mm",
    [
        0.0,
        -0.4,
        math.nan,
        math.inf,
        -math.inf,
        None,
    ],
)
def test_analysis_rejects_invalid_nozzle_diameter(
    nozzle_diameter_mm,
):
    with pytest.raises((TypeError, ValueError)):
        AtlasNozzleDetailAnalyzer.analyze(
            measurements=(
                AtlasNozzleDetailMeasurement(
                    component="window",
                    detail_size_mm=0.5,
                    nozzle_diameter_mm=0.4,
                ),
            ),
            nozzle_diameter_mm=nozzle_diameter_mm,
        )


def test_analysis_rejects_empty_measurements():
    with pytest.raises(ValueError):
        AtlasNozzleDetailAnalyzer.analyze(
            measurements=(),
            nozzle_diameter_mm=0.4,
        )


def test_analysis_rejects_invalid_measurement_items():
    with pytest.raises((TypeError, ValueError)):
        AtlasNozzleDetailAnalyzer.analyze(
            measurements=("not-a-measurement",),
            nozzle_diameter_mm=0.4,
        )
