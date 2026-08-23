import pytest

from CORE.atlas_canonical_head_prnet_benchmark_evidence import (
    AtlasCanonicalHeadPrnetBenchmarkEvidence,
)


def test_records_prnet_candidate_identity_and_architecture_family():
    assert (
        AtlasCanonicalHeadPrnetBenchmarkEvidence.CANDIDATE_ID
        == "prnet"
    )
    assert (
        AtlasCanonicalHeadPrnetBenchmarkEvidence.ARCHITECTURE_FAMILY
        == "direct_neural_dense"
    )


def test_records_verified_prnet_topology():
    assert (
        AtlasCanonicalHeadPrnetBenchmarkEvidence.VERTEX_COUNT
        == 43867
    )
    assert (
        AtlasCanonicalHeadPrnetBenchmarkEvidence.TRIANGLE_COUNT
        == 86906
    )


def test_records_verified_silhouette_measurements():
    evidence = AtlasCanonicalHeadPrnetBenchmarkEvidence

    assert evidence.FRONT_CASE_COUNT == 2
    assert evidence.LATERAL_CASE_COUNT == 4

    assert evidence.FRONT_MEAN_IOU == pytest.approx(
        0.8580595773782285
    )
    assert evidence.LATERAL_MEAN_IOU == pytest.approx(
        0.7694332569672948
    )
    assert evidence.LATERAL_MIN_IOU == pytest.approx(
        0.7140243158622372
    )
    assert evidence.LATERAL_MEAN_ABSOLUTE_OFFSET == pytest.approx(
        0.5696098447867725
    )


def test_preserves_silhouette_measurement_interpretation_boundary():
    evidence = AtlasCanonicalHeadPrnetBenchmarkEvidence

    assert evidence.SILHOUETTE_REFERENCE_KIND == (
        "mediapipe_face_oval_projection"
    )
    assert evidence.SILHOUETTE_REFERENCE_IS_3D_GROUND_TRUTH is False
    assert evidence.SILHOUETTE_REFERENCE_IS_MANUAL_SEGMENTATION is False
    assert evidence.SIDE_CASES_CANONICALLY_CLASSIFIED_AS_PROFILE is False


def test_exposes_conservative_phase_8_10_evidence_coverage():
    coverage = (
        AtlasCanonicalHeadPrnetBenchmarkEvidence
        .coverage()
    )

    assert coverage.candidate_id == "prnet"

    assert coverage.identity_preservation_support == "MISSING"
    assert coverage.multi_view_consistency == "MISSING"

    assert coverage.silhouette_profile_support == "PARTIAL"

    assert coverage.head_ratio_support == "MISSING"
    assert coverage.jaw_chin_support == "MISSING"
    assert coverage.nose_projection_support == "MISSING"
    assert coverage.orbital_cheek_volume_support == "MISSING"
    assert coverage.expression_separation_support == "MISSING"
    assert coverage.pose_separation_support == "MISSING"

    assert coverage.topology_suitability == "DIRECT"
    assert coverage.physical_suitability == "MISSING"
    assert coverage.apple_silicon_runtime_support == "DIRECT"
    assert coverage.reproducibility_support == "DIRECT"


def test_catalog_does_not_expose_support_or_phase_9_decision():
    evidence = AtlasCanonicalHeadPrnetBenchmarkEvidence

    assert not hasattr(
        evidence,
        "candidate_observation",
    )
    assert not hasattr(
        evidence,
        "silhouette_profile_support",
    )
    assert not hasattr(
        evidence,
        "decision",
    )
    assert not hasattr(
        evidence,
        "phase_9_authorized",
    )


def test_coverage_does_not_fabricate_candidate_support():
    coverage = (
        AtlasCanonicalHeadPrnetBenchmarkEvidence
        .coverage()
    )

    assert not hasattr(
        coverage,
        "decision",
    )
    assert not hasattr(
        coverage,
        "phase_9_authorized",
    )
    assert not hasattr(
        coverage,
        "support_score",
    )
