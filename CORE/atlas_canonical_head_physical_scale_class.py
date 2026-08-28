from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadPhysicalScaleClass:
    representation_id: str
    representation_kind: str

    head_width_mm: float | None
    head_height_mm: float | None
    head_depth_mm: float | None

    output_width_mm: float | None
    output_height_mm: float | None
    output_depth_mm: float | None

    physical_unit: str
    measurement_provenance: str

    head_width_state: str
    head_height_state: str
    head_depth_state: str

    output_width_state: str
    output_height_state: str
    output_depth_state: str

    SUPPORTED_REPRESENTATION_KINDS = (
        "relief",
        "bust",
        "figurine_head",
        "story_kit_component",
    )

    SUPPORTED_MEASUREMENT_STATES = (
        "OBSERVED",
        "NOT_APPLICABLE",
        "UNRESOLVED",
    )

    DIMENSION_FIELDS = (
        "head_width_mm",
        "head_height_mm",
        "head_depth_mm",
        "output_width_mm",
        "output_height_mm",
        "output_depth_mm",
    )

    STATE_FIELDS = (
        "head_width_state",
        "head_height_state",
        "head_depth_state",
        "output_width_state",
        "output_height_state",
        "output_depth_state",
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

        measurement_provenance = str(
            self.measurement_provenance
        ).strip()

        if not measurement_provenance:
            raise ValueError(
                "measurement_provenance must be non-blank."
            )

        physical_unit = str(
            self.physical_unit
        ).strip().lower()

        if physical_unit != "mm":
            raise ValueError(
                "physical_unit must be 'mm'."
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
        object.__setattr__(
            self,
            "measurement_provenance",
            measurement_provenance,
        )
        object.__setattr__(
            self,
            "physical_unit",
            physical_unit,
        )

        normalized_states = {}

        for field_name in self.STATE_FIELDS:
            state = "_".join(
                str(
                    getattr(self, field_name)
                )
                .strip()
                .upper()
                .split()
            )

            if (
                state
                not in self.SUPPORTED_MEASUREMENT_STATES
            ):
                raise ValueError(
                    f"{field_name} must be one of "
                    f"{self.SUPPORTED_MEASUREMENT_STATES}."
                )

            normalized_states[field_name] = state

            object.__setattr__(
                self,
                field_name,
                state,
            )

        for dimension_field, state_field in zip(
            self.DIMENSION_FIELDS,
            self.STATE_FIELDS,
        ):
            raw_value = getattr(
                self,
                dimension_field,
            )
            state = normalized_states[state_field]

            if raw_value is None:
                if state == "OBSERVED":
                    raise ValueError(
                        f"{dimension_field} must be provided "
                        "when measurement state is OBSERVED."
                    )

                object.__setattr__(
                    self,
                    dimension_field,
                    None,
                )
                continue

            if state != "OBSERVED":
                raise ValueError(
                    f"{dimension_field} must be None when "
                    f"measurement state is {state}."
                )

            try:
                value = float(raw_value)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"{dimension_field} must be numeric when provided."
                ) from exc

            if not isfinite(value) or value <= 0.0:
                raise ValueError(
                    f"{dimension_field} must be finite and positive."
                )

            object.__setattr__(
                self,
                dimension_field,
                value,
            )
