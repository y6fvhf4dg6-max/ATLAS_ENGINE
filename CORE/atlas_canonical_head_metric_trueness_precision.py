from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadMetricTruenessPrecisionObservation:
    concept: str
    evidence_state: str
    value_mm: float | None
    provenance_reference: str
    evidence_basis: str | None = None

    CONCEPTS = (
        "TRUENESS",
        "PRECISION",
    )

    EVIDENCE_STATES = (
        "QUANTIFIED",
        "UNRESOLVED",
    )

    EVIDENCE_BASES = (
        "REFERENCE_TRUTH_COMPARISON",
        "REPEATED_MEASUREMENT_CONSISTENCY",
    )

    CONCEPT_EVIDENCE_BASIS = {
        "TRUENESS": "REFERENCE_TRUTH_COMPARISON",
        "PRECISION": "REPEATED_MEASUREMENT_CONSISTENCY",
    }

    def __post_init__(self) -> None:
        concept = self._normalize_state(
            self.concept,
            name="concept",
        )
        evidence_state = self._normalize_state(
            self.evidence_state,
            name="evidence_state",
        )

        if concept not in self.CONCEPTS:
            raise ValueError(
                f"concept must be one of {self.CONCEPTS}."
            )

        if evidence_state not in self.EVIDENCE_STATES:
            raise ValueError(
                f"evidence_state must be one of {self.EVIDENCE_STATES}."
            )

        expected_evidence_basis = self.CONCEPT_EVIDENCE_BASIS[concept]

        if self.evidence_basis is None:
            if evidence_state == "QUANTIFIED":
                raise ValueError(
                    "QUANTIFIED measurement concept requires explicit "
                    "evidence_basis."
                )
            evidence_basis = None
        else:
            evidence_basis = self._normalize_state(
                self.evidence_basis,
                name="evidence_basis",
            )

            if evidence_basis not in self.EVIDENCE_BASES:
                raise ValueError(
                    f"evidence_basis must be one of {self.EVIDENCE_BASES}."
                )

            if evidence_basis != expected_evidence_basis:
                raise ValueError(
                    f"{concept} evidence_basis must be "
                    f"{expected_evidence_basis}."
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
            if self.value_mm is None:
                raise ValueError(
                    "QUANTIFIED measurement concept requires value_mm."
                )

            value_mm = float(self.value_mm)

            if (
                not np.isfinite(value_mm)
                or value_mm < 0.0
            ):
                raise ValueError(
                    "value_mm must be finite and non-negative."
                )
        else:
            if self.value_mm is not None:
                raise ValueError(
                    "UNRESOLVED measurement concept cannot carry numeric "
                    "value_mm."
                )

            value_mm = None

        object.__setattr__(
            self,
            "concept",
            concept,
        )
        object.__setattr__(
            self,
            "evidence_state",
            evidence_state,
        )
        object.__setattr__(
            self,
            "value_mm",
            value_mm,
        )
        object.__setattr__(
            self,
            "provenance_reference",
            provenance_reference,
        )
        object.__setattr__(
            self,
            "evidence_basis",
            evidence_basis,
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
class AtlasCanonicalHeadMetricTruenessPrecisionEvaluationResult:
    observations: tuple[
        AtlasCanonicalHeadMetricTruenessPrecisionObservation,
        ...
    ]
    quantified_concepts: tuple[str, ...]
    unresolved_concepts: tuple[str, ...]
    missing_concepts: tuple[str, ...]
    coverage_state: str


class AtlasCanonicalHeadMetricTruenessPrecisionEvaluation:
    @classmethod
    def evaluate(
        cls,
        *,
        observations: tuple[
            AtlasCanonicalHeadMetricTruenessPrecisionObservation,
            ...
        ],
    ) -> AtlasCanonicalHeadMetricTruenessPrecisionEvaluationResult:
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
                AtlasCanonicalHeadMetricTruenessPrecisionObservation,
            ):
                raise TypeError(
                    "observations must contain only "
                    "AtlasCanonicalHeadMetricTruenessPrecisionObservation."
                )

            try:
                observation = (
                    AtlasCanonicalHeadMetricTruenessPrecisionObservation(
                        concept=observation.concept,
                        evidence_state=observation.evidence_state,
                        value_mm=observation.value_mm,
                        provenance_reference=observation.provenance_reference,
                        evidence_basis=observation.evidence_basis,
                    )
                )
            except AttributeError as exc:
                raise ValueError(
                    "measurement observations must satisfy the complete "
                    "AtlasCanonicalHeadMetricTruenessPrecisionObservation "
                    "contract."
                ) from exc

            normalized_observations.append(observation)

        normalized_observations = tuple(normalized_observations)

        concepts = tuple(
            observation.concept
            for observation in normalized_observations
        )

        if len(set(concepts)) != len(concepts):
            raise ValueError(
                "measurement concepts must be unique; duplicate concept detected."
            )

        quantified_concepts = tuple(
            observation.concept
            for observation in normalized_observations
            if observation.evidence_state == "QUANTIFIED"
        )

        unresolved_concepts = tuple(
            observation.concept
            for observation in normalized_observations
            if observation.evidence_state == "UNRESOLVED"
        )

        present_concepts = set(concepts)

        missing_concepts = tuple(
            concept
            for concept in AtlasCanonicalHeadMetricTruenessPrecisionObservation.CONCEPTS
            if concept not in present_concepts
        )

        coverage_state = (
            "COMPLETE"
            if not missing_concepts
            else "INCOMPLETE"
        )

        return AtlasCanonicalHeadMetricTruenessPrecisionEvaluationResult(
            observations=normalized_observations,
            quantified_concepts=quantified_concepts,
            unresolved_concepts=unresolved_concepts,
            missing_concepts=missing_concepts,
            coverage_state=coverage_state,
        )
