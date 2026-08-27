from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_landmark_surface_agreement_evidence import (
    AtlasCanonicalHeadLandmarkSurfaceAgreementEvidence,
)


def test_defines_exact_item9_13_criteria():
    assert AtlasCanonicalHeadLandmarkSurfaceAgreementEvidence.CRITERIA == (
        "landmark_success_with_surface_failure",
        "surface_success_with_landmark_failure",
        "local_landmark_localization_uncertainty",
        "regional_measurement_confidence_limitations",
    )


def test_defines_exact_evaluation_spaces():
    assert AtlasCanonicalHeadLandmarkSurfaceAgreementEvidence.EVALUATION_SPACES == (
        "2d_observation",
        "canonical_model",
        "metric_3d_ground_truth",
    )


def test_defines_exact_evidence_statuses():
    assert AtlasCanonicalHeadLandmarkSurfaceAgreementEvidence.EVIDENCE_STATUSES == (
        "not_established",
        "unresolved",
        "bounded_negative",
    )


def test_defines_exact_evidence_origins():
    assert AtlasCanonicalHeadLandmarkSurfaceAgreementEvidence.EVIDENCE_ORIGINS == (
        "directly_observed",
        "multiview_constrained",
        "model_prior_inferred",
        "generated_completion",
        "unresolved",
    )


@pytest.mark.parametrize(
    ("criterion", "status"),
    (
        ("landmark_success_with_surface_failure", "not_established"),
        ("surface_success_with_landmark_failure", "not_established"),
        ("local_landmark_localization_uncertainty", "unresolved"),
        ("regional_measurement_confidence_limitations", "bounded_negative"),
    ),
)
def test_accepts_exact_item9_13_criterion_status_pairs(criterion, status):
    evidence = AtlasCanonicalHeadLandmarkSurfaceAgreementEvidence(
        criterion=criterion,
        evaluation_space="2d_observation",
        evidence_status=status,
        evidence_origin="MULTIVIEW_CONSTRAINED",
        source_reference="persisted Item 9 evidence",
        semantic_scope="Item 9.13 bounded agreement audit",
        permitted_claim="bounded Item 9.13 interpretation only",
        prohibited_claims=(
            "landmark fit proves surface accuracy",
            "2d reprojection proves metric 3d accuracy",
            "unsupported phase decision",
        ),
        bounded_interpretation="claim remains limited to verified evidence",
    )

    assert evidence.criterion == criterion
    assert evidence.evidence_status == status
    assert evidence.evidence_origin == "multiview_constrained"


def test_landmark_success_with_surface_failure_is_not_established():
    evidence = AtlasCanonicalHeadLandmarkSurfaceAgreementEvidence(
        criterion="landmark_success_with_surface_failure",
        evaluation_space="metric_3d_ground_truth",
        evidence_status="not_established",
        evidence_origin="unresolved",
        source_reference=(
            "Item 9.10 regional reprojection evidence + "
            "Item 9.12 regional surface error boundary"
        ),
        semantic_scope=(
            "same subject and facial region landmark success versus "
            "independent metric surface failure"
        ),
        permitted_claim=(
            "landmark success and independent metric surface failure "
            "have not been jointly established"
        ),
        prohibited_claims=(
            "good landmark reprojection proves good surface geometry",
            "canonical displacement alone is surface failure",
            "nose_body reprojection degradation proves metric anatomical failure",
        ),
        bounded_interpretation=(
            "real subject-specific regional metric surface truth remains blocked"
        ),
    )

    assert evidence.evidence_status == "not_established"


def test_surface_success_with_landmark_failure_is_not_established():
    evidence = AtlasCanonicalHeadLandmarkSurfaceAgreementEvidence(
        criterion="surface_success_with_landmark_failure",
        evaluation_space="metric_3d_ground_truth",
        evidence_status="not_established",
        evidence_origin="unresolved",
        source_reference="Item 9.12 regional surface error evidence",
        semantic_scope=(
            "same subject and facial region independent metric surface success "
            "versus landmark failure"
        ),
        permitted_claim=(
            "surface success with landmark failure is not established"
        ),
        prohibited_claims=(
            "metric surface success exists for current real subject evidence",
            "synthetic point-to-surface tests are subject-specific surface success",
        ),
        bounded_interpretation=(
            "no admissible real regional metric surface result currently exists"
        ),
    )

    assert evidence.evidence_status == "not_established"


