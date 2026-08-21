import pytest

from CORE.atlas_canonical_head_benchmark_candidate_observation import (
    AtlasCanonicalHeadBenchmarkCandidateObservation,
)
from CORE.atlas_canonical_head_benchmark_decision_gate import (
    AtlasCanonicalHeadBenchmarkDecisionGate,
)


def _candidate(
    candidate_id,
    architecture_kind,
    **overrides,
):
    values = {
        "candidate_id": candidate_id,
        "architecture_kind": architecture_kind,
        "identity_preservation_support": 0.82,
        "multi_view_consistency": 0.82,
        "silhouette_profile_support": 0.82,
        "head_ratio_support": 0.82,
        "jaw_chin_support": 0.82,
        "nose_projection_support": 0.82,
        "orbital_cheek_volume_support": 0.82,
        "expression_separation_support": 0.82,
        "pose_separation_support": 0.82,
        "topology_suitability": 0.82,
        "physical_suitability": 0.82,
        "apple_silicon_runtime_support": 0.82,
        "reproducibility_support": 0.82,
        "commercial_license_acceptable": True,
        "privacy_data_retention_acceptable": True,
        "model_weight_restrictions_acceptable": True,
        "dataset_restrictions_acceptable": True,
        "processing_time_seconds": 20.0,
        "processing_cost_eur": 0.05,
    }
    values.update(overrides)
    return AtlasCanonicalHeadBenchmarkCandidateObservation(
        **values
    )


def _complete_benchmark(**hybrid_overrides):
    return (
        _candidate(
            "parametric-v1",
            "parametric_fixed_topology",
            identity_preservation_support=0.76,
        ),
        _candidate(
            "neural-v1",
            "direct_neural_dense",
            topology_suitability=0.62,
        ),
        _candidate(
            "hybrid-v1",
            "hybrid_canonical_detail",
            identity_preservation_support=0.90,
            topology_suitability=0.94,
            physical_suitability=0.90,
            reproducibility_support=0.91,
            **hybrid_overrides,
        ),
    )


def test_complete_benchmark_selects_best_go_candidate():
    result = AtlasCanonicalHeadBenchmarkDecisionGate.evaluate(
        _complete_benchmark()
    )

    assert result.decision == "GO"
    assert result.status == "LOCK_READY"
    assert result.selected_candidate_id == "hybrid-v1"
    assert (
        result.selected_architecture_kind
        == "hybrid_canonical_detail"
    )
    assert result.blocked_reasons == ()


def test_requires_all_three_architecture_classes():
    candidates = _complete_benchmark()[:2]

    result = AtlasCanonicalHeadBenchmarkDecisionGate.evaluate(
        candidates
    )

    assert result.decision == "HOLD"
    assert result.status == "BLOCKED"
    assert result.selected_candidate_id is None
    assert result.blocked_reasons == (
        "BLOCKED_INCOMPLETE_CANONICAL_BENCHMARK",
    )


def test_rejects_duplicate_architecture_class():
    candidates = (
        _candidate(
            "parametric-a",
            "parametric_fixed_topology",
        ),
        _candidate(
            "parametric-b",
            "parametric_fixed_topology",
        ),
        _candidate(
            "hybrid-v1",
            "hybrid_canonical_detail",
        ),
    )

    with pytest.raises(
        ValueError,
        match="architecture_kind",
    ):
        AtlasCanonicalHeadBenchmarkDecisionGate.evaluate(
            candidates
        )


def test_no_go_candidate_cannot_open_phase_9():
    candidates = tuple(
        _candidate(
            candidate_id,
            architecture_kind,
            identity_preservation_support=0.60,
        )
        for candidate_id, architecture_kind in (
            (
                "parametric-v1",
                "parametric_fixed_topology",
            ),
            (
                "neural-v1",
                "direct_neural_dense",
            ),
            (
                "hybrid-v1",
                "hybrid_canonical_detail",
            ),
        )
    )

    result = AtlasCanonicalHeadBenchmarkDecisionGate.evaluate(
        candidates
    )

    assert result.decision == "HOLD"
    assert result.status == "BLOCKED"
    assert result.selected_candidate_id is None
    assert result.phase_9_authorized is False


def test_policy_rejected_candidate_cannot_be_selected():
    candidates = list(_complete_benchmark())
    candidates[2] = _candidate(
        "hybrid-v1",
        "hybrid_canonical_detail",
        identity_preservation_support=1.0,
        commercial_license_acceptable=False,
    )

    result = AtlasCanonicalHeadBenchmarkDecisionGate.evaluate(
        tuple(candidates)
    )

    assert result.selected_candidate_id != "hybrid-v1"


def test_identity_quality_precedes_processing_cost():
    candidates = (
        _candidate(
            "parametric-v1",
            "parametric_fixed_topology",
            identity_preservation_support=0.78,
            processing_cost_eur=0.0,
        ),
        _candidate(
            "neural-v1",
            "direct_neural_dense",
            identity_preservation_support=0.80,
            processing_cost_eur=0.0,
        ),
        _candidate(
            "hybrid-v1",
            "hybrid_canonical_detail",
            identity_preservation_support=0.92,
            processing_cost_eur=5.0,
        ),
    )

    result = AtlasCanonicalHeadBenchmarkDecisionGate.evaluate(
        candidates
    )

    assert result.selected_candidate_id == "hybrid-v1"


def test_tie_break_is_deterministic():
    candidates = (
        _candidate(
            "parametric-v1",
            "parametric_fixed_topology",
        ),
        _candidate(
            "neural-v1",
            "direct_neural_dense",
        ),
        _candidate(
            "hybrid-v1",
            "hybrid_canonical_detail",
        ),
    )

    first = AtlasCanonicalHeadBenchmarkDecisionGate.evaluate(
        candidates
    )
    second = AtlasCanonicalHeadBenchmarkDecisionGate.evaluate(
        tuple(reversed(candidates))
    )

    assert first.selected_candidate_id == second.selected_candidate_id


def test_go_authorizes_phase_9_only_for_selected_candidate():
    result = AtlasCanonicalHeadBenchmarkDecisionGate.evaluate(
        _complete_benchmark()
    )

    assert result.decision == "GO"
    assert result.phase_9_authorized is True
    assert result.selected_candidate_id is not None


def test_rejects_non_candidate_observation():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadBenchmarkCandidateObservation",
    ):
        AtlasCanonicalHeadBenchmarkDecisionGate.evaluate(
            ({}, {}, {})
        )


def test_result_does_not_claim_provider_or_geometry():
    result = AtlasCanonicalHeadBenchmarkDecisionGate.evaluate(
        _complete_benchmark()
    )

    assert not hasattr(result, "provider_id")
    assert not hasattr(result, "vertices")
    assert not hasattr(result, "faces")
