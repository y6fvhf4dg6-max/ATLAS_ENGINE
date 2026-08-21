import pytest

from CORE.atlas_canonical_head_benchmark_candidate_gate import (
    AtlasCanonicalHeadBenchmarkCandidateGate,
)
from CORE.atlas_canonical_head_benchmark_candidate_observation import (
    AtlasCanonicalHeadBenchmarkCandidateObservation,
)


def _observation(**overrides):
    values = {
        "candidate_id": "hybrid-head-v1",
        "architecture_kind": "hybrid_canonical_detail",
        "identity_preservation_support": 0.90,
        "multi_view_consistency": 0.86,
        "silhouette_profile_support": 0.84,
        "head_ratio_support": 0.82,
        "jaw_chin_support": 0.80,
        "nose_projection_support": 0.81,
        "orbital_cheek_volume_support": 0.79,
        "expression_separation_support": 0.92,
        "pose_separation_support": 0.94,
        "topology_suitability": 0.96,
        "physical_suitability": 0.85,
        "apple_silicon_runtime_support": 0.88,
        "reproducibility_support": 0.90,
        "commercial_license_acceptable": True,
        "privacy_data_retention_acceptable": True,
        "model_weight_restrictions_acceptable": True,
        "dataset_restrictions_acceptable": True,
        "processing_time_seconds": 18.0,
        "processing_cost_eur": 0.05,
    }
    values.update(overrides)
    return AtlasCanonicalHeadBenchmarkCandidateObservation(**values)


def test_strong_candidate_returns_go():
    result = AtlasCanonicalHeadBenchmarkCandidateGate.evaluate(
        _observation()
    )

    assert result.decision == "GO"
    assert result.status == "ACCEPTED"
    assert result.blocked_reasons == ()
    assert result.failure_reasons == ()


@pytest.mark.parametrize(
    ("field_name", "expected_reason"),
    (
        (
            "commercial_license_acceptable",
            "BLOCKED_COMMERCIAL_LICENSE",
        ),
        (
            "privacy_data_retention_acceptable",
            "BLOCKED_PRIVACY_DATA_RETENTION",
        ),
        (
            "model_weight_restrictions_acceptable",
            "BLOCKED_MODEL_WEIGHT_RESTRICTIONS",
        ),
        (
            "dataset_restrictions_acceptable",
            "BLOCKED_DATASET_RESTRICTIONS",
        ),
    ),
)
def test_policy_failure_is_hard_reject(
    field_name,
    expected_reason,
):
    result = AtlasCanonicalHeadBenchmarkCandidateGate.evaluate(
        _observation(**{field_name: False})
    )

    assert result.decision == "REJECT"
    assert result.status == "BLOCKED"
    assert expected_reason in result.blocked_reasons


def test_weak_identity_preservation_is_rejected():
    result = AtlasCanonicalHeadBenchmarkCandidateGate.evaluate(
        _observation(
            identity_preservation_support=0.40,
        )
    )

    assert result.decision == "REJECT"
    assert result.status == "BLOCKED"
    assert result.failure_reasons == (
        "INSUFFICIENT_IDENTITY_PRESERVATION",
    )


def test_limited_anatomical_identity_evidence_returns_hold():
    result = AtlasCanonicalHeadBenchmarkCandidateGate.evaluate(
        _observation(
            jaw_chin_support=0.62,
        )
    )

    assert result.decision == "HOLD"
    assert result.status == "BLOCKED"
    assert result.failure_reasons == (
        "LIMITED_JAW_CHIN_SUPPORT",
    )


def test_limited_runtime_support_returns_hold():
    result = AtlasCanonicalHeadBenchmarkCandidateGate.evaluate(
        _observation(
            apple_silicon_runtime_support=0.60,
        )
    )

    assert result.decision == "HOLD"
    assert result.status == "BLOCKED"
    assert result.failure_reasons == (
        "LIMITED_APPLE_SILICON_RUNTIME_SUPPORT",
    )


