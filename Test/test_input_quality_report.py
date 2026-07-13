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


def test_enforce_policy_allows_warn_and_blocks_fail():
    warn_policy = {
        "risk_level": "MEDIUM",
        "action": "WARN",
        "reasons": [
            "building_height_coverage_below_25",
        ],
    }

    fail_policy = {
        "risk_level": "HIGH",
        "action": "FAIL",
        "reasons": [
            "terrain_coverage_percent_below_80",
        ],
    }

    assert (
        AtlasInputQualityReport.enforce_policy(
            policy=warn_policy,
            strict=True,
        )
        is None
    )

    with pytest.raises(
        RuntimeError,
        match="Input quality policy failed",
    ):
        AtlasInputQualityReport.enforce_policy(
            policy=fail_policy,
            strict=True,
        )

    assert (
        AtlasInputQualityReport.enforce_policy(
            policy=fail_policy,
            strict=False,
        )
        is None
    )


def test_input_quality_report_records_automatic_corrections():
    report = AtlasInputQualityReport.build(
        buildings=[],
        castles=[],
        castle_geometry={
            "unknown_castles": [],
            "inferred_perimeter_walls": [
                {"id": 10},
                {"id": 11},
            ],
        },
        terrain_grid={
            "sample_count": 100,
            "missing_sample_count": 5,
        },
        castle_focus_result={
            "used_fallback": True,
        },
    )

    corrections = report["automatic_corrections"]

    assert corrections["terrain_missing_samples_filled"] == 5
    assert corrections["inferred_perimeter_walls"] == 2
    assert corrections["castle_focus_fallback_used"] is True
    assert corrections["total_count"] == 8


def test_input_quality_report_adds_corrected_castle_roles():
    report = {
        "automatic_corrections": {
            "terrain_missing_samples_filled": 2,
            "inferred_perimeter_walls": 1,
            "castle_focus_fallback_used": False,
            "total_count": 3,
        },
    }

    shell_meshes = [
        {
            "roles_corrected": True,
        },
        {
            "roles_corrected": False,
        },
        {
            "roles_corrected": True,
        },
    ]

    AtlasInputQualityReport.add_shell_corrections(
        report=report,
        shell_meshes=shell_meshes,
    )

    corrections = report["automatic_corrections"]

    assert corrections["castle_relation_roles_corrected"] == 2
    assert corrections["total_count"] == 5


def test_input_quality_report_classifies_geometry_issues():
    buildings = [
        {
            "id": 1,
            "geometry": [
                (0.0, 0.0),
                (0.0, 1.0),
                (1.0, 1.0),
                (1.0, 0.0),
            ],
        },
        {
            "id": 2,
            "geometry": [
                (0.0, 0.0),
                (1.0, 1.0),
            ],
        },
        {
            "id": 3,
            "geometry": [
                (0.0, 0.0),
                (0.0, 1.0),
                (0.0, 1.0),
                (1.0, 0.0),
            ],
        },
        {
            "id": 4,
            "geometry": [
                (0.0, 0.0),
                (1.0, 1.0),
                (2.0, 2.0),
            ],
        },
        {
            "id": 5,
            "geometry": [
                (0.0, 0.0),
                (1.0, 1.0),
                (0.0, 1.0),
                (1.0, 0.0),
            ],
        },
    ]

    report = AtlasInputQualityReport.build(
        buildings=buildings,
        castles=[],
        castle_geometry={
            "unknown_castles": [],
        },
        terrain_grid={
            "sample_count": 1,
            "missing_sample_count": 0,
        },
    )

    issues = report["geometry"]["issue_counts"]

    assert issues["valid"] == 1
    assert issues["not_enough_points"] == 1
    assert issues["duplicate_points"] == 1
    assert issues["zero_area"] == 1
    assert issues["self_intersection"] == 1


def test_input_quality_report_classifies_semantic_issues():
    buildings = [
        {
            "id": 1,
            "geometry": [
                (0.0, 0.0),
                (0.0, 1.0),
                (1.0, 1.0),
            ],
            "tags": {
                "building": "yes",
                "height": "abc",
                "building:levels": "3",
                "roof:shape": "gable",
            },
        },
        {
            "id": 2,
            "geometry": [
                (2.0, 2.0),
                (2.0, 3.0),
                (3.0, 3.0),
            ],
            "tags": {
                "building": "yes",
                "height": "-5",
                "building:levels": "0",
                "roof:shape": "mystery_roof",
            },
        },
        {
            "id": 3,
            "geometry": [
                (4.0, 4.0),
                (4.0, 5.0),
                (5.0, 5.0),
            ],
            "tags": {
                "building": "yes",
                "height": "12 m",
                "building:levels": "three",
                "roof:shape": "hipped",
            },
        },
    ]

    report = AtlasInputQualityReport.build(
        buildings=buildings,
        castles=[],
        castle_geometry={
            "unknown_castles": [],
        },
        terrain_grid={
            "sample_count": 1,
            "missing_sample_count": 0,
        },
    )

    issues = report["semantics"]["issue_counts"]

    assert issues["invalid_height"] == 1
    assert issues["non_positive_height"] == 1
    assert issues["invalid_levels"] == 1
    assert issues["non_positive_levels"] == 1
    assert issues["unknown_roof_shape"] == 1


