from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_nose_quality_evidence import (
    AtlasCanonicalHeadNoseQualityEvidence,
)


def test_defines_exact_item9_4_criteria():
    assert AtlasCanonicalHeadNoseQualityEvidence.CRITERIA == (
        "bridge",
        "dorsum_body",
        "base",
        "tip_projection",
        "alar_width",
        "nasolabial_relation",
        "profile_projection",
        "bilateral_consistency",
        "cross_view_consistency",
    )


def test_defines_exact_evaluation_spaces():
    assert AtlasCanonicalHeadNoseQualityEvidence.EVALUATION_SPACES == (
        "2d_observation",
        "canonical_model",
        "metric_3d_ground_truth",
        "physical_output",
    )


def test_defines_exact_evidence_statuses():
    assert AtlasCanonicalHeadNoseQualityEvidence.EVIDENCE_STATUSES == (
        "bounded_model_space",
        "bounded_negative_not_established",
        "blocked",
    )


def test_defines_exact_evidence_origins():
    assert AtlasCanonicalHeadNoseQualityEvidence.EVIDENCE_ORIGINS == (
        "directly_observed",
        "multiview_constrained",
        "model_prior_inferred",
        "generated_completion",
        "unresolved",
    )


def test_accepts_bounded_bridge_model_space_evidence():
    evidence = AtlasCanonicalHeadNoseQualityEvidence(
        criterion="bridge",
        evaluation_space="canonical_model",
        evidence_status="bounded_model_space",
        evidence_origin="MULTIVIEW_CONSTRAINED",
        source_reference="ITEM8_H2_CANONICAL_3D_REGION_MEASUREMENT_RESULT.json",
        permitted_claim=(
            "bounded canonical-model displacement evidence on the frozen "
            "nose_bridge anchor-supported topology footprint"
        ),
        prohibited_claims=(
            "metric 3d anatomical accuracy",
            "dense anatomical nose-bridge segmentation",
            "provider-authored finer mapping",
        ),
        bounded_interpretation=(
            "nose_bridge has a frozen 12-vertex anchor-supported footprint "
            "with canonical-model displacement measurements"
        ),
    )

    assert evidence.criterion == "bridge"
    assert evidence.evidence_status == "bounded_model_space"
    assert evidence.evidence_origin == "multiview_constrained"


def test_accepts_bounded_negative_dorsum_body_evidence():
    evidence = AtlasCanonicalHeadNoseQualityEvidence(
        criterion="dorsum_body",
        evaluation_space="2d_observation",
        evidence_status="bounded_negative_not_established",
        evidence_origin="MULTIVIEW_CONSTRAINED",
        source_reference="ITEM8_H1_POSE_REGIONAL_REGRESSION_DIAGNOSIS.json",
        permitted_claim=(
            "nose_body reprojection degraded in all three held-out pose views"
        ),
        prohibited_claims=(
            "true metric 3d anatomical nose degradation",
            "camera-only explanation",
            "global nose-quality pass",
        ),
        bounded_interpretation=(
            "the 3/3 held-out observation-space regression remains explicit; "
            "H2 shows accompanying non-zero canonical-model change but no "
            "metric ground-truth correctness target exists"
        ),
    )

    assert evidence.evidence_status == "bounded_negative_not_established"


def test_accepts_bounded_base_model_space_evidence_without_tip_promotion():
    evidence = AtlasCanonicalHeadNoseQualityEvidence(
        criterion="base",
        evaluation_space="canonical_model",
        evidence_status="bounded_model_space",
        evidence_origin="MULTIVIEW_CONSTRAINED",
        source_reference="ITEM8_H2_EXACT_BARYCENTRIC_ANCHOR_TOPOLOGY_FOOTPRINT.json",
        permitted_claim=(
            "bounded canonical-model evidence for the frozen nose_base "
            "anchor-supported topology footprint"
        ),
        prohibited_claims=(
            "nose_base_tip mapping established",
            "tip projection accuracy",
            "metric millimetre accuracy",
        ),
        bounded_interpretation=(
            "nose_base has a frozen 6-vertex anchor-supported footprint; "
            "it is not promoted to nose_base_tip"
        ),
    )

    assert evidence.evidence_status == "bounded_model_space"


@pytest.mark.parametrize(
    "criterion",
    (
        "tip_projection",
        "alar_width",
        "nasolabial_relation",
        "profile_projection",
        "bilateral_consistency",
    ),
)
def test_accepts_blocked_specialized_nose_criteria_without_fabricating_evidence(
    criterion,
):
    evidence = AtlasCanonicalHeadNoseQualityEvidence(
        criterion=criterion,
        evaluation_space="metric_3d_ground_truth",
        evidence_status="blocked",
        evidence_origin="UNRESOLVED",
        source_reference="Item 9.4 specialized nose evidence audit",
        permitted_claim="criterion remains blocked by missing appropriate evidence",
        prohibited_claims=(
            "fabricated nose measurement",
            "metric millimetre accuracy",
            "anatomical correctness",
        ),
        bounded_interpretation=(
            "no criterion-specific metric ground-truth evidence is available"
        ),
    )

    assert evidence.evidence_status == "blocked"


def test_accepts_bounded_negative_cross_view_consistency_evidence():
    evidence = AtlasCanonicalHeadNoseQualityEvidence(
        criterion="cross_view_consistency",
        evaluation_space="2d_observation",
        evidence_status="bounded_negative_not_established",
        evidence_origin="MULTIVIEW_CONSTRAINED",
        source_reference="ITEM8_H1_NOSE_BODY_PER_LANDMARK_DIAGNOSIS.json",
        permitted_claim=(
            "nose_body degradation is observed in 3/3 held-out views"
        ),
        prohibited_claims=(
            "nose-wide feature consistency established",
            "metric 3d cross-view anatomical consistency",
            "global identity preservation proof",
        ),
        bounded_interpretation=(
            "the repeated 3-view failure is cross-view negative evidence, "
            "not a positive feature-consistency metric"
        ),
    )

    assert evidence.evidence_status == "bounded_negative_not_established"


def test_rejects_unknown_criterion():
    with pytest.raises(ValueError, match="criterion"):
        AtlasCanonicalHeadNoseQualityEvidence(
            criterion="nose_quality",
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
        AtlasCanonicalHeadNoseQualityEvidence(
            criterion="bridge",
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
        AtlasCanonicalHeadNoseQualityEvidence(
            criterion="bridge",
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
        AtlasCanonicalHeadNoseQualityEvidence(
            criterion="bridge",
            evaluation_space="canonical_model",
            evidence_status="blocked",
            evidence_origin="observed",
            source_reference="source",
            permitted_claim="blocked",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="unresolved",
        )


def test_contract_is_immutable():
    evidence = AtlasCanonicalHeadNoseQualityEvidence(
        criterion="bridge",
        evaluation_space="canonical_model",
        evidence_status="blocked",
        evidence_origin="unresolved",
        source_reference="source",
        permitted_claim="blocked",
        prohibited_claims=("unsupported claim",),
        bounded_interpretation="unresolved",
    )

    with pytest.raises(FrozenInstanceError):
        evidence.evidence_status = "bounded_model_space"


def test_contract_does_not_claim_geometry_threshold_or_phase_decision():
    evidence = AtlasCanonicalHeadNoseQualityEvidence(
        criterion="bridge",
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
