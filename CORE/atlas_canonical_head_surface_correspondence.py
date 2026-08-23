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

            if (
                weight < 0.0
                or weight > 1.0
            ):
                raise ValueError(
                    "barycentric weights must be "
                    "inside the 0.0..1.0 range."
                )

            weights.append(
                weight
            )

        normalized = tuple(
            weights
        )

        if not math.isclose(
            sum(normalized),
            1.0,
            rel_tol=0.0,
            abs_tol=1e-9,
        ):
            raise ValueError(
                "barycentric weights must sum to 1.0."
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
