from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from numbers import Integral, Real
from types import MappingProxyType

from CORE.atlas_canonical_head_topology import (
    AtlasCanonicalHeadTopology,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadSurfaceCorrespondence:
    correspondence_id: str
    topology: AtlasCanonicalHeadTopology
    observed_sample_to_canonical_surface: Mapping[
        int,
        tuple[int, tuple[float, float, float]],
    ]

    def __post_init__(self) -> None:
        correspondence_id = self._normalize_identifier(
            self.correspondence_id,
            name="correspondence_id",
        )

        if not isinstance(
            self.topology,
            AtlasCanonicalHeadTopology,
        ):
            raise TypeError(
                "topology must be an "
                "AtlasCanonicalHeadTopology."
            )

        mapping = self._normalize_mapping(
            self.observed_sample_to_canonical_surface,
            face_count=len(self.topology.faces),
        )

        object.__setattr__(
            self,
            "correspondence_id",
            correspondence_id,
        )
        object.__setattr__(
            self,
            "observed_sample_to_canonical_surface",
            MappingProxyType(mapping),
        )

    @property
    def observed_sample_indices(
        self,
    ) -> tuple[int, ...]:
        return tuple(
            self.observed_sample_to_canonical_surface.keys()
        )

    @property
    def canonical_face_indices(
        self,
    ) -> tuple[int, ...]:
        return tuple(
            location[0]
            for location in (
                self.observed_sample_to_canonical_surface.values()
            )
        )

    @property
    def correspondence_count(
        self,
    ) -> int:
        return len(
            self.observed_sample_to_canonical_surface
        )

    @property
    def connectivity_signature(
        self,
    ) -> str:
        return self.topology.connectivity_signature

    def canonical_surface_location(
        self,
        observed_sample_index: int,
    ) -> tuple[
        int,
        tuple[float, float, float],
    ]:
        return self.observed_sample_to_canonical_surface[
            observed_sample_index
        ]

    @staticmethod
    def _normalize_identifier(
        value: object,
        *,
        name: str,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{name} must be a string."
            )

        normalized = "_".join(
            value.strip().lower().split()
        )

        if not normalized:
            raise ValueError(
                f"{name} must not be blank."
            )

        return normalized

    @classmethod
    def _normalize_mapping(
        cls,
        value: object,
        *,
        face_count: int,
    ) -> dict[
        int,
        tuple[int, tuple[float, float, float]],
    ]:
        if not isinstance(
            value,
            Mapping,
        ):
            raise TypeError(
                "observed_sample_to_canonical_surface "
                "must be a mapping."
            )

        if not value:
            raise ValueError(
                "observed_sample_to_canonical_surface "
                "must not be empty."
            )

        normalized = {}

        for observed_index, raw_location in value.items():
            observed_index = cls._normalize_nonnegative_integer(
                observed_index,
                name="observed sample index",
            )

            try:
                face_index, raw_weights = raw_location
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise ValueError(
                    "canonical surface location must contain "
                    "canonical face index and barycentric weights."
                ) from exc

            face_index = cls._normalize_nonnegative_integer(
                face_index,
                name="canonical face index",
            )

            if face_index >= face_count:
                raise ValueError(
                    "canonical face index must be "
                    "inside topology faces."
                )

            weights = cls._normalize_barycentric_weights(
                raw_weights
            )

            normalized[
                observed_index
            ] = (
                face_index,
                weights,
            )

        return normalized

    @staticmethod
    def _normalize_barycentric_weights(
        value: object,
    ) -> tuple[float, float, float]:
        if isinstance(
            value,
            (str, bytes),
        ):
            raise TypeError(
                "barycentric weights must contain "
                "exactly three numeric values."
            )

        try:
            raw_weights = tuple(
                value
            )
        except TypeError as exc:
            raise TypeError(
                "barycentric weights must contain "
                "exactly three numeric values."
            ) from exc

        if len(raw_weights) != 3:
            raise ValueError(
                "barycentric weights must contain "
                "exactly three values."
            )

        weights = []

        for raw_weight in raw_weights:
            if (
                isinstance(raw_weight, bool)
                or not isinstance(
                    raw_weight,
                    Real,
                )
            ):
                raise TypeError(
                    "barycentric weights must be numeric."
                )

            weight = float(
                raw_weight
            )

            if not math.isfinite(
                weight
            ):
                raise ValueError(
                    "barycentric weights must be finite."
                )

            tolerance = 1e-12

            if (
                weight < -tolerance
                or weight > 1.0 + tolerance
            ):
                raise ValueError(
                    "barycentric weights must be "
                    "inside the 0.0..1.0 range."
                )

            weights.append(
                min(
                    1.0,
                    max(
                        0.0,
                        weight,
                    ),
                )
            )

        weight_sum = sum(
            weights
        )

        if not math.isclose(
            weight_sum,
            1.0,
            rel_tol=0.0,
            abs_tol=1e-9,
        ):
            raise ValueError(
                "barycentric weights must sum to 1.0."
            )

        normalized = tuple(
            weight / weight_sum
            for weight in weights
        )

        return normalized

    @staticmethod
    def _normalize_nonnegative_integer(
        value: object,
        *,
        name: str,
    ) -> int:
        if (
            isinstance(value, bool)
            or not isinstance(
                value,
                Integral,
            )
        ):
            raise TypeError(
                f"{name} must be an integer."
            )

        normalized = int(
            value
        )

        if normalized < 0:
            raise ValueError(
                f"{name} must not be negative."
            )

        return normalized


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadSurfaceCorrespondenceAuditResult:
    correspondence_evidence_class: str
    correspondence_direction: str
    bidirectional_evaluation_state: str
    topology_independent_evaluation_state: str
    closest_point_assumption: str
    barycentric_projection_state: str
    source_sampling_density: str
    target_sampling_density: str
    resampling_method: str
    area_weighting: str
    density_normalization_assumption: str
    anatomical_homology_state: str

    EVIDENCE_CLASSES = (
        "DENSE_ANATOMICAL_CORRESPONDENCE",
        "VERIFIED_SEMANTIC_BARYCENTRIC_CORRESPONDENCE",
        "SPARSE_LANDMARK_CORRESPONDENCE",
        "GEOMETRIC_CLOSEST_POINT_CORRESPONDENCE",
        "UNRESOLVED_CORRESPONDENCE",
    )

    DIRECTIONS = (
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

    TOPOLOGY_INDEPENDENT_STATES = (
        "VERIFIED",
        "NOT_ESTABLISHED",
        "UNRESOLVED",
    )

    USAGE_STATES = (
        "USED",
        "NOT_USED",
        "UNRESOLVED",
    )

    BARYCENTRIC_STATES = (
        "VERIFIED",
        "NOT_USED",
        "UNRESOLVED",
    )

    SAMPLING_DENSITY_STATES = (
        "KNOWN",
        "UNRESOLVED",
    )

    WEIGHTING_STATES = (
        "APPLIED",
        "NOT_APPLIED",
        "UNRESOLVED",
    )

    HOMOLOGY_STATES = (
        "CLAIMED",
        "NOT_CLAIMED",
        "UNRESOLVED",
    )

    def __post_init__(self) -> None:
        enum_fields = {
            "correspondence_evidence_class": self.EVIDENCE_CLASSES,
            "correspondence_direction": self.DIRECTIONS,
            "bidirectional_evaluation_state": self.BIDIRECTIONAL_STATES,
            "topology_independent_evaluation_state": (
                self.TOPOLOGY_INDEPENDENT_STATES
            ),
            "closest_point_assumption": self.USAGE_STATES,
            "barycentric_projection_state": self.BARYCENTRIC_STATES,
            "source_sampling_density": self.SAMPLING_DENSITY_STATES,
            "target_sampling_density": self.SAMPLING_DENSITY_STATES,
            "area_weighting": self.WEIGHTING_STATES,
            "density_normalization_assumption": self.WEIGHTING_STATES,
            "anatomical_homology_state": self.HOMOLOGY_STATES,
        }

        for field_name, allowed in enum_fields.items():
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

        resampling_method = self._normalize_resampling_method(
            self.resampling_method
        )
        object.__setattr__(
            self,
            "resampling_method",
            resampling_method,
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

        if (
            self.correspondence_evidence_class
            == "GEOMETRIC_CLOSEST_POINT_CORRESPONDENCE"
        ):
            if self.closest_point_assumption != "USED":
                raise ValueError(
                    "geometric closest-point correspondence requires "
                    "closest-point assumption USED."
                )

            if self.anatomical_homology_state == "CLAIMED":
                raise ValueError(
                    "geometric closest-point correspondence must not "
                    "claim anatomical homology."
                )

        if (
            self.correspondence_evidence_class
            == "VERIFIED_SEMANTIC_BARYCENTRIC_CORRESPONDENCE"
            and self.barycentric_projection_state != "VERIFIED"
        ):
            raise ValueError(
                "verified semantic barycentric correspondence requires "
                "VERIFIED barycentric projection state."
            )

        if (
            self.correspondence_evidence_class
            == "DENSE_ANATOMICAL_CORRESPONDENCE"
            and self.anatomical_homology_state != "CLAIMED"
        ):
            raise ValueError(
                "dense anatomical correspondence requires explicit "
                "anatomical homology evidence; barycentric projection "
                "alone cannot promote correspondence to dense anatomical."
            )

        if (
            self.correspondence_evidence_class
            == "UNRESOLVED_CORRESPONDENCE"
            and self.anatomical_homology_state == "CLAIMED"
        ):
            raise ValueError(
                "unresolved correspondence cannot claim anatomical homology."
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
    def _normalize_resampling_method(
        value: object,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                "resampling_method must be a string."
            )

        normalized = "_".join(
            value.strip().upper().split()
        )

        if not normalized:
            raise ValueError(
                "resampling_method must not be blank."
            )

        return normalized


class AtlasCanonicalHeadSurfaceCorrespondenceAudit:
    @classmethod
    def evaluate(
        cls,
        *,
        correspondence_evidence_class: object,
        correspondence_direction: object,
        bidirectional_evaluation_state: object,
        topology_independent_evaluation_state: object,
        closest_point_assumption: object,
        barycentric_projection_state: object,
        source_sampling_density: object,
        target_sampling_density: object,
        resampling_method: object,
        area_weighting: object,
        density_normalization_assumption: object,
        anatomical_homology_state: object = "UNRESOLVED",
    ) -> AtlasCanonicalHeadSurfaceCorrespondenceAuditResult:
        return AtlasCanonicalHeadSurfaceCorrespondenceAuditResult(
            correspondence_evidence_class=correspondence_evidence_class,
            correspondence_direction=correspondence_direction,
            bidirectional_evaluation_state=bidirectional_evaluation_state,
            topology_independent_evaluation_state=(
                topology_independent_evaluation_state
            ),
            closest_point_assumption=closest_point_assumption,
            barycentric_projection_state=barycentric_projection_state,
            source_sampling_density=source_sampling_density,
            target_sampling_density=target_sampling_density,
            resampling_method=resampling_method,
            area_weighting=area_weighting,
            density_normalization_assumption=(
                density_normalization_assumption
            ),
            anatomical_homology_state=anatomical_homology_state,
        )
