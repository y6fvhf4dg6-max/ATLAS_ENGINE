from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_forehead_cranial_quality_evidence import (
    AtlasCanonicalHeadForeheadCranialQualityEvidence,
)


def test_defines_exact_item9_8_criteria():
    assert AtlasCanonicalHeadForeheadCranialQualityEvidence.CRITERIA == (
        "forehead_height",
        "forehead_slope",
        "frontal_curvature",
        "temple_transition",
        "cranial_width",
        "cranial_depth",
        "overall_skull_head_envelope",
    )


def test_defines_exact_evaluation_spaces():
    assert AtlasCanonicalHeadForeheadCranialQualityEvidence.EVALUATION_SPACES == (
        "2d_observation",
        "canonical_model",
        "metric_3d_ground_truth",
        "physical_output",
    )


def test_defines_exact_evidence_statuses():
    assert AtlasCanonicalHeadForeheadCranialQualityEvidence.EVIDENCE_STATUSES == (
        "blocked",
    )


def test_defines_exact_evidence_origins():
    assert AtlasCanonicalHeadForeheadCranialQualityEvidence.EVIDENCE_ORIGINS == (
        "directly_observed",
        "multiview_constrained",
        "model_prior_inferred",
        "generated_completion",
        "unresolved",
    )


@pytest.mark.parametrize(
    "criterion",
    (
        "forehead_height",
        "forehead_slope",
        "frontal_curvature",
        "temple_transition",
        "cranial_width",
        "cranial_depth",
        "overall_skull_head_envelope",
    ),
)
def test_accepts_blocked_item9_8_criteria(criterion):
    evidence = AtlasCanonicalHeadForeheadCranialQualityEvidence(
        criterion=criterion,
        evaluation_space="metric_3d_ground_truth",
        evidence_status="blocked",
        evidence_origin="UNRESOLVED",
        source_reference="Item 9.8 forehead/cranial evidence audit",
        permitted_claim=(
            "criterion remains blocked by missing subject-specific "
            "forehead/cranial quality evidence"
        ),
        prohibited_claims=(
            "provider semantic mask treated as quality measurement",
            "model-space extent treated as subject anatomical truth",
            "lower-jaw silhouette evidence promoted to cranial envelope quality",
            "metric millimetre accuracy",
        ),
        bounded_interpretation=(
            "no verified criterion-specific subject evidence currently "
            "establishes this forehead or cranial property"
        ),
    )

    assert evidence.criterion == criterion
    assert evidence.evidence_status == "blocked"
    assert evidence.evidence_origin == "unresolved"


def test_rejects_unknown_criterion():
    with pytest.raises(ValueError, match="criterion"):
        AtlasCanonicalHeadForeheadCranialQualityEvidence(
            criterion="cranial_quality",
            evaluation_space="canonical_model",
            evidence_status="blocked",
            evidence_origin="unresolved",
            source_reference="source",
            permitted_claim="blocked",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="unresolved",
        )


def test_rejects_unknown_evaluation_space():
    with pytest.raises(ValueError, match="evaluation_space"):
        AtlasCanonicalHeadForeheadCranialQualityEvidence(
            criterion="forehead_height",
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
        AtlasCanonicalHeadForeheadCranialQualityEvidence(
            criterion="forehead_height",
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
        AtlasCanonicalHeadForeheadCranialQualityEvidence(
            criterion="forehead_height",
            evaluation_space="canonical_model",
            evidence_status="blocked",
            evidence_origin="observed",
            source_reference="source",
            permitted_claim="blocked",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="unresolved",
        )


def test_contract_is_immutable():
    evidence = AtlasCanonicalHeadForeheadCranialQualityEvidence(
        criterion="forehead_height",
        evaluation_space="canonical_model",
        evidence_status="blocked",
        evidence_origin="unresolved",
        source_reference="source",
        permitted_claim="blocked",
        prohibited_claims=("unsupported claim",),
        bounded_interpretation="unresolved",
    )

    with pytest.raises(FrozenInstanceError):
        evidence.evidence_status = "pass"


def test_contract_does_not_claim_geometry_threshold_or_phase_decision():
    evidence = AtlasCanonicalHeadForeheadCranialQualityEvidence(
        criterion="forehead_height",
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
