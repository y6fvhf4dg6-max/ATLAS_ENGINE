from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_canonical_head_identity_confidence_observation import (
    AtlasCanonicalHeadIdentityConfidenceObservation,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadIdentityConfidenceResult:
    decision: str
    production_status: str
    confidence_class: str
    blocked_reasons: tuple[str, ...]
    failure_reasons: tuple[str, ...]


class AtlasCanonicalHeadIdentityConfidenceGate:
    REJECT_THRESHOLD = 0.35
    GO_THRESHOLD = 0.70

    @classmethod
    def evaluate(
        cls,
        observation: AtlasCanonicalHeadIdentityConfidenceObservation,
    ) -> AtlasCanonicalHeadIdentityConfidenceResult:
        if not isinstance(
            observation,
            AtlasCanonicalHeadIdentityConfidenceObservation,
        ):
            raise TypeError(
                "observation must be an "
                "AtlasCanonicalHeadIdentityConfidenceObservation."
            )

        decision_channels = (
            (
                "VIEW_COVERAGE_SUPPORT",
                observation.view_coverage_support,
                True,
            ),
            (
                "MULTI_VIEW_CONSISTENCY",
                observation.multi_view_consistency,
                True,
            ),
            (
                "SILHOUETTE_SUPPORT",
                observation.silhouette_support,
                True,
            ),
            (
                "PROFILE_SUPPORT",
                observation.profile_support,
                True,
            ),
            (
                "IDENTITY_SHAPE_SUPPORT",
                observation.identity_shape_support,
                True,
            ),
            (
                "ASYMMETRY_SUPPORT",
                observation.asymmetry_support,
                False,
            ),
        )

        insufficient_reasons = tuple(
            f"INSUFFICIENT_{name}"
            for name, value, reject_capable in decision_channels
            if reject_capable and value < cls.REJECT_THRESHOLD
        )

        if insufficient_reasons:
            return AtlasCanonicalHeadIdentityConfidenceResult(
                decision="REJECT",
                production_status="BLOCKED",
                confidence_class="INSUFFICIENT",
                blocked_reasons=(
                    "BLOCKED_INSUFFICIENT_IDENTITY_EVIDENCE",
                ),
                failure_reasons=insufficient_reasons,
            )

        limited_reasons = tuple(
            f"LIMITED_{name}"
            for name, value, _ in decision_channels
            if value < cls.GO_THRESHOLD
        )

        if limited_reasons:
            return AtlasCanonicalHeadIdentityConfidenceResult(
                decision="HOLD",
                production_status="BLOCKED",
                confidence_class="LIMITED",
                blocked_reasons=(
                    "BLOCKED_INSUFFICIENT_IDENTITY_EVIDENCE",
                ),
                failure_reasons=limited_reasons,
            )

        return AtlasCanonicalHeadIdentityConfidenceResult(
            decision="GO",
            production_status="ACCEPTED",
            confidence_class="STRONG",
            blocked_reasons=(),
            failure_reasons=(),
        )
