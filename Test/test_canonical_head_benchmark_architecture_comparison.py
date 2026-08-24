from CORE.atlas_canonical_head_benchmark_architecture_comparison import (
    AtlasCanonicalHeadBenchmarkArchitectureComparison,
)


def test_compares_exactly_three_required_architecture_classes():
    comparison = (
        AtlasCanonicalHeadBenchmarkArchitectureComparison.build()
    )

    assert tuple(
        item["architecture_kind"]
        for item in comparison
    ) == (
        "parametric_fixed_topology",
        "direct_neural_dense",
        "hybrid_canonical_detail",
    )


def test_preserves_candidate_vs_architecture_level_boundary():
    comparison = (
        AtlasCanonicalHeadBenchmarkArchitectureComparison.build()
    )

    parametric, neural, hybrid = comparison

    assert parametric["candidate_id"] == "flame-2023-open"
    assert neural["candidate_id"] == "prnet"

    assert "candidate_id" not in hybrid
    assert hybrid["comparison_scope"] == "architecture_level"


def test_records_policy_blockers_without_fabricating_scores():
    comparison = (
        AtlasCanonicalHeadBenchmarkArchitectureComparison.build()
    )

    parametric, neural, hybrid = comparison

    assert parametric["commercial_license_state"] == "ACCEPTABLE"

    assert neural["commercial_license_state"] == "BLOCKED"
    assert (
        "commercial_license_state"
        in neural["blocked_policy_channels"]
    )

    assert hybrid["verified_policy_blocker"] == (
        "DSINE_CURRENT_LICENSE_NONCOMMERCIAL"
    )

    for item in comparison:
        assert "support_score" not in item
        assert "decision" not in item
        assert "phase_9_authorized" not in item


def test_comparison_cannot_select_winner_from_incomplete_evidence():
    assert (
        AtlasCanonicalHeadBenchmarkArchitectureComparison
        .selected_architecture_kind()
        is None
    )

    assert (
        AtlasCanonicalHeadBenchmarkArchitectureComparison
        .comparison_complete_for_final_scoring()
        is False
    )
