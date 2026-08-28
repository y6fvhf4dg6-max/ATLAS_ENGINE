from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadLoDIdentityPreservation:
    representation_id: str
    source_lod_level: int
    target_lod_level: int
    region_name: str
    pre_lod_measurement: float | None
    post_lod_measurement: float | None
    measurement_state: str
    measurement_provenance: str

    REQUIRED_REGIONS = (
        "silhouette",
        "profile",
        "nose",
        "jaw_chin",
        "orbital_cheek",
        "mouth",
    )

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

        for field_name in (
            "source_lod_level",
            "target_lod_level",
        ):
            value = getattr(self, field_name)

            if (
                isinstance(value, bool)
                or not isinstance(value, int)
            ):
                raise TypeError(
                    f"{field_name} must be an integer "
                    "in the 0..4 range."
                )

            if not 0 <= value <= 4:
                raise ValueError(
                    f"{field_name} must be an integer "
                    "in the 0..4 range."
                )

        if self.target_lod_level >= self.source_lod_level:
            raise ValueError(
                "target_lod_level must be lower than "
                "source_lod_level for LoD reduction."
            )

        region_name = "_".join(
            str(self.region_name)
            .strip()
            .lower()
            .split()
        )

        if region_name not in self.REQUIRED_REGIONS:
            raise ValueError(
                "region_name must be one of "
                f"{self.REQUIRED_REGIONS}."
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

        if measurement_state == "UNRESOLVED":
            if (
                self.pre_lod_measurement is not None
                or self.post_lod_measurement is not None
            ):
                raise ValueError(
                    "pre_lod_measurement and "
                    "post_lod_measurement must both be None "
                    "when measurement_state is UNRESOLVED."
                )

            pre_lod_measurement = None
            post_lod_measurement = None
        else:
            if (
                self.pre_lod_measurement is None
                or self.post_lod_measurement is None
            ):
                raise ValueError(
                    "pre_lod_measurement and "
                    "post_lod_measurement must both be provided "
                    "when measurement_state is OBSERVED."
                )

            try:
                pre_lod_measurement = float(
                    self.pre_lod_measurement
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "pre_lod_measurement must be numeric "
                    "when measurement_state is OBSERVED."
                ) from exc

            try:
                post_lod_measurement = float(
                    self.post_lod_measurement
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "post_lod_measurement must be numeric "
                    "when measurement_state is OBSERVED."
                ) from exc

            if (
                not isfinite(pre_lod_measurement)
                or pre_lod_measurement <= 0.0
            ):
                raise ValueError(
                    "pre_lod_measurement must be finite and "
                    "positive when measurement_state is OBSERVED."
                )

            if (
                not isfinite(post_lod_measurement)
                or post_lod_measurement < 0.0
            ):
                raise ValueError(
                    "post_lod_measurement must be finite and "
                    "nonnegative when measurement_state is OBSERVED."
                )

        object.__setattr__(
            self,
            "representation_id",
            representation_id,
        )
        object.__setattr__(
            self,
            "region_name",
            region_name,
        )
        object.__setattr__(
            self,
            "pre_lod_measurement",
            pre_lod_measurement,
        )
        object.__setattr__(
            self,
            "post_lod_measurement",
            post_lod_measurement,
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
    def preservation_ratio(self) -> float | None:
        if self.measurement_state != "OBSERVED":
            return None

        return (
            self.post_lod_measurement
            / self.pre_lod_measurement
        )

    @property
    def loss_fraction(self) -> float | None:
        ratio = self.preservation_ratio

        if ratio is None or ratio > 1.0:
            return None

        return 1.0 - ratio

    @property
    def preservation_state(self) -> str:
        if self.measurement_state != "OBSERVED":
            return "UNRESOLVED"

        ratio = self.preservation_ratio

        if ratio == 0.0:
            return "LOST"

        if ratio < 1.0:
            return "DEGRADED"

        if ratio > 1.0:
            return "EXAGGERATED"

        return "PRESERVED"
