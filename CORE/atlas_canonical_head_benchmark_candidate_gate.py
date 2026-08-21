from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_canonical_head_benchmark_candidate_observation import (
    AtlasCanonicalHeadBenchmarkCandidateObservation,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadBenchmarkCandidateResult:
    decision: str
    status: str
    blocked_reasons: tuple[str, ...]
    failure_reasons: tuple[str, ...]


class AtlasCanonicalHeadBenchmarkCandidateGate:
    REJECT_THRESHOLD = 0.50
    GO_THRESHOLD = 0.70

    @classmethod
    def evaluate(
        cls,
        observation: AtlasCanonicalHeadBenchmarkCandidateObservation,
    ) -> AtlasCanonicalHeadBenchmarkCandidateResult:
        if not isinstance(
            observation,
            AtlasCanonicalHeadBenchmarkCandidateObservation,
        ):
            raise TypeError(
                "observation must be an "
                "AtlasCanonicalHeadBenchmarkCandidateObservation."
            )

        policy_blocked_reasons = []

        if not observation.commercial_license_acceptable:
            policy_blocked_reasons.append(
                "BLOCKED_COMMERCIAL_LICENSE"
            )

        if not observation.privacy_data_retention_acceptable:
            policy_blocked_reasons.append(
                "BLOCKED_PRIVACY_DATA_RETENTION"
            )

        if not observation.model_weight_restrictions_acceptable:
            policy_blocked_reasons.append(
                "BLOCKED_MODEL_WEIGHT_RESTRICTIONS"
            )

        if not observation.dataset_restrictions_acceptable:
            policy_blocked_reasons.append(
                "BLOCKED_DATASET_RESTRICTIONS"
            )

        if policy_blocked_reasons:
            return AtlasCanonicalHeadBenchmarkCandidateResult(
                decision="REJECT",
                status="BLOCKED",
                blocked_reasons=tuple(
                    policy_blocked_reasons
                ),
                failure_reasons=(),
            )

        quality_channels = (
            (
                "IDENTITY_PRESERVATION",
                observation.identity_preservation_support,
            ),
            (
                "MULTI_VIEW_CONSISTENCY",
                observation.multi_view_consistency,
            ),
            (
                "SILHOUETTE_PROFILE_SUPPORT",
                observation.silhouette_profile_support,
            ),
            (
                "HEAD_RATIO_SUPPORT",
                observation.head_ratio_support,
            ),
            (
                "JAW_CHIN_SUPPORT",
                observation.jaw_chin_support,
            ),
            (
                "NOSE_PROJECTION_SUPPORT",
                observation.nose_projection_support,
            ),
            (
                "ORBITAL_CHEEK_VOLUME_SUPPORT",
                observation.orbital_cheek_volume_support,
            ),
            (
                "EXPRESSION_SEPARATION_SUPPORT",
                observation.expression_separation_support,
            ),
            (
                "POSE_SEPARATION_SUPPORT",
                observation.pose_separation_support,
            ),
            (
                "TOPOLOGY_SUITABILITY",
                observation.topology_suitability,
            ),
            (
                "PHYSICAL_SUITABILITY",
                observation.physical_suitability,
            ),
            (
                "APPLE_SILICON_RUNTIME_SUPPORT",
                observation.apple_silicon_runtime_support,
            ),
            (
                "REPRODUCIBILITY_SUPPORT",
                observation.reproducibility_support,
            ),
        )

        insufficient_reasons = tuple(
            f"INSUFFICIENT_{name}"
            for name, value in quality_channels
            if value < cls.REJECT_THRESHOLD
        )

        if insufficient_reasons:
            return AtlasCanonicalHeadBenchmarkCandidateResult(
                decision="REJECT",
                status="BLOCKED",
                blocked_reasons=(),
                failure_reasons=insufficient_reasons,
            )

        limited_reasons = tuple(
            f"LIMITED_{name}"
            for name, value in quality_channels
            if value < cls.GO_THRESHOLD
        )

        if limited_reasons:
            return AtlasCanonicalHeadBenchmarkCandidateResult(
                decision="HOLD",
                status="BLOCKED",
                blocked_reasons=(),
                failure_reasons=limited_reasons,
            )

        return AtlasCanonicalHeadBenchmarkCandidateResult(
            decision="GO",
            status="ACCEPTED",
            blocked_reasons=(),
            failure_reasons=(),
        )
