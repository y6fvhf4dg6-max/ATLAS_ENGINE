from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_canonical_head_physical_representation_observation import (
    AtlasCanonicalHeadPhysicalRepresentationObservation,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadPhysicalRepresentationResult:
    decision: str
    production_status: str
    blocked_reasons: tuple[str, ...]
    failure_reasons: tuple[str, ...]


class AtlasCanonicalHeadPhysicalRepresentationGate:
    MIN_HEAD_HEIGHT_MM = 18.0
    MIN_FEATURE_MM = 0.40

    REJECT_IDENTITY_THRESHOLD = 0.50
    GO_PRESERVATION_THRESHOLD = 0.70

    MAX_GO_LOD_LEVEL = 4

    @classmethod
    def evaluate(
        cls,
        observation: AtlasCanonicalHeadPhysicalRepresentationObservation,
    ) -> AtlasCanonicalHeadPhysicalRepresentationResult:
        if not isinstance(
            observation,
            AtlasCanonicalHeadPhysicalRepresentationObservation,
        ):
            raise TypeError(
                "observation must be an "
                "AtlasCanonicalHeadPhysicalRepresentationObservation."
            )

        reject_reasons = []

        if observation.target_head_height_mm < cls.MIN_HEAD_HEIGHT_MM:
            reject_reasons.append(
                "INSUFFICIENT_HEAD_HEIGHT"
            )

        if observation.minimum_feature_mm < cls.MIN_FEATURE_MM:
            reject_reasons.append(
                "INSUFFICIENT_PHYSICAL_FEATURE_SIZE"
            )

        if (
            observation.identity_preservation_support
            < cls.REJECT_IDENTITY_THRESHOLD
        ):
            reject_reasons.append(
                "INSUFFICIENT_IDENTITY_PRESERVATION"
            )

        if reject_reasons:
            return AtlasCanonicalHeadPhysicalRepresentationResult(
                decision="REJECT",
                production_status="BLOCKED",
                blocked_reasons=(
                    "BLOCKED_PHYSICAL_IDENTITY_REPRESENTATION",
                ),
                failure_reasons=tuple(reject_reasons),
            )

        limited_reasons = []

        if (
            observation.identity_preservation_support
            < cls.GO_PRESERVATION_THRESHOLD
        ):
            limited_reasons.append(
                "LIMITED_IDENTITY_PRESERVATION"
            )

        if (
            observation.silhouette_preservation_support
            < cls.GO_PRESERVATION_THRESHOLD
        ):
            limited_reasons.append(
                "LIMITED_SILHOUETTE_PRESERVATION"
            )

        if (
            observation.profile_preservation_support
            < cls.GO_PRESERVATION_THRESHOLD
        ):
            limited_reasons.append(
                "LIMITED_PROFILE_PRESERVATION"
            )

        if observation.lod_level > cls.MAX_GO_LOD_LEVEL:
            limited_reasons.append(
                "LIMITED_BY_LOD"
            )

        if limited_reasons:
            return AtlasCanonicalHeadPhysicalRepresentationResult(
                decision="HOLD",
                production_status="BLOCKED",
                blocked_reasons=(
                    "BLOCKED_PHYSICAL_IDENTITY_REPRESENTATION",
                ),
                failure_reasons=tuple(limited_reasons),
            )

        return AtlasCanonicalHeadPhysicalRepresentationResult(
            decision="GO",
            production_status="ACCEPTED",
            blocked_reasons=(),
            failure_reasons=(),
        )
