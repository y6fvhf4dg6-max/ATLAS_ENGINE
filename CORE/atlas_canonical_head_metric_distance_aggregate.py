from __future__ import annotations

from dataclasses import dataclass

import numpy as np


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
