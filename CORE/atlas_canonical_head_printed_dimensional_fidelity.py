from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadPrintedDimensionalFidelity:
    representation_id: str
    representation_kind: str
    feature_name: str
    intended_digital_dimension_mm: float
    measured_printed_dimension_mm: float | None
    tolerance_mm: float
    measurement_state: str
    measurement_provenance: str

    SUPPORTED_REPRESENTATION_KINDS = (
        "relief",
        "bust",
        "figurine_head",
        "story_kit_component",
    )

    SUPPORTED_MEASUREMENT_STATES = (
        "OBSERVED",
        "UNRESOLVED",
        "NOT_MEASURABLE",
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

        feature_name = str(
            self.feature_name
        ).strip()

        if not feature_name:
            raise ValueError(
                "feature_name must be non-blank."
            )

        measurement_provenance = str(
            self.measurement_provenance
        ).strip()

        if not measurement_provenance:
            raise ValueError(
                "measurement_provenance must be non-blank."
            )

        intended = self._positive_finite(
            self.intended_digital_dimension_mm,
            name="intended_digital_dimension_mm",
        )

        tolerance = self._positive_finite(
            self.tolerance_mm,
            name="tolerance_mm",
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

        raw_printed = self.measured_printed_dimension_mm

        if measurement_state == "OBSERVED":
            if raw_printed is None:
                raise ValueError(
                    "measured_printed_dimension_mm must be provided "
                    "when measurement_state is OBSERVED."
                )

            try:
                printed = float(raw_printed)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "measured_printed_dimension_mm must be numeric "
                    "when measurement_state is OBSERVED."
                ) from exc

            if (
                not isfinite(printed)
                or printed <= 0.0
            ):
                raise ValueError(
                    "measured_printed_dimension_mm must be finite "
                    "and positive when measurement_state is OBSERVED."
                )
        else:
            if raw_printed is not None:
                raise ValueError(
                    "measured_printed_dimension_mm must be None when "
                    f"measurement_state is {measurement_state}."
                )

            printed = None

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
            "intended_digital_dimension_mm",
            intended,
        )
        object.__setattr__(
            self,
            "measured_printed_dimension_mm",
            printed,
        )
        object.__setattr__(
            self,
            "tolerance_mm",
            tolerance,
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
    def absolute_error_mm(self) -> float | None:
        if self.measurement_state != "OBSERVED":
            return None

        return abs(
            self.measured_printed_dimension_mm
            - self.intended_digital_dimension_mm
        )

    @property
    def relative_error(self) -> float | None:
        if self.measurement_state != "OBSERVED":
            return None

        return (
            self.absolute_error_mm
            / self.intended_digital_dimension_mm
        )

    @property
    def fidelity_state(self) -> str:
        if self.measurement_state != "OBSERVED":
            return self.measurement_state

        if self.absolute_error_mm <= self.tolerance_mm:
            return "WITHIN_TOLERANCE"

        return "OUTSIDE_TOLERANCE"

    @staticmethod
    def _positive_finite(
        value: object,
        *,
        name: str,
    ) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                f"{name} must be numeric."
            ) from exc

        if (
            not isfinite(numeric)
            or numeric <= 0.0
        ):
            raise ValueError(
                f"{name} must be finite and positive."
            )

        return numeric
