from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_jaw_chin_quality_evidence import (
    AtlasCanonicalHeadJawChinQualityEvidence,
)


def test_defines_exact_item9_3_criteria():
    assert AtlasCanonicalHeadJawChinQualityEvidence.CRITERIA == (
        "mandibular_width",
        "jaw_angle",
        "chin_width",
        "chin_projection",
        "chin_vertical_position",
        "left_right_contour",
        "frontal_consistency",
        "profile_consistency",
        "cross_view_stability",
    )


def test_defines_exact_evaluation_spaces():
    assert AtlasCanonicalHeadJawChinQualityEvidence.EVALUATION_SPACES == (
        "2d_observation",
        "canonical_model",
        "metric_3d_ground_truth",
        "physical_output",
    )


def test_defines_bounded_evidence_statuses_without_acceptance_threshold():
    assert AtlasCanonicalHeadJawChinQualityEvidence.EVIDENCE_STATUSES == (
        "bounded_positive",
        "bounded_negative_not_established",
        "bounded_aggregate_only",
        "blocked",
    )


def test_defines_exact_evidence_origins():
    assert AtlasCanonicalHeadJawChinQualityEvidence.EVIDENCE_ORIGINS == (
        "directly_observed",
        "multiview_constrained",
        "model_prior_inferred",
        "generated_completion",
        "unresolved",
    )


def test_accepts_bounded_positive_profile_evidence():
    evidence = AtlasCanonicalHeadJawChinQualityEvidence(
        criterion="profile_consistency",
        evaluation_space="2d_observation",
        evidence_status="bounded_positive",
        evidence_origin="MULTIVIEW_CONSTRAINED",
        source_reference="REPRODUCIBILITY_ITEM8_9_REGION_WISE.json",
        permitted_claim="bounded 2d side-profile contour improvement",
        prohibited_claims=(
            "3d jaw anatomy accuracy",
            "identity preservation proof",
            "metric millimetre accuracy",
        ),
        bounded_interpretation=(
            "turn_left and turn_right contour errors both improved"
        ),
    )

    assert evidence.criterion == "profile_consistency"
    assert evidence.evaluation_space == "2d_observation"
    assert evidence.evidence_status == "bounded_positive"
    assert evidence.evidence_origin == "multiview_constrained"


def test_accepts_bounded_negative_frontal_evidence():
    evidence = AtlasCanonicalHeadJawChinQualityEvidence(
        criterion="frontal_consistency",
        evaluation_space="2d_observation",
        evidence_status="bounded_negative_not_established",
        evidence_origin="DIRECTLY_OBSERVED",
        source_reference="PHASE8_10_PERSONAL_MULTIVIEW_SILHOUETTE_RECOVERY_EVIDENCE.md",
        permitted_claim=(
            "preferred candidate shows a bounded front-view contour trade-off"
        ),
        prohibited_claims=(
            "frontal jaw consistency established",
            "3d jaw anatomy accuracy",
        ),
        bounded_interpretation=(
            "front visible error increased from baseline for the preferred candidate"
        ),
    )

    assert evidence.evidence_status == "bounded_negative_not_established"


def test_accepts_bounded_aggregate_cross_view_evidence():
    evidence = AtlasCanonicalHeadJawChinQualityEvidence(
        criterion="cross_view_stability",
        evaluation_space="2d_observation",
        evidence_status="bounded_aggregate_only",
        evidence_origin="MULTIVIEW_CONSTRAINED",
        source_reference="PHASE8_10_PERSONAL_MULTIVIEW_SILHOUETTE_RECOVERY_EVIDENCE.md",
        permitted_claim="bounded aggregate 3-view dynamic improvement only",
        prohibited_claims=(
            "feature-specific jaw stability established",
            "3d cross-view anatomical consistency",
        ),
        bounded_interpretation=(
            "aggregate 3-view dynamic error improved but no same-feature stability metric exists"
        ),
    )

    assert evidence.evidence_status == "bounded_aggregate_only"


