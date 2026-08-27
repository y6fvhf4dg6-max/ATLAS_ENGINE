from __future__ import annotations

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadForeheadCranialQualityEvidence:
    criterion: str
    evaluation_space: str
    evidence_status: str
    evidence_origin: str
    source_reference: str
    permitted_claim: str
    prohibited_claims: tuple[str, ...]
    bounded_interpretation: str

    CRITERIA = (
        "forehead_height",
        "forehead_slope",
        "frontal_curvature",
        "temple_transition",
        "cranial_width",
        "cranial_depth",
        "overall_skull_head_envelope",
    )

    EVALUATION_SPACES = (
        "2d_observation",
        "canonical_model",
        "metric_3d_ground_truth",
        "physical_output",
    )

    EVIDENCE_STATUSES = (
        "blocked",
    )

    EVIDENCE_ORIGINS = (
        "directly_observed",
        "multiview_constrained",
        "model_prior_inferred",
        "generated_completion",
        "unresolved",
    )

    def __post_init__(self) -> None:
        criterion = self._normalize_identifier(
            self.criterion,
            field_name="criterion",
        )
        evaluation_space = self._normalize_identifier(
            self.evaluation_space,
            field_name="evaluation_space",
        )
        evidence_status = self._normalize_identifier(
            self.evidence_status,
            field_name="evidence_status",
        )
        evidence_origin = self._normalize_identifier(
            self.evidence_origin,
            field_name="evidence_origin",
        )

        if criterion not in self.CRITERIA:
            raise ValueError(
                "criterion must be one of the exact Item 9.8 criteria."
            )

        if evaluation_space not in self.EVALUATION_SPACES:
            raise ValueError(
                "evaluation_space must be one of the exact evaluation spaces."
            )

        if evidence_status not in self.EVIDENCE_STATUSES:
            raise ValueError(
                "evidence_status must be one of the exact Item 9.8 evidence statuses."
            )

        if evidence_origin not in self.EVIDENCE_ORIGINS:
            raise ValueError(
                "evidence_origin must be one of the exact evidence-origin states."
            )

        source_reference = self._normalize_required_text(
            self.source_reference,
            field_name="source_reference",
        )
        permitted_claim = self._normalize_required_text(
            self.permitted_claim,
            field_name="permitted_claim",
        )
        prohibited_claims = self._normalize_prohibited_claims(
            self.prohibited_claims,
        )
        bounded_interpretation = self._normalize_required_text(
            self.bounded_interpretation,
            field_name="bounded_interpretation",
        )

        object.__setattr__(self, "criterion", criterion)
        object.__setattr__(self, "evaluation_space", evaluation_space)
        object.__setattr__(self, "evidence_status", evidence_status)
        object.__setattr__(self, "evidence_origin", evidence_origin)
        object.__setattr__(self, "source_reference", source_reference)
        object.__setattr__(self, "permitted_claim", permitted_claim)
        object.__setattr__(self, "prohibited_claims", prohibited_claims)
        object.__setattr__(
            self,
            "bounded_interpretation",
            bounded_interpretation,
        )

    @staticmethod
    def _normalize_identifier(
        value: object,
        *,
        field_name: str,
    ) -> str:
        normalized = "_".join(
            str(value).strip().lower().split()
        )

        if not normalized:
            raise ValueError(
                f"{field_name} must not be blank."
            )

        return normalized

    @staticmethod
    def _normalize_required_text(
        value: object,
        *,
        field_name: str,
    ) -> str:
        normalized = str(value).strip()

        if not normalized:
            raise ValueError(
                f"{field_name} must not be blank."
            )

        return normalized

    @classmethod
    def _normalize_prohibited_claims(
        cls,
        value: object,
    ) -> tuple[str, ...]:
        if isinstance(
            value,
            (str, bytes),
        ):
            raise TypeError(
                "prohibited_claims must be a non-empty sequence."
            )

        try:
            raw_claims = tuple(value)
        except TypeError as exc:
            raise TypeError(
                "prohibited_claims must be a non-empty sequence."
            ) from exc

        if not raw_claims:
            raise ValueError(
                "prohibited_claims must not be empty."
            )

        return tuple(
            cls._normalize_required_text(
                claim,
                field_name="prohibited_claims",
            )
            for claim in raw_claims
        )
