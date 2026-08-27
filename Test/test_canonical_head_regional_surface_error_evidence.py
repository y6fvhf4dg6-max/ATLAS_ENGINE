from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_regional_surface_error_evidence import (
    AtlasCanonicalHeadRegionalSurfaceErrorEvidence,
)


def test_defines_exact_item9_12_criteria():
    assert AtlasCanonicalHeadRegionalSurfaceErrorEvidence.CRITERIA == (
        "point_to_surface_distance",
        "bidirectional_symmetric_surface_error",
        "mean_distance",
        "median_distance",
        "rms_distance",
        "p95_distance",
        "maximum_outlier_characterization",
        "surface_normal_discrepancy",
        "real_metric_regional_result",
    )


def test_defines_exact_evaluation_spaces():
    assert AtlasCanonicalHeadRegionalSurfaceErrorEvidence.EVALUATION_SPACES == (
        "metric_3d_ground_truth",
        "canonical_model",
    )


def test_defines_exact_evidence_statuses():
    assert AtlasCanonicalHeadRegionalSurfaceErrorEvidence.EVIDENCE_STATUSES == (
        "capability_present",
        "capability_present_metric_result_blocked",
        "blocked",
        "not_established",
    )


def test_defines_exact_blocker_states():
    assert AtlasCanonicalHeadRegionalSurfaceErrorEvidence.BLOCKER_STATES == (
        "alignment_inadmissible",
        "regional_correspondence_unverified",
        "region_mapping_unverified",
        "metric_ground_truth_unavailable",
        "none",
    )


def test_defines_exact_supported_raw_metric_families():
    assert AtlasCanonicalHeadRegionalSurfaceErrorEvidence.SUPPORTED_RAW_METRIC_FAMILIES == (
        "point_to_surface_distance",
        "mean",
        "median",
        "rms",
        "p95",
        "maximum",
    )


def test_accepts_capability_present_metric_result_blocked_evidence():
    evidence = AtlasCanonicalHeadRegionalSurfaceErrorEvidence(
        criterion="real_metric_regional_result",
        evaluation_space="metric_3d_ground_truth",
        evidence_status="CAPABILITY_PRESENT_METRIC_RESULT_BLOCKED",
        blocker_states=(
            "alignment_inadmissible",
            "regional_correspondence_unverified",
            "region_mapping_unverified",
        ),
        source_reference=(
            "HSRD Metric-GT HOLD closure + "
            "AtlasCanonicalHeadMetricPointToSurfaceDistance + "
            "AtlasCanonicalHeadMetricRegionDistanceAggregate"
        ),
        semantic_scope=(
            "real subject-specific regional surface error in millimetres"
        ),
        permitted_claim=(
            "ATLAS has regional surface-error measurement capability, "
            "but real metric regional results remain blocked"
        ),
        prohibited_claims=(
            "jaw millimetre error",
            "nose millimetre error",
            "orbital millimetre error",
            "cheek millimetre error",
            "real subject-specific surface accuracy",
        ),
        bounded_interpretation=(
            "measurement capability exists, while HSRD A03 remains "
            "inadmissible for strict-face metric execution"
        ),
    )

    assert evidence.evidence_status == "capability_present_metric_result_blocked"
    assert evidence.blocker_states == (
        "alignment_inadmissible",
        "regional_correspondence_unverified",
        "region_mapping_unverified",
    )


@pytest.mark.parametrize(
    ("criterion", "status"),
    (
        ("point_to_surface_distance", "capability_present"),
        ("mean_distance", "capability_present"),
        ("median_distance", "capability_present"),
        ("rms_distance", "capability_present"),
        ("p95_distance", "capability_present"),
        ("maximum_outlier_characterization", "capability_present"),
        ("bidirectional_symmetric_surface_error", "not_established"),
        ("surface_normal_discrepancy", "not_established"),
        (
            "real_metric_regional_result",
            "capability_present_metric_result_blocked",
        ),
    ),
)
def test_accepts_item9_12_criterion_status_pairs(criterion, status):
    blockers = (
        ("none",)
        if status == "capability_present"
        else (
            "alignment_inadmissible",
            "regional_correspondence_unverified",
            "region_mapping_unverified",
        )
        if status == "capability_present_metric_result_blocked"
        else ("none",)
    )

    evidence = AtlasCanonicalHeadRegionalSurfaceErrorEvidence(
        criterion=criterion,
        evaluation_space="metric_3d_ground_truth",
        evidence_status=status,
        blocker_states=blockers,
        source_reference="persisted metric capability / HSRD evidence",
        semantic_scope="Item 9.12 bounded evidence",
        permitted_claim="bounded Item 9.12 claim only",
        prohibited_claims=(
            "unverified millimetre accuracy",
            "unsupported real subject-specific regional surface accuracy",
        ),
        bounded_interpretation="claim remains bounded to verified evidence",
    )

    assert evidence.criterion == criterion
    assert evidence.evidence_status == status


def test_point_to_surface_capability_does_not_imply_real_gt_execution():
    evidence = AtlasCanonicalHeadRegionalSurfaceErrorEvidence(
        criterion="point_to_surface_distance",
        evaluation_space="canonical_model",
        evidence_status="capability_present",
        blocker_states=("none",),
        source_reference="AtlasCanonicalHeadMetricPointToSurfaceDistance",
        semantic_scope="provider-independent point-to-triangle distance implementation",
        permitted_claim="raw point-to-surface measurement capability exists",
        prohibited_claims=(
            "real HSRD strict-face result was executed",
            "real subject-specific metric accuracy",
        ),
        bounded_interpretation=(
            "capability presence is not evidence of admissible real-GT execution"
        ),
    )

    assert "real HSRD strict-face result was executed" in evidence.prohibited_claims


