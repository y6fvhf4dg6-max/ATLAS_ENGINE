from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_cross_region_compensation_evidence import (
    AtlasCanonicalHeadCrossRegionCompensationEvidence,
)


def test_defines_exact_item9_11_criteria():
    assert AtlasCanonicalHeadCrossRegionCompensationEvidence.CRITERIA == (
        "global_improvement_with_local_degradation",
        "camera_compensation",
        "pose_compensation",
        "cross_region_compensation",
        "alignment_concealing_local_failure",
    )


def test_defines_exact_evaluation_spaces():
    assert AtlasCanonicalHeadCrossRegionCompensationEvidence.EVALUATION_SPACES == (
        "2d_observation",
        "canonical_model",
        "metric_3d_ground_truth",
        "physical_output",
    )


def test_defines_exact_evidence_statuses():
    assert AtlasCanonicalHeadCrossRegionCompensationEvidence.EVIDENCE_STATUSES == (
        "bounded_positive",
        "bounded_mixed",
        "not_established_as_primary_explanation",
    )


def test_defines_exact_evidence_origins():
    assert AtlasCanonicalHeadCrossRegionCompensationEvidence.EVIDENCE_ORIGINS == (
        "directly_observed",
        "multiview_constrained",
        "model_prior_inferred",
        "generated_completion",
        "unresolved",
    )


@pytest.mark.parametrize(
    ("criterion", "status"),
    (
        ("global_improvement_with_local_degradation", "bounded_positive"),
        ("camera_compensation", "bounded_positive"),
        ("pose_compensation", "not_established_as_primary_explanation"),
        ("cross_region_compensation", "bounded_mixed"),
        ("alignment_concealing_local_failure", "bounded_positive"),
    ),
)
def test_accepts_exact_item9_11_criterion_status_pairs(criterion, status):
    evidence = AtlasCanonicalHeadCrossRegionCompensationEvidence(
        criterion=criterion,
        evaluation_space="2d_observation",
        evidence_status=status,
        evidence_origin="MULTIVIEW_CONSTRAINED",
        source_reference="persisted Item8/9 evidence",
        semantic_scope="held-out observation-space compensation audit",
        permitted_claim="bounded Item 9.11 evidence only",
        prohibited_claims=(
            "metric 3d anatomical correctness",
            "uniform regional success",
            "global absence of optimizer leakage",
        ),
        bounded_interpretation="interpretation remains limited to the tested evidence path",
    )

    assert evidence.criterion == criterion
    assert evidence.evidence_status == status
    assert evidence.evidence_origin == "multiview_constrained"


def test_global_improvement_can_coexist_with_local_degradation():
    evidence = AtlasCanonicalHeadCrossRegionCompensationEvidence(
        criterion="global_improvement_with_local_degradation",
        evaluation_space="2d_observation",
        evidence_status="bounded_positive",
        evidence_origin="multiview_constrained",
        source_reference=(
            "REPRODUCIBILITY_HELD_OUT.json + "
            "REPRODUCIBILITY_ITEM8_9_REGION_WISE.json"
        ),
        semantic_scope=(
            "3/3 held-out global IOD-NME and bbox-NME improve while "
            "21 region-view comparisons contain 12 improvements and 9 degradations"
        ),
        permitted_claim=(
            "global held-out improvement coexists with local regional degradation"
        ),
        prohibited_claims=(
            "global improvement proves uniform facial-region improvement",
            "local 2d degradation proves metric 3d anatomical degradation",
            "phase decision",
        ),
        bounded_interpretation=(
            "nose_body degrades in all 3/3 held-out views despite positive global metrics"
        ),
    )

    assert evidence.evidence_status == "bounded_positive"


def test_camera_compensation_is_bounded_observation_space_evidence():
    evidence = AtlasCanonicalHeadCrossRegionCompensationEvidence(
        criterion="camera_compensation",
        evaluation_space="2d_observation",
        evidence_status="bounded_positive",
        evidence_origin="directly_observed",
        source_reference="ITEM8_H1_ANALYTIC_CAMERA_COMPENSATION_ISOLATION.json",
        semantic_scope=(
            "geometry-conditioned analytic weak-perspective camera compensation "
            "measured in front, turn-left, and turn-right"
        ),
        permitted_claim=(
            "analytic camera re-solving reduces a material portion of tested "
            "geometry-conditioned nose_body reprojection error"
        ),
        prohibited_claims=(
            "camera compensation proves physical 3d correction",
            "camera compensation equals structural identity-camera leakage",
            "all camera models behave equivalently",
        ),
        bounded_interpretation=(
            "camera compensation is verified for the persisted weak-perspective "
            "observation-space evaluation path"
        ),
    )

    assert evidence.evidence_status == "bounded_positive"


def test_pose_is_not_established_as_primary_three_view_explanation():
    evidence = AtlasCanonicalHeadCrossRegionCompensationEvidence(
        criterion="pose_compensation",
        evaluation_space="2d_observation",
        evidence_status="not_established_as_primary_explanation",
        evidence_origin="multiview_constrained",
        source_reference=(
            "ITEM8_H1_POSE_REGIONAL_REGRESSION_DIAGNOSIS.json + "
            "ITEM8_H3_POSE_ONLY_COUNTERFACTUAL_STRESS_RESULT.json"
        ),
        semantic_scope="three-view nose_body regression and pose-only counterfactuals",
        permitted_claim=(
            "pose-only effects do not establish the complete three-view "
            "nose_body regression pattern as pose-driven"
        ),
        prohibited_claims=(
            "pose has no effect",
            "complete absence of identity-pose leakage in every future optimizer",
            "pose counterfactual proves metric anatomy",
        ),
        bounded_interpretation=(
            "tested H3 pose changes preserve canonical identity state exactly, "
            "while H1 does not support pose as the primary explanation"
        ),
    )

    assert evidence.evidence_status == "not_established_as_primary_explanation"


