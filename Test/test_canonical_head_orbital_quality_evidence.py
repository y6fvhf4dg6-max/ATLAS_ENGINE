from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_orbital_quality_evidence import (
    AtlasCanonicalHeadOrbitalQualityEvidence,
)


def test_defines_exact_item9_5_criteria():
    assert AtlasCanonicalHeadOrbitalQualityEvidence.CRITERIA == (
        "inter_orbital_relation",
        "orbital_rim",
        "eye_socket_form_depth",
        "upper_orbital_contour",
        "lower_orbital_contour",
        "left_right_asymmetry",
        "eye_region_nose_bridge_relation",
    )


def test_defines_exact_evaluation_spaces():
    assert AtlasCanonicalHeadOrbitalQualityEvidence.EVALUATION_SPACES == (
        "2d_observation",
        "canonical_model",
        "metric_3d_ground_truth",
        "physical_output",
    )


def test_defines_exact_evidence_statuses():
    assert AtlasCanonicalHeadOrbitalQualityEvidence.EVIDENCE_STATUSES == (
        "bounded_not_established",
        "blocked",
    )


def test_defines_exact_evidence_origins():
    assert AtlasCanonicalHeadOrbitalQualityEvidence.EVIDENCE_ORIGINS == (
        "directly_observed",
        "multiview_constrained",
        "model_prior_inferred",
        "generated_completion",
        "unresolved",
    )


def test_accepts_bounded_inter_orbital_relation_evidence():
    evidence = AtlasCanonicalHeadOrbitalQualityEvidence(
        criterion="inter_orbital_relation",
        evaluation_space="2d_observation",
        evidence_status="bounded_not_established",
        evidence_origin="MULTIVIEW_CONSTRAINED",
        source_reference="REPRODUCIBILITY_ITEM8_9_REGION_WISE.json",
        permitted_claim=(
            "bounded left/right eye-region reprojection evidence exists"
        ),
        prohibited_claims=(
            "subject-specific orbital anatomy accuracy",
            "metric inter-orbital distance",
            "orbital rim accuracy",
        ),
        bounded_interpretation=(
            "both eye regions have full static105 support and held-out "
            "view-specific reprojection measurements, but no explicit "
            "inter-orbital quality metric exists"
        ),
    )

    assert evidence.criterion == "inter_orbital_relation"
    assert evidence.evidence_status == "bounded_not_established"
    assert evidence.evidence_origin == "multiview_constrained"


@pytest.mark.parametrize(
    "criterion",
    (
        "orbital_rim",
        "eye_socket_form_depth",
        "upper_orbital_contour",
        "lower_orbital_contour",
    ),
)
def test_accepts_blocked_orbital_anatomy_criteria_without_promoting_eye_region(
    criterion,
):
    evidence = AtlasCanonicalHeadOrbitalQualityEvidence(
        criterion=criterion,
        evaluation_space="metric_3d_ground_truth",
        evidence_status="blocked",
        evidence_origin="UNRESOLVED",
        source_reference="Item 9.5 specialized orbital evidence audit",
        permitted_claim=(
            "criterion remains blocked by missing orbital-specific evidence"
        ),
        prohibited_claims=(
            "eye_region relabelled as orbital anatomy",
            "fabricated orbital measurement",
            "metric millimetre accuracy",
        ),
        bounded_interpretation=(
            "provider eye-region masks and parametric eye-socket priors do not "
            "establish criterion-specific orbital anatomy quality"
        ),
    )

    assert evidence.evidence_status == "blocked"


def test_accepts_bounded_left_right_asymmetry_evidence():
    evidence = AtlasCanonicalHeadOrbitalQualityEvidence(
        criterion="left_right_asymmetry",
        evaluation_space="2d_observation",
        evidence_status="bounded_not_established",
        evidence_origin="MULTIVIEW_CONSTRAINED",
        source_reference="REPRODUCIBILITY_ITEM8_9_REGION_WISE.json",
        permitted_claim=(
            "left and right eye-region reprojection behavior differs by view"
        ),
        prohibited_claims=(
            "subject-specific anatomical asymmetry established",
            "metric orbital asymmetry",
            "bilateral orbital accuracy",
        ),
        bounded_interpretation=(
            "held-out eye-region error deltas differ between left and right "
            "channels, but no anatomical asymmetry quality metric exists"
        ),
    )

    assert evidence.evidence_status == "bounded_not_established"


def test_accepts_bounded_eye_region_nose_bridge_relation_evidence():
    evidence = AtlasCanonicalHeadOrbitalQualityEvidence(
        criterion="eye_region_nose_bridge_relation",
        evaluation_space="2d_observation",
        evidence_status="bounded_not_established",
        evidence_origin="MULTIVIEW_CONSTRAINED",
        source_reference="REPRODUCIBILITY_ITEM8_9_REGION_WISE.json",
        permitted_claim=(
            "eye-region and nose-bridge channels are separately observed"
        ),
        prohibited_claims=(
            "explicit eye-to-nose spatial relation established",
            "metric 3d relation accuracy",
            "orbital anatomy correctness",
        ),
        bounded_interpretation=(
            "left/right eye regions and nose_bridge have separate held-out "
            "reprojection evidence, but no explicit spatial-relation metric exists"
        ),
    )

    assert evidence.evidence_status == "bounded_not_established"


def test_rejects_unknown_criterion():
    with pytest.raises(ValueError, match="criterion"):
        AtlasCanonicalHeadOrbitalQualityEvidence(
            criterion="eye_quality",
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
        AtlasCanonicalHeadOrbitalQualityEvidence(
            criterion="orbital_rim",
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
        AtlasCanonicalHeadOrbitalQualityEvidence(
            criterion="orbital_rim",
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
        AtlasCanonicalHeadOrbitalQualityEvidence(
            criterion="orbital_rim",
            evaluation_space="canonical_model",
            evidence_status="blocked",
            evidence_origin="observed",
            source_reference="source",
            permitted_claim="blocked",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="unresolved",
        )


def test_contract_is_immutable():
    evidence = AtlasCanonicalHeadOrbitalQualityEvidence(
        criterion="orbital_rim",
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
    evidence = AtlasCanonicalHeadOrbitalQualityEvidence(
        criterion="orbital_rim",
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
