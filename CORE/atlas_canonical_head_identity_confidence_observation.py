from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadIdentityConfidenceObservation:
    observation_id: str
    view_coverage_support: float
    multi_view_consistency: float
    silhouette_support: float
    profile_support: float
    identity_shape_support: float
    landmark_support: float
    asymmetry_support: float

    def __post_init__(self) -> None:
        observation_id = str(self.observation_id).strip()

        if not observation_id:
            raise ValueError(
                "observation_id must be non-blank."
            )

        object.__setattr__(
            self,
            "observation_id",
            observation_id,
        )

        for field_name in (
            "view_coverage_support",
            "multi_view_consistency",
            "silhouette_support",
            "profile_support",
            "identity_shape_support",
            "landmark_support",
            "asymmetry_support",
        ):
            value = float(
                getattr(self, field_name)
            )

            if not isfinite(value):
                raise ValueError(
                    f"{field_name} must be finite."
                )

            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{field_name} must be within [0, 1]."
                )

            object.__setattr__(
                self,
                field_name,
                value,
            )
