from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True, slots=True)
class AtlasCanonicalHeadSlicerGateObservation:
    representation_id: str
    representation_kind: str
    slicer_name: str
    slicer_version: str
    printer_model: str
    nozzle_diameter_mm: float
    layer_height_mm: float
    slice_attempt_state: str
    slice_completed: bool | None
    slicer_error_count: int | None
    mesh_repair_count: int | None
    support_enabled: bool | None
    artifact_provenance: str

    SUPPORTED_REPRESENTATION_KINDS = (
        "relief",
        "bust",
        "figurine_head",
        "story_kit_component",
    )

    SUPPORTED_SLICE_ATTEMPT_STATES = (
        "ATTEMPTED",
        "NOT_ATTEMPTED",
        "UNRESOLVED",
    )

    def __post_init__(self) -> None:
        for field_name in (
            "representation_id",
            "slicer_name",
            "slicer_version",
            "printer_model",
            "artifact_provenance",
        ):
            value = str(
                getattr(self, field_name)
            ).strip()

            if not value:
                raise ValueError(
                    f"{field_name} must be non-blank."
                )

            object.__setattr__(
                self,
                field_name,
                value,
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
            "representation_kind",
            representation_kind,
        )

        object.__setattr__(
            self,
            "nozzle_diameter_mm",
            self._positive_finite(
                self.nozzle_diameter_mm,
                name="nozzle_diameter_mm",
            ),
        )

        object.__setattr__(
            self,
            "layer_height_mm",
            self._positive_finite(
                self.layer_height_mm,
                name="layer_height_mm",
            ),
        )

        slice_attempt_state = (
            str(self.slice_attempt_state)
            .strip()
            .upper()
            .replace(" ", "_")
        )

        if (
            slice_attempt_state
            not in self.SUPPORTED_SLICE_ATTEMPT_STATES
        ):
            raise ValueError(
                "slice_attempt_state must be one of "
                f"{self.SUPPORTED_SLICE_ATTEMPT_STATES}."
            )

        object.__setattr__(
            self,
            "slice_attempt_state",
            slice_attempt_state,
        )

        if slice_attempt_state == "ATTEMPTED":
            if self.slice_completed is None:
                raise ValueError(
                    "ATTEMPTED requires slice_completed."
                )

            if not isinstance(
                self.slice_completed,
                bool,
            ):
                raise TypeError(
                    "slice_completed must be a boolean."
                )

            object.__setattr__(
                self,
                "slicer_error_count",
                self._nonnegative_strict_int(
                    self.slicer_error_count,
                    name="slicer_error_count",
                ),
            )

            object.__setattr__(
                self,
                "mesh_repair_count",
                self._nonnegative_strict_int(
                    self.mesh_repair_count,
                    name="mesh_repair_count",
                ),
            )

            if not isinstance(
                self.support_enabled,
                bool,
            ):
                raise TypeError(
                    "support_enabled must be a boolean."
                )

            return

        for field_name in (
            "slice_completed",
            "slicer_error_count",
            "mesh_repair_count",
            "support_enabled",
        ):
            if getattr(self, field_name) is not None:
                raise ValueError(
                    f"{slice_attempt_state} requires "
                    f"{field_name} to be None."
                )

    @property
    def slicer_gate_state(self) -> str:
        if self.slice_attempt_state != "ATTEMPTED":
            return "UNRESOLVED"

        if (
            self.slice_completed is True
            and self.slicer_error_count == 0
        ):
            return "PASSED"

        return "FAILED"

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

        if not math.isfinite(numeric) or numeric <= 0.0:
            raise ValueError(
                f"{name} must be finite and positive."
            )

        return numeric

    @staticmethod
    def _nonnegative_strict_int(
        value: object,
        *,
        name: str,
    ) -> int:
        if isinstance(value, bool) or not isinstance(
            value,
            int,
        ):
            raise TypeError(
                f"{name} must be an integer."
            )

        if value < 0:
            raise ValueError(
                f"{name} must be nonnegative."
            )

        return value
