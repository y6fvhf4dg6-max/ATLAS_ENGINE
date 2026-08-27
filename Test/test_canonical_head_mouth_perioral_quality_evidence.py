from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_mouth_perioral_quality_evidence import (
    AtlasCanonicalHeadMouthPerioralQualityEvidence,
)


def test_defines_exact_item9_7_criteria():
    assert AtlasCanonicalHeadMouthPerioralQualityEvidence.CRITERIA == (
        "mouth_width",
        "upper_lower_lip_relation",
        "philtrum_region",
        "lip_projection",
        "commissures",
        "neutral_geometry_vs_expression_deformation",
        "nasolabial_perioral_contamination",
    )


def test_defines_exact_evaluation_spaces():
    assert AtlasCanonicalHeadMouthPerioralQualityEvidence.EVALUATION_SPACES == (
        "2d_observation",
        "canonical_model",
        "metric_3d_ground_truth",
        "physical_output",
    )


def test_defines_exact_evidence_statuses():
    assert AtlasCanonicalHeadMouthPerioralQualityEvidence.EVIDENCE_STATUSES == (
        "bounded_not_established",
        "bounded_structural",
        "blocked",
    )


def test_defines_exact_evidence_origins():
    assert AtlasCanonicalHeadMouthPerioralQualityEvidence.EVIDENCE_ORIGINS == (
        "directly_observed",
        "multiview_constrained",
        "model_prior_inferred",
        "generated_completion",
        "unresolved",
    )


@pytest.mark.parametrize(
    "criterion",
    (
        "mouth_width",
        "philtrum_region",
        "lip_projection",
        "commissures",
        "nasolabial_perioral_contamination",
    ),
)
def test_accepts_blocked_item9_7_criteria(criterion):
    evidence = AtlasCanonicalHeadMouthPerioralQualityEvidence(
        criterion=criterion,
        evaluation_space="metric_3d_ground_truth",
        evidence_status="blocked",
        evidence_origin="UNRESOLVED",
        source_reference="Item 9.7 mouth/perioral evidence audit",
        permitted_claim=(
            "criterion remains blocked by missing subject-specific "
            "mouth/perioral quality evidence"
        ),
        prohibited_claims=(
            "parametric mouth or lip prior treated as subject observation",
            "relief semantic mask treated as canonical 3d ground truth",
            "fabricated regional surface accuracy",
            "metric millimetre accuracy",
        ),
        bounded_interpretation=(
            "no verified criterion-specific canonical or metric quality "
            "measurement currently establishes this mouth/perioral property"
        ),
    )

    assert evidence.criterion == criterion
    assert evidence.evidence_status == "blocked"
    assert evidence.evidence_origin == "unresolved"


def test_accepts_bounded_upper_lower_lip_relation_evidence():
    evidence = AtlasCanonicalHeadMouthPerioralQualityEvidence(
        criterion="upper_lower_lip_relation",
        evaluation_space="2d_observation",
        evidence_status="bounded_not_established",
        evidence_origin="MULTIVIEW_CONSTRAINED",
        source_reference="REPRODUCIBILITY_ITEM8_9_REGION_WISE.json",
        permitted_claim=(
            "upper and lower lip observation channels have held-out "
            "reprojection evidence"
        ),
        prohibited_claims=(
            "explicit upper-to-lower lip geometry relation established",
            "lip surface accuracy",
            "metric 3d lip relation",
        ),
        bounded_interpretation=(
            "upper_lip has full static105 coverage and lower_lip has partial "
            "static105 overlap; both improve in the three held-out pose views, "
            "but no explicit inter-lip relation metric exists"
        ),
    )

    assert evidence.evidence_status == "bounded_not_established"
    assert evidence.evidence_origin == "multiview_constrained"


def test_accepts_bounded_structural_expression_separation_evidence():
    evidence = AtlasCanonicalHeadMouthPerioralQualityEvidence(
        criterion="neutral_geometry_vs_expression_deformation",
        evaluation_space="canonical_model",
        evidence_status="bounded_structural",
        evidence_origin="MULTIVIEW_CONSTRAINED",
        source_reference=(
            "ITEM8_H3_BOUNDED_COUNTERFACTUAL_SEPARATION_INTERPRETATION.json"
        ),
        permitted_claim=(
            "expression-dependent geometry can change while locked identity "
            "state and identity-only canonical geometry remain invariant"
        ),
        prohibited_claims=(
            "mouth-specific expression accuracy",
            "absence of identity leakage in every future optimizer",
            "customer-visible mouth quality acceptance",
        ),
        bounded_interpretation=(
            "H3 supports structural counterfactual separation of expression "
            "from canonical identity, but does not provide mouth-specific "
            "regional accuracy or dense perioral anatomy evidence"
        ),
    )

    assert evidence.evidence_status == "bounded_structural"
    assert evidence.evidence_origin == "multiview_constrained"


def test_rejects_unknown_criterion():
    with pytest.raises(ValueError, match="criterion"):
        AtlasCanonicalHeadMouthPerioralQualityEvidence(
            criterion="mouth_quality",
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
        AtlasCanonicalHeadMouthPerioralQualityEvidence(
            criterion="mouth_width",
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
        AtlasCanonicalHeadMouthPerioralQualityEvidence(
            criterion="mouth_width",
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
        AtlasCanonicalHeadMouthPerioralQualityEvidence(
            criterion="mouth_width",
            evaluation_space="canonical_model",
            evidence_status="blocked",
            evidence_origin="observed",
            source_reference="source",
            permitted_claim="blocked",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="unresolved",
        )


def test_contract_is_immutable():
    evidence = AtlasCanonicalHeadMouthPerioralQualityEvidence(
        criterion="mouth_width",
        evaluation_space="canonical_model",
        evidence_status="blocked",
        evidence_origin="unresolved",
        source_reference="source",
        permitted_claim="blocked",
        prohibited_claims=("unsupported claim",),
        bounded_interpretation="unresolved",
    )

    with pytest.raises(FrozenInstanceError):
        evidence.evidence_status = "bounded_not_established"


def test_contract_does_not_claim_geometry_threshold_or_phase_decision():
    evidence = AtlasCanonicalHeadMouthPerioralQualityEvidence(
        criterion="mouth_width",
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
