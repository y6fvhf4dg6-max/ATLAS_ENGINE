from __future__ import annotations

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadMetricGroundTruthUsage:
    evaluation_only: bool
    used_during_fitting: bool
    used_during_tuning: bool
    used_during_model_selection: bool
    provenance_reference: str

    def __post_init__(self) -> None:
        for name in (
            "evaluation_only",
            "used_during_fitting",
            "used_during_tuning",
            "used_during_model_selection",
        ):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(
                    f"{name} must be a bool."
                )

        provenance_reference = self.provenance_reference
        if (
            not isinstance(provenance_reference, str)
            or not provenance_reference.strip()
        ):
            raise ValueError(
                "provenance_reference must be a non-empty string."
            )

        if (
            self.evaluation_only
            and (
                self.used_during_fitting
                or self.used_during_tuning
                or self.used_during_model_selection
            )
        ):
            raise ValueError(
                "evaluation_only ground truth cannot also be used during "
                "fitting, tuning, or model selection."
            )

        if not (
            self.evaluation_only
            or self.used_during_fitting
            or self.used_during_tuning
            or self.used_during_model_selection
        ):
            raise ValueError(
                "ground-truth usage must explicitly identify evaluation_only, "
                "fitting, tuning, or model-selection use."
            )

        object.__setattr__(
            self,
            "provenance_reference",
            provenance_reference.strip(),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadMetricGroundTruthLeakageObservation:
    dimension: str
    evidence_state: str
    provenance_reference: str

    DIMENSIONS = (
        "GROUND_TRUTH_USAGE",
        "SUBJECT_TRAINING_OVERLAP",
        "VALIDATION_OVERLAP",
        "REGISTRATION_LEAKAGE",
        "CORRESPONDENCE_LEAKAGE",
        "EVALUATION_REGION_LEAKAGE",
        "POST_HOC_REGION_SELECTION",
        "REPEATED_BENCHMARK_ADAPTATION",
    )

    EVIDENCE_STATES = (
        "NO_LEAKAGE_IDENTIFIED",
        "LEAKAGE_PRESENT",
        "UNRESOLVED",
        "NOT_APPLICABLE",
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
            "provenance_reference",
            provenance_reference.strip(),
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
class AtlasCanonicalHeadMetricGroundTruthLeakageEvaluationResult:
    observations: tuple[
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
        ...
    ]
    no_leakage_identified_dimensions: tuple[str, ...]
    leakage_present_dimensions: tuple[str, ...]
    unresolved_dimensions: tuple[str, ...]
    not_applicable_dimensions: tuple[str, ...]
    missing_dimensions: tuple[str, ...]
    coverage_state: str


class AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation:
    @classmethod
    def evaluate(
        cls,
        *,
        observations: tuple[
            AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
            ...
        ],
        ground_truth_usage: AtlasCanonicalHeadMetricGroundTruthUsage | None = None,
    ) -> AtlasCanonicalHeadMetricGroundTruthLeakageEvaluationResult:
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
                AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
            ):
                raise TypeError(
                    "observations must contain only "
                    "AtlasCanonicalHeadMetricGroundTruthLeakageObservation."
                )

            try:
                observation = (
                    AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
                        dimension=observation.dimension,
                        evidence_state=observation.evidence_state,
                        provenance_reference=observation.provenance_reference,
                    )
                )
            except AttributeError as exc:
                raise ValueError(
                    "ground-truth leakage observations must satisfy the "
                    "complete "
                    "AtlasCanonicalHeadMetricGroundTruthLeakageObservation "
                    "contract."
                ) from exc

            normalized_observations.append(observation)

        normalized_observations = tuple(normalized_observations)

        dimensions = tuple(
            observation.dimension
            for observation in normalized_observations
        )

        if len(set(dimensions)) != len(dimensions):
            raise ValueError(
                "ground-truth leakage dimensions must be unique; "
                "duplicate dimension detected."
            )

        usage_observation = next(
            (
                observation
                for observation in normalized_observations
                if observation.dimension == "GROUND_TRUTH_USAGE"
            ),
            None,
        )

        if usage_observation is not None:
            usage_state_requires_known_usage = (
                usage_observation.evidence_state
                in (
                    "NO_LEAKAGE_IDENTIFIED",
                    "LEAKAGE_PRESENT",
                )
            )

            if usage_state_requires_known_usage and not isinstance(
                ground_truth_usage,
                AtlasCanonicalHeadMetricGroundTruthUsage,
            ):
                raise TypeError(
                    "GROUND_TRUTH_USAGE clean/leakage claims require explicit "
                    "ground_truth_usage satisfying "
                    "AtlasCanonicalHeadMetricGroundTruthUsage."
                )

            if ground_truth_usage is not None:
                if not isinstance(
                    ground_truth_usage,
                    AtlasCanonicalHeadMetricGroundTruthUsage,
                ):
                    raise TypeError(
                        "ground_truth_usage must be an "
                        "AtlasCanonicalHeadMetricGroundTruthUsage."
                    )

                try:
                    ground_truth_usage = AtlasCanonicalHeadMetricGroundTruthUsage(
                        evaluation_only=ground_truth_usage.evaluation_only,
                        used_during_fitting=ground_truth_usage.used_during_fitting,
                        used_during_tuning=ground_truth_usage.used_during_tuning,
                        used_during_model_selection=(
                            ground_truth_usage.used_during_model_selection
                        ),
                        provenance_reference=(
                            ground_truth_usage.provenance_reference
                        ),
                    )
                except AttributeError as exc:
                    raise ValueError(
                        "ground_truth_usage must satisfy the complete "
                        "AtlasCanonicalHeadMetricGroundTruthUsage contract."
                    ) from exc

            if ground_truth_usage is not None:
                dependency_present = (
                    ground_truth_usage.used_during_fitting
                    or ground_truth_usage.used_during_tuning
                    or ground_truth_usage.used_during_model_selection
                )

                expected_usage_state = (
                    "LEAKAGE_PRESENT"
                    if dependency_present
                    else "NO_LEAKAGE_IDENTIFIED"
                )

                if usage_observation.evidence_state != expected_usage_state:
                    raise ValueError(
                        "GROUND_TRUTH_USAGE evidence_state contradicts known "
                        "ground_truth_usage; known evaluation-only usage requires "
                        "NO_LEAKAGE_IDENTIFIED, while known fitting/tuning/"
                        "model-selection dependency requires LEAKAGE_PRESENT. "
                        "UNRESOLVED or NOT_APPLICABLE cannot be used when "
                        "ground_truth_usage is known."
                    )

        no_leakage_identified_dimensions = tuple(
            observation.dimension
            for observation in normalized_observations
            if observation.evidence_state == "NO_LEAKAGE_IDENTIFIED"
        )

        leakage_present_dimensions = tuple(
            observation.dimension
            for observation in normalized_observations
            if observation.evidence_state == "LEAKAGE_PRESENT"
        )

        unresolved_dimensions = tuple(
            observation.dimension
            for observation in normalized_observations
            if observation.evidence_state == "UNRESOLVED"
        )

        not_applicable_dimensions = tuple(
            observation.dimension
            for observation in normalized_observations
            if observation.evidence_state == "NOT_APPLICABLE"
        )

        present_dimensions = set(dimensions)

        missing_dimensions = tuple(
            dimension
            for dimension in (
                AtlasCanonicalHeadMetricGroundTruthLeakageObservation
                .DIMENSIONS
            )
            if dimension not in present_dimensions
        )

        coverage_state = (
            "COMPLETE"
            if not missing_dimensions
            else "INCOMPLETE"
        )

        return AtlasCanonicalHeadMetricGroundTruthLeakageEvaluationResult(
            observations=normalized_observations,
            no_leakage_identified_dimensions=(
                no_leakage_identified_dimensions
            ),
            leakage_present_dimensions=leakage_present_dimensions,
            unresolved_dimensions=unresolved_dimensions,
            not_applicable_dimensions=not_applicable_dimensions,
            missing_dimensions=missing_dimensions,
            coverage_state=coverage_state,
        )
