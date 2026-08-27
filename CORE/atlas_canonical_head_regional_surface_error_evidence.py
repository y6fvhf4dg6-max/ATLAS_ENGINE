from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class AtlasCanonicalHeadRegionalSurfaceErrorEvidence:
    """Bounded evidence contract for Phase 8 Item 9.12.

    Records regional surface-error measurement capability and the current
    metric-GT blockers without fabricating real subject-specific millimetre
    results or Phase decisions.
    """

    CRITERIA: ClassVar[tuple[str, ...]] = (
        "point_to_surface_distance",
        "bidirectional_symmetric_surface_error",
        "mean_distance",
        "median_distance",
        "rms_distance",
        "p95_distance",
        "maximum_outlier_characterization",
        "surface_normal_discrepancy",
        "real_metric_regional_result",
    )

    EVALUATION_SPACES: ClassVar[tuple[str, ...]] = (
        "metric_3d_ground_truth",
        "canonical_model",
    )

    EVIDENCE_STATUSES: ClassVar[tuple[str, ...]] = (
        "capability_present",
        "capability_present_metric_result_blocked",
        "blocked",
        "not_established",
    )

    BLOCKER_STATES: ClassVar[tuple[str, ...]] = (
        "alignment_inadmissible",
        "regional_correspondence_unverified",
        "region_mapping_unverified",
        "metric_ground_truth_unavailable",
        "none",
    )

    SUPPORTED_RAW_METRIC_FAMILIES: ClassVar[tuple[str, ...]] = (
        "point_to_surface_distance",
        "mean",
        "median",
        "rms",
        "p95",
        "maximum",
    )

    criterion: str
    evaluation_space: str
    evidence_status: str
    blocker_states: tuple[str, ...]
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

        blockers = self.blocker_states
        if not isinstance(blockers, tuple):
            blockers = tuple(blockers)

        if not blockers:
            raise ValueError("blocker_states must not be empty")

        normalized_blockers = tuple(
            self._normalize_identifier(blocker)
            for blocker in blockers
        )

        for blocker in normalized_blockers:
            if blocker not in self.BLOCKER_STATES:
                raise ValueError(
                    "blocker_states must contain only "
                    f"{self.BLOCKER_STATES}"
                )

        if (
            "none" in normalized_blockers
            and len(normalized_blockers) != 1
        ):
            raise ValueError(
                "blocker_states 'none' must not be combined "
                "with other blocker states"
            )

        object.__setattr__(
            self,
            "blocker_states",
            normalized_blockers,
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
                    "prohibited_claims must contain only "
                    "non-empty strings"
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
