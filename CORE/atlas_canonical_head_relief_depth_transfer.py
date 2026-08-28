from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadReliefDepthTransfer:
    representation_id: str
    canonical_depth_mm: float | None
    relief_depth_mm: float | None
    measurement_state: str
    measurement_provenance: str
    clipped: bool
    local_identity_shape_loss_observed: bool

    SUPPORTED_MEASUREMENT_STATES = (
        "OBSERVED",
        "UNRESOLVED",
    )

    def __post_init__(self) -> None:
        representation_id = str(
            self.representation_id
        ).strip()

        if not representation_id:
            raise ValueError(
                "representation_id must be non-blank."
            )

        measurement_state = "_".join(
            str(self.measurement_state)
            .strip()
            .upper()
            .split()
        )

        if (
            measurement_state
            not in self.SUPPORTED_MEASUREMENT_STATES
        ):
            raise ValueError(
                "measurement_state must be one of "
                f"{self.SUPPORTED_MEASUREMENT_STATES}."
            )

        measurement_provenance = str(
            self.measurement_provenance
        ).strip()

        if not measurement_provenance:
            raise ValueError(
                "measurement_provenance must be non-blank."
            )

        if not isinstance(self.clipped, bool):
            raise TypeError(
                "clipped must be a boolean."
            )

        if not isinstance(
            self.local_identity_shape_loss_observed,
            bool,
        ):
            raise TypeError(
                "local_identity_shape_loss_observed "
                "must be a boolean."
            )

        if measurement_state == "UNRESOLVED":
            if (
                self.canonical_depth_mm is not None
                or self.relief_depth_mm is not None
            ):
                raise ValueError(
                    "canonical_depth_mm and relief_depth_mm "
                    "must both be None when measurement_state "
                    "is UNRESOLVED."
                )

            canonical_depth_mm = None
            relief_depth_mm = None
        else:
            if (
                self.canonical_depth_mm is None
                or self.relief_depth_mm is None
            ):
                raise ValueError(
                    "canonical_depth_mm and relief_depth_mm "
                    "must both be provided when "
                    "measurement_state is OBSERVED."
                )

            try:
                canonical_depth_mm = float(
                    self.canonical_depth_mm
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "canonical_depth_mm must be numeric "
                    "when measurement_state is OBSERVED."
                ) from exc

            try:
                relief_depth_mm = float(
                    self.relief_depth_mm
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "relief_depth_mm must be numeric "
                    "when measurement_state is OBSERVED."
                ) from exc

            if (
                not isfinite(canonical_depth_mm)
                or canonical_depth_mm <= 0.0
            ):
                raise ValueError(
                    "canonical_depth_mm must be finite and "
                    "positive when measurement_state is "
                    "OBSERVED."
                )

            if (
                not isfinite(relief_depth_mm)
                or relief_depth_mm < 0.0
            ):
                raise ValueError(
                    "relief_depth_mm must be finite and "
                    "nonnegative when measurement_state is "
                    "OBSERVED."
                )

        object.__setattr__(
            self,
            "representation_id",
            representation_id,
        )
        object.__setattr__(
            self,
            "canonical_depth_mm",
            canonical_depth_mm,
        )
        object.__setattr__(
            self,
            "relief_depth_mm",
            relief_depth_mm,
        )
        object.__setattr__(
            self,
            "measurement_state",
            measurement_state,
        )
        object.__setattr__(
            self,
            "measurement_provenance",
            measurement_provenance,
        )

    @property
    def depth_transfer_ratio(self) -> float | None:
        if self.measurement_state != "OBSERVED":
            return None

        return (
            self.relief_depth_mm
            / self.canonical_depth_mm
        )

    @property
    def compression_fraction(self) -> float | None:
        ratio = self.depth_transfer_ratio

        if ratio is None or ratio > 1.0:
            return None

        return 1.0 - ratio

    @property
    def transfer_state(self) -> str:
        if self.measurement_state != "OBSERVED":
            return "UNRESOLVED"

        ratio = self.depth_transfer_ratio

        if ratio == 0.0:
            return "FLATTENED"

        if ratio < 1.0:
            return "COMPRESSED"

        if ratio > 1.0:
            return "EXAGGERATED"

        return "PRESERVED"
