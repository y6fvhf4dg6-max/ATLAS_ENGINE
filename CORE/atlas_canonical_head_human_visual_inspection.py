from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadHumanVisualInspection:
    representation_id: str
    representation_kind: str
    inspection_id: str
    view_conditions: tuple[str, ...]
    viewing_distance_mm: float
    illumination_condition: str
    camera_view_comparison_condition: str
    inspection_state: str
    evidence_provenance: str
    evidence_kind: str

    SUPPORTED_REPRESENTATION_KINDS = (
        "relief",
        "bust",
        "figurine_head",
        "story_kit_component",
    )

    SUPPORTED_VIEW_CONDITIONS = (
        "front",
        "three_quarter",
        "profile",
    )

    SUPPORTED_INSPECTION_STATES = (
        "OBSERVED",
        "UNRESOLVED",
        "NOT_PERFORMED",
    )

    EVIDENCE_KIND = "SUBJECTIVE"

    def __post_init__(self) -> None:
        representation_id = self._required_text(
            self.representation_id,
            field_name="representation_id",
        )

        representation_kind = self._normalize_lower_identifier(
            self.representation_kind,
            field_name="representation_kind",
        )

        if (
            representation_kind
            not in self.SUPPORTED_REPRESENTATION_KINDS
        ):
            raise ValueError(
                "representation_kind must be one of "
                f"{self.SUPPORTED_REPRESENTATION_KINDS}."
            )

        inspection_id = self._required_text(
            self.inspection_id,
            field_name="inspection_id",
        )

        view_conditions = self._normalize_view_conditions(
            self.view_conditions,
        )

        viewing_distance_mm = self._positive_finite_numeric(
            self.viewing_distance_mm,
            field_name="viewing_distance_mm",
        )

        illumination_condition = self._required_text(
            self.illumination_condition,
            field_name="illumination_condition",
        )

        camera_view_comparison_condition = self._required_text(
            self.camera_view_comparison_condition,
            field_name="camera_view_comparison_condition",
        )

        inspection_state = self._normalize_upper_identifier(
            self.inspection_state,
            field_name="inspection_state",
        )

        if (
            inspection_state
            not in self.SUPPORTED_INSPECTION_STATES
        ):
            raise ValueError(
                "inspection_state must be one of "
                f"{self.SUPPORTED_INSPECTION_STATES}."
            )

        evidence_provenance = self._required_text(
            self.evidence_provenance,
            field_name="evidence_provenance",
        )

        evidence_kind = self._normalize_upper_identifier(
            self.evidence_kind,
            field_name="evidence_kind",
        )

        if evidence_kind != self.EVIDENCE_KIND:
            raise ValueError(
                "evidence_kind must be SUBJECTIVE."
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
            "inspection_id",
            inspection_id,
        )
        object.__setattr__(
            self,
            "view_conditions",
            view_conditions,
        )
        object.__setattr__(
            self,
            "viewing_distance_mm",
            viewing_distance_mm,
        )
        object.__setattr__(
            self,
            "illumination_condition",
            illumination_condition,
        )
        object.__setattr__(
            self,
            "camera_view_comparison_condition",
            camera_view_comparison_condition,
        )
        object.__setattr__(
            self,
            "inspection_state",
            inspection_state,
        )
        object.__setattr__(
            self,
            "evidence_provenance",
            evidence_provenance,
        )
        object.__setattr__(
            self,
            "evidence_kind",
            evidence_kind,
        )

    @classmethod
    def _normalize_view_conditions(
        cls,
        value: object,
    ) -> tuple[str, ...]:
        if isinstance(value, (str, bytes)):
            raise TypeError(
                "view_conditions must be a sequence of view identifiers."
            )

        try:
            raw_views = tuple(value)
        except TypeError as exc:
            raise TypeError(
                "view_conditions must be iterable."
            ) from exc

        if not raw_views:
            raise ValueError(
                "view_conditions must contain at least one view."
            )

        normalized = []
        seen = set()

        for raw_view in raw_views:
            view = cls._normalize_lower_identifier(
                raw_view,
                field_name="view_conditions",
            )

            if view not in cls.SUPPORTED_VIEW_CONDITIONS:
                raise ValueError(
                    "view_conditions must contain only "
                    f"{cls.SUPPORTED_VIEW_CONDITIONS}."
                )

            if view in seen:
                continue

            seen.add(view)
            normalized.append(view)

        return tuple(normalized)

    @staticmethod
    def _required_text(
        value: object,
        *,
        field_name: str,
    ) -> str:
        if value is None:
            raise ValueError(
                f"{field_name} must not be blank."
            )

        normalized = str(value).strip()

        if not normalized:
            raise ValueError(
                f"{field_name} must not be blank."
            )

        return normalized

    @staticmethod
    def _normalize_lower_identifier(
        value: object,
        *,
        field_name: str,
    ) -> str:
        normalized = "_".join(
            str(value).strip().lower().split()
        )

        if not normalized:
            raise ValueError(
                f"{field_name} must not be blank."
            )

        return normalized

    @staticmethod
    def _normalize_upper_identifier(
        value: object,
        *,
        field_name: str,
    ) -> str:
        normalized = "_".join(
            str(value).strip().upper().split()
        )

        if not normalized:
            raise ValueError(
                f"{field_name} must not be blank."
            )

        return normalized

    @staticmethod
    def _positive_finite_numeric(
        value: object,
        *,
        field_name: str,
    ) -> float:
        try:
            numeric = float(value)
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{field_name} must be numeric."
            ) from exc

        if not math.isfinite(numeric):
            raise ValueError(
                f"{field_name} must be finite."
            )

        if numeric <= 0.0:
            raise ValueError(
                f"{field_name} must be greater than zero."
            )

        return numeric
