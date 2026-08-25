from __future__ import annotations

from CORE.atlas_canonical_head_benchmark_gap_closure_observation import (
    AtlasCanonicalHeadBenchmarkGapClosureObservation,
)
from CORE.atlas_canonical_head_flame_benchmark_evidence import (
    AtlasCanonicalHeadFlameBenchmarkEvidence,
)
from CORE.atlas_canonical_head_prnet_benchmark_evidence import (
    AtlasCanonicalHeadPrnetBenchmarkEvidence,
)


class AtlasCanonicalHeadBenchmarkGapClosureEvidence:
    @classmethod
    def flame_candidate(
        cls,
    ) -> AtlasCanonicalHeadBenchmarkGapClosureObservation:
        return AtlasCanonicalHeadBenchmarkGapClosureObservation(
            candidate_id="flame-2023-open",
            architecture_kind="parametric_fixed_topology",
            coverage=AtlasCanonicalHeadFlameBenchmarkEvidence.coverage(),
            commercial_license_state="ACCEPTABLE",
            privacy_data_retention_state="ACCEPTABLE",
            model_weight_restrictions_state="ACCEPTABLE",
            dataset_restrictions_state="ACCEPTABLE",
            evidence_limitations=(
                "BENCHMARK_MEDIAPIPE_EMBEDDING_PROVENANCE_UNRESOLVED",
                "NO_METRIC_3D_GROUND_TRUTH",
                "NO_EXPRESSION_VARIATION_BENCHMARK",
                "NO_CANDIDATE_SPECIFIC_PHYSICAL_EVIDENCE",
            ),
        )

    @classmethod
    def prnet_candidate(
        cls,
    ) -> AtlasCanonicalHeadBenchmarkGapClosureObservation:
        return AtlasCanonicalHeadBenchmarkGapClosureObservation(
            candidate_id="prnet",
            architecture_kind="direct_neural_dense",
            coverage=AtlasCanonicalHeadPrnetBenchmarkEvidence.coverage(),
            commercial_license_state="BLOCKED",
            privacy_data_retention_state="ACCEPTABLE",
            model_weight_restrictions_state="BLOCKED",
            dataset_restrictions_state="BLOCKED",
            evidence_limitations=(
                "NO_METRIC_3D_GROUND_TRUTH",
                "PRETRAINED_MODEL_TRAINING_DATA_NONCOMMERCIAL",
                "NO_CANDIDATE_SPECIFIC_PHYSICAL_EVIDENCE",
            ),
        )

    @classmethod
    def hybrid_architecture(
        cls,
    ) -> dict[str, object]:
        return {
            "architecture_kind": "hybrid_canonical_detail",
            "candidate_observation_created": False,
            "support_score_created": False,
            "phase_9_authorized": False,
            "verified_policy_blocker": (
                "DSINE_CURRENT_LICENSE_NONCOMMERCIAL"
            ),
            "evidence_limitations": (
                "ARCHITECTURE_LEVEL_EVIDENCE_ONLY",
                "NO_STANDALONE_HYBRID_CANDIDATE_ID",
                "NO_METRIC_3D_GROUND_TRUTH",
                "NO_CANDIDATE_SPECIFIC_PHYSICAL_EVIDENCE",
            ),
        }
