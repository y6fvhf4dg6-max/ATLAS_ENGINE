from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_cross_view_regional_consistency_evidence import (
    AtlasCanonicalHeadCrossViewRegionalConsistencyEvidence,
)


def test_defines_exact_item9_10_criteria():
    assert AtlasCanonicalHeadCrossViewRegionalConsistencyEvidence.CRITERIA == (
        "same_region_across_views",
        "view_conditioned_residual_behavior",
        "consistent_regional_improvement",
        "consistent_regional_degradation",
        "mixed_view_conditioned_behavior",
        "profile_sensitive_region_behavior",
        "coverage_consistency",
        "uniform_regional_success",
    )


def test_defines_exact_evaluation_spaces():
    assert AtlasCanonicalHeadCrossViewRegionalConsistencyEvidence.EVALUATION_SPACES == (
        "2d_observation",
        "canonical_model",
        "metric_3d_ground_truth",
        "physical_output",
    )


def test_defines_exact_evidence_statuses():
    assert AtlasCanonicalHeadCrossViewRegionalConsistencyEvidence.EVIDENCE_STATUSES == (
        "bounded_positive",
        "bounded_negative",
        "bounded_mixed",
        "bounded_partial",
        "not_established",
    )


def test_defines_exact_evidence_origins():
    assert AtlasCanonicalHeadCrossViewRegionalConsistencyEvidence.EVIDENCE_ORIGINS == (
        "directly_observed",
        "multiview_constrained",
        "model_prior_inferred",
        "generated_completion",
        "unresolved",
    )


@pytest.mark.parametrize(
    ("criterion", "status"),
    (
        ("same_region_across_views", "bounded_positive"),
        ("view_conditioned_residual_behavior", "bounded_mixed"),
        ("consistent_regional_improvement", "bounded_positive"),
        ("consistent_regional_degradation", "bounded_negative"),
        ("mixed_view_conditioned_behavior", "bounded_mixed"),
        ("profile_sensitive_region_behavior", "bounded_partial"),
        ("coverage_consistency", "bounded_partial"),
        ("uniform_regional_success", "not_established"),
    ),
)
def test_accepts_exact_item9_10_criterion_status_pairs(criterion, status):
    evidence = AtlasCanonicalHeadCrossViewRegionalConsistencyEvidence(
        criterion=criterion,
        evaluation_space="2d_observation",
        evidence_status=status,
        evidence_origin="MULTIVIEW_CONSTRAINED",
        source_reference="REPRODUCIBILITY_ITEM8_9_REGION_WISE.json",
        semantic_scope="held-out front / turn-left / turn-right region-wise observation space",
        permitted_claim="bounded cross-view regional evidence only",
        prohibited_claims=(
            "metric 3d anatomical consistency",
            "surface accuracy",
            "uniform regional success from aggregate multiview performance",
        ),
        bounded_interpretation="claim remains limited to the persisted held-out regional evidence",
    )

    assert evidence.criterion == criterion
    assert evidence.evidence_status == status
    assert evidence.evidence_origin == "multiview_constrained"


def test_uniform_regional_success_remains_not_established():
    evidence = AtlasCanonicalHeadCrossViewRegionalConsistencyEvidence(
        criterion="uniform_regional_success",
        evaluation_space="2d_observation",
        evidence_status="not_established",
        evidence_origin="multiview_constrained",
        source_reference="REPRODUCIBILITY_ITEM8_9_REGION_WISE.json",
        semantic_scope=(
            "21 held-out region-view comparisons contain both improvement and degradation"
        ),
        permitted_claim="uniform regional success is not established",
        prohibited_claims=(
            "aggregate multiview success promoted to uniform regional success",
            "global facial-region pass",
            "phase decision",
        ),
        bounded_interpretation=(
            "12 comparisons improve and 9 degrade; region behavior is non-uniform"
        ),
    )

    assert evidence.evidence_status == "not_established"


def test_nose_body_can_record_three_view_bounded_negative_evidence():
    evidence = AtlasCanonicalHeadCrossViewRegionalConsistencyEvidence(
        criterion="consistent_regional_degradation",
        evaluation_space="2d_observation",
        evidence_status="bounded_negative",
        evidence_origin="directly_observed",
        source_reference="ITEM8_H1_NOSE_BODY_PER_LANDMARK_DIAGNOSIS.json",
        semantic_scope=(
            "nose_body partial_static105_overlap; degradation in front, turn-left, turn-right"
        ),
        permitted_claim="nose_body observation-space degradation is present in 3/3 held-out views",
        prohibited_claims=(
            "true metric 3d anatomical degradation",
            "dense anatomical nose-body segmentation",
            "surface error",
        ),
        bounded_interpretation=(
            "repeated held-out regression is observation-space evidence only"
        ),
    )

    assert evidence.evidence_status == "bounded_negative"


