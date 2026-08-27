from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_head_ratio_anthropometric_quality_evidence import (
    AtlasCanonicalHeadHeadRatioAnthropometricQualityEvidence,
)


def test_defines_exact_item9_9_criteria():
    assert AtlasCanonicalHeadHeadRatioAnthropometricQualityEvidence.CRITERIA == (
        "facial_width_height",
        "bizygomatic_relation",
        "bigonial_relation",
        "interocular_relation",
        "nose_width_height",
        "mouth_width",
        "upper_lower_facial_proportions",
        "cranial_to_facial_relationship",
    )


def test_defines_exact_evaluation_spaces():
    assert AtlasCanonicalHeadHeadRatioAnthropometricQualityEvidence.EVALUATION_SPACES == (
        "2d_observation",
        "canonical_model",
        "metric_3d_ground_truth",
        "physical_output",
    )


def test_defines_exact_evidence_statuses():
    assert AtlasCanonicalHeadHeadRatioAnthropometricQualityEvidence.EVIDENCE_STATUSES == (
        "bounded_2d_observation_only",
        "blocked",
    )


def test_defines_exact_evidence_origins():
    assert AtlasCanonicalHeadHeadRatioAnthropometricQualityEvidence.EVIDENCE_ORIGINS == (
        "directly_observed",
        "multiview_constrained",
        "model_prior_inferred",
        "generated_completion",
        "unresolved",
    )


@pytest.mark.parametrize(
    "criterion",
    (
        "facial_width_height",
        "bigonial_relation",
        "interocular_relation",
        "nose_width_height",
        "mouth_width",
    ),
)
def test_accepts_bounded_2d_observation_only_criteria(criterion):
    evidence = AtlasCanonicalHeadHeadRatioAnthropometricQualityEvidence(
        criterion=criterion,
        evaluation_space="2d_observation",
        evidence_status="bounded_2d_observation_only",
        evidence_origin="DIRECTLY_OBSERVED",
        source_measurement="deterministic frontal portrait landmark measurement",
        semantic_scope="2D frontal landmark-derived proportion or surrogate only",
        permitted_claim=(
            "criterion has bounded subject-specific 2D observation-space support"
        ),
        prohibited_claims=(
            "metric 3D anthropometric truth",
            "canonical surface accuracy",
            "population average used as identity target",
        ),
        bounded_interpretation=(
            "support is limited to deterministic frontal landmark geometry"
        ),
    )

    assert evidence.criterion == criterion
    assert evidence.evidence_status == "bounded_2d_observation_only"
    assert evidence.evidence_origin == "directly_observed"


@pytest.mark.parametrize(
    "criterion",
    (
        "bizygomatic_relation",
        "upper_lower_facial_proportions",
        "cranial_to_facial_relationship",
    ),
)
def test_accepts_blocked_criteria(criterion):
    evidence = AtlasCanonicalHeadHeadRatioAnthropometricQualityEvidence(
        criterion=criterion,
        evaluation_space="metric_3d_ground_truth",
        evidence_status="blocked",
        evidence_origin="UNRESOLVED",
        source_measurement="no verified subject-specific criterion measurement",
        semantic_scope="criterion-specific anthropometric relation unresolved",
        permitted_claim="criterion remains blocked",
        prohibited_claims=(
            "population reference promoted to identity target",
            "surrogate measurement promoted to anatomical ground truth",
            "metric millimetre accuracy",
        ),
        bounded_interpretation=(
            "no verified subject-specific evidence currently establishes this relation"
        ),
    )

    assert evidence.evidence_status == "blocked"
    assert evidence.evidence_origin == "unresolved"


def test_nose_width_height_can_express_unresolved_denominator_semantics():
    evidence = AtlasCanonicalHeadHeadRatioAnthropometricQualityEvidence(
        criterion="nose_width_height",
        evaluation_space="2d_observation",
        evidence_status="bounded_2d_observation_only",
        evidence_origin="directly_observed",
        source_measurement="nose_width and nose_length frontal landmarks",
        semantic_scope=(
            "2D observation support exists; exact Item 9.9 denominator semantics unresolved"
        ),
        permitted_claim="bounded 2D frontal ratio support only",
        prohibited_claims=(
            "fixed anthropometric denominator semantics",
            "metric 3D anatomical ratio",
        ),
        bounded_interpretation=(
            "measurement ingredients exist but protocol-level denominator is not yet fixed"
        ),
    )

    assert "denominator" in evidence.semantic_scope


def test_rejects_unknown_criterion():
    with pytest.raises(ValueError, match="criterion"):
        AtlasCanonicalHeadHeadRatioAnthropometricQualityEvidence(
            criterion="head_ratio",
            evaluation_space="2d_observation",
            evidence_status="blocked",
            evidence_origin="unresolved",
            source_measurement="source",
            semantic_scope="scope",
            permitted_claim="blocked",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="unresolved",
        )


def test_rejects_unknown_evaluation_space():
    with pytest.raises(ValueError, match="evaluation_space"):
        AtlasCanonicalHeadHeadRatioAnthropometricQualityEvidence(
            criterion="facial_width_height",
            evaluation_space="3d",
            evidence_status="blocked",
            evidence_origin="unresolved",
            source_measurement="source",
            semantic_scope="scope",
            permitted_claim="blocked",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="unresolved",
        )


def test_rejects_unknown_evidence_status():
    with pytest.raises(ValueError, match="evidence_status"):
        AtlasCanonicalHeadHeadRatioAnthropometricQualityEvidence(
            criterion="facial_width_height",
            evaluation_space="2d_observation",
            evidence_status="pass",
            evidence_origin="unresolved",
            source_measurement="source",
            semantic_scope="scope",
            permitted_claim="blocked",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="unresolved",
        )


def test_rejects_unknown_evidence_origin():
    with pytest.raises(ValueError, match="evidence_origin"):
        AtlasCanonicalHeadHeadRatioAnthropometricQualityEvidence(
            criterion="facial_width_height",
            evaluation_space="2d_observation",
            evidence_status="blocked",
            evidence_origin="observed",
            source_measurement="source",
            semantic_scope="scope",
            permitted_claim="blocked",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="unresolved",
        )


def test_contract_is_immutable():
    evidence = AtlasCanonicalHeadHeadRatioAnthropometricQualityEvidence(
        criterion="facial_width_height",
        evaluation_space="2d_observation",
        evidence_status="bounded_2d_observation_only",
        evidence_origin="directly_observed",
        source_measurement="source",
        semantic_scope="scope",
        permitted_claim="bounded",
        prohibited_claims=("unsupported claim",),
        bounded_interpretation="bounded",
    )

    with pytest.raises(FrozenInstanceError):
        evidence.evidence_status = "blocked"


def test_contract_does_not_claim_threshold_metric_or_phase_decision():
    evidence = AtlasCanonicalHeadHeadRatioAnthropometricQualityEvidence(
        criterion="facial_width_height",
        evaluation_space="2d_observation",
        evidence_status="bounded_2d_observation_only",
        evidence_origin="directly_observed",
        source_measurement="source",
        semantic_scope="scope",
        permitted_claim="bounded",
        prohibited_claims=("unsupported claim",),
        bounded_interpretation="bounded",
    )

    assert not hasattr(evidence, "population_target")
    assert not hasattr(evidence, "threshold")
    assert not hasattr(evidence, "metric_accuracy_mm")
    assert not hasattr(evidence, "confidence_score")
    assert not hasattr(evidence, "decision")
    assert not hasattr(evidence, "phase_9_authorized")