def test_local_landmark_localization_uncertainty_is_unresolved():
    evidence = AtlasCanonicalHeadLandmarkSurfaceAgreementEvidence(
        criterion="local_landmark_localization_uncertainty",
        evaluation_space="2d_observation",
        evidence_status="unresolved",
        evidence_origin="unresolved",
        source_reference=(
            "AtlasCanonicalHeadHeldOutViewObservation + "
            "AtlasCanonicalHeadLandmarkCorrespondence"
        ),
        semantic_scope="per-landmark localization uncertainty",
        permitted_claim=(
            "current held-out and correspondence contracts do not provide "
            "verified per-landmark localization uncertainty"
        ),
        prohibited_claims=(
            "provider top-level confidence is per-landmark uncertainty",
            "DSINE confidence is landmark localization confidence",
            "unknown uncertainty equals zero uncertainty",
        ),
        bounded_interpretation=(
            "no verified per-landmark sigma, variance, covariance, or equivalent "
            "uncertainty channel was found"
        ),
    )

    assert evidence.evidence_status == "unresolved"


def test_regional_measurement_confidence_limitations_are_bounded_negative():
    evidence = AtlasCanonicalHeadLandmarkSurfaceAgreementEvidence(
        criterion="regional_measurement_confidence_limitations",
        evaluation_space="2d_observation",
        evidence_status="bounded_negative",
        evidence_origin="multiview_constrained",
        source_reference=(
            "REPRODUCIBILITY_ITEM8_9_REGION_WISE.json + "
            "Item 9.2 mapping boundary + Item 9.12 metric boundary"
        ),
        semantic_scope="regional landmark/surface measurement coverage limitations",
        permitted_claim=(
            "regional measurement confidence is limited by partial landmark "
            "coverage, bounded semantic mappings, and unavailable real metric GT"
        ),
        prohibited_claims=(
            "partial static105 overlap is full semantic-region coverage",
            "eye-region landmarks establish orbital surface accuracy",
            "anchor-supported nose footprints are dense anatomical ground truth",
        ),
        bounded_interpretation=(
            "9/21 regional comparisons use partial static105 overlap; jaw/face "
            "oval is outside static105; real regional metric GT remains blocked"
        ),
    )

    assert evidence.evidence_status == "bounded_negative"


def test_claim_boundary_prevents_landmark_to_surface_promotion():
    evidence = AtlasCanonicalHeadLandmarkSurfaceAgreementEvidence(
        criterion="landmark_success_with_surface_failure",
        evaluation_space="2d_observation",
        evidence_status="not_established",
        evidence_origin="multiview_constrained",
        source_reference="AtlasCanonicalHeadEvaluationSpaceClaimBoundary",
        semantic_scope="landmark versus surface claim promotion",
        permitted_claim="landmark and surface evidence must remain separate",
        prohibited_claims=(
            "landmark_fit -> surface_accuracy",
            "2d_reprojection -> metric_3d_accuracy",
        ),
        bounded_interpretation=(
            "cross-space promotion remains explicitly forbidden"
        ),
    )

    assert "landmark_fit -> surface_accuracy" in evidence.prohibited_claims


def test_rejects_unknown_criterion():
    with pytest.raises(ValueError, match="criterion"):
        AtlasCanonicalHeadLandmarkSurfaceAgreementEvidence(
            criterion="agreement",
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
        AtlasCanonicalHeadLandmarkSurfaceAgreementEvidence(
            criterion="landmark_success_with_surface_failure",
            evaluation_space="physical_output",
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
        AtlasCanonicalHeadLandmarkSurfaceAgreementEvidence(
            criterion="landmark_success_with_surface_failure",
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
        AtlasCanonicalHeadLandmarkSurfaceAgreementEvidence(
            criterion="landmark_success_with_surface_failure",
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
    evidence = AtlasCanonicalHeadLandmarkSurfaceAgreementEvidence(
        criterion="regional_measurement_confidence_limitations",
        evaluation_space="2d_observation",
        evidence_status="bounded_negative",
        evidence_origin="multiview_constrained",
        source_reference="source",
        semantic_scope="scope",
        permitted_claim="bounded",
        prohibited_claims=("unsupported claim",),
        bounded_interpretation="bounded",
    )

    with pytest.raises(FrozenInstanceError):
        evidence.evidence_status = "not_established"


def test_contract_does_not_add_surface_scores_uncertainty_values_or_phase_decision():
    evidence = AtlasCanonicalHeadLandmarkSurfaceAgreementEvidence(
        criterion="local_landmark_localization_uncertainty",
        evaluation_space="2d_observation",
        evidence_status="unresolved",
        evidence_origin="unresolved",
        source_reference="source",
        semantic_scope="scope",
        permitted_claim="bounded",
        prohibited_claims=("unsupported claim",),
        bounded_interpretation="bounded",
    )

    assert not hasattr(evidence, "surface_error_mm")
    assert not hasattr(evidence, "landmark_sigma_px")
    assert not hasattr(evidence, "landmark_variance")
    assert not hasattr(evidence, "confidence_score")
    assert not hasattr(evidence, "threshold")
    assert not hasattr(evidence, "decision")
    assert not hasattr(evidence, "phase_9_authorized")
