from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

import numpy as np

from CORE.atlas_canonical_head_metric_distance_aggregate import (
    AtlasCanonicalHeadMetricDistanceAggregate,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadMetricRegionDistanceAggregate:
    regions: object

    def __post_init__(self) -> None:
        if not isinstance(
            self.regions,
            dict,
        ):
            raise TypeError(
                "regions must be a dictionary."
            )

        if not self.regions:
            raise ValueError(
                "regions must not be empty."
            )

        normalized = {}

        for raw_name, aggregate in self.regions.items():
            name = self._normalize_region_name(
                raw_name
            )

            if name in normalized:
                raise ValueError(
                    "region names must be unique after normalization."
                )

            if not isinstance(
                aggregate,
                AtlasCanonicalHeadMetricDistanceAggregate,
            ):
                raise TypeError(
                    "region values must be "
                    "AtlasCanonicalHeadMetricDistanceAggregate."
                )

            normalized[name] = aggregate

        object.__setattr__(
            self,
            "regions",
            MappingProxyType(normalized),
        )

    @classmethod
    def from_regions(
        cls,
        *,
        distances_mm: object,
        region_sample_indices: object,
    ) -> "AtlasCanonicalHeadMetricRegionDistanceAggregate":
        distances = np.asarray(
            distances_mm,
            dtype=np.float64,
        )

        if (
            distances.ndim != 1
            or distances.shape[0] == 0
            or not np.all(np.isfinite(distances))
            or np.any(distances < 0.0)
        ):
            raise ValueError(
                "distances_mm must be a non-empty "
                "1D array of finite nonnegative values."
            )

        if not isinstance(
            region_sample_indices,
            dict,
        ) or not region_sample_indices:
            raise ValueError(
                "region_sample_indices must be a non-empty dictionary."
            )

        regions = {}

        for raw_name, raw_indices in region_sample_indices.items():
            name = cls._normalize_region_name(
                raw_name
            )

            try:
                indices = tuple(
                    raw_indices
                )
            except TypeError as exc:
                raise ValueError(
                    "region_sample_indices must contain "
                    "iterable sample-index sets."
                ) from exc

            if not indices:
                raise ValueError(
                    "region_sample_indices must not contain "
                    "empty sample-index sets."
                )

            normalized_indices = []

            for raw_index in indices:
                if (
                    isinstance(raw_index, bool)
                    or not isinstance(
                        raw_index,
                        (int, np.integer),
                    )
                ):
                    raise ValueError(
                        "region_sample_indices must contain integer indices."
                    )

                index = int(
                    raw_index
                )

                if (
                    index < 0
                    or index >= distances.shape[0]
                ):
                    raise ValueError(
                        "region_sample_indices must stay "
                        "inside distance bounds."
                    )

                normalized_indices.append(
                    index
                )

            regions[name] = (
                AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
                    distances_mm=distances[
                        normalized_indices
                    ]
                )
            )

        return cls(
            regions=regions
        )

    @property
    def region_names(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            self.regions.keys()
        )

    def region(
        self,
        semantic_name: object,
    ) -> AtlasCanonicalHeadMetricDistanceAggregate:
        name = self._normalize_region_name(
            semantic_name
        )

        return self.regions[
            name
        ]

    @staticmethod
    def _normalize_region_name(
        value: object,
    ) -> str:
        normalized = "_".join(
            str(value).strip().lower().split()
        )

        if not normalized:
            raise ValueError(
                "region name must not be blank."
            )

        return normalized


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadMetricRegionEvaluationResult:
    semantic_region: str
    aggregate: AtlasCanonicalHeadMetricDistanceAggregate
    region_definition_origin: str
    ground_truth_region_mapping: str
    prediction_region_mapping: str
    correspondence_evidence_class: str
    valid_sample_count: int
    coverage_ratio: float
    region_alignment_overlap: str
    expression_compatibility: str
    posture_compatibility: str
    regional_metric_admissibility: str

    REGION_DEFINITION_ORIGINS = (
        "PROVIDER_VERIFIED",
        "INDEPENDENTLY_VERIFIED_ATLAS_DERIVED",
        "ITEM8_H2_ANCHOR_SUPPORTED_FOOTPRINT",
        "UNRESOLVED_BLOCKED",
    )

    REGION_MAPPING_STATES = (
        "VERIFIED",
        "ANCHOR_SUPPORTED_ONLY",
        "UNRESOLVED_BLOCKED",
    )

    CORRESPONDENCE_CLASSES = (
        "DENSE_ANATOMICAL_CORRESPONDENCE",
        "VERIFIED_SEMANTIC_BARYCENTRIC_CORRESPONDENCE",
        "SPARSE_LANDMARK_CORRESPONDENCE",
        "GEOMETRIC_CLOSEST_POINT_CORRESPONDENCE",
        "UNRESOLVED_CORRESPONDENCE",
    )

    ALIGNMENT_OVERLAP_STATES = (
        "OVERLAP_PRESENT",
        "NO_OVERLAP_IDENTIFIED",
        "UNRESOLVED",
    )

    COMPATIBILITY_STATES = (
        "COMPATIBLE",
        "INCOMPATIBLE",
        "UNRESOLVED",
    )

    ADMISSIBILITY_STATES = (
        "ADMISSIBLE",
        "BLOCKED",
        "UNRESOLVED",
    )

    def __post_init__(self) -> None:
        semantic_region = self._normalize_region_name(
            self.semantic_region
        )
        object.__setattr__(
            self,
            "semantic_region",
            semantic_region,
        )

        if not isinstance(
            self.aggregate,
            AtlasCanonicalHeadMetricDistanceAggregate,
        ):
            raise TypeError(
                "aggregate must be an "
                "AtlasCanonicalHeadMetricDistanceAggregate."
            )

        if (
            isinstance(self.valid_sample_count, bool)
            or not isinstance(
                self.valid_sample_count,
                (int, np.integer),
            )
        ):
            raise TypeError(
                "valid_sample_count must be an integer."
            )

        valid_sample_count = int(
            self.valid_sample_count
        )

        if valid_sample_count <= 0:
            raise ValueError(
                "valid_sample_count must be greater than zero."
            )

        if valid_sample_count != self.aggregate.sample_count:
            raise ValueError(
                "valid_sample_count must equal aggregate.sample_count."
            )

        object.__setattr__(
            self,
            "valid_sample_count",
            valid_sample_count,
        )

        coverage_ratio = float(
            self.coverage_ratio
        )

        if (
            not np.isfinite(coverage_ratio)
            or coverage_ratio < 0.0
            or coverage_ratio > 1.0
        ):
            raise ValueError(
                "coverage_ratio must be finite and within [0, 1]."
            )

        object.__setattr__(
            self,
            "coverage_ratio",
            coverage_ratio,
        )

        allowed_states = {
            "region_definition_origin": self.REGION_DEFINITION_ORIGINS,
            "ground_truth_region_mapping": self.REGION_MAPPING_STATES,
            "prediction_region_mapping": self.REGION_MAPPING_STATES,
            "correspondence_evidence_class": self.CORRESPONDENCE_CLASSES,
            "region_alignment_overlap": self.ALIGNMENT_OVERLAP_STATES,
            "expression_compatibility": self.COMPATIBILITY_STATES,
            "posture_compatibility": self.COMPATIBILITY_STATES,
            "regional_metric_admissibility": self.ADMISSIBILITY_STATES,
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

        if self.regional_metric_admissibility == "ADMISSIBLE":
            if self.region_definition_origin not in (
                "PROVIDER_VERIFIED",
                "INDEPENDENTLY_VERIFIED_ATLAS_DERIVED",
            ):
                raise ValueError(
                    "ADMISSIBLE regional metric evaluation requires a "
                    "verified region_definition_origin; anchor-supported "
                    "or unresolved region definitions are not admissible."
                )

            if self.ground_truth_region_mapping != "VERIFIED":
                raise ValueError(
                    "ADMISSIBLE regional metric evaluation requires "
                    "VERIFIED ground_truth_region_mapping; anchor-supported "
                    "or unresolved GT region mapping is not admissible."
                )

            if self.prediction_region_mapping != "VERIFIED":
                raise ValueError(
                    "ADMISSIBLE regional metric evaluation requires "
                    "VERIFIED prediction_region_mapping; anchor-supported "
                    "or unresolved prediction region mapping is not admissible."
                )

            if (
                self.correspondence_evidence_class
                == "UNRESOLVED_CORRESPONDENCE"
            ):
                raise ValueError(
                    "ADMISSIBLE regional metric evaluation requires "
                    "resolved correspondence evidence."
                )

            if self.expression_compatibility != "COMPATIBLE":
                raise ValueError(
                    "ADMISSIBLE regional metric evaluation requires "
                    "COMPATIBLE expression evidence."
                )

            if self.posture_compatibility != "COMPATIBLE":
                raise ValueError(
                    "ADMISSIBLE regional metric evaluation requires "
                    "COMPATIBLE posture evidence."
                )

            if self.coverage_ratio <= 0.0:
                raise ValueError(
                    "ADMISSIBLE regional metric evaluation requires "
                    "coverage_ratio greater than zero."
                )

        if (
            self.region_definition_origin
            == "ITEM8_H2_ANCHOR_SUPPORTED_FOOTPRINT"
            and self.correspondence_evidence_class
            == "DENSE_ANATOMICAL_CORRESPONDENCE"
        ):
            raise ValueError(
                "Item 8 H2 anchor-supported footprint cannot be "
                "promoted to dense anatomical metric correspondence."
            )

        if (
            self.ground_truth_region_mapping == "ANCHOR_SUPPORTED_ONLY"
            or self.prediction_region_mapping == "ANCHOR_SUPPORTED_ONLY"
        ) and (
            self.correspondence_evidence_class
            == "DENSE_ANATOMICAL_CORRESPONDENCE"
        ):
            raise ValueError(
                "anchor-supported region mapping cannot establish "
                "dense anatomical correspondence."
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

    @staticmethod
    def _normalize_region_name(
        value: object,
    ) -> str:
        normalized = "_".join(
            str(value).strip().lower().split()
        )

        if not normalized:
            raise ValueError(
                "semantic_region must not be blank."
            )

        return normalized


class AtlasCanonicalHeadMetricRegionEvaluation:
    @classmethod
    def evaluate(
        cls,
        *,
        semantic_region: object,
        aggregate: object,
        region_definition_origin: object,
        ground_truth_region_mapping: object,
        prediction_region_mapping: object,
        correspondence_evidence_class: object,
        valid_sample_count: object,
        coverage_ratio: object,
        region_alignment_overlap: object,
        expression_compatibility: object,
        posture_compatibility: object,
        regional_metric_admissibility: object,
    ) -> AtlasCanonicalHeadMetricRegionEvaluationResult:
        return AtlasCanonicalHeadMetricRegionEvaluationResult(
            semantic_region=semantic_region,
            aggregate=aggregate,
            region_definition_origin=region_definition_origin,
            ground_truth_region_mapping=ground_truth_region_mapping,
            prediction_region_mapping=prediction_region_mapping,
            correspondence_evidence_class=correspondence_evidence_class,
            valid_sample_count=valid_sample_count,
            coverage_ratio=coverage_ratio,
            region_alignment_overlap=region_alignment_overlap,
            expression_compatibility=expression_compatibility,
            posture_compatibility=posture_compatibility,
            regional_metric_admissibility=regional_metric_admissibility,
        )
