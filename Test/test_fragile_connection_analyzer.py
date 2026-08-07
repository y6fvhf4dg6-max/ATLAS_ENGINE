import dataclasses
import math

import pytest

from CORE.atlas_fragile_connection_analyzer import (
    AtlasConnectionMeasurement,
    AtlasFragileConnectionAnalysis,
    AtlasFragileConnectionAnalyzer,
)


def test_connection_measurement_normalizes_component_and_calculates_ratio():
    measurement = AtlasConnectionMeasurement(
        component="  MINARET ",
        connection_width_mm=0.8,
        component_span_mm=4.0,
    )

    assert measurement.component == "minaret"
    assert measurement.connection_width_mm == pytest.approx(0.8)
    assert measurement.component_span_mm == pytest.approx(4.0)
    assert measurement.connection_ratio == pytest.approx(0.2)


def test_connection_ratio_is_derived_and_not_constructor_input():
    with pytest.raises(TypeError):
        AtlasConnectionMeasurement(
            component="tower",
            connection_width_mm=1.0,
            component_span_mm=5.0,
            connection_ratio=0.9,
        )


def test_connection_measurement_is_immutable():
    measurement = AtlasConnectionMeasurement(
        component="tower",
        connection_width_mm=1.0,
        component_span_mm=5.0,
    )

    with pytest.raises(dataclasses.FrozenInstanceError):
        measurement.connection_width_mm = 2.0


@pytest.mark.parametrize(
    ("component", "connection_width_mm", "component_span_mm"),
    [
        ("", 1.0, 5.0),
        ("   ", 1.0, 5.0),
        ("tower", 0.0, 5.0),
        ("tower", -1.0, 5.0),
        ("tower", 1.0, 0.0),
        ("tower", 1.0, -5.0),
        ("tower", math.nan, 5.0),
        ("tower", math.inf, 5.0),
        ("tower", 1.0, math.nan),
        ("tower", 1.0, math.inf),
        ("tower", 6.0, 5.0),
    ],
)
def test_connection_measurement_rejects_invalid_values(
    component,
    connection_width_mm,
    component_span_mm,
):
    with pytest.raises((TypeError, ValueError)):
        AtlasConnectionMeasurement(
            component=component,
            connection_width_mm=connection_width_mm,
            component_span_mm=component_span_mm,
        )


def test_analysis_marks_ratio_at_or_above_threshold_as_safe():
    result = AtlasFragileConnectionAnalyzer.analyze(
        measurements=(
            AtlasConnectionMeasurement(
                component="tower",
                connection_width_mm=1.0,
                component_span_mm=5.0,
            ),
            AtlasConnectionMeasurement(
                component="roof",
                connection_width_mm=3.0,
                component_span_mm=6.0,
            ),
        ),
        minimum_connection_ratio=0.20,
    )

    assert isinstance(result, AtlasFragileConnectionAnalysis)
    assert result.minimum_connection_ratio == pytest.approx(0.20)
    assert result.minimum_observed_ratio == pytest.approx(0.20)
    assert result.fragile_components == ()
    assert result.has_fragile_connections is False


def test_analysis_reports_connections_below_ratio_threshold():
    result = AtlasFragileConnectionAnalyzer.analyze(
        measurements=(
            AtlasConnectionMeasurement(
                component="minaret",
                connection_width_mm=0.5,
                component_span_mm=5.0,
            ),
            AtlasConnectionMeasurement(
                component="spire",
                connection_width_mm=0.75,
                component_span_mm=5.0,
            ),
            AtlasConnectionMeasurement(
                component="tower",
                connection_width_mm=2.0,
                component_span_mm=5.0,
            ),
        ),
        minimum_connection_ratio=0.20,
    )

    assert result.minimum_observed_ratio == pytest.approx(0.10)
    assert result.fragile_components == (
        "minaret",
        "spire",
    )
    assert result.has_fragile_connections is True


def test_analysis_freezes_measurement_collection():
    measurements = [
        AtlasConnectionMeasurement(
            component="tower",
            connection_width_mm=2.0,
            component_span_mm=5.0,
        )
    ]

    result = AtlasFragileConnectionAnalyzer.analyze(
        measurements=measurements,
        minimum_connection_ratio=0.20,
    )

    assert isinstance(result.measurements, tuple)
    assert result.measurements == tuple(measurements)

    measurements.append(
        AtlasConnectionMeasurement(
            component="spire",
            connection_width_mm=0.5,
            component_span_mm=5.0,
        )
    )

    assert len(result.measurements) == 1


def test_analysis_preserves_fragile_component_order_without_duplicates():
    result = AtlasFragileConnectionAnalyzer.analyze(
        measurements=(
            AtlasConnectionMeasurement(
                component="minaret",
                connection_width_mm=0.5,
                component_span_mm=5.0,
            ),
            AtlasConnectionMeasurement(
                component="spire",
                connection_width_mm=0.5,
                component_span_mm=4.0,
            ),
            AtlasConnectionMeasurement(
                component="minaret",
                connection_width_mm=0.4,
                component_span_mm=5.0,
            ),
        ),
        minimum_connection_ratio=0.20,
    )

    assert result.fragile_components == (
        "minaret",
        "spire",
    )


@pytest.mark.parametrize(
    "minimum_connection_ratio",
    [
        0.0,
        -0.1,
        1.01,
        math.nan,
        math.inf,
        -math.inf,
        None,
    ],
)
def test_analysis_rejects_invalid_minimum_connection_ratio(
    minimum_connection_ratio,
):
    with pytest.raises((TypeError, ValueError)):
        AtlasFragileConnectionAnalyzer.analyze(
            measurements=(
                AtlasConnectionMeasurement(
                    component="tower",
                    connection_width_mm=2.0,
                    component_span_mm=5.0,
                ),
            ),
            minimum_connection_ratio=minimum_connection_ratio,
        )


def test_analysis_accepts_one_as_ratio_threshold():
    result = AtlasFragileConnectionAnalyzer.analyze(
        measurements=(
            AtlasConnectionMeasurement(
                component="column",
                connection_width_mm=5.0,
                component_span_mm=5.0,
            ),
        ),
        minimum_connection_ratio=1.0,
    )

    assert result.fragile_components == ()
    assert result.has_fragile_connections is False


def test_analysis_rejects_empty_measurements():
    with pytest.raises(ValueError):
        AtlasFragileConnectionAnalyzer.analyze(
            measurements=(),
            minimum_connection_ratio=0.20,
        )


def test_analysis_rejects_invalid_measurement_items():
    with pytest.raises((TypeError, ValueError)):
        AtlasFragileConnectionAnalyzer.analyze(
            measurements=("not-a-measurement",),
            minimum_connection_ratio=0.20,
        )