def test_upper_lip_can_record_three_view_full_coverage_improvement():
    evidence = AtlasCanonicalHeadCrossViewRegionalConsistencyEvidence(
        criterion="consistent_regional_improvement",
        evaluation_space="2d_observation",
        evidence_status="bounded_positive",
        evidence_origin="directly_observed",
        source_reference="REPRODUCIBILITY_ITEM8_9_REGION_WISE.json",
        semantic_scope="upper_lip full coverage in all three held-out views",
        permitted_claim="upper_lip reprojection improves in all three held-out views",
        prohibited_claims=(
            "surface accuracy improvement",
            "metric 3d lip accuracy",
            "global facial quality pass",
        ),
        bounded_interpretation="full static105 support remains a 2D landmark/reprojection channel",
    )

    assert evidence.evidence_status == "bounded_positive"


def test_partial_overlap_must_remain_explicit():
    evidence = AtlasCanonicalHeadCrossViewRegionalConsistencyEvidence(
        criterion="coverage_consistency",
        evaluation_space="2d_observation",
        evidence_status="bounded_partial",
        evidence_origin="directly_observed",
        source_reference="REPRODUCIBILITY_ITEM8_9_REGION_WISE.json",
        semantic_scope=(
            "lower_lip, nose_base, and nose_body use partial_static105_overlap"
        ),
        permitted_claim="partial overlap is explicitly preserved",
        prohibited_claims=(
            "partial overlap promoted to full semantic-region support",
            "dense regional coverage",
        ),
        bounded_interpretation="coverage state constrains every regional interpretation",
    )

    assert evidence.evidence_status == "bounded_partial"


def test_rejects_unknown_criterion():
    with pytest.raises(ValueError, match="criterion"):
        AtlasCanonicalHeadCrossViewRegionalConsistencyEvidence(
            criterion="cross_view_quality",
            evaluation_space="2d_observation",
            evidence_status="not_established",
            evidence_origin="unresolved",
            source_reference="source",
            semantic_scope="scope",
            permitted_claim="bounded",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="bounded",
        )


def test_rejects_unknown_evaluation_space():
    with pytest.raises(ValueError, match="evaluation_space"):
        AtlasCanonicalHeadCrossViewRegionalConsistencyEvidence(
            criterion="uniform_regional_success",
            evaluation_space="3d",
            evidence_status="not_established",
            evidence_origin="unresolved",
            source_reference="source",
            semantic_scope="scope",
            permitted_claim="bounded",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="bounded",
        )


def test_rejects_unknown_evidence_status():
    with pytest.raises(ValueError, match="evidence_status"):
        AtlasCanonicalHeadCrossViewRegionalConsistencyEvidence(
            criterion="uniform_regional_success",
            evaluation_space="2d_observation",
            evidence_status="pass",
            evidence_origin="unresolved",
            source_reference="source",
            semantic_scope="scope",
            permitted_claim="bounded",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="bounded",
        )


def test_rejects_unknown_evidence_origin():
    with pytest.raises(ValueError, match="evidence_origin"):
        AtlasCanonicalHeadCrossViewRegionalConsistencyEvidence(
            criterion="uniform_regional_success",
            evaluation_space="2d_observation",
            evidence_status="not_established",
            evidence_origin="observed",
            source_reference="source",
            semantic_scope="scope",
            permitted_claim="bounded",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="bounded",
        )


def test_contract_is_immutable():
    evidence = AtlasCanonicalHeadCrossViewRegionalConsistencyEvidence(
        criterion="uniform_regional_success",
        evaluation_space="2d_observation",
        evidence_status="not_established",
        evidence_origin="multiview_constrained",
        source_reference="source",
        semantic_scope="scope",
        permitted_claim="bounded",
        prohibited_claims=("unsupported claim",),
        bounded_interpretation="bounded",
    )

    with pytest.raises(FrozenInstanceError):
        evidence.evidence_status = "bounded_positive"


def test_contract_does_not_claim_metric_threshold_or_phase_decision():
    evidence = AtlasCanonicalHeadCrossViewRegionalConsistencyEvidence(
        criterion="uniform_regional_success",
        evaluation_space="2d_observation",
        evidence_status="not_established",
        evidence_origin="multiview_constrained",
        source_reference="source",
        semantic_scope="scope",
        permitted_claim="bounded",
        prohibited_claims=("unsupported claim",),
        bounded_interpretation="bounded",
    )

    assert not hasattr(evidence, "metric_accuracy_mm")
    assert not hasattr(evidence, "surface_error")
    assert not hasattr(evidence, "threshold")
    assert not hasattr(evidence, "confidence_score")
    assert not hasattr(evidence, "decision")
    assert not hasattr(evidence, "phase_9_authorized")
