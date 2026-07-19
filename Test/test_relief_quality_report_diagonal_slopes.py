import math

import pytest

from CORE.atlas_relief_mesh_builder import (
    AtlasReliefMeshBuilder,
)
from CORE.atlas_relief_quality_report import (
    AtlasReliefQualityReport,
)


def _diagonal_ramp():
    return AtlasReliefMeshBuilder.build(
        [
            [0.0, 0.5],
            [0.5, 1.0],
        ],
        width_mm=1.0,
        depth_mm=1.0,
        relief_height_mm=2.0,
    )


def test_surface_analysis_counts_mesh_diagonal():
    report = AtlasReliefQualityReport.build(
        _diagonal_ramp()
    )

    assert report["surface_edge_count"] == 5


def test_diagonal_can_define_maximum_surface_slope():
    report = AtlasReliefQualityReport.build(
        _diagonal_ramp()
    )

    expected = math.degrees(
        math.atan2(
            2.0,
            math.sqrt(2.0),
        )
    )

    assert report[
        "maximum_slope_degrees"
    ] == pytest.approx(expected)

    assert report[
        "maximum_slope_degrees"
    ] > 45.0


def test_diagonal_can_define_maximum_adjacent_rise():
    report = AtlasReliefQualityReport.build(
        _diagonal_ramp()
    )

    assert report[
        "maximum_adjacent_rise_mm"
    ] == pytest.approx(2.0)


def test_diagonal_slope_can_trigger_warning():
    report = AtlasReliefQualityReport.build(
        _diagonal_ramp(),
        warning_slope_degrees=50.0,
        critical_slope_degrees=70.0,
    )

    assert report[
        "print_risk_status"
    ] == "WARN"

    assert report[
        "print_risk_issues"
    ][0]["code"] == "steep_surface_slope"


def test_flat_diagonal_does_not_create_false_slope():
    relief = AtlasReliefMeshBuilder.build(
        [
            [0.5, 0.5],
            [0.5, 0.5],
        ],
        width_mm=1.0,
        depth_mm=1.0,
        relief_height_mm=2.0,
    )

    report = AtlasReliefQualityReport.build(
        relief
    )

    assert report["surface_edge_count"] == 5
    assert report[
        "maximum_slope_degrees"
    ] == pytest.approx(0.0)