def test_region_aggregate_requires_legitimate_region_mapping():
    evidence = AtlasCanonicalHeadRegionalSurfaceErrorEvidence(
        criterion="real_metric_regional_result",
        evaluation_space="metric_3d_ground_truth",
        evidence_status="capability_present_metric_result_blocked",
        blocker_states=(
            "regional_correspondence_unverified",
            "region_mapping_unverified",
        ),
        source_reference=(
            "AtlasCanonicalHeadMetricRegionDistanceAggregate + Item 10.9 boundary"
        ),
        semantic_scope="semantic region-wise metric aggregation",
        permitted_claim=(
            "region-wise aggregation capability requires explicit legitimate mapping"
        ),
        prohibited_claims=(
            "infer facial regions from geometry",
            "reuse anchor-supported FLAME regions as scan GT regions without validation",
        ),
        bounded_interpretation=(
            "metric region application remains blocked until correspondence "
            "and region mapping are legitimately established"
        ),
    )

    assert "region_mapping_unverified" in evidence.blocker_states


def test_hsrd_hold_is_not_geometry_failure_claim():
    evidence = AtlasCanonicalHeadRegionalSurfaceErrorEvidence(
        criterion="real_metric_regional_result",
        evaluation_space="metric_3d_ground_truth",
        evidence_status="capability_present_metric_result_blocked",
        blocker_states=("alignment_inadmissible",),
        source_reference="Phase 8.10 HSRD Metric-GT HOLD Closure",
        semantic_scope="HSRD A03 strict-face metric admissibility",
        permitted_claim=(
            "current A03 evidence cannot support a defensible strict-face "
            "millimetre error claim"
        ),
        prohibited_claims=(
            "FLAME geometry is poor",
            "strict-face millimetre error is known",
        ),
        bounded_interpretation=(
            "HOLD reflects inadmissible alignment, not a geometry-quality verdict"
        ),
    )

    assert evidence.evidence_status == "capability_present_metric_result_blocked"


def test_rejects_unknown_criterion():
    with pytest.raises(ValueError, match="criterion"):
        AtlasCanonicalHeadRegionalSurfaceErrorEvidence(
            criterion="regional_error",
            evaluation_space="metric_3d_ground_truth",
            evidence_status="blocked",
            blocker_states=("metric_ground_truth_unavailable",),
            source_reference="source",
            semantic_scope="scope",
            permitted_claim="bounded",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="bounded",
        )


def test_rejects_unknown_evaluation_space():
    with pytest.raises(ValueError, match="evaluation_space"):
        AtlasCanonicalHeadRegionalSurfaceErrorEvidence(
            criterion="real_metric_regional_result",
            evaluation_space="2d_observation",
            evidence_status="blocked",
            blocker_states=("metric_ground_truth_unavailable",),
            source_reference="source",
            semantic_scope="scope",
            permitted_claim="bounded",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="bounded",
        )


def test_rejects_unknown_evidence_status():
    with pytest.raises(ValueError, match="evidence_status"):
        AtlasCanonicalHeadRegionalSurfaceErrorEvidence(
            criterion="real_metric_regional_result",
            evaluation_space="metric_3d_ground_truth",
            evidence_status="pass",
            blocker_states=("metric_ground_truth_unavailable",),
            source_reference="source",
            semantic_scope="scope",
            permitted_claim="bounded",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="bounded",
        )


def test_rejects_unknown_blocker_state():
    with pytest.raises(ValueError, match="blocker_states"):
        AtlasCanonicalHeadRegionalSurfaceErrorEvidence(
            criterion="real_metric_regional_result",
            evaluation_space="metric_3d_ground_truth",
            evidence_status="blocked",
            blocker_states=("bad_alignment",),
            source_reference="source",
            semantic_scope="scope",
            permitted_claim="bounded",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="bounded",
        )


def test_contract_is_immutable():
    evidence = AtlasCanonicalHeadRegionalSurfaceErrorEvidence(
        criterion="real_metric_regional_result",
        evaluation_space="metric_3d_ground_truth",
        evidence_status="capability_present_metric_result_blocked",
        blocker_states=("alignment_inadmissible",),
        source_reference="source",
        semantic_scope="scope",
        permitted_claim="bounded",
        prohibited_claims=("unsupported claim",),
        bounded_interpretation="bounded",
    )

    with pytest.raises(FrozenInstanceError):
        evidence.evidence_status = "blocked"


def test_contract_does_not_add_metric_values_thresholds_or_phase_decision():
    evidence = AtlasCanonicalHeadRegionalSurfaceErrorEvidence(
        criterion="real_metric_regional_result",
        evaluation_space="metric_3d_ground_truth",
        evidence_status="capability_present_metric_result_blocked",
        blocker_states=("alignment_inadmissible",),
        source_reference="source",
        semantic_scope="scope",
        permitted_claim="bounded",
        prohibited_claims=("unsupported claim",),
        bounded_interpretation="bounded",
    )

    assert not hasattr(evidence, "mean_distance_mm")
    assert not hasattr(evidence, "median_distance_mm")
    assert not hasattr(evidence, "rms_distance_mm")
    assert not hasattr(evidence, "p95_distance_mm")
    assert not hasattr(evidence, "max_distance_mm")
    assert not hasattr(evidence, "threshold")
    assert not hasattr(evidence, "confidence_score")
    assert not hasattr(evidence, "decision")
    assert not hasattr(evidence, "phase_9_authorized")
