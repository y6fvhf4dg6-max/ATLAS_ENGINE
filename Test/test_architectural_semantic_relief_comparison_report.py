import pytest

from CORE.atlas_architectural_semantic_relief_comparison_report import (
    AtlasArchitecturalSemanticReliefComparisonReport,
)


def test_semantic_relief_comparison_passes_when_semantic_readability_improves():
    report = AtlasArchitecturalSemanticReliefComparisonReport.build(
        baseline={
            "feature_readability_score": 0.42,
        },
        semantic={
            "feature_readability_score": 0.78,
        },
    )

    assert report["type"] == (
        "architectural_semantic_relief_comparison_report"
    )
    assert report["baseline_feature_readability_score"] == 0.42
    assert report["semantic_feature_readability_score"] == 0.78
    assert report["readability_delta"] == pytest.approx(0.36)
    assert report["semantic_more_readable"] is True
    assert report["status"] == "PASS"


def test_semantic_relief_comparison_fails_without_improvement():
    report = AtlasArchitecturalSemanticReliefComparisonReport.build(
        baseline={
            "feature_readability_score": 0.70,
        },
        semantic={
            "feature_readability_score": 0.70,
        },
    )

    assert report["readability_delta"] == 0.0
    assert report["semantic_more_readable"] is False
    assert report["status"] == "FAIL"


def test_feature_retention_score_is_derived_from_physical_feature_decisions():
    from CORE.atlas_physical_feature_resolver import (
        AtlasPhysicalFeatureDecision,
    )

    decisions = (
        AtlasPhysicalFeatureDecision(
            feature_id="opening_1",
            semantic_class="recessed_opening",
            action="preserve",
            measured_width_mm=1.2,
            measured_height_mm=1.6,
            resolved_width_mm=1.2,
            resolved_height_mm=1.6,
            semantic_importance=1.0,
            readability_priority=1.0,
            physical_feature_policy="preserve_if_readable",
            reason="already_readable",
            requires_operator_review=False,
            adjustments=(),
        ),
        AtlasPhysicalFeatureDecision(
            feature_id="rosette_1",
            semantic_class="rosette",
            action="enlarge",
            measured_width_mm=0.7,
            measured_height_mm=0.7,
            resolved_width_mm=1.0,
            resolved_height_mm=1.0,
            semantic_importance=1.0,
            readability_priority=1.0,
            physical_feature_policy="enlarge_if_needed",
            reason="below_minimum",
            requires_operator_review=False,
            adjustments=(),
        ),
        AtlasPhysicalFeatureDecision(
            feature_id="minor_detail_1",
            semantic_class="minor_detail",
            action="omit",
            measured_width_mm=0.1,
            measured_height_mm=0.1,
            resolved_width_mm=0.0,
            resolved_height_mm=0.0,
            semantic_importance=0.2,
            readability_priority=0.2,
            physical_feature_policy="omit_if_unreadable",
            reason="below_omit_threshold",
            requires_operator_review=False,
            adjustments=(),
        ),
    )

    score = (
        AtlasArchitecturalSemanticReliefComparisonReport
        .feature_retention_score(
            decisions
        )
    )

    assert score == pytest.approx(2.0 / 3.0)


def test_comparison_report_builds_from_baseline_and_semantic_decisions():
    from CORE.atlas_physical_feature_resolver import (
        AtlasPhysicalFeatureDecision,
    )

    def decision(feature_id, action):
        return AtlasPhysicalFeatureDecision(
            feature_id=feature_id,
            semantic_class="architectural_feature",
            action=action,
            measured_width_mm=1.0,
            measured_height_mm=1.0,
            resolved_width_mm=1.0,
            resolved_height_mm=1.0,
            semantic_importance=1.0,
            readability_priority=1.0,
            physical_feature_policy="test_policy",
            reason="test",
            requires_operator_review=False,
            adjustments=(),
        )

    baseline = (
        decision("opening_1", "preserve"),
        decision("ornament_1", "omit"),
        decision("panel_1", "omit"),
    )

    semantic = (
        decision("opening_1", "preserve"),
        decision("ornament_1", "enlarge"),
        decision("panel_1", "preserve"),
    )

    report = (
        AtlasArchitecturalSemanticReliefComparisonReport
        .build_from_decisions(
            baseline_decisions=baseline,
            semantic_decisions=semantic,
        )
    )

    assert report[
        "baseline_feature_readability_score"
    ] == pytest.approx(1.0 / 3.0)

    assert report[
        "semantic_feature_readability_score"
    ] == pytest.approx(1.0)

    assert report["semantic_more_readable"] is True
    assert report["status"] == "PASS"
