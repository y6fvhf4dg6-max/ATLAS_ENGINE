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