@pytest.mark.parametrize(
    "criterion",
    (
        "mandibular_width",
        "jaw_angle",
        "chin_width",
        "chin_projection",
        "chin_vertical_position",
    ),
)
def test_accepts_blocked_anatomical_criteria_without_fabricating_mapping(criterion):
    evidence = AtlasCanonicalHeadJawChinQualityEvidence(
        criterion=criterion,
        evaluation_space="canonical_model",
        evidence_status="blocked",
        evidence_origin="UNRESOLVED",
        source_reference="Item 9.2 semantic mapping audit",
        permitted_claim="criterion evaluation blocked by missing verified jaw/chin mapping",
        prohibited_claims=(
            "guessed FLAME vertex indices",
            "anatomical ground truth",
            "metric millimetre accuracy",
        ),
        bounded_interpretation=(
            "verified FLAME jaw/chin subregion mapping is unavailable"
        ),
    )

    assert evidence.evidence_status == "blocked"


def test_rejects_unknown_criterion():
    with pytest.raises(ValueError, match="criterion"):
        AtlasCanonicalHeadJawChinQualityEvidence(
            criterion="jaw_quality",
            evaluation_space="2d_observation",
            evidence_status="blocked",
            evidence_origin="unresolved",
            source_reference="source",
            permitted_claim="blocked",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="unresolved",
        )


def test_rejects_unknown_evaluation_space():
    with pytest.raises(ValueError, match="evaluation_space"):
        AtlasCanonicalHeadJawChinQualityEvidence(
            criterion="jaw_angle",
            evaluation_space="3d",
            evidence_status="blocked",
            evidence_origin="unresolved",
            source_reference="source",
            permitted_claim="blocked",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="unresolved",
        )


def test_rejects_unknown_evidence_status():
    with pytest.raises(ValueError, match="evidence_status"):
        AtlasCanonicalHeadJawChinQualityEvidence(
            criterion="jaw_angle",
            evaluation_space="canonical_model",
            evidence_status="pass",
            evidence_origin="unresolved",
            source_reference="source",
            permitted_claim="blocked",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="unresolved",
        )


def test_rejects_unknown_evidence_origin():
    with pytest.raises(ValueError, match="evidence_origin"):
        AtlasCanonicalHeadJawChinQualityEvidence(
            criterion="jaw_angle",
            evaluation_space="canonical_model",
            evidence_status="blocked",
            evidence_origin="observed",
            source_reference="source",
            permitted_claim="blocked",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="unresolved",
        )


def test_contract_is_immutable():
    evidence = AtlasCanonicalHeadJawChinQualityEvidence(
        criterion="jaw_angle",
        evaluation_space="canonical_model",
        evidence_status="blocked",
        evidence_origin="unresolved",
        source_reference="source",
        permitted_claim="blocked",
        prohibited_claims=("unsupported claim",),
        bounded_interpretation="unresolved",
    )

    with pytest.raises(FrozenInstanceError):
        evidence.evidence_status = "bounded_positive"


def test_contract_does_not_claim_geometry_threshold_or_phase_decision():
    evidence = AtlasCanonicalHeadJawChinQualityEvidence(
        criterion="jaw_angle",
        evaluation_space="canonical_model",
        evidence_status="blocked",
        evidence_origin="unresolved",
        source_reference="source",
        permitted_claim="blocked",
        prohibited_claims=("unsupported claim",),
        bounded_interpretation="unresolved",
    )

    assert not hasattr(evidence, "vertices")
    assert not hasattr(evidence, "vertex_indices")
    assert not hasattr(evidence, "metric_accuracy_mm")
    assert not hasattr(evidence, "confidence_score")
    assert not hasattr(evidence, "threshold")
    assert not hasattr(evidence, "decision")
    assert not hasattr(evidence, "phase_9_authorized")
