import copy

import numpy as np
import pytest

from CORE.atlas_architectural_relief_mesh_producer import (
    AtlasArchitecturalReliefMeshProducer,
)
from CORE.atlas_architectural_relief_physical_profile import (
    AtlasArchitecturalReliefPhysicalProfile,
)
from CORE.atlas_architectural_relief_quality_report import (
    AtlasArchitecturalReliefQualityReport,
)
from CORE.atlas_relief_risk_profile import (
    AtlasReliefRiskProfile,
)


def _production(
    height_map=None,
):
    if height_map is None:
        height_map = np.full(
            (3, 3),
            0.5,
            dtype=np.float64,
        )

    return (
        AtlasArchitecturalReliefMeshProducer
        .build(
            height_map=height_map,
            width_mm=8.0,
            depth_mm=4.0,
            physical_profile=(
                AtlasArchitecturalReliefPhysicalProfile(
                    name="architectural-premium-v1",
                    base_thickness_mm=1.0,
                    relief_height_mm=2.0,
                    target_sample_spacing_mm=2.0,
                )
            ),
        )
    )


def test_builds_pass_report_for_valid_production():
    production = _production()

    report = (
        AtlasArchitecturalReliefQualityReport
        .build(
            production,
            risk_profile=(
                AtlasReliefRiskProfile(
                    name="architectural-safe",
                    warning_slope_degrees=55.0,
                    critical_slope_degrees=75.0,
                )
            ),
        )
    )

    assert report["type"] == (
        "architectural_relief_quality_report"
    )
    assert report["status"] == "PASS"
    assert report["is_print_ready"] is True
    assert report["issue_count"] == 0
    assert report["issues"] == ()
    assert report["risk_profile_name"] == (
        "architectural-safe"
    )


def test_embeds_general_relief_quality_report():
    report = (
        AtlasArchitecturalReliefQualityReport
        .build(
            _production()
        )
    )

    general = report[
        "general_quality_report"
    ]

    assert general[
        "is_printable_topology"
    ] is True
    assert general["open_edge_count"] == 0
    assert (
        general["non_manifold_edge_count"]
        == 0
    )
    assert general["width_mm"] == pytest.approx(
        8.0
    )
    assert general["depth_mm"] == pytest.approx(
        4.0
    )
    assert general[
        "total_height_mm"
    ] == pytest.approx(2.0)


def test_reports_physical_plan_consistency():
    production = _production()

    report = (
        AtlasArchitecturalReliefQualityReport
        .build(
            production
        )
    )

    assert report[
        "physical_dimensions_match"
    ] is True
    assert report[
        "total_height_matches"
    ] is True
    assert report[
        "triangle_count_matches"
    ] is True
    assert report["expected_triangle_count"] == (
        production["expected_triangle_count"]
    )
    assert report["actual_triangle_count"] == (
        production["triangle_count"]
    )


def test_general_warning_becomes_architectural_warning():
    production = _production(
        np.array(
            [
                [0.0, 1.0],
                [0.0, 1.0],
            ],
            dtype=np.float64,
        )
    )

    report = (
        AtlasArchitecturalReliefQualityReport
        .build(
            production,
            risk_profile=(
                AtlasReliefRiskProfile(
                    warning_slope_degrees=10.0,
                    critical_slope_degrees=80.0,
                )
            ),
        )
    )

    assert report["status"] == "WARN"
    assert report["is_print_ready"] is False
    assert any(
        issue["code"]
        in {
            "steep_surface_slope",
            "steep_surface_slope_area",
        }
        for issue in report["issues"]
    )


def test_triangle_count_mismatch_fails():
    production = _production()
    production = copy.deepcopy(
        production
    )
    production[
        "expected_triangle_count"
    ] += 2

    report = (
        AtlasArchitecturalReliefQualityReport
        .build(
            production
        )
    )

    assert report["status"] == "FAIL"
    assert report[
        "triangle_count_matches"
    ] is False
    assert {
        issue["code"]
        for issue in report["issues"]
    } >= {
        "architectural_triangle_count_mismatch"
    }


def test_physical_dimension_mismatch_fails():
    production = _production()
    production = copy.deepcopy(
        production
    )
    production["physical_plan"][
        "width_mm"
    ] = 9.0

    report = (
        AtlasArchitecturalReliefQualityReport
        .build(
            production
        )
    )

    assert report["status"] == "FAIL"
    assert report[
        "physical_dimensions_match"
    ] is False
    assert {
        issue["code"]
        for issue in report["issues"]
    } >= {
        "architectural_physical_dimension_mismatch"
    }


def test_total_height_mismatch_fails():
    production = _production()
    production = copy.deepcopy(
        production
    )
    production["physical_plan"][
        "total_height_mm"
    ] = 1.5

    report = (
        AtlasArchitecturalReliefQualityReport
        .build(
            production
        )
    )

    assert report["status"] == "FAIL"
    assert report[
        "total_height_matches"
    ] is False
    assert {
        issue["code"]
        for issue in report["issues"]
    } >= {
        "architectural_total_height_mismatch"
    }


def test_rejects_invalid_production_contract():
    with pytest.raises(
        ValueError,
        match="mesh_production",
    ):
        AtlasArchitecturalReliefQualityReport.build(
            {}
        )


def test_rejects_invalid_risk_profile_type():
    with pytest.raises(
        TypeError,
        match="risk_profile",
    ):
        AtlasArchitecturalReliefQualityReport.build(
            _production(),
            risk_profile=object(),
        )


def test_report_does_not_mutate_production():
    production = _production()
    triangle_count_before = len(
        production["mesh"]["triangles"]
    )
    plan_before = dict(
        production["physical_plan"]
    )

    AtlasArchitecturalReliefQualityReport.build(
        production
    )

    assert len(
        production["mesh"]["triangles"]
    ) == triangle_count_before
    assert production["physical_plan"][
        "width_mm"
    ] == plan_before["width_mm"]
    assert production["physical_plan"][
        "depth_mm"
    ] == plan_before["depth_mm"]
    assert production["physical_plan"][
        "total_height_mm"
    ] == plan_before["total_height_mm"]