def test_input_quality_report_classifies_castle_semantic_issues():
    castles = [
        {
            "id": 1,
            "geometry_type": "relation",
            "geometry": [],
            "outer_geometries": [],
            "inner_geometries": [],
            "tags": {
                "historic": "castle",
            },
        },
        {
            "id": 2,
            "geometry_type": "way",
            "geometry": [
                (0.0, 0.0),
                (0.0, 1.0),
                (1.0, 1.0),
            ],
            "outer_geometries": [],
            "inner_geometries": [
                [
                    (0.2, 0.2),
                    (0.2, 0.4),
                    (0.4, 0.4),
                ],
            ],
            "tags": {
                "historic": "castle",
            },
        },
        {
            "id": 3,
            "geometry_type": "collection",
            "geometry": [
                (2.0, 2.0),
                (2.0, 3.0),
                (3.0, 3.0),
            ],
            "outer_geometries": [],
            "inner_geometries": [],
            "tags": {
                "historic": "castle",
            },
        },
        {
            "id": 4,
            "geometry_type": "way",
            "geometry": [
                (4.0, 4.0),
                (4.0, 5.0),
                (5.0, 5.0),
            ],
            "outer_geometries": [],
            "inner_geometries": [],
            "tags": {
                "tourism": "attraction",
            },
        },
    ]

    report = AtlasInputQualityReport.build(
        buildings=[],
        castles=castles,
        castle_geometry={
            "unknown_castles": [],
        },
        terrain_grid={
            "sample_count": 1,
            "missing_sample_count": 0,
        },
    )

    issues = report["semantics"]["issue_counts"]

    assert issues["relation_missing_outer_geometry"] == 1
    assert issues["way_has_inner_geometry"] == 1
    assert issues["unsupported_castle_geometry_type"] == 1
    assert issues["missing_castle_tag"] == 1


def test_input_quality_policy_fails_for_structural_castle_semantic_issues():
    report = {
        "geometry": {
            "valid_percent": 100.0,
        },
        "semantics": {
            "building_count": 0,
            "height_coverage_percent": 100.0,
            "roof_coverage_percent": 100.0,
            "unknown_castle_count": 0,
            "issue_counts": {
                "invalid_height": 0,
                "non_positive_height": 0,
                "invalid_levels": 0,
                "non_positive_levels": 0,
                "unknown_roof_shape": 0,
                "relation_missing_outer_geometry": 1,
                "way_has_inner_geometry": 0,
                "unsupported_castle_geometry_type": 0,
                "missing_castle_tag": 0,
            },
        },
        "terrain": {
            "coverage_percent": 100.0,
        },
    }

    policy = AtlasInputQualityReport.evaluate_policy(
        report
    )

    assert policy["risk_level"] == "HIGH"
    assert policy["action"] == "FAIL"
    assert (
        "castle_relation_missing_outer_geometry"
        in policy["reasons"]
    )


def test_input_quality_policy_warns_for_non_structural_semantic_issues():
    report = {
        "geometry": {
            "valid_percent": 100.0,
        },
        "semantics": {
            "building_count": 1,
            "height_coverage_percent": 100.0,
            "roof_coverage_percent": 100.0,
            "unknown_castle_count": 0,
            "issue_counts": {
                "invalid_height": 1,
                "non_positive_height": 0,
                "invalid_levels": 0,
                "non_positive_levels": 0,
                "unknown_roof_shape": 0,
                "relation_missing_outer_geometry": 0,
                "way_has_inner_geometry": 0,
                "unsupported_castle_geometry_type": 0,
                "missing_castle_tag": 1,
            },
        },
        "terrain": {
            "coverage_percent": 100.0,
        },
    }

    policy = AtlasInputQualityReport.evaluate_policy(
        report
    )

    assert policy["risk_level"] == "MEDIUM"
    assert policy["action"] == "WARN"
    assert "invalid_building_height_present" in policy["reasons"]
    assert "castle_record_missing_tag" in policy["reasons"]