def test_limited_reproducibility_returns_hold():
    result = AtlasCanonicalHeadBenchmarkCandidateGate.evaluate(
        _observation(
            reproducibility_support=0.65,
        )
    )

    assert result.decision == "HOLD"
    assert result.status == "BLOCKED"
    assert result.failure_reasons == (
        "LIMITED_REPRODUCIBILITY_SUPPORT",
    )


def test_high_landmark_like_geometric_channels_cannot_override_bad_topology():
    result = AtlasCanonicalHeadBenchmarkCandidateGate.evaluate(
        _observation(
            identity_preservation_support=1.0,
            multi_view_consistency=1.0,
            silhouette_profile_support=1.0,
            topology_suitability=0.40,
        )
    )

    assert result.decision == "REJECT"
    assert result.failure_reasons == (
        "INSUFFICIENT_TOPOLOGY_SUITABILITY",
    )


def test_multiple_failures_are_reported_deterministically():
    result = AtlasCanonicalHeadBenchmarkCandidateGate.evaluate(
        _observation(
            jaw_chin_support=0.60,
            physical_suitability=0.62,
            reproducibility_support=0.61,
        )
    )

    assert result.decision == "HOLD"
    assert result.failure_reasons == (
        "LIMITED_JAW_CHIN_SUPPORT",
        "LIMITED_PHYSICAL_SUITABILITY",
        "LIMITED_REPRODUCIBILITY_SUPPORT",
    )


def test_rejects_wrong_observation_type():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadBenchmarkCandidateObservation",
    ):
        AtlasCanonicalHeadBenchmarkCandidateGate.evaluate({})


def test_result_does_not_claim_selected_provider_or_geometry():
    result = AtlasCanonicalHeadBenchmarkCandidateGate.evaluate(
        _observation()
    )

    assert not hasattr(result, "selected_candidate")
    assert not hasattr(result, "provider_id")
    assert not hasattr(result, "vertices")
    assert not hasattr(result, "faces")


def test_quality_just_below_reject_threshold_is_rejected():
    result = AtlasCanonicalHeadBenchmarkCandidateGate.evaluate(
        _observation(
            identity_preservation_support=0.499999,
        )
    )

    assert result.decision == "REJECT"
    assert result.failure_reasons == (
        "INSUFFICIENT_IDENTITY_PRESERVATION",
    )


def test_quality_at_reject_threshold_is_hold():
    result = AtlasCanonicalHeadBenchmarkCandidateGate.evaluate(
        _observation(
            identity_preservation_support=0.50,
        )
    )

    assert result.decision == "HOLD"
    assert result.failure_reasons == (
        "LIMITED_IDENTITY_PRESERVATION",
    )


def test_all_quality_channels_at_go_threshold_are_accepted():
    observation = _observation(
        identity_preservation_support=0.70,
        multi_view_consistency=0.70,
        silhouette_profile_support=0.70,
        head_ratio_support=0.70,
        jaw_chin_support=0.70,
        nose_projection_support=0.70,
        orbital_cheek_volume_support=0.70,
        expression_separation_support=0.70,
        pose_separation_support=0.70,
        topology_suitability=0.70,
        physical_suitability=0.70,
        apple_silicon_runtime_support=0.70,
        reproducibility_support=0.70,
    )

    result = AtlasCanonicalHeadBenchmarkCandidateGate.evaluate(
        observation
    )

    assert result.decision == "GO"
    assert result.status == "ACCEPTED"


def test_policy_blocker_overrides_perfect_quality():
    result = AtlasCanonicalHeadBenchmarkCandidateGate.evaluate(
        _observation(
            identity_preservation_support=1.0,
            multi_view_consistency=1.0,
            silhouette_profile_support=1.0,
            head_ratio_support=1.0,
            jaw_chin_support=1.0,
            nose_projection_support=1.0,
            orbital_cheek_volume_support=1.0,
            expression_separation_support=1.0,
            pose_separation_support=1.0,
            topology_suitability=1.0,
            physical_suitability=1.0,
            apple_silicon_runtime_support=1.0,
            reproducibility_support=1.0,
            commercial_license_acceptable=False,
        )
    )

    assert result.decision == "REJECT"
    assert result.status == "BLOCKED"
    assert result.blocked_reasons == (
        "BLOCKED_COMMERCIAL_LICENSE",
    )
