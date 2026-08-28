from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadMetricRepeatabilityObservation:
    dimension: str
    evidence_state: str
    repeatability_mm: float | None
    provenance_reference: str

    DIMENSIONS = (
        "REPEATED_SENSOR_ACQUISITION",
        "REPEATED_PREPROCESSING",
        "REPEATED_RECONSTRUCTION",
        "REPEATED_REGISTRATION_EVALUATION",
        "INTRA_RUN_REPEATABILITY",
        "INTER_RUN_REPEATABILITY",
        "INTER_CAPTURE_REPEATABILITY",
        "INTER_OPERATOR_REPEATABILITY",
    )

    EVIDENCE_STATES = (
        "QUANTIFIED",
        "UNRESOLVED",
        "NOT_AVAILABLE",
    )

    def __post_init__(self) -> None:
        dimension = self._normalize_state(
            self.dimension,
            name="dimension",
        )
        evidence_state = self._normalize_state(
            self.evidence_state,
            name="evidence_state",
        )

        if dimension not in self.DIMENSIONS:
            raise ValueError(
                f"dimension must be one of {self.DIMENSIONS}."
            )

        if evidence_state not in self.EVIDENCE_STATES:
            raise ValueError(
                f"evidence_state must be one of {self.EVIDENCE_STATES}."
            )

        provenance_reference = self.provenance_reference
        if (
            not isinstance(provenance_reference, str)
            or not provenance_reference.strip()
        ):
            raise ValueError(
                "provenance_reference must be a non-empty string."
            )

        provenance_reference = provenance_reference.strip()

        if evidence_state == "QUANTIFIED":
            if self.repeatability_mm is None:
                raise ValueError(
                    "QUANTIFIED repeatability requires repeatability_mm."
                )

            repeatability_mm = float(
                self.repeatability_mm
            )

            if (
                not np.isfinite(repeatability_mm)
                or repeatability_mm < 0.0
            ):
                raise ValueError(
                    "repeatability_mm must be finite and non-negative."
                )
        else:
            if self.repeatability_mm is not None:
                raise ValueError(
                    f"{evidence_state} repeatability cannot carry numeric "
                    "repeatability_mm."
                )

            repeatability_mm = None

        object.__setattr__(
            self,
            "dimension",
            dimension,
        )
        object.__setattr__(
            self,
            "evidence_state",
            evidence_state,
        )
        object.__setattr__(
            self,
            "repeatability_mm",
            repeatability_mm,
        )
        object.__setattr__(
            self,
            "provenance_reference",
            provenance_reference,
        )

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

        normalized = "_".join(
            value.strip().upper().replace("-", "_").split()
        )

        if not normalized:
            raise ValueError(
                f"{name} must not be blank."
            )

        return normalized


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadMetricRepeatabilityEvaluationResult:
    observations: tuple[
        AtlasCanonicalHeadMetricRepeatabilityObservation,
        ...
    ]
    quantified_dimensions: tuple[str, ...]
    unresolved_dimensions: tuple[str, ...]
    not_available_dimensions: tuple[str, ...]
    missing_dimensions: tuple[str, ...]
    coverage_state: str


class AtlasCanonicalHeadMetricRepeatabilityEvaluation:
    @classmethod
    def evaluate(
        cls,
        *,
        observations: tuple[
            AtlasCanonicalHeadMetricRepeatabilityObservation,
            ...
        ],
    ) -> AtlasCanonicalHeadMetricRepeatabilityEvaluationResult:
        if not isinstance(observations, tuple):
            raise TypeError(
                "observations must be a tuple."
            )

        if not observations:
            raise ValueError(
                "observations must not be empty."
            )

        normalized_observations = []

        for observation in observations:
            if not isinstance(
                observation,
                AtlasCanonicalHeadMetricRepeatabilityObservation,
            ):
                raise TypeError(
                    "observations must contain only "
                    "AtlasCanonicalHeadMetricRepeatabilityObservation."
                )

            try:
                observation = AtlasCanonicalHeadMetricRepeatabilityObservation(
                    dimension=observation.dimension,
                    evidence_state=observation.evidence_state,
                    repeatability_mm=observation.repeatability_mm,
                    provenance_reference=observation.provenance_reference,
                )
            except AttributeError as exc:
                raise ValueError(
                    "repeatability observations must satisfy the complete "
                    "AtlasCanonicalHeadMetricRepeatabilityObservation contract."
                ) from exc

            normalized_observations.append(
                observation
            )

        normalized_observations = tuple(
            normalized_observations
        )

        dimensions = tuple(
            observation.dimension
            for observation in normalized_observations
        )

        if len(set(dimensions)) != len(dimensions):
            raise ValueError(
                "repeatability observation dimensions must be unique; "
                "duplicate dimension detected."
            )

        quantified_dimensions = tuple(
            observation.dimension
            for observation in normalized_observations
            if observation.evidence_state == "QUANTIFIED"
        )
        unresolved_dimensions = tuple(
            observation.dimension
            for observation in normalized_observations
            if observation.evidence_state == "UNRESOLVED"
        )
        not_available_dimensions = tuple(
            observation.dimension
            for observation in normalized_observations
            if observation.evidence_state == "NOT_AVAILABLE"
        )

        present_dimensions = set(dimensions)

        missing_dimensions = tuple(
            dimension
            for dimension in AtlasCanonicalHeadMetricRepeatabilityObservation.DIMENSIONS
            if dimension not in present_dimensions
        )

        coverage_state = (
            "COMPLETE"
            if not missing_dimensions
            else "INCOMPLETE"
        )

        return AtlasCanonicalHeadMetricRepeatabilityEvaluationResult(
            observations=normalized_observations,
            quantified_dimensions=quantified_dimensions,
            unresolved_dimensions=unresolved_dimensions,
            not_available_dimensions=not_available_dimensions,
            missing_dimensions=missing_dimensions,
            coverage_state=coverage_state,
        )
