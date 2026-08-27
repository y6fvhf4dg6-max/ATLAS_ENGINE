from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_cheek_midface_quality_evidence import (
    AtlasCanonicalHeadCheekMidfaceQualityEvidence,
)


def test_defines_exact_item9_6_criteria():
    assert AtlasCanonicalHeadCheekMidfaceQualityEvidence.CRITERIA == (
        "zygomatic_width",
        "cheek_prominence",
        "anterior_projection",
        "midface_fullness",
        "cheek_to_nose_transition",
        "cheek_to_jaw_transition",
        "bilateral_asymmetry",
    )


def test_defines_exact_evaluation_spaces():
    assert AtlasCanonicalHeadCheekMidfaceQualityEvidence.EVALUATION_SPACES == (
        "2d_observation",
        "canonical_model",
        "metric_3d_ground_truth",
        "physical_output",
    )


def test_defines_exact_evidence_statuses():
    assert AtlasCanonicalHeadCheekMidfaceQualityEvidence.EVIDENCE_STATUSES == (
        "blocked",
    )


def test_defines_exact_evidence_origins():
    assert AtlasCanonicalHeadCheekMidfaceQualityEvidence.EVIDENCE_ORIGINS == (
        "directly_observed",
        "multiview_constrained",
        "model_prior_inferred",
        "generated_completion",
        "unresolved",
    )


@pytest.mark.parametrize(
    "criterion",
    (
        "zygomatic_width",
        "cheek_prominence",
        "anterior_projection",
        "midface_fullness",
        "cheek_to_nose_transition",
        "cheek_to_jaw_transition",
        "bilateral_asymmetry",
    ),
)
def test_accepts_blocked_item9_6_criteria(criterion):
    evidence = AtlasCanonicalHeadCheekMidfaceQualityEvidence(
        criterion=criterion,
        evaluation_space="metric_3d_ground_truth",
        evidence_status="blocked",
        evidence_origin="UNRESOLVED",
        source_reference="Item 9.6 cheek/midface evidence audit",
        permitted_claim=(
            "criterion remains blocked by missing subject-specific "
            "cheek/midface evidence"
        ),
        prohibited_claims=(
            "parametric cheek prior treated as subject observation",
            "relief cheek mask treated as canonical 3d ground truth",
            "fabricated regional surface accuracy",
            "metric millimetre accuracy",
        ),
        bounded_interpretation=(
            "no verified subject-specific cheek/midface mapping or "
            "criterion-specific quality measurement is currently available"
        ),
    )

    assert evidence.criterion == criterion
    assert evidence.evidence_status == "blocked"
    assert evidence.evidence_origin == "unresolved"


def test_rejects_unknown_criterion():
    with pytest.raises(ValueError, match="criterion"):
        AtlasCanonicalHeadCheekMidfaceQualityEvidence(
            criterion="midface_quality",
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
        AtlasCanonicalHeadCheekMidfaceQualityEvidence(
            criterion="zygomatic_width",
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
        AtlasCanonicalHeadCheekMidfaceQualityEvidence(
            criterion="zygomatic_width",
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
        AtlasCanonicalHeadCheekMidfaceQualityEvidence(
            criterion="zygomatic_width",
            evaluation_space="canonical_model",
            evidence_status="blocked",
            evidence_origin="observed",
            source_reference="source",
            permitted_claim="blocked",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="unresolved",
        )


def test_contract_is_immutable():
    evidence = AtlasCanonicalHeadCheekMidfaceQualityEvidence(
        criterion="zygomatic_width",
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
    evidence = AtlasCanonicalHeadCheekMidfaceQualityEvidence(
        criterion="zygomatic_width",
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


def test_contract_does_not_promote_bizygomatic_relation_into_item9_6():
    assert "bizygomatic_relation" not in (
        AtlasCanonicalHeadCheekMidfaceQualityEvidence.CRITERIA
    )
