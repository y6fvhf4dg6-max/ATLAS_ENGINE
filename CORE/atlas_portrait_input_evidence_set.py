from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from CORE.atlas_portrait_input_evidence import (
    AtlasPortraitInputEvidence,
)


_THREE_QUARTER_VIEWS = {
    "three_quarter_left",
    "three_quarter_right",
}

_PROFILE_VIEWS = {
    "profile_left",
    "profile_right",
}

_BLOCKED_REASON = (
    "BLOCKED_INSUFFICIENT_IDENTITY_EVIDENCE"
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasPortraitInputEvidenceSet:
    items: tuple[AtlasPortraitInputEvidence, ...]

    def __init__(
        self,
        items: Any,
    ) -> None:
        normalized = self._normalize_items(
            items
        )

        object.__setattr__(
            self,
            "items",
            normalized,
        )

    @property
    def coverage_class(self) -> str:
        views = {
            item.view_type
            for item in self.items
        }

        has_front = (
            "front" in views
        )
        has_three_quarter = bool(
            views & _THREE_QUARTER_VIEWS
        )
        has_profile = bool(
            views & _PROFILE_VIEWS
        )

        if (
            has_front
            and has_three_quarter
            and has_profile
        ):
            return (
                "high_confidence_multiview"
            )

        if (
            has_front
            and has_three_quarter
        ):
            return "multiview_partial"

        if has_front:
            return "single_view_fallback"

        return "insufficient"

    @property
    def production_evidence_eligible(
        self,
    ) -> bool:
        return (
            self.coverage_class
            != "insufficient"
        )

    @property
    def blocked_reason(
        self,
    ) -> str | None:
        if self.production_evidence_eligible:
            return None

        return _BLOCKED_REASON

    @staticmethod
    def _normalize_items(
        items: Any,
    ) -> tuple[AtlasPortraitInputEvidence, ...]:
        if isinstance(
            items,
            (str, bytes),
        ):
            raise TypeError(
                "items must be a sequence of "
                "AtlasPortraitInputEvidence values."
            )

        try:
            normalized = tuple(
                items
            )
        except TypeError as exc:
            raise TypeError(
                "items must be a sequence of "
                "AtlasPortraitInputEvidence values."
            ) from exc

        if not normalized:
            raise ValueError(
                "items must not be empty."
            )

        for item in normalized:
            if not isinstance(
                item,
                AtlasPortraitInputEvidence,
            ):
                raise TypeError(
                    "items must contain only "
                    "AtlasPortraitInputEvidence values."
                )

        evidence_ids = [
            item.evidence_id
            for item in normalized
        ]

        if len(evidence_ids) != len(
            set(evidence_ids)
        ):
            raise ValueError(
                "evidence_id values must be unique."
            )

        return normalized
