from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class AtlasCanonicalHeadCustomerVisibleLikenessRiskEvidence:
    """Bounded evidence contract for Phase 8 Item 9.14.

    Separates potential identity-bearing/customer-visible risk from verified
    customer-visible degradation or commercial likeness acceptance/rejection.
    """

    REGIONS: ClassVar[tuple[str, ...]] = (
        "nose",
        "jaw_chin",
        "orbital_region",
        "cheek_midface",
        "head_silhouette_profile",
    )

    RISK_STATUSES: ClassVar[tuple[str, ...]] = (
        "bounded_potential_likeness_risk",
        "bounded_mixed_likeness_risk",
        "unresolved_likeness_risk",
    )

    VERIFICATION_STATES: ClassVar[tuple[str, ...]] = (
        "potential_not_verified_customer_visible",
        "not_verified_customer_visible",
    )

    EVIDENCE_ORIGINS: ClassVar[tuple[str, ...]] = (
        "directly_observed",
        "multiview_constrained",
        "model_prior_inferred",
        "generated_completion",
        "unresolved",
    )

    region: str
    risk_status: str
    verification_state: str
    evidence_origin: str
    source_reference: str
    semantic_scope: str
    permitted_claim: str
    prohibited_claims: tuple[str, ...]
    bounded_interpretation: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "region",
            self._normalize_identifier(self.region),
        )
        object.__setattr__(
            self,
            "risk_status",
            self._normalize_identifier(self.risk_status),
        )
        object.__setattr__(
            self,
            "verification_state",
            self._normalize_identifier(self.verification_state),
        )
        object.__setattr__(
            self,
            "evidence_origin",
            self._normalize_identifier(self.evidence_origin),
        )

        if self.region not in self.REGIONS:
            raise ValueError(
                f"region must be one of {self.REGIONS}"
            )

        if self.risk_status not in self.RISK_STATUSES:
            raise ValueError(
                "risk_status must be one of "
                f"{self.RISK_STATUSES}"
            )

        if self.verification_state not in self.VERIFICATION_STATES:
            raise ValueError(
                "verification_state must be one of "
                f"{self.VERIFICATION_STATES}"
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
