from __future__ import annotations

from dataclasses import dataclass, fields

import numpy as np

from CORE.atlas_canonical_head_metric_ground_truth_observation import (
    AtlasCanonicalHeadMetricGroundTruthObservation,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadMetricDistanceAggregate:
    sample_count: int
    mean_distance_mm: float
    median_distance_mm: float
    rmse_distance_mm: float
    p95_distance_mm: float
    max_distance_mm: float

    @classmethod
    def from_distances(
        cls,
        *,
        distances_mm: object,
    ) -> "AtlasCanonicalHeadMetricDistanceAggregate":
        distances = np.asarray(
            distances_mm,
            dtype=np.float64,
        )

        if (
            distances.ndim != 1
            or distances.shape[0] == 0
        ):
            raise ValueError(
                "distances_mm must be a non-empty 1D array."
            )

        if (
            not np.all(np.isfinite(distances))
            or np.any(distances < 0.0)
        ):
            raise ValueError(
                "distances_mm must contain finite nonnegative values."
            )

        return cls(
            sample_count=int(distances.shape[0]),
            mean_distance_mm=float(np.mean(distances)),
            median_distance_mm=float(np.median(distances)),
            rmse_distance_mm=float(
                np.sqrt(
                    np.mean(
                        np.square(distances)
                    )
                )
            ),
            p95_distance_mm=float(
                np.percentile(
                    distances,
                    95.0,
                )
            ),
            max_distance_mm=float(np.max(distances)),
        )

    def __post_init__(self) -> None:
        if (
            isinstance(self.sample_count, bool)
            or not isinstance(
                self.sample_count,
                (int, np.integer),
            )
            or int(self.sample_count) <= 0
        ):
            raise ValueError(
                "sample_count must be a positive integer."
            )

        object.__setattr__(
            self,
            "sample_count",
            int(self.sample_count),
        )

        for field_name in (
            "mean_distance_mm",
            "median_distance_mm",
            "rmse_distance_mm",
            "p95_distance_mm",
            "max_distance_mm",
        ):
            value = float(
                getattr(self, field_name)
            )

            if (
                not np.isfinite(value)
                or value < 0.0
            ):
                raise ValueError(
                    f"{field_name} must be finite and nonnegative."
                )

            object.__setattr__(
                self,
                field_name,
                value,
            )


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadGlobalMetricErrorEvaluationResult:
    aggregate: AtlasCanonicalHeadMetricDistanceAggregate
    source_to_target_aggregate: AtlasCanonicalHeadMetricDistanceAggregate | None
    target_to_source_aggregate: AtlasCanonicalHeadMetricDistanceAggregate | None
    symmetric_bidirectional_aggregate: AtlasCanonicalHeadMetricDistanceAggregate | None
    valid_correspondence_count: int
    evaluation_coverage_denominator: int
    missing_surface_fraction: float
    normal_orientation_angular_discrepancy_deg: float | None
    ground_truth_observation_id: str
    ground_truth_source_id: str
    ground_truth_admissibility_state: str
    alignment_admissibility: str
    alignment_bias_leakage_risk: str
    correspondence_evidence_class: str
    correspondence_direction: str
    bidirectional_evaluation_state: str
    regional_blocker_state: str
    global_metric_result_state: str

    GROUND_TRUTH_STATES = (
        "ACCEPTABLE",
        "BLOCKED",
        "UNRESOLVED",
    )

    ALIGNMENT_STATES = (
        "ADMISSIBLE",
        "INADMISSIBLE",
        "UNRESOLVED",
    )

    LEAKAGE_RISK_STATES = (
        "OVERLAP_PRESENT",
        "NO_OVERLAP_IDENTIFIED",
    )

    CORRESPONDENCE_CLASSES = (
        "DENSE_ANATOMICAL_CORRESPONDENCE",
        "VERIFIED_SEMANTIC_BARYCENTRIC_CORRESPONDENCE",
        "SPARSE_LANDMARK_CORRESPONDENCE",
        "GEOMETRIC_CLOSEST_POINT_CORRESPONDENCE",
        "UNRESOLVED_CORRESPONDENCE",
    )

    CORRESPONDENCE_DIRECTIONS = (
        "SOURCE_TO_TARGET",
        "TARGET_TO_SOURCE",
        "BIDIRECTIONAL",
        "UNRESOLVED",
    )

    BIDIRECTIONAL_STATES = (
        "VERIFIED",
        "NOT_PERFORMED",
        "UNRESOLVED",
    )

    REGIONAL_BLOCKER_STATES = (
        "PRESENT",
        "NONE",
        "UNRESOLVED",
    )

    GLOBAL_RESULT_STATES = (
        "ADMISSIBLE",
        "BLOCKED",
        "UNRESOLVED",
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.aggregate,
            AtlasCanonicalHeadMetricDistanceAggregate,
        ):
            raise TypeError(
                "aggregate must be an "
                "AtlasCanonicalHeadMetricDistanceAggregate."
            )

        for field_name in (
            "source_to_target_aggregate",
            "target_to_source_aggregate",
            "symmetric_bidirectional_aggregate",
        ):
            value = getattr(self, field_name)
            if (
                value is not None
                and not isinstance(
                    value,
                    AtlasCanonicalHeadMetricDistanceAggregate,
                )
            ):
                raise TypeError(
                    f"{field_name} must be an "
                    "AtlasCanonicalHeadMetricDistanceAggregate or None."
                )

        for field_name in (
            "valid_correspondence_count",
            "evaluation_coverage_denominator",
        ):
            value = getattr(self, field_name)

            if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
                raise TypeError(
                    f"{field_name} must be an integer."
                )

            value = int(value)

            if value < 0:
                raise ValueError(
                    f"{field_name} must be non-negative."
                )

            object.__setattr__(
                self,
                field_name,
                value,
            )

        if self.evaluation_coverage_denominator <= 0:
            raise ValueError(
                "evaluation_coverage_denominator must be greater than zero."
            )

        if self.valid_correspondence_count <= 0:
            raise ValueError(
                "valid_correspondence_count must be greater than zero "
                "for an admissible global metric result."
            )

        if self.valid_correspondence_count != self.aggregate.sample_count:
            raise ValueError(
                "valid_correspondence_count must equal "
                "aggregate.sample_count."
            )

        if self.valid_correspondence_count > self.evaluation_coverage_denominator:
            raise ValueError(
                "valid_correspondence_count cannot exceed "
                "evaluation_coverage_denominator."
            )

        missing_surface_fraction = float(
            self.missing_surface_fraction
        )

        if (
            not np.isfinite(missing_surface_fraction)
            or missing_surface_fraction < 0.0
            or missing_surface_fraction > 1.0
        ):
            raise ValueError(
                "missing_surface_fraction must be finite and within [0, 1]."
            )

        expected_missing_surface_fraction = (
            1.0
            - (
                self.valid_correspondence_count
                / self.evaluation_coverage_denominator
            )
        )

        if not np.isclose(
            missing_surface_fraction,
            expected_missing_surface_fraction,
            rtol=0.0,
            atol=1e-12,
        ):
            raise ValueError(
                "missing_surface_fraction must match "
                "valid_correspondence_count / evaluation_coverage_denominator."
            )

        object.__setattr__(
            self,
            "missing_surface_fraction",
            missing_surface_fraction,
        )

        angular_discrepancy = (
            self.normal_orientation_angular_discrepancy_deg
        )

        if angular_discrepancy is not None:
            angular_discrepancy = float(
                angular_discrepancy
            )

            if (
                not np.isfinite(angular_discrepancy)
                or angular_discrepancy < 0.0
                or angular_discrepancy > 180.0
            ):
                raise ValueError(
                    "normal_orientation_angular_discrepancy_deg "
                    "must be finite and within [0, 180] when provided."
                )

            object.__setattr__(
                self,
                "normal_orientation_angular_discrepancy_deg",
                angular_discrepancy,
            )

        allowed_states = {
            "ground_truth_admissibility_state": self.GROUND_TRUTH_STATES,
            "alignment_admissibility": self.ALIGNMENT_STATES,
            "alignment_bias_leakage_risk": self.LEAKAGE_RISK_STATES,
            "correspondence_evidence_class": self.CORRESPONDENCE_CLASSES,
            "correspondence_direction": self.CORRESPONDENCE_DIRECTIONS,
            "bidirectional_evaluation_state": self.BIDIRECTIONAL_STATES,
            "regional_blocker_state": self.REGIONAL_BLOCKER_STATES,
            "global_metric_result_state": self.GLOBAL_RESULT_STATES,
        }

        for field_name, allowed in allowed_states.items():
            value = self._normalize_state(
                getattr(self, field_name),
                name=field_name,
            )

            if value not in allowed:
                raise ValueError(
                    f"{field_name} must be one of {allowed}."
                )

            object.__setattr__(
                self,
                field_name,
                value,
            )

        if (
            self.bidirectional_evaluation_state == "VERIFIED"
            and self.correspondence_direction != "BIDIRECTIONAL"
        ):
            raise ValueError(
                "VERIFIED bidirectional evaluation requires "
                "BIDIRECTIONAL correspondence direction."
            )

        if (
            self.correspondence_direction == "BIDIRECTIONAL"
            and self.bidirectional_evaluation_state != "VERIFIED"
        ):
            raise ValueError(
                "BIDIRECTIONAL correspondence direction requires "
                "VERIFIED bidirectional evaluation state."
            )

        if self.bidirectional_evaluation_state == "VERIFIED":
            if (
                self.source_to_target_aggregate is None
                or self.target_to_source_aggregate is None
                or self.symmetric_bidirectional_aggregate is None
            ):
                raise ValueError(
                    "VERIFIED bidirectional evaluation requires both "
                    "directional aggregates and a symmetric aggregate."
                )
        elif self.symmetric_bidirectional_aggregate is not None:
            raise ValueError(
                "symmetric bidirectional aggregate requires VERIFIED "
                "bidirectional evaluation."
            )

        if self.correspondence_direction == "SOURCE_TO_TARGET":
            if self.source_to_target_aggregate is None:
                raise ValueError(
                    "SOURCE_TO_TARGET evaluation requires "
                    "source_to_target_aggregate."
                )
        elif self.correspondence_direction == "TARGET_TO_SOURCE":
            if self.target_to_source_aggregate is None:
                raise ValueError(
                    "TARGET_TO_SOURCE evaluation requires "
                    "target_to_source_aggregate."
                )

        expected_result_state = self._derive_result_state(
            ground_truth_admissibility_state=(
                self.ground_truth_admissibility_state
            ),
            alignment_admissibility=self.alignment_admissibility,
            correspondence_evidence_class=(
                self.correspondence_evidence_class
            ),
            correspondence_direction=self.correspondence_direction,
            bidirectional_evaluation_state=(
                self.bidirectional_evaluation_state
            ),
        )

        if self.global_metric_result_state != expected_result_state:
            raise ValueError(
                "global_metric_result_state must be derived from "
                "ground-truth, alignment, and correspondence admissibility."
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
            value.strip().upper().split()
        )

        if not normalized:
            raise ValueError(
                f"{name} must not be blank."
            )

        return normalized

    @staticmethod
    def _derive_result_state(
        *,
        ground_truth_admissibility_state: str,
        alignment_admissibility: str,
        correspondence_evidence_class: str,
        correspondence_direction: str,
        bidirectional_evaluation_state: str,
    ) -> str:
        if ground_truth_admissibility_state == "BLOCKED":
            return "BLOCKED"

        if alignment_admissibility == "INADMISSIBLE":
            return "BLOCKED"

        if correspondence_evidence_class == "UNRESOLVED_CORRESPONDENCE":
            return "BLOCKED"

        unresolved = (
            ground_truth_admissibility_state != "ACCEPTABLE"
            or alignment_admissibility != "ADMISSIBLE"
            or correspondence_direction == "UNRESOLVED"
            or bidirectional_evaluation_state == "UNRESOLVED"
        )

        if unresolved:
            return "UNRESOLVED"

        return "ADMISSIBLE"


class AtlasCanonicalHeadGlobalMetricErrorEvaluation:
    @classmethod
    def evaluate(
        cls,
        *,
        aggregate: object,
        ground_truth_observation: object,
        alignment_admissibility: object,
        alignment_bias_leakage_risk: object,
        correspondence_evidence_class: object,
        correspondence_direction: object,
        bidirectional_evaluation_state: object,
        regional_blocker_state: object,
        source_to_target_aggregate: object = None,
        target_to_source_aggregate: object = None,
        symmetric_bidirectional_aggregate: object = None,
        valid_correspondence_count: object = None,
        evaluation_coverage_denominator: object = None,
        missing_surface_fraction: object = None,
        normal_orientation_angular_discrepancy_deg: object = None,
    ) -> AtlasCanonicalHeadGlobalMetricErrorEvaluationResult:
        if not isinstance(
            ground_truth_observation,
            AtlasCanonicalHeadMetricGroundTruthObservation,
        ):
            raise TypeError(
                "ground_truth_observation must be an "
                "AtlasCanonicalHeadMetricGroundTruthObservation."
            )

        try:
            ground_truth_observation = (
                AtlasCanonicalHeadMetricGroundTruthObservation(
                    **{
                        field.name: getattr(
                            ground_truth_observation,
                            field.name,
                        )
                        for field in fields(
                            AtlasCanonicalHeadMetricGroundTruthObservation
                        )
                    }
                )
            )
        except AttributeError as exc:
            raise ValueError(
                "ground_truth_observation must satisfy the complete "
                "AtlasCanonicalHeadMetricGroundTruthObservation contract."
            ) from exc

        normalized_gt = (
            AtlasCanonicalHeadGlobalMetricErrorEvaluationResult
            ._normalize_state(
                ground_truth_observation.ground_truth_admissibility_state,
                name="ground_truth_admissibility_state",
            )
        )
        normalized_alignment = (
            AtlasCanonicalHeadGlobalMetricErrorEvaluationResult
            ._normalize_state(
                alignment_admissibility,
                name="alignment_admissibility",
            )
        )
        normalized_correspondence = (
            AtlasCanonicalHeadGlobalMetricErrorEvaluationResult
            ._normalize_state(
                correspondence_evidence_class,
                name="correspondence_evidence_class",
            )
        )
        normalized_direction = (
            AtlasCanonicalHeadGlobalMetricErrorEvaluationResult
            ._normalize_state(
                correspondence_direction,
                name="correspondence_direction",
            )
        )
        normalized_bidirectional = (
            AtlasCanonicalHeadGlobalMetricErrorEvaluationResult
            ._normalize_state(
                bidirectional_evaluation_state,
                name="bidirectional_evaluation_state",
            )
        )

        if normalized_gt != "ACCEPTABLE":
            raise ValueError(
                "global metric result requires ACCEPTABLE "
                "ground_truth_admissibility_state."
            )

        if normalized_alignment != "ADMISSIBLE":
            raise ValueError(
                "global metric result requires ADMISSIBLE alignment."
            )

        if normalized_correspondence == "UNRESOLVED_CORRESPONDENCE":
            raise ValueError(
                "global metric result requires resolved correspondence."
            )

        if (
            normalized_bidirectional == "VERIFIED"
            and normalized_direction != "BIDIRECTIONAL"
        ):
            raise ValueError(
                "verified bidirectional metric evaluation requires "
                "bidirectional correspondence direction."
            )

        if (
            normalized_direction == "BIDIRECTIONAL"
            and normalized_bidirectional != "VERIFIED"
        ):
            raise ValueError(
                "bidirectional correspondence direction requires "
                "verified bidirectional metric evaluation."
            )

        if normalized_direction == "SOURCE_TO_TARGET":
            if source_to_target_aggregate is None:
                source_to_target_aggregate = aggregate
        elif normalized_direction == "TARGET_TO_SOURCE":
            if target_to_source_aggregate is None:
                target_to_source_aggregate = aggregate

        if valid_correspondence_count is None:
            valid_correspondence_count = aggregate.sample_count

        if evaluation_coverage_denominator is None:
            evaluation_coverage_denominator = valid_correspondence_count

        if missing_surface_fraction is None:
            missing_surface_fraction = (
                1.0
                - (
                    valid_correspondence_count
                    / evaluation_coverage_denominator
                )
            )

        return AtlasCanonicalHeadGlobalMetricErrorEvaluationResult(
            aggregate=aggregate,
            source_to_target_aggregate=source_to_target_aggregate,
            target_to_source_aggregate=target_to_source_aggregate,
            symmetric_bidirectional_aggregate=symmetric_bidirectional_aggregate,
            valid_correspondence_count=valid_correspondence_count,
            evaluation_coverage_denominator=evaluation_coverage_denominator,
            missing_surface_fraction=missing_surface_fraction,
            normal_orientation_angular_discrepancy_deg=(
                normal_orientation_angular_discrepancy_deg
            ),
            ground_truth_observation_id=ground_truth_observation.observation_id,
            ground_truth_source_id=ground_truth_observation.source_id,
            ground_truth_admissibility_state=normalized_gt,
            alignment_admissibility=normalized_alignment,
            alignment_bias_leakage_risk=alignment_bias_leakage_risk,
            correspondence_evidence_class=normalized_correspondence,
            correspondence_direction=normalized_direction,
            bidirectional_evaluation_state=normalized_bidirectional,
            regional_blocker_state=regional_blocker_state,
            global_metric_result_state="ADMISSIBLE",
        )