def test_cross_region_tradeoff_does_not_claim_region_to_region_causality():
    evidence = AtlasCanonicalHeadCrossRegionCompensationEvidence(
        criterion="cross_region_compensation",
        evaluation_space="2d_observation",
        evidence_status="bounded_mixed",
        evidence_origin="multiview_constrained",
        source_reference="REPRODUCIBILITY_ITEM8_9_REGION_WISE.json",
        semantic_scope=(
            "same candidate contains regional improvements and degradations "
            "across held-out views"
        ),
        permitted_claim="measurable cross-region performance trade-off is present",
        prohibited_claims=(
            "one facial region causally compensates for another region",
            "regional trade-off proves 3d anatomical transfer",
            "aggregate score may hide a material regional blocker",
        ),
        bounded_interpretation=(
            "cross-region compensation is descriptive mixed evidence, "
            "not a causal region-to-region mechanism claim"
        ),
    )

    assert evidence.evidence_status == "bounded_mixed"


def test_alignment_can_conceal_local_failure_only_with_bounded_claim():
    evidence = AtlasCanonicalHeadCrossRegionCompensationEvidence(
        criterion="alignment_concealing_local_failure",
        evaluation_space="2d_observation",
        evidence_status="bounded_positive",
        evidence_origin="multiview_constrained",
        source_reference=(
            "REPRODUCIBILITY_HELD_OUT.json + "
            "ITEM8_H1_ANALYTIC_CAMERA_COMPENSATION_ISOLATION.json"
        ),
        semantic_scope=(
            "held-out root-pose optimization plus analytic weak-perspective "
            "camera re-solving"
        ),
        permitted_claim=(
            "the tested nuisance/alignment evaluation chain can reduce aggregate "
            "reprojection error while local nose_body failure remains visible"
        ),
        prohibited_claims=(
            "all alignment methods conceal local failure",
            "alignment alone caused every regional degradation",
            "metric 3d surface failure proven",
        ),
        bounded_interpretation=(
            "claim is limited to the persisted pose-and-camera-resolved "
            "observation-space protocol"
        ),
    )

    assert evidence.evidence_status == "bounded_positive"


def test_contract_can_preserve_h3_optimizer_leakage_boundary():
    evidence = AtlasCanonicalHeadCrossRegionCompensationEvidence(
        criterion="camera_compensation",
        evaluation_space="canonical_model",
        evidence_status="bounded_positive",
        evidence_origin="multiview_constrained",
        source_reference="ITEM8_H3_OFFICIAL_CLOSURE.json",
        semantic_scope="tested FLAME forward-model structural nuisance separation",
        permitted_claim=(
            "tested camera-only counterfactual preserves identity state and fixed 3d geometry"
        ),
        prohibited_claims=(
            "unconstrained optimizer leakage globally ruled out",
            "identity refitting under nuisance was tested",
        ),
        bounded_interpretation=(
            "H3 explicitly did not test unconstrained identity refitting under nuisance stress"
        ),
    )

    assert "unconstrained optimizer leakage globally ruled out" in evidence.prohibited_claims


def test_rejects_unknown_criterion():
    with pytest.raises(ValueError, match="criterion"):
        AtlasCanonicalHeadCrossRegionCompensationEvidence(
            criterion="compensation",
            evaluation_space="2d_observation",
            evidence_status="bounded_mixed",
            evidence_origin="unresolved",
            source_reference="source",
            semantic_scope="scope",
            permitted_claim="bounded",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="bounded",
        )


def test_rejects_unknown_evaluation_space():
    with pytest.raises(ValueError, match="evaluation_space"):
        AtlasCanonicalHeadCrossRegionCompensationEvidence(
            criterion="cross_region_compensation",
            evaluation_space="3d",
            evidence_status="bounded_mixed",
            evidence_origin="unresolved",
            source_reference="source",
            semantic_scope="scope",
            permitted_claim="bounded",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="bounded",
        )


def test_rejects_unknown_evidence_status():
    with pytest.raises(ValueError, match="evidence_status"):
        AtlasCanonicalHeadCrossRegionCompensationEvidence(
            criterion="cross_region_compensation",
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
        AtlasCanonicalHeadCrossRegionCompensationEvidence(
            criterion="cross_region_compensation",
            evaluation_space="2d_observation",
            evidence_status="bounded_mixed",
            evidence_origin="observed",
            source_reference="source",
            semantic_scope="scope",
            permitted_claim="bounded",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="bounded",
        )


def test_contract_is_immutable():
    evidence = AtlasCanonicalHeadCrossRegionCompensationEvidence(
        criterion="cross_region_compensation",
        evaluation_space="2d_observation",
        evidence_status="bounded_mixed",
        evidence_origin="multiview_constrained",
        source_reference="source",
        semantic_scope="scope",
        permitted_claim="bounded",
        prohibited_claims=("unsupported claim",),
        bounded_interpretation="bounded",
    )

    with pytest.raises(FrozenInstanceError):
        evidence.evidence_status = "bounded_positive"


def test_contract_does_not_claim_metric_threshold_causality_or_phase_decision():
    evidence = AtlasCanonicalHeadCrossRegionCompensationEvidence(
        criterion="cross_region_compensation",
        evaluation_space="2d_observation",
        evidence_status="bounded_mixed",
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
    assert not hasattr(evidence, "causal_region_source")
    assert not hasattr(evidence, "decision")
    assert not hasattr(evidence, "phase_9_authorized")
