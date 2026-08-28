from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True, slots=True)
class AtlasCanonicalHeadTopologyManufacturability:
    representation_id: str
    representation_kind: str

    open_edge_count: int | None
    non_manifold_edge_count: int | None
    self_intersection_count: int | None
    degenerate_geometry_count: int | None

    minimum_observed_thickness_mm: float | None
    minimum_required_thickness_mm: float | None

    unsupported_structure_count: int | None
    unintended_disconnected_component_count: int | None

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
    )

    def __post_init__(self) -> None:
        representation_id = str(
            self.representation_id
        ).strip()

        if not representation_id:
            raise ValueError(
                "representation_id must be non-blank."
            )

        object.__setattr__(
            self,
            "representation_id",
            representation_id,
        )

        representation_kind = self._normalize_identifier(
            self.representation_kind,
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

        measurement_state = (
            str(self.measurement_state)
            .strip()
            .upper()
        )

        if (
            measurement_state
            not in self.SUPPORTED_MEASUREMENT_STATES
        ):
            raise ValueError(
                "measurement_state must be one of "
                f"{self.SUPPORTED_MEASUREMENT_STATES}."
            )

        object.__setattr__(
            self,
            "measurement_state",
            measurement_state,
        )

        measurement_provenance = str(
            self.measurement_provenance
        ).strip()

        if not measurement_provenance:
            raise ValueError(
                "measurement_provenance must be non-blank."
            )

        object.__setattr__(
            self,
            "measurement_provenance",
            measurement_provenance,
        )

        count_fields = (
            "open_edge_count",
            "non_manifold_edge_count",
            "self_intersection_count",
            "degenerate_geometry_count",
            "unsupported_structure_count",
            "unintended_disconnected_component_count",
        )

        measurement_fields = (
            *count_fields,
            "minimum_observed_thickness_mm",
            "minimum_required_thickness_mm",
        )

        if measurement_state == "UNRESOLVED":
            if any(
                getattr(self, field_name) is not None
                for field_name in measurement_fields
            ):
                raise ValueError(
                    "UNRESOLVED requires all measurements "
                    "to be None."
                )

            return

        if any(
            getattr(self, field_name) is None
            for field_name in measurement_fields
        ):
            raise ValueError(
                "OBSERVED requires all measurements."
            )

        for field_name in count_fields:
            object.__setattr__(
                self,
                field_name,
                self._nonnegative_strict_int(
                    getattr(self, field_name),
                    name=field_name,
                ),
            )

        for field_name in (
            "minimum_observed_thickness_mm",
            "minimum_required_thickness_mm",
        ):
            object.__setattr__(
                self,
                field_name,
                self._positive_finite(
                    getattr(self, field_name),
                    name=field_name,
                ),
            )

    @property
    def closed_manifold_state(self) -> str:
        if self.measurement_state == "UNRESOLVED":
            return "UNRESOLVED"

        return (
            "SATISFIED"
            if (
                self.open_edge_count == 0
                and self.non_manifold_edge_count == 0
            )
            else "VIOLATED"
        )

    @property
    def self_intersection_state(self) -> str:
        return self._count_state(
            self.self_intersection_count
        )

    @property
    def degenerate_geometry_state(self) -> str:
        return self._count_state(
            self.degenerate_geometry_count
        )

    @property
    def thickness_state(self) -> str:
        if self.measurement_state == "UNRESOLVED":
            return "UNRESOLVED"

        return (
            "SATISFIED"
            if (
                self.minimum_observed_thickness_mm
                >= self.minimum_required_thickness_mm
            )
            else "VIOLATED"
        )

    @property
    def unsupported_structure_state(self) -> str:
        return self._count_state(
            self.unsupported_structure_count
        )

    @property
    def disconnected_geometry_state(self) -> str:
        return self._count_state(
            self.unintended_disconnected_component_count
        )

    @property
    def manufacturability_state(self) -> str:
        if self.measurement_state == "UNRESOLVED":
            return "UNRESOLVED"

        states = (
            self.closed_manifold_state,
            self.self_intersection_state,
            self.degenerate_geometry_state,
            self.thickness_state,
            self.unsupported_structure_state,
            self.disconnected_geometry_state,
        )

        return (
            "SATISFIED"
            if all(
                state == "SATISFIED"
                for state in states
            )
            else "VIOLATED"
        )

    def _count_state(
        self,
        value: int | None,
    ) -> str:
        if self.measurement_state == "UNRESOLVED":
            return "UNRESOLVED"

        return (
            "SATISFIED"
            if value == 0
            else "VIOLATED"
        )

    @staticmethod
    def _normalize_identifier(
        value: object,
    ) -> str:
        normalized = "_".join(
            str(value).strip().lower().split()
        )

        if not normalized:
            raise ValueError(
                "identifier must be non-blank."
            )

        return normalized

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
