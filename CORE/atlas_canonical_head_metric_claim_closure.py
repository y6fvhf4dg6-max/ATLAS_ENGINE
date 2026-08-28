from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class AtlasCanonicalHeadMetricClaimClosure:
    """Phase 8 / Item 10.15 claim-specific metric closure contract.

    Classifies one intended metric claim from the explicit prerequisite
    evidence states required by Item 10.15. This contract does not produce
    a global metric score, a Phase 8 decision, or Phase 9 authorization.
    """

    claim_id: str
    claim_scope: str

    ground_truth_admissibility: str
    unit_certainty: str
    scale_traceability: str
    coordinate_system_certainty: str
    alignment_admissibility: str
    correspondence_admissibility: str
    uncertainty: str
    coverage: str
    leakage: str

    provenance_reference: str

    CLAIM_SCOPES: ClassVar[tuple[str, ...]] = (
        "GLOBAL",
        "REGIONAL",
    )

    EVIDENCE_STATES: ClassVar[tuple[str, ...]] = (
        "SUPPORTED",
        "PARTIAL",
        "MISSING",
        "BLOCKED",
    )

    PREREQUISITE_FIELDS: ClassVar[tuple[str, ...]] = (
        "ground_truth_admissibility",
        "unit_certainty",
        "scale_traceability",
        "coordinate_system_certainty",
        "alignment_admissibility",
        "correspondence_admissibility",
        "uncertainty",
        "coverage",
        "leakage",
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "claim_id",
            self._normalize_required_text(
                self.claim_id,
                name="claim_id",
            ),
        )

        claim_scope = self._normalize_state(
            self.claim_scope,
            name="claim_scope",
        )
        if claim_scope not in self.CLAIM_SCOPES:
            raise ValueError(
                f"claim_scope must be one of {self.CLAIM_SCOPES}."
            )
        object.__setattr__(
            self,
            "claim_scope",
            claim_scope,
        )

        for field_name in self.PREREQUISITE_FIELDS:
            normalized = self._normalize_state(
                getattr(self, field_name),
                name=field_name,
            )
            if normalized not in self.EVIDENCE_STATES:
                raise ValueError(
                    f"{field_name} must be one of "
                    f"{self.EVIDENCE_STATES}."
                )
            object.__setattr__(
                self,
                field_name,
                normalized,
            )

        object.__setattr__(
            self,
            "provenance_reference",
            self._normalize_required_text(
                self.provenance_reference,
                name="provenance_reference",
            ),
        )

    HARD_BLOCKER_FIELDS: ClassVar[tuple[str, ...]] = (
        "ground_truth_admissibility",
        "unit_certainty",
        "alignment_admissibility",
        "correspondence_admissibility",
    )

    @property
    def evidence_state(self) -> str:
        hard_blocker_states = tuple(
            getattr(self, field_name)
            for field_name in self.HARD_BLOCKER_FIELDS
        )

        if any(
            state != "SUPPORTED"
            for state in hard_blocker_states
        ):
            return "BLOCKED"

        states = tuple(
            getattr(self, field_name)
            for field_name in self.PREREQUISITE_FIELDS
        )

        if "BLOCKED" in states:
            return "BLOCKED"

        if "MISSING" in states:
            return "MISSING"

        if "PARTIAL" in states:
            return "PARTIAL"

        return "SUPPORTED"

    @staticmethod
    def _normalize_required_text(
        value: object,
        *,
        name: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{name} must be a string."
            )

        normalized = value.strip()
        if not normalized:
            raise ValueError(
                f"{name} must be non-blank."
            )

        return normalized

    @staticmethod
    def _normalize_state(
        value: object,
        *,
        name: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{name} must be a string."
            )

        normalized = value.strip().upper()
        if not normalized:
            raise ValueError(
                f"{name} must be non-blank."
            )

        return normalized
