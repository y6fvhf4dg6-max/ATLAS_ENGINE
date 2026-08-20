from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_portrait_input_evidence_set import (
    AtlasPortraitInputEvidenceSet,
)
from CORE.atlas_portrait_input_quality_observation import (
    AtlasPortraitInputQualityObservation,
)


MIN_FACE_COVERAGE_RATIO = 0.18
MAX_OCCLUSION_RATIO = 0.35
MIN_BLUR_SCORE = 0.40
MAX_PERSPECTIVE_DISTORTION_SCORE = 0.55


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasPortraitInputUsabilityResult:
    usable: bool
    status: str
    blocked_reasons: tuple[str, ...]


class AtlasPortraitInputUsabilityGate:
    @classmethod
    def evaluate(
        cls,
        evidence_set: AtlasPortraitInputEvidenceSet,
        observations: tuple[
            AtlasPortraitInputQualityObservation,
            ...,
        ],
    ) -> AtlasPortraitInputUsabilityResult:
        if not isinstance(
            evidence_set,
            AtlasPortraitInputEvidenceSet,
        ):
            raise TypeError(
                "evidence_set must be an "
                "AtlasPortraitInputEvidenceSet."
            )

        observations = tuple(
            observations
        )

        for observation in observations:
            if not isinstance(
                observation,
                AtlasPortraitInputQualityObservation,
            ):
                raise TypeError(
                    "observations must contain only "
                    "AtlasPortraitInputQualityObservation values."
                )

        evidence_ids = {
            item.evidence_id
            for item in evidence_set.items
        }

        observation_ids = [
            observation.evidence_id
            for observation in observations
        ]

        if len(observation_ids) != len(
            set(observation_ids)
        ):
            raise ValueError(
                "quality observation evidence_id values "
                "must be unique."
            )

        unknown_ids = set(
            observation_ids
        ) - evidence_ids

        if unknown_ids:
            raise ValueError(
                "quality observation evidence_id must "
                "match evidence-set items."
            )

        if set(observation_ids) != evidence_ids:
            raise ValueError(
                "one quality observation is required "
                "for every evidence item."
            )

        blocked_reasons: list[str] = []

        if not evidence_set.production_evidence_eligible:
            blocked_reasons.append(
                evidence_set.blocked_reason
            )

        for observation in observations:
            if not observation.face_detected:
                blocked_reasons.append(
                    "BLOCKED_FACE_NOT_DETECTED"
                )

            if (
                observation.face_coverage_ratio
                < MIN_FACE_COVERAGE_RATIO
            ):
                blocked_reasons.append(
                    "BLOCKED_INSUFFICIENT_FACE_COVERAGE"
                )

            if (
                observation.occlusion_ratio
                > MAX_OCCLUSION_RATIO
            ):
                blocked_reasons.append(
                    "BLOCKED_EXCESSIVE_OCCLUSION"
                )

            if (
                observation.blur_score
                < MIN_BLUR_SCORE
            ):
                blocked_reasons.append(
                    "BLOCKED_EXCESSIVE_BLUR"
                )

            if (
                observation.perspective_distortion_score
                > MAX_PERSPECTIVE_DISTORTION_SCORE
            ):
                blocked_reasons.append(
                    "BLOCKED_EXCESSIVE_PERSPECTIVE_DISTORTION"
                )

        unique_reasons = tuple(
            dict.fromkeys(
                reason
                for reason in blocked_reasons
                if reason is not None
            )
        )

        usable = not unique_reasons

        return AtlasPortraitInputUsabilityResult(
            usable=usable,
            status=(
                "ACCEPTED"
                if usable
                else "BLOCKED"
            ),
            blocked_reasons=unique_reasons,
        )
