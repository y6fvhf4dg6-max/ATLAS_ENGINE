from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadPhysicalFeatureSurvival:
    representation_id: str
    representation_kind: str
    feature_name: str
    measurement_mm: float | None
    minimum_required_mm: float
    measurement_state: str
    measurement_provenance: str

    SUPPORTED_REPRESENTATION_KINDS = (
        "relief",
        "bust",
        "figurine_head",
        "story_kit_component",
    )

    REQUIRED_FEATURES = (
        "nose_edge_profile",
        "nose_base",
        "upper_lip_boundary",
        "lower_lip_boundary",
        "left_eyelid_orbital_boundary",
        "right_eyelid_orbital_boundary",
        "jaw_edge",
        "chin",
        "left_ear_structure",
        "right_ear_structure",
    )

    SUPPORTED_MEASUREMENT_STATES = (
        "OBSERVED",
        "UNRESOLVED",
        "NOT_APPLICABLE",
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

        feature_name = "_".join(
            str(self.feature_name)
            .strip()
            .lower()
            .split()
        )

        if feature_name not in self.REQUIRED_FEATURES:
            raise ValueError(
                "feature_name must be one of "
                f"{self.REQUIRED_FEATURES}."
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

        try:
            minimum_required_mm = float(
                self.minimum_required_mm
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "minimum_required_mm must be numeric."
            ) from exc

        if (
            not isfinite(minimum_required_mm)
            or minimum_required_mm <= 0.0
        ):
            raise ValueError(
                "minimum_required_mm must be finite and positive."
            )

        raw_measurement = self.measurement_mm

        if measurement_state == "OBSERVED":
            if raw_measurement is None:
                raise ValueError(
                    "measurement_mm must be provided when "
                    "measurement_state is OBSERVED."
                )

            try:
                measurement_mm = float(
                    raw_measurement
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "measurement_mm must be numeric when "
                    "measurement_state is OBSERVED."
                ) from exc

            if (
                not isfinite(measurement_mm)
                or measurement_mm <= 0.0
            ):
                raise ValueError(
                    "measurement_mm must be finite and positive "
                    "when measurement_state is OBSERVED."
                )
        else:
            if raw_measurement is not None:
                raise ValueError(
                    "measurement_mm must be None when "
                    f"measurement_state is {measurement_state}."
                )

            measurement_mm = None

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
        object.__setattr__(
            self,
            "feature_name",
            feature_name,
        )
        object.__setattr__(
            self,
            "measurement_mm",
            measurement_mm,
        )
        object.__setattr__(
            self,
            "minimum_required_mm",
            minimum_required_mm,
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
    def survival_state(self) -> str:
        if self.measurement_state != "OBSERVED":
            return self.measurement_state

        if self.measurement_mm >= self.minimum_required_mm:
            return "SURVIVES"

        return "BELOW_MINIMUM"
