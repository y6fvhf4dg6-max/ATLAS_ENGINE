from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_canonical_head_benchmark_candidate_observation import (
    AtlasCanonicalHeadBenchmarkCandidateObservation,
)
from CORE.atlas_canonical_head_benchmark_evidence_coverage import (
    AtlasCanonicalHeadBenchmarkEvidenceCoverage,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadBenchmarkGapClosureObservation:
    candidate_id: str
    architecture_kind: str
    coverage: AtlasCanonicalHeadBenchmarkEvidenceCoverage

    commercial_license_state: str
    privacy_data_retention_state: str
    model_weight_restrictions_state: str
    dataset_restrictions_state: str

    evidence_limitations: tuple[str, ...]

    SUPPORTED_POLICY_STATES = (
        "ACCEPTABLE",
        "BLOCKED",
        "UNRESOLVED",
    )

    POLICY_FIELDS = (
        "commercial_license_state",
        "privacy_data_retention_state",
        "model_weight_restrictions_state",
        "dataset_restrictions_state",
    )

    def __post_init__(self) -> None:
        candidate_id = str(
            self.candidate_id
        ).strip()

        if not candidate_id:
            raise ValueError(
                "candidate_id must be non-blank."
            )

        object.__setattr__(
            self,
            "candidate_id",
            candidate_id,
        )

        architecture_kind = "_".join(
            str(
                self.architecture_kind
            )
            .strip()
            .lower()
            .split()
        )

        if (
            architecture_kind
            not in AtlasCanonicalHeadBenchmarkCandidateObservation
            .SUPPORTED_ARCHITECTURE_KINDS
        ):
            raise ValueError(
                "architecture_kind must be one of "
                f"{AtlasCanonicalHeadBenchmarkCandidateObservation.SUPPORTED_ARCHITECTURE_KINDS}."
            )

        object.__setattr__(
            self,
            "architecture_kind",
            architecture_kind,
        )

        if not isinstance(
            self.coverage,
            AtlasCanonicalHeadBenchmarkEvidenceCoverage,
        ):
            raise TypeError(
                "coverage must be an "
                "AtlasCanonicalHeadBenchmarkEvidenceCoverage."
            )

        if self.coverage.candidate_id != candidate_id:
            raise ValueError(
                "candidate_id must match coverage.candidate_id."
            )

        for field_name in self.POLICY_FIELDS:
            value = getattr(
                self,
                field_name,
            )

            if not isinstance(
                value,
                str,
            ):
                raise TypeError(
                    f"{field_name} must be a string."
                )

            normalized = value.strip().upper()

            if (
                normalized
                not in self.SUPPORTED_POLICY_STATES
            ):
                raise ValueError(
                    f"{field_name} must be one of "
                    f"{self.SUPPORTED_POLICY_STATES}."
                )

            object.__setattr__(
                self,
                field_name,
                normalized,
            )

        normalized_limitations = tuple(
            str(item).strip()
            for item in self.evidence_limitations
        )

        if any(
            not item
            for item in normalized_limitations
        ):
            raise ValueError(
                "evidence_limitations must not contain blank values."
            )

        object.__setattr__(
            self,
            "evidence_limitations",
            normalized_limitations,
        )

    @property
    def unresolved_quality_channels(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            field_name
            for field_name in self.coverage.QUALITY_CHANNELS
            if getattr(
                self.coverage,
                field_name,
            )
            in (
                "PARTIAL",
                "MISSING",
            )
        )

    @property
    def blocked_policy_channels(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            field_name
            for field_name in self.POLICY_FIELDS
            if getattr(
                self,
                field_name,
            )
            == "BLOCKED"
        )

    @property
    def unresolved_policy_channels(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            field_name
            for field_name in self.POLICY_FIELDS
            if getattr(
                self,
                field_name,
            )
            == "UNRESOLVED"
        )
