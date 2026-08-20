from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from numbers import Integral
from types import MappingProxyType

from CORE.atlas_canonical_head_topology import (
    AtlasCanonicalHeadTopology,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadLandmarkCorrespondence:
    correspondence_id: str
    topology: AtlasCanonicalHeadTopology
    observed_to_canonical_vertex: Mapping[int, int]

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
            self.observed_to_canonical_vertex,
            vertex_count=self.topology.vertex_count,
        )

        object.__setattr__(
            self,
            "correspondence_id",
            correspondence_id,
        )
        object.__setattr__(
            self,
            "observed_to_canonical_vertex",
            MappingProxyType(mapping),
        )

    @property
    def observed_landmark_ids(
        self,
    ) -> tuple[int, ...]:
        return tuple(
            self.observed_to_canonical_vertex.keys()
        )

    @property
    def canonical_vertex_indices(
        self,
    ) -> tuple[int, ...]:
        return tuple(
            self.observed_to_canonical_vertex.values()
        )

    @property
    def correspondence_count(
        self,
    ) -> int:
        return len(
            self.observed_to_canonical_vertex
        )

    @property
    def connectivity_signature(
        self,
    ) -> str:
        return self.topology.connectivity_signature

    def canonical_vertex_index(
        self,
        observed_landmark_id: int,
    ) -> int:
        return self.observed_to_canonical_vertex[
            observed_landmark_id
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
        vertex_count: int,
    ) -> dict[int, int]:
        if not isinstance(
            value,
            Mapping,
        ):
            raise TypeError(
                "observed_to_canonical_vertex "
                "must be a mapping."
            )

        if not value:
            raise ValueError(
                "observed_to_canonical_vertex "
                "must not be empty."
            )

        normalized = {}

        for observed_id, canonical_index in value.items():
            observed_id = cls._normalize_nonnegative_integer(
                observed_id,
                name="observed landmark id",
            )
            canonical_index = cls._normalize_nonnegative_integer(
                canonical_index,
                name="canonical vertex index",
            )

            if canonical_index >= vertex_count:
                raise ValueError(
                    "canonical vertex index must be "
                    "inside topology vertex_count."
                )

            normalized[
                observed_id
            ] = canonical_index

        canonical_targets = tuple(
            normalized.values()
        )

        if len(
            canonical_targets
        ) != len(
            set(canonical_targets)
        ):
            raise ValueError(
                "canonical vertex targets must be unique."
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
