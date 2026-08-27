from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class AtlasCanonicalHeadCrossRegionCompensationEvidence:
    CRITERIA: ClassVar[tuple[str, ...]] = (
        "global_improvement_with_local_degradation",
        "camera_compensation",
        "pose_compensation",
        "cross_region_compensation",
        "alignment_concealing_local_failure",
    )

    EVALUATION_SPACES: ClassVar[tuple[str, ...]] = (
        "2d_observation",
        "canonical_model",
        "metric_3d_ground_truth",
        "physical_output",
    )

    EVIDENCE_STATUSES: ClassVar[tuple[str, ...]] = (
        "bounded_positive",
        "bounded_mixed",
        "not_established_as_primary_explanation",
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
        for field_name in (
            "criterion",
            "evaluation_space",
            "evidence_status",
            "evidence_origin",
        ):
            object.__setattr__(
                self,
                field_name,
                self._normalize_identifier(getattr(self, field_name)),
            )

        if self.criterion not in self.CRITERIA:
            raise ValueError(f"criterion must be one of {self.CRITERIA}")
        if self.evaluation_space not in self.EVALUATION_SPACES:
            raise ValueError(
                f"evaluation_space must be one of {self.EVALUATION_SPACES}"
            )
        if self.evidence_status not in self.EVIDENCE_STATUSES:
            raise ValueError(
                f"evidence_status must be one of {self.EVIDENCE_STATUSES}"
            )
        if self.evidence_origin not in self.EVIDENCE_ORIGINS:
            raise ValueError(
                f"evidence_origin must be one of {self.EVIDENCE_ORIGINS}"
            )

        for field_name in (
            "source_reference",
            "semantic_scope",
            "permitted_claim",
            "bounded_interpretation",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
            object.__setattr__(self, field_name, value.strip())

        claims = self.prohibited_claims
        if not isinstance(claims, tuple):
            claims = tuple(claims)

        if not claims:
            raise ValueError("prohibited_claims must not be empty")

        normalized_claims = tuple(
            claim.strip()
            for claim in claims
            if isinstance(claim, str) and claim.strip()
        )
        if len(normalized_claims) != len(claims):
            raise ValueError(
                "prohibited_claims must contain only non-empty strings"
            )

        object.__setattr__(self, "prohibited_claims", normalized_claims)

    @staticmethod
    def _normalize_identifier(value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("identifier fields must be strings")
        value = value.strip().lower().replace("-", "_").replace(" ", "_")
        if not value:
            raise ValueError("identifier fields must not be empty")
        return value
