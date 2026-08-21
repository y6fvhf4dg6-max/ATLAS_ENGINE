from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadPhysicalRepresentationObservation:
    representation_id: str
    representation_kind: str
    target_head_height_mm: float
    minimum_feature_mm: float
    lod_level: int
    identity_preservation_support: float
    silhouette_preservation_support: float
    profile_preservation_support: float

    SUPPORTED_REPRESENTATION_KINDS = (
        "relief",
        "bust",
        "figurine_head",
        "story_kit_component",
    )

    def __post_init__(self) -> None:
        representation_id = str(
            self.representation_id
        ).strip()

        if not representation_id:
            raise ValueError(
                "representation_id must be non-blank."
            )

        representation_kind = "_".join(
            str(self.representation_kind)
            .strip()
            .lower()
            .split()
        )

        if (
            representation_kind
            not in self.SUPPORTED_REPRESENTATION_KINDS
        ):
            raise ValueError(
                "representation_kind must be one of "
                f"{self.SUPPORTED_REPRESENTATION_KINDS}."
            )

        object.__setattr__(
            self,
            "representation_id",
            representation_id,
        )
        object.__setattr__(
            self,
            "representation_kind",
            representation_kind,
        )

        for field_name in (
            "target_head_height_mm",
            "minimum_feature_mm",
        ):
            value = float(
                getattr(self, field_name)
            )

            if not isfinite(value) or value <= 0.0:
                raise ValueError(
                    f"{field_name} must be finite and positive."
                )

            object.__setattr__(
                self,
                field_name,
                value,
            )

        if (
            isinstance(self.lod_level, bool)
            or not isinstance(self.lod_level, int)
        ):
            raise TypeError(
                "lod_level must be a nonnegative integer."
            )

        if self.lod_level < 0:
            raise ValueError(
                "lod_level must be nonnegative."
            )

        for field_name in (
            "identity_preservation_support",
            "silhouette_preservation_support",
            "profile_preservation_support",
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