def test_strict_input_quality_rejects_structural_castle_semantic_failure():
    report = {
        "geometry": {
            "valid_percent": 100.0,
        },
        "semantics": {
            "building_count": 0,
            "height_coverage_percent": 100.0,
            "roof_coverage_percent": 100.0,
            "unknown_castle_count": 0,
            "issue_counts": {
                "invalid_height": 0,
                "non_positive_height": 0,
                "invalid_levels": 0,
                "non_positive_levels": 0,
                "unknown_roof_shape": 0,
                "relation_missing_outer_geometry": 0,
                "way_has_inner_geometry": 1,
                "unsupported_castle_geometry_type": 0,
                "missing_castle_tag": 0,
            },
        },
        "terrain": {
            "coverage_percent": 100.0,
        },
    }

    policy = AtlasInputQualityReport.evaluate_policy(
        report
    )

    try:
        AtlasInputQualityReport.enforce_policy(
            policy,
            strict=True,
        )
    except RuntimeError as error:
        assert (
            "castle_way_has_inner_geometry"
            in str(error)
        )
    else:
        raise AssertionError(
            "Strict input quality did not reject "
            "structural castle semantic failure."
        )


def test_non_strict_input_quality_allows_structural_castle_semantic_failure():
    policy = {
        "risk_level": "HIGH",
        "action": "FAIL",
        "reasons": [
            "castle_relation_missing_outer_geometry",
        ],
    }

    AtlasInputQualityReport.enforce_policy(
        policy,
        strict=False,
    )


def test_semantic_coverage_excludes_invalid_values():
    buildings = [
        {
            "id": 1,
            "geometry": [
                (0.0, 0.0),
                (0.0, 1.0),
                (1.0, 1.0),
            ],
            "tags": {
                "building": "yes",
                "height": "abc",
                "roof:shape": "mystery_roof",
            },
        },
        {
            "id": 2,
            "geometry": [
                (2.0, 2.0),
                (2.0, 3.0),
                (3.0, 3.0),
            ],
            "tags": {
                "building": "yes",
                "building:levels": "0",
                "roof:shape": "gable",
            },
        },
        {
            "id": 3,
            "geometry": [
                (4.0, 4.0),
                (4.0, 5.0),
                (5.0, 5.0),
            ],
            "tags": {
                "building": "yes",
                "height": "12 m",
                "roof:shape": "hipped",
            },
        },
    ]

    report = AtlasInputQualityReport.build(
        buildings=buildings,
        castles=[],
        castle_geometry={
            "unknown_castles": [],
        },
        terrain_grid={
            "sample_count": 1,
            "missing_sample_count": 0,
        },
    )

    semantics = report["semantics"]

    assert semantics["height_count"] == 1
    assert abs(
        semantics["height_coverage_percent"]
        - (100.0 / 3.0)
    ) < 1e-9

    assert semantics["roof_count"] == 2
    assert abs(
        semantics["roof_coverage_percent"]
        - (200.0 / 3.0)
    ) < 1e-9


def test_semantic_issues_include_direct_building_fields():
    buildings = [
        {
            "id": 1,
            "geometry": [
                (0.0, 0.0),
                (0.0, 1.0),
                (1.0, 1.0),
            ],
            "height": "abc",
            "roof_type": "mystery_roof",
            "tags": {
                "building": "yes",
            },
        },
        {
            "id": 2,
            "geometry": [
                (2.0, 2.0),
                (2.0, 3.0),
                (3.0, 3.0),
            ],
            "height": -4.0,
            "roof_type": "gable",
            "tags": {
                "building": "yes",
            },
        },
    ]

    report = AtlasInputQualityReport.build(
        buildings=buildings,
        castles=[],
        castle_geometry={
            "unknown_castles": [],
        },
        terrain_grid={
            "sample_count": 1,
            "missing_sample_count": 0,
        },
    )

    issues = report["semantics"]["issue_counts"]

    assert issues["invalid_height"] == 1
    assert issues["non_positive_height"] == 1
    assert issues["unknown_roof_shape"] == 1

    assert report["semantics"]["height_count"] == 0
    assert report["semantics"]["roof_count"] == 1


