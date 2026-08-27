from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class AtlasCanonicalHeadFacialRegionQualityClosure:
    """Phase 8 / Main Checklist Item 9.15 closure contract.

    Records the bounded Item 9 closure while preserving the ability for later,
    stronger evidence to reopen or explicitly supersede regional conclusions.
    """

    DECISIONS: ClassVar[tuple[str, ...]] = (
        "pass",
        "bounded_pass",
        "hold",
        "revision_required",
    )

    SUPERSEDING_SOURCES: ClassVar[tuple[str, ...]] = (
        "item_10_metric_ground_truth",
        "item_11_physical_representation",
        "item_14_three_class_architecture_comparison",
        "item_15_phase8_final_decision",
        "explicit_plan_revision",
    )

    decision: str
    evidence_date: str
    retained_limitations: tuple[str, ...]
    bounded_interpretation: str
    reopen_on_new_evidence: bool
    superseding_sources: tuple[str, ...]
    historical_record_policy: str
    prohibited_claims: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "decision",
            self._normalize_identifier(self.decision),
        )

        if self.decision not in self.DECISIONS:
            raise ValueError(
                f"decision must be one of {self.DECISIONS}"
            )

        if not isinstance(self.evidence_date, str) or not self.evidence_date.strip():
            raise ValueError("evidence_date must be a non-empty string")
        object.__setattr__(
            self,
            "evidence_date",
            self.evidence_date.strip(),
        )

        object.__setattr__(
            self,
            "retained_limitations",
            self._normalize_nonempty_string_tuple(
                self.retained_limitations,
                field_name="retained_limitations",
            ),
        )

        if (
            not isinstance(self.bounded_interpretation, str)
            or not self.bounded_interpretation.strip()
        ):
            raise ValueError(
                "bounded_interpretation must be a non-empty string"
            )
        object.__setattr__(
            self,
            "bounded_interpretation",
            self.bounded_interpretation.strip(),
        )

        if self.reopen_on_new_evidence is not True:
            raise ValueError(
                "reopen_on_new_evidence must be True for this bounded closure"
            )

        normalized_sources = tuple(
            self._normalize_identifier(source)
            for source in self.superseding_sources
        )
        if not normalized_sources:
            raise ValueError(
                "superseding_sources must not be empty"
            )
        unknown_sources = tuple(
            source
            for source in normalized_sources
            if source not in self.SUPERSEDING_SOURCES
        )
        if unknown_sources:
            raise ValueError(
                "superseding_sources contains unsupported source(s): "
                f"{unknown_sources}"
            )
        object.__setattr__(
            self,
            "superseding_sources",
            normalized_sources,
        )

        if (
            not isinstance(self.historical_record_policy, str)
            or not self.historical_record_policy.strip()
        ):
            raise ValueError(
                "historical_record_policy must be a non-empty string"
            )
        object.__setattr__(
            self,
            "historical_record_policy",
            self.historical_record_policy.strip(),
        )

        object.__setattr__(
            self,
            "prohibited_claims",
            self._normalize_nonempty_string_tuple(
                self.prohibited_claims,
                field_name="prohibited_claims",
            ),
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

    @staticmethod
    def _normalize_nonempty_string_tuple(
        values: tuple[str, ...],
        *,
        field_name: str,
    ) -> tuple[str, ...]:
        if not isinstance(values, tuple):
            values = tuple(values)

        if not values:
            raise ValueError(
                f"{field_name} must not be empty"
            )

        normalized = []
        for value in values:
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must contain only non-empty strings"
                )
            normalized.append(value.strip())

        return tuple(normalized)
