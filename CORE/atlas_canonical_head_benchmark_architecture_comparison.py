from __future__ import annotations

from CORE.atlas_canonical_head_benchmark_gap_closure_evidence import (
    AtlasCanonicalHeadBenchmarkGapClosureEvidence,
)


class AtlasCanonicalHeadBenchmarkArchitectureComparison:
    @classmethod
    def build(
        cls,
    ) -> tuple[dict[str, object], ...]:
        flame = (
            AtlasCanonicalHeadBenchmarkGapClosureEvidence
            .flame_candidate()
        )
        prnet = (
            AtlasCanonicalHeadBenchmarkGapClosureEvidence
            .prnet_candidate()
        )
        hybrid = (
            AtlasCanonicalHeadBenchmarkGapClosureEvidence
            .hybrid_architecture()
        )

        return (
            {
                "architecture_kind": flame.architecture_kind,
                "comparison_scope": "candidate_level",
                "candidate_id": flame.candidate_id,
                "unresolved_quality_channels": (
                    flame.unresolved_quality_channels
                ),
                "blocked_policy_channels": (
                    flame.blocked_policy_channels
                ),
                "unresolved_policy_channels": (
                    flame.unresolved_policy_channels
                ),
                "commercial_license_state": (
                    flame.commercial_license_state
                ),
                "evidence_limitations": (
                    flame.evidence_limitations
                ),
            },
            {
                "architecture_kind": prnet.architecture_kind,
                "comparison_scope": "candidate_level",
                "candidate_id": prnet.candidate_id,
                "unresolved_quality_channels": (
                    prnet.unresolved_quality_channels
                ),
                "blocked_policy_channels": (
                    prnet.blocked_policy_channels
                ),
                "unresolved_policy_channels": (
                    prnet.unresolved_policy_channels
                ),
                "commercial_license_state": (
                    prnet.commercial_license_state
                ),
                "evidence_limitations": (
                    prnet.evidence_limitations
                ),
            },
            {
                "architecture_kind": hybrid[
                    "architecture_kind"
                ],
                "comparison_scope": "architecture_level",
                "verified_policy_blocker": hybrid[
                    "verified_policy_blocker"
                ],
                "evidence_limitations": hybrid[
                    "evidence_limitations"
                ],
                "candidate_observation_created": False,
                "support_score_created": False,
            },
        )

    @classmethod
    def selected_architecture_kind(
        cls,
    ) -> None:
        return None

    @classmethod
    def comparison_complete_for_final_scoring(
        cls,
    ) -> bool:
        return False
