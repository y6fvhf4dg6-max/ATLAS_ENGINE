"""
ATLAS Input Quality Report Regression Tests

Ham OSM ve terrain girdilerinin ölçülebilir kalite metriklerini
tek bir raporda toplamasını doğrular.
"""

import pytest

from CORE.atlas_input_quality_report import (
    AtlasInputQualityReport,
)


def test_input_quality_report_calculates_objective_metrics():
    buildings = [
        {
            "id": 1,
            "geometry": [
                (0.0, 0.0),
                (0.0, 1.0),
                (1.0, 1.0),
                (1.0, 0.0),
            ],
            "tags": {
                "building": "yes",
                "height": "12",
                "roof:shape": "gable",
            },
        },
        {
            "id": 2,
            "geometry": [
                (0.0, 0.0),
                (0.0, 1.0),
                (0.0, 1.0),
                (1.0, 0.0),
            ],
            "tags": {
                "building": "yes",
            },
        },
    ]

    castles = [
        {
            "id": 10,
            "geometry_type": "relation",
            "geometry": [
                (2.0, 2.0),
                (2.0, 3.0),
                (3.0, 3.0),
                (3.0, 2.0),
            ],
            "tags": {
                "historic": "castle",
            },
        },
    ]

    castle_geometry = {
        "unknown_castles": [],
    }

    terrain_grid = {
        "sample_count": 100,
        "missing_sample_count": 5,
    }

    report = AtlasInputQualityReport.build(
        buildings=buildings,
        castles=castles,
        castle_geometry=castle_geometry,
        terrain_grid=terrain_grid,
    )

    assert report["geometry"]["total_count"] == 3
    assert report["geometry"]["valid_count"] == 2
    assert report["geometry"]["invalid_count"] == 1
    assert report["geometry"]["valid_percent"] == pytest.approx(
        66.6666667
    )

    assert report["semantics"]["building_count"] == 2
    assert report["semantics"]["height_coverage_percent"] == 50.0
    assert report["semantics"]["roof_coverage_percent"] == 50.0
    assert report["semantics"]["unknown_castle_count"] == 0

    assert report["terrain"]["sample_count"] == 100
    assert report["terrain"]["missing_sample_count"] == 5
    assert report["terrain"]["coverage_percent"] == 95.0


@pytest.mark.parametrize(
    (
        "valid_percent",
        "terrain_coverage_percent",
        "unknown_castle_count",
        "expected_risk",
        "expected_action",
    ),
    [
        (
            100.0,
            100.0,
            0,
            "LOW",
            "CONTINUE",
        ),
        (
            85.0,
            92.0,
            1,
            "MEDIUM",
            "WARN",
        ),
        (
            60.0,
            100.0,
            0,
            "HIGH",
            "FAIL",
        ),
        (
            100.0,
            70.0,
            0,
            "HIGH",
            "FAIL",
        ),
    ],
)
def test_input_quality_policy_classifies_risk_and_action(
    valid_percent,
    terrain_coverage_percent,
    unknown_castle_count,
    expected_risk,
    expected_action,
):
    report = {
        "geometry": {
            "valid_percent": valid_percent,
        },
        "semantics": {
            "unknown_castle_count": unknown_castle_count,
        },
        "terrain": {
            "coverage_percent": terrain_coverage_percent,
        },
    }

    result = AtlasInputQualityReport.evaluate_policy(
        report
    )

    assert result["risk_level"] == expected_risk
    assert result["action"] == expected_action


def test_input_quality_policy_warns_for_low_semantic_coverage():
    report = {
        "geometry": {
            "valid_percent": 100.0,
        },
        "semantics": {
            "unknown_castle_count": 0,
            "building_count": 100,
            "height_coverage_percent": 2.0,
            "roof_coverage_percent": 0.0,
        },
        "terrain": {
            "coverage_percent": 100.0,
        },
    }

    result = AtlasInputQualityReport.evaluate_policy(
        report
    )

    assert result["risk_level"] == "MEDIUM"
    assert result["action"] == "WARN"

    assert (
        "building_height_coverage_below_25"
        in result["reasons"]
    )

    assert (
        "building_roof_coverage_below_10"
        in result["reasons"]
    )
