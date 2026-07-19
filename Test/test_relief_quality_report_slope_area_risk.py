import pytest

from CORE.atlas_relief_mesh_builder import (
    AtlasReliefMeshBuilder,
)
from CORE.atlas_relief_quality_report import (
    AtlasReliefQualityReport,
)


def _cross_slope_relief():
    """
    Produces two planar top triangles whose true
    plane slope is about 54.7356 degrees.

    Horizontal, vertical and builder-diagonal edge
    samples are no steeper than 45 degrees. This
    isolates risk that can only be detected from
    the actual triangle planes.
    """
    return AtlasReliefMeshBuilder.build(
        [
            [0.5, 1.0],
            [0.0, 0.5],
        ],
        width_mm=1.0,
        depth_mm=1.0,
        relief_height_mm=2.0,
    )


def test_triangle_area_can_trigger_warning_when_edges_do_not():
    report = AtlasReliefQualityReport.build(
        _cross_slope_relief(),
        warning_slope_degrees=50.0,
        critical_slope_degrees=60.0,
    )

    assert report[
        "maximum_slope_degrees"
    ] == pytest.approx(45.0)

    assert report[
        "warning_slope_surface_area_percent"
    ] == pytest.approx(100.0)

    assert report["print_risk_status"] == "WARN"

    assert report["print_risk_issues"] == [
        {
            "severity": "WARN",
            "code": "steep_surface_slope_area",
            "value": pytest.approx(
                54.735610317245346
            ),
            "area_percent": pytest.approx(100.0),
            "area_mm2": pytest.approx(
                report[
                    "classified_slope_surface_area_mm2"
                ]
            ),
            "limit": 50.0,
        }
    ]


def test_triangle_area_can_trigger_failure_when_edges_do_not():
    report = AtlasReliefQualityReport.build(
        _cross_slope_relief(),
        warning_slope_degrees=50.0,
        critical_slope_degrees=52.0,
    )

    assert report[
        "maximum_slope_degrees"
    ] == pytest.approx(45.0)

    assert report[
        "critical_slope_surface_area_percent"
    ] == pytest.approx(100.0)

    assert report["print_risk_status"] == "FAIL"

    assert report["print_risk_issues"] == [
        {
            "severity": "FAIL",
            "code": "critical_surface_slope_area",
            "value": pytest.approx(
                54.735610317245346
            ),
            "area_percent": pytest.approx(100.0),
            "area_mm2": pytest.approx(
                report[
                    "classified_slope_surface_area_mm2"
                ]
            ),
            "limit": 52.0,
        }
    ]


def test_existing_maximum_slope_issue_is_not_duplicated():
    relief = AtlasReliefMeshBuilder.build(
        [
            [0.0, 1.0],
            [0.0, 1.0],
        ],
        width_mm=1.0,
        depth_mm=10.0,
        relief_height_mm=2.0,
    )

    report = AtlasReliefQualityReport.build(
        relief,
        warning_slope_degrees=50.0,
        critical_slope_degrees=80.0,
    )

    slope_issue_codes = [
        issue["code"]
        for issue in report["print_risk_issues"]
        if "slope" in issue["code"]
    ]

    assert slope_issue_codes == [
        "steep_surface_slope"
    ]


def test_missing_surface_analysis_does_not_add_area_issue():
    relief = _cross_slope_relief()

    report = AtlasReliefQualityReport.build(
        {
            "type": relief["type"],
            "geometry_type": relief["geometry_type"],
            "triangles": relief["triangles"],
        },
        warning_slope_degrees=50.0,
        critical_slope_degrees=60.0,
    )

    assert report["print_risk_status"] == "WARN"
    assert report["print_risk_issues"] == [
        {
            "severity": "WARN",
            "code": "surface_analysis_unavailable",
        }
    ]
