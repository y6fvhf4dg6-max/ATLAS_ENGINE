import pytest

from CORE.atlas_relief_mesh_builder import (
    AtlasReliefMeshBuilder,
)
from CORE.atlas_relief_quality_report import (
    AtlasReliefQualityReport,
)


def _relief():
    return AtlasReliefMeshBuilder.build(
        [
            [0.0, 0.5, 1.0],
            [0.25, 0.75, 0.5],
            [0.0, 0.25, 1.0],
        ],
        width_mm=20.0,
        depth_mm=10.0,
        base_thickness_mm=0.8,
        relief_height_mm=2.0,
        origin_x=3.0,
        origin_y=4.0,
        origin_z=1.0,
    )


def test_report_contains_topology_result():
    report = AtlasReliefQualityReport.build(
        _relief()
    )

    assert report["open_edge_count"] == 0
    assert (
        report["non_manifold_edge_count"]
        == 0
    )
    assert report["is_closed"] is True
    assert report["is_manifold"] is True
    assert (
        report["is_printable_topology"]
        is True
    )


def test_report_contains_dimensions():
    report = AtlasReliefQualityReport.build(
        _relief()
    )

    assert report["width_mm"] == pytest.approx(
        20.0
    )
    assert report["depth_mm"] == pytest.approx(
        10.0
    )
    assert report[
        "total_height_mm"
    ] == pytest.approx(2.8)


def test_report_contains_coordinate_bounds():
    report = AtlasReliefQualityReport.build(
        _relief()
    )

    assert report["minimum_x"] == pytest.approx(
        3.0
    )
    assert report["maximum_x"] == pytest.approx(
        23.0
    )
    assert report["minimum_y"] == pytest.approx(
        4.0
    )
    assert report["maximum_y"] == pytest.approx(
        14.0
    )
    assert report["minimum_z"] == pytest.approx(
        1.0
    )
    assert report["maximum_z"] == pytest.approx(
        3.8
    )


def test_report_triangle_count_matches_mesh():
    relief = _relief()

    report = AtlasReliefQualityReport.build(
        relief
    )

    assert report["triangle_count"] == len(
        relief["triangles"]
    )


def test_report_preserves_geometry_type():
    report = AtlasReliefQualityReport.build(
        _relief()
    )

    assert report["geometry_type"] == (
        "height_map_relief"
    )


@pytest.mark.parametrize(
    "invalid_mesh",
    [
        None,
        [],
        {},
        {"triangles": None},
        {"triangles": []},
    ],
)
def test_report_rejects_invalid_mesh(
    invalid_mesh,
):
    with pytest.raises(ValueError):
        AtlasReliefQualityReport.build(
            invalid_mesh
        )


def test_report_rejects_non_finite_vertex():
    mesh = {
        "triangles": [
            (
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (0.0, 1.0, float("nan")),
            ),
        ],
    }

    with pytest.raises(ValueError):
        AtlasReliefQualityReport.build(mesh)


def test_report_contains_surface_sampling_metrics():
    report = AtlasReliefQualityReport.build(
        _relief()
    )

    assert report[
        "surface_analysis_available"
    ] is True

    assert report[
        "sample_spacing_x_mm"
    ] == pytest.approx(10.0)

    assert report[
        "sample_spacing_y_mm"
    ] == pytest.approx(5.0)

    assert report["surface_edge_count"] == 16


def test_report_contains_slope_metrics():
    report = AtlasReliefQualityReport.build(
        _relief()
    )

    assert report[
        "maximum_adjacent_rise_mm"
    ] == pytest.approx(1.5)

    assert (
        0.0
        < report["average_slope_degrees"]
        <= report["maximum_slope_degrees"]
        < 90.0
    )


def test_flat_relief_has_zero_surface_slope():
    relief = AtlasReliefMeshBuilder.build(
        [
            [0.5, 0.5],
            [0.5, 0.5],
        ],
        width_mm=10.0,
        depth_mm=8.0,
        base_thickness_mm=0.8,
        relief_height_mm=2.0,
    )

    report = AtlasReliefQualityReport.build(
        relief
    )

    assert report[
        "maximum_adjacent_rise_mm"
    ] == pytest.approx(0.0)

    assert report[
        "maximum_slope_degrees"
    ] == pytest.approx(0.0)

    assert report[
        "average_slope_degrees"
    ] == pytest.approx(0.0)


def test_report_without_top_grid_marks_analysis_unavailable():
    relief = _relief()

    triangle_only_mesh = {
        "type": relief["type"],
        "geometry_type": (
            relief["geometry_type"]
        ),
        "triangles": relief["triangles"],
    }

    report = AtlasReliefQualityReport.build(
        triangle_only_mesh
    )

    assert report[
        "surface_analysis_available"
    ] is False

    assert report[
        "maximum_slope_degrees"
    ] is None

    assert report["surface_edge_count"] == 0


def test_surface_analysis_is_deterministic():
    first = AtlasReliefQualityReport.build(
        _relief()
    )

    second = AtlasReliefQualityReport.build(
        _relief()
    )

    assert first == second


def test_report_rejects_irregular_top_grid():
    relief = _relief()

    relief["top_grid"][1] = relief[
        "top_grid"
    ][1][:-1]

    with pytest.raises(ValueError):
        AtlasReliefQualityReport.build(
            relief
        )


def test_flat_relief_print_risk_passes():
    relief = AtlasReliefMeshBuilder.build(
        [
            [0.5, 0.5],
            [0.5, 0.5],
        ],
        width_mm=10.0,
        depth_mm=10.0,
    )

    report = AtlasReliefQualityReport.build(
        relief
    )

    assert report[
        "print_risk_status"
    ] == "PASS"

    assert report[
        "print_risk_issue_count"
    ] == 0


def test_steep_relief_print_risk_warns():
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

    assert report[
        "print_risk_status"
    ] == "WARN"

    assert report[
        "print_risk_issues"
    ][0]["code"] == "steep_surface_slope"


def test_critical_relief_slope_fails():
    relief = AtlasReliefMeshBuilder.build(
        [
            [0.0, 1.0],
            [0.0, 1.0],
        ],
        width_mm=0.2,
        depth_mm=10.0,
        relief_height_mm=2.0,
    )

    report = AtlasReliefQualityReport.build(
        relief,
        warning_slope_degrees=50.0,
        critical_slope_degrees=80.0,
    )

    assert report[
        "print_risk_status"
    ] == "FAIL"

    assert report[
        "print_risk_issues"
    ][0]["code"] == (
        "critical_surface_slope"
    )


def test_missing_surface_analysis_warns():
    relief = _relief()

    triangle_only_mesh = {
        "type": relief["type"],
        "geometry_type": (
            relief["geometry_type"]
        ),
        "triangles": relief["triangles"],
    }

    report = AtlasReliefQualityReport.build(
        triangle_only_mesh
    )

    assert report[
        "print_risk_status"
    ] == "WARN"

    assert report[
        "print_risk_issues"
    ][0]["code"] == (
        "surface_analysis_unavailable"
    )


@pytest.mark.parametrize(
    "warning,critical",
    [
        (-1.0, 75.0),
        (90.0, 95.0),
        (55.0, 0.0),
        (55.0, 90.0),
        (75.0, 55.0),
        (55.0, 55.0),
        (float("nan"), 75.0),
        (55.0, float("inf")),
    ],
)
def test_print_risk_rejects_invalid_thresholds(
    warning,
    critical,
):
    with pytest.raises(ValueError):
        AtlasReliefQualityReport.build(
            _relief(),
            warning_slope_degrees=warning,
            critical_slope_degrees=critical,
        )
