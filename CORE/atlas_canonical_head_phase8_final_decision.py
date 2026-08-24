from __future__ import annotations

from CORE.atlas_canonical_head_benchmark_architecture_comparison import (
    AtlasCanonicalHeadBenchmarkArchitectureComparison,
)


class AtlasCanonicalHeadPhase8FinalDecision:
    @classmethod
    def evaluate_current(
        cls,
    ) -> dict[str, object]:
        comparison = (
            AtlasCanonicalHeadBenchmarkArchitectureComparison
            .build()
        )

        prnet = comparison[1]
        hybrid = comparison[2]

        blocked_reasons: list[str] = []

        if not (
            AtlasCanonicalHeadBenchmarkArchitectureComparison
            .comparison_complete_for_final_scoring()
        ):
            blocked_reasons.append(
                "INCOMPLETE_FINAL_SCORING_EVIDENCE"
            )

        if prnet["blocked_policy_channels"]:
            blocked_reasons.append(
                "PRNET_POLICY_BLOCKED"
            )

        if (
            hybrid["verified_policy_blocker"]
            == "DSINE_CURRENT_LICENSE_NONCOMMERCIAL"
        ):
            blocked_reasons.append(
                "HYBRID_DSINE_LICENSE_BLOCKED"
            )

        return {
            "decision": "HOLD",
            "status": "BLOCKED",
            "selected_candidate_id": None,
            "selected_architecture_kind": None,
            "blocked_reasons": tuple(blocked_reasons),
            "phase_9_authorized": False,
        }
