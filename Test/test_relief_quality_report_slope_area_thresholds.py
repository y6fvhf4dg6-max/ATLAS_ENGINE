import pytest

from CORE.atlas_relief_mesh_builder import (
    AtlasReliefMeshBuilder,
)
from CORE.atlas_relief_quality_report import (
    AtlasReliefQualityReport,
)


def _localized_cross_slope(column_count=101):
    top_row = (
        [0.5, 1.0]
        + [0.5] * (column_count - 2)
    )
    bottom_row = (
        [0.0, 0.5]
        + [0.5] * (column_count - 2)
    )

    return AtlasReliefMeshBuilder.build(
        [
            top_row,
            bottom_row,
        ],
        width_mm=float(column_count - 1),
        depth_mm=1.0,
        relief_height_mm=2.0,
    )


def test_default_area_threshold_preserves_existing_warning():
    report = AtlasReliefQualityReport.build(
        _localized_cross_slope(),
        warning_slope_degrees=50.0,
        critical_slope_degrees=60.0,
    )

    assert report[
        "warning_slope_surface_area_percent"
    ] == pytest.approx(
        1.712421925177493
    )

    assert report["print_risk_status"] == "WARN"
    assert report["warning_slope_area_percent"] == 0.0
    assert report["critical_slope_area_percent"] == 0.0


def test_small_warning_area_can_be_ignored_by_threshold():
    report = AtlasReliefQualityReport.build(
        _localized_cross_slope(),
        warning_slope_degrees=50.0,
        critical_slope_degrees=60.0,
        warning_slope_area_percent=2.0,
    )

    assert report[
        "warning_slope_surface_area_percent"
    ] < 2.0

    assert report["print_risk_status"] == "PASS"
    assert report["print_risk_issue_count"] == 0
    assert report["warning_slope_area_percent"] == 2.0


def test_warning_area_equal_to_threshold_triggers_warning():
    baseline = AtlasReliefQualityReport.build(
        _localized_cross_slope(),
        warning_slope_degrees=50.0,
        critical_slope_degrees=60.0,
    )

    exact_threshold = baseline[
        "warning_slope_surface_area_percent"
    ]

    report = AtlasReliefQualityReport.build(
        _localized_cross_slope(),
        warning_slope_degrees=50.0,
        critical_slope_degrees=60.0,
        warning_slope_area_percent=exact_threshold,
    )

    assert report["print_risk_status"] == "WARN"
    assert report["print_risk_issues"][0][
        "code"
    ] == "steep_surface_slope_area"


def test_critical_area_has_independent_threshold():
    report = AtlasReliefQualityReport.build(
        _localized_cross_slope(),
        warning_slope_degrees=50.0,
        critical_slope_degrees=52.0,
        warning_slope_area_percent=90.0,
        critical_slope_area_percent=2.0,
    )

    assert report[
        "critical_slope_surface_area_percent"
    ] < 2.0

    assert report["print_risk_status"] == "PASS"
    assert report["print_risk_issue_count"] == 0


@pytest.mark.parametrize(
    "warning_area,critical_area",
    [
        (-0.1, 0.0),
        (100.1, 0.0),
        (0.0, -0.1),
        (0.0, 100.1),
        (float("nan"), 0.0),
        (0.0, float("inf")),
    ],
)
def test_rejects_invalid_area_thresholds(
    warning_area,
    critical_area,
):
    with pytest.raises(ValueError):
        AtlasReliefQualityReport.build(
            _localized_cross_slope(),
            warning_slope_area_percent=warning_area,
            critical_slope_area_percent=critical_area,
        )


def test_critical_area_equal_to_threshold_triggers_failure():
    baseline = AtlasReliefQualityReport.build(
        _localized_cross_slope(),
        warning_slope_degrees=50.0,
        critical_slope_degrees=52.0,
    )

    exact_threshold = baseline[
        "critical_slope_surface_area_percent"
    ]

    report = AtlasReliefQualityReport.build(
        _localized_cross_slope(),
        warning_slope_degrees=50.0,
        critical_slope_degrees=52.0,
        warning_slope_area_percent=100.0,
        critical_slope_area_percent=exact_threshold,
    )

    assert report["print_risk_status"] == "FAIL"
    assert report["print_risk_issues"][0][
        "code"
    ] == "critical_surface_slope_area"
