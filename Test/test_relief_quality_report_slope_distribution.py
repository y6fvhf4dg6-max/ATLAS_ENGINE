import pytest

from CORE.atlas_relief_mesh_builder import (
    AtlasReliefMeshBuilder,
)
from CORE.atlas_relief_quality_report import (
    AtlasReliefQualityReport,
)


def _mixed_slope_relief():
    return AtlasReliefMeshBuilder.build(
        [
            [0.0, 0.0, 1.0],
            [0.0, 0.5, 1.0],
        ],
        width_mm=2.0,
        depth_mm=1.0,
        relief_height_mm=2.0,
    )


def test_report_contains_slope_distribution_counts():
    report = AtlasReliefQualityReport.build(
        _mixed_slope_relief(),
        warning_slope_degrees=40.0,
        critical_slope_degrees=60.0,
    )

    assert report[
        "safe_slope_sample_count"
    ] == 4

    assert report[
        "warning_slope_sample_count"
    ] == 4

    assert report[
        "critical_slope_sample_count"
    ] == 1

    assert report[
        "classified_slope_sample_count"
    ] == 9


def test_slope_distribution_percentages_sum_to_one_hundred():
    report = AtlasReliefQualityReport.build(
        _mixed_slope_relief(),
        warning_slope_degrees=40.0,
        critical_slope_degrees=60.0,
    )

    total = (
        report["safe_slope_sample_percent"]
        + report[
            "warning_slope_sample_percent"
        ]
        + report[
            "critical_slope_sample_percent"
        ]
    )

    assert total == pytest.approx(100.0)


def test_slope_distribution_uses_active_thresholds():
    lower_threshold_report = (
        AtlasReliefQualityReport.build(
            _mixed_slope_relief(),
            warning_slope_degrees=20.0,
            critical_slope_degrees=50.0,
        )
    )

    higher_threshold_report = (
        AtlasReliefQualityReport.build(
            _mixed_slope_relief(),
            warning_slope_degrees=50.0,
            critical_slope_degrees=80.0,
        )
    )

    assert lower_threshold_report[
        "critical_slope_sample_count"
    ] > higher_threshold_report[
        "critical_slope_sample_count"
    ]

    assert lower_threshold_report[
        "safe_slope_sample_count"
    ] < higher_threshold_report[
        "safe_slope_sample_count"
    ]


def test_flat_surface_distribution_is_entirely_safe():
    relief = AtlasReliefMeshBuilder.build(
        [
            [0.5, 0.5],
            [0.5, 0.5],
        ],
        width_mm=1.0,
        depth_mm=1.0,
    )

    report = AtlasReliefQualityReport.build(
        relief
    )

    assert report[
        "safe_slope_sample_count"
    ] == 5
    assert report[
        "warning_slope_sample_count"
    ] == 0
    assert report[
        "critical_slope_sample_count"
    ] == 0
    assert report[
        "safe_slope_sample_percent"
    ] == pytest.approx(100.0)


def test_missing_surface_analysis_has_no_distribution():
    relief = _mixed_slope_relief()

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
        "classified_slope_sample_count"
    ] == 0
    assert report[
        "safe_slope_sample_count"
    ] == 0
    assert report[
        "warning_slope_sample_count"
    ] == 0
    assert report[
        "critical_slope_sample_count"
    ] == 0
    assert report[
        "safe_slope_sample_percent"
    ] is None
    assert report[
        "warning_slope_sample_percent"
    ] is None
    assert report[
        "critical_slope_sample_percent"
    ] is None