def test_semantic_issues_detect_conflicting_direct_and_tag_values():
    buildings = [
        {
            "id": 1,
            "geometry": [
                (0.0, 0.0),
                (0.0, 1.0),
                (1.0, 1.0),
            ],
            "height": 10.0,
            "roof_type": "gable",
            "tags": {
                "building": "yes",
                "height": "12 m",
                "roof:shape": "hipped",
            },
        },
        {
            "id": 2,
            "geometry": [
                (2.0, 2.0),
                (2.0, 3.0),
                (3.0, 3.0),
            ],
            "height": 8.0,
            "roof_type": "flat",
            "tags": {
                "building": "yes",
                "height": "8 m",
                "roof:shape": "flat",
            },
        },
    ]

    report = AtlasInputQualityReport.build(
        buildings=buildings,
        castles=[],
        castle_geometry={
            "unknown_castles": [],
        },
        terrain_grid={
            "sample_count": 1,
            "missing_sample_count": 0,
        },
    )

    issues = report["semantics"]["issue_counts"]

    assert issues["conflicting_height_values"] == 1
    assert issues["conflicting_roof_shapes"] == 1


def test_input_quality_policy_warns_for_conflicting_semantic_values():
    report = {
        "geometry": {
            "valid_percent": 100.0,
        },
        "semantics": {
            "building_count": 2,
            "height_coverage_percent": 100.0,
            "roof_coverage_percent": 100.0,
            "unknown_castle_count": 0,
            "issue_counts": {
                "invalid_height": 0,
                "non_positive_height": 0,
                "invalid_levels": 0,
                "non_positive_levels": 0,
                "unknown_roof_shape": 0,
                "conflicting_height_values": 1,
                "conflicting_roof_shapes": 1,
                "relation_missing_outer_geometry": 0,
                "way_has_inner_geometry": 0,
                "unsupported_castle_geometry_type": 0,
                "missing_castle_tag": 0,
            },
        },
        "terrain": {
            "coverage_percent": 100.0,
        },
    }

    policy = AtlasInputQualityReport.evaluate_policy(
        report
    )

    assert policy["risk_level"] == "MEDIUM"
    assert policy["action"] == "WARN"
    assert (
        "conflicting_building_height_values_present"
        in policy["reasons"]
    )
    assert (
        "conflicting_building_roof_shapes_present"
        in policy["reasons"]
    )


def test_osm_cone_roof_is_known_and_many_roof_is_complex():
    buildings = [
        {
            "id": 1,
            "geometry": [
                (0.0, 0.0),
                (0.0, 1.0),
                (1.0, 1.0),
            ],
            "tags": {
                "building": "tower",
                "roof:shape": "cone",
            },
        },
        {
            "id": 2,
            "geometry": [
                (2.0, 2.0),
                (2.0, 3.0),
                (3.0, 3.0),
            ],
            "tags": {
                "building": "yes",
                "roof:shape": "many",
            },
        },
    ]

    report = AtlasInputQualityReport.build(
        buildings=buildings,
        castles=[],
        castle_geometry={
            "unknown_castles": [],
        },
        terrain_grid={
            "sample_count": 1,
            "missing_sample_count": 0,
        },
    )

    semantics = report["semantics"]
    issues = semantics["issue_counts"]

    assert issues["unknown_roof_shape"] == 0
    assert issues["complex_roof_shape"] == 1

    assert semantics["roof_count"] == 2
    assert semantics["roof_coverage_percent"] == 100.0


def test_input_quality_report_records_semantic_issue_details():
    buildings = [
        {
            "id": 101,
            "geometry": [
                (0.0, 0.0),
                (0.0, 1.0),
                (1.0, 1.0),
            ],
            "tags": {
                "building": "yes",
                "height": "abc",
                "roof:shape": "many",
            },
        },
    ]

    castles = [
        {
            "id": 202,
            "geometry_type": "way",
            "geometry": [
                (2.0, 2.0),
                (2.0, 3.0),
                (3.0, 3.0),
            ],
            "outer_geometries": [],
            "inner_geometries": [],
            "tags": {
                "tourism": "attraction",
            },
        },
    ]

    report = AtlasInputQualityReport.build(
        buildings=buildings,
        castles=castles,
        castle_geometry={
            "unknown_castles": [],
        },
        terrain_grid={
            "sample_count": 1,
            "missing_sample_count": 0,
        },
    )

    records = report["semantics"]["issue_records"]

    assert records["invalid_height"] == [
        {
            "record_type": "building",
            "id": 101,
            "field": "height",
            "value": "abc",
        },
    ]

    assert records["complex_roof_shape"] == [
        {
            "record_type": "building",
            "id": 101,
            "field": "roof:shape",
            "value": "many",
        },
    ]

    assert records["missing_castle_tag"] == [
        {
            "record_type": "castle",
            "id": 202,
            "field": "historic/building",
            "value": None,
        },
    ]
