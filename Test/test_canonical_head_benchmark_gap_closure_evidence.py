from CORE.atlas_canonical_head_benchmark_gap_closure_evidence import (
    AtlasCanonicalHeadBenchmarkGapClosureEvidence,
)


def test_exposes_flame_and_prnet_candidate_gap_closures():
    flame = (
        AtlasCanonicalHeadBenchmarkGapClosureEvidence
        .flame_candidate()
    )
    prnet = (
        AtlasCanonicalHeadBenchmarkGapClosureEvidence
        .prnet_candidate()
    )

    assert flame.candidate_id == "flame-2023-open"
    assert flame.architecture_kind == "parametric_fixed_topology"

    assert prnet.candidate_id == "prnet"
    assert prnet.architecture_kind == "direct_neural_dense"


def test_records_hybrid_as_architecture_level_gap_not_fabricated_candidate():
    hybrid = (
        AtlasCanonicalHeadBenchmarkGapClosureEvidence
        .hybrid_architecture()
    )

    assert hybrid["architecture_kind"] == "hybrid_canonical_detail"
    assert "candidate_id" not in hybrid
    assert hybrid["candidate_observation_created"] is False
    assert hybrid["support_score_created"] is False
    assert hybrid["phase_9_authorized"] is False


def test_records_verified_policy_states_without_final_candidate_decision():
    flame = (
        AtlasCanonicalHeadBenchmarkGapClosureEvidence
        .flame_candidate()
    )
    prnet = (
        AtlasCanonicalHeadBenchmarkGapClosureEvidence
        .prnet_candidate()
    )

    assert flame.commercial_license_state == "ACCEPTABLE"

    assert prnet.commercial_license_state == "BLOCKED"
    assert prnet.model_weight_restrictions_state == "BLOCKED"
    assert prnet.dataset_restrictions_state == "BLOCKED"

    assert not hasattr(flame, "decision")
    assert not hasattr(prnet, "decision")
