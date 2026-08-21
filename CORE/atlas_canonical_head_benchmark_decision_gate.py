from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from CORE.atlas_canonical_head_benchmark_candidate_gate import (
    AtlasCanonicalHeadBenchmarkCandidateGate,
)
from CORE.atlas_canonical_head_benchmark_candidate_observation import (
    AtlasCanonicalHeadBenchmarkCandidateObservation,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadBenchmarkDecisionResult:
    decision: str
    status: str
    selected_candidate_id: str | None
    selected_architecture_kind: str | None
    blocked_reasons: tuple[str, ...]
    phase_9_authorized: bool


class AtlasCanonicalHeadBenchmarkDecisionGate:
    REQUIRED_ARCHITECTURE_KINDS = (
        "parametric_fixed_topology",
        "direct_neural_dense",
        "hybrid_canonical_detail",
    )

    @classmethod
    def evaluate(
        cls,
        candidates: Iterable[
            AtlasCanonicalHeadBenchmarkCandidateObservation
        ],
    ) -> AtlasCanonicalHeadBenchmarkDecisionResult:
        candidates = tuple(candidates)

        for candidate in candidates:
            if not isinstance(
                candidate,
                AtlasCanonicalHeadBenchmarkCandidateObservation,
            ):
                raise TypeError(
                    "each candidate must be an "
                    "AtlasCanonicalHeadBenchmarkCandidateObservation."
                )

        architecture_kinds = tuple(
            candidate.architecture_kind
            for candidate in candidates
        )

        if len(set(architecture_kinds)) != len(
            architecture_kinds
        ):
            raise ValueError(
                "architecture_kind must be unique "
                "within one canonical benchmark."
            )

        if set(architecture_kinds) != set(
            cls.REQUIRED_ARCHITECTURE_KINDS
        ):
            return AtlasCanonicalHeadBenchmarkDecisionResult(
                decision="HOLD",
                status="BLOCKED",
                selected_candidate_id=None,
                selected_architecture_kind=None,
                blocked_reasons=(
                    "BLOCKED_INCOMPLETE_CANONICAL_BENCHMARK",
                ),
                phase_9_authorized=False,
            )

        go_candidates = tuple(
            candidate
            for candidate in candidates
            if (
                AtlasCanonicalHeadBenchmarkCandidateGate.evaluate(
                    candidate
                ).decision
                == "GO"
            )
        )

        if not go_candidates:
            return AtlasCanonicalHeadBenchmarkDecisionResult(
                decision="HOLD",
                status="BLOCKED",
                selected_candidate_id=None,
                selected_architecture_kind=None,
                blocked_reasons=(
                    "BLOCKED_NO_GO_CANONICAL_CANDIDATE",
                ),
                phase_9_authorized=False,
            )

        selected = max(
            go_candidates,
            key=cls._selection_key,
        )

        return AtlasCanonicalHeadBenchmarkDecisionResult(
            decision="GO",
            status="LOCK_READY",
            selected_candidate_id=selected.candidate_id,
            selected_architecture_kind=(
                selected.architecture_kind
            ),
            blocked_reasons=(),
            phase_9_authorized=True,
        )

    @staticmethod
    def _selection_key(
        candidate: AtlasCanonicalHeadBenchmarkCandidateObservation,
    ) -> tuple[object, ...]:
        return (
            candidate.identity_preservation_support,
            candidate.physical_suitability,
            candidate.topology_suitability,
            candidate.reproducibility_support,
            candidate.apple_silicon_runtime_support,
            candidate.multi_view_consistency,
            candidate.silhouette_profile_support,
            candidate.head_ratio_support,
            candidate.jaw_chin_support,
            candidate.nose_projection_support,
            candidate.orbital_cheek_volume_support,
            candidate.expression_separation_support,
            candidate.pose_separation_support,
            -candidate.processing_time_seconds,
            -candidate.processing_cost_eur,
            candidate.candidate_id,
        )
