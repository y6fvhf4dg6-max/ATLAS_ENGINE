from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class AtlasCanonicalHeadLandmarkSurfaceAgreementEvidence:
    """Bounded evidence contract for Phase 8 Item 9.13.

    Keeps landmark/reprojection evidence separate from canonical/model-space
    geometry and independent metric surface accuracy.
    """

    CRITERIA: ClassVar[tuple[str, ...]] = (
        "landmark_success_with_surface_failure",
        "surface_success_with_landmark_failure",
        "local_landmark_localization_uncertainty",
        "regional_measurement_confidence_limitations",
    )

    EVALUATION_SPACES: ClassVar[tuple[str, ...]] = (
        "2d_observation",
        "canonical_model",
        "metric_3d_ground_truth",
    )

    EVIDENCE_STATUSES: ClassVar[tuple[str, ...]] = (
        "not_established",
        "unresolved",
        "bounded_negative",
    )

    EVIDENCE_ORIGINS: ClassVar[tuple[str, ...]] = (
        "directly_observed",
        "multiview_constrained",
        "model_prior_inferred",
        "generated_completion",
        "unresolved",
    )

    criterion: str
    evaluation_space: str
    evidence_status: str
    evidence_origin: str
    source_reference: str
    semantic_scope: str
    permitted_claim: str
    prohibited_claims: tuple[str, ...]
    bounded_interpretation: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "criterion",
            self._normalize_identifier(self.criterion),
        )
        object.__setattr__(
            self,
            "evaluation_space",
            self._normalize_identifier(self.evaluation_space),
        )
        object.__setattr__(
            self,
            "evidence_status",
            self._normalize_identifier(self.evidence_status),
        )
        object.__setattr__(
            self,
            "evidence_origin",
            self._normalize_identifier(self.evidence_origin),
        )

        if self.criterion not in self.CRITERIA:
            raise ValueError(
                f"criterion must be one of {self.CRITERIA}"
            )

        if self.evaluation_space not in self.EVALUATION_SPACES:
            raise ValueError(
                "evaluation_space must be one of "
                f"{self.EVALUATION_SPACES}"
            )

        if self.evidence_status not in self.EVIDENCE_STATUSES:
            raise ValueError(
                "evidence_status must be one of "
                f"{self.EVIDENCE_STATUSES}"
            )

        if self.evidence_origin not in self.EVIDENCE_ORIGINS:
            raise ValueError(
                "evidence_origin must be one of "
                f"{self.EVIDENCE_ORIGINS}"
            )

        for field_name in (
            "source_reference",
            "semantic_scope",
            "permitted_claim",
            "bounded_interpretation",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string"
                )
            object.__setattr__(
                self,
                field_name,
                value.strip(),
            )

        claims = self.prohibited_claims
        if not isinstance(claims, tuple):
            claims = tuple(claims)

        if not claims:
            raise ValueError(
                "prohibited_claims must not be empty"
            )

        normalized_claims = []
        for claim in claims:
            if not isinstance(claim, str) or not claim.strip():
                raise ValueError(
                    "prohibited_claims must contain only non-empty strings"
                )
            normalized_claims.append(
                claim.strip()
            )

        object.__setattr__(
            self,
            "prohibited_claims",
            tuple(normalized_claims),
        )

    @staticmethod
    def _normalize_identifier(value: str) -> str:
        if not isinstance(value, str):
            raise ValueError(
                "identifier fields must be strings"
            )

        normalized = (
            value.strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )

        if not normalized:
            raise ValueError(
                "identifier fields must not be empty"
            )

        return normalized
