import math

import pytest

from CORE.atlas_relief_mesh_builder import (
    AtlasReliefMeshBuilder,
)
from CORE.atlas_relief_quality_report import (
    AtlasReliefQualityReport,
)


def _unequal_triangle_relief():
    return AtlasReliefMeshBuilder.build(
        [
            [0.0, 0.0],
            [0.0, 1.0],
        ],
        width_mm=2.0,
        depth_mm=1.0,
        relief_height_mm=2.0,
    )


def test_report_contains_slope_area_distribution():
    report = AtlasReliefQualityReport.build(
        _unequal_triangle_relief(),
        warning_slope_degrees=50.0,
        critical_slope_degrees=60.0,
    )

    expected_safe_area = math.sqrt(2.0)
    expected_critical_area = math.sqrt(5.0)
    expected_total_area = (
        expected_safe_area
        + expected_critical_area
    )

    assert report[
        "classified_slope_triangle_count"
    ] == 2

    assert report[
        "safe_slope_surface_area_mm2"
    ] == pytest.approx(
        expected_safe_area
    )

    assert report[
        "warning_slope_surface_area_mm2"
    ] == pytest.approx(0.0)

    assert report[
        "critical_slope_surface_area_mm2"
    ] == pytest.approx(
        expected_critical_area
    )

    assert report[
        "classified_slope_surface_area_mm2"
    ] == pytest.approx(
        expected_total_area
    )


def test_slope_area_percentages_sum_to_one_hundred():
    report = AtlasReliefQualityReport.build(
        _unequal_triangle_relief(),
        warning_slope_degrees=50.0,
        critical_slope_degrees=60.0,
    )

    total_percent = (
        report[
            "safe_slope_surface_area_percent"
        ]
        + report[
            "warning_slope_surface_area_percent"
        ]
        + report[
            "critical_slope_surface_area_percent"
        ]
    )

    assert total_percent == pytest.approx(100.0)


def test_slope_area_distribution_is_area_weighted():
    report = AtlasReliefQualityReport.build(
        _unequal_triangle_relief(),
        warning_slope_degrees=50.0,
        critical_slope_degrees=60.0,
    )

    assert report[
        "critical_slope_surface_area_percent"
    ] > 50.0

    assert report[
        "safe_slope_surface_area_percent"
    ] < 50.0


def test_flat_surface_area_is_entirely_safe():
    relief = AtlasReliefMeshBuilder.build(
        [
            [0.5, 0.5],
            [0.5, 0.5],
        ],
        width_mm=2.0,
        depth_mm=1.0,
    )

    report = AtlasReliefQualityReport.build(
        relief
    )

    assert report[
        "classified_slope_triangle_count"
    ] == 2

    assert report[
        "classified_slope_surface_area_mm2"
    ] == pytest.approx(2.0)

    assert report[
        "safe_slope_surface_area_mm2"
    ] == pytest.approx(2.0)

    assert report[
        "warning_slope_surface_area_mm2"
    ] == pytest.approx(0.0)

    assert report[
        "critical_slope_surface_area_mm2"
    ] == pytest.approx(0.0)

    assert report[
        "safe_slope_surface_area_percent"
    ] == pytest.approx(100.0)


def test_missing_surface_analysis_has_no_area_distribution():
    relief = _unequal_triangle_relief()

    report = AtlasReliefQualityReport.build(
        {
            "type": relief["type"],
            "geometry_type": (
                relief["geometry_type"]
            ),
            "triangles": relief["triangles"],
        }
    )

    assert report[
        "classified_slope_triangle_count"
    ] == 0

    assert report[
        "classified_slope_surface_area_mm2"
    ] == pytest.approx(0.0)

    assert report[
        "safe_slope_surface_area_mm2"
    ] == pytest.approx(0.0)

    assert report[
        "warning_slope_surface_area_mm2"
    ] == pytest.approx(0.0)

    assert report[
        "critical_slope_surface_area_mm2"
    ] == pytest.approx(0.0)

    assert report[
        "safe_slope_surface_area_percent"
    ] is None

    assert report[
        "warning_slope_surface_area_percent"
    ] is None

    assert report[
        "critical_slope_surface_area_percent"
    ] is None
