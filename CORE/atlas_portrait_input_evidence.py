from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any


_ALLOWED_MEDIA_KINDS = {
    "image",
    "video",
}

_ALLOWED_VIEW_TYPES = {
    "front",
    "three_quarter_left",
    "three_quarter_right",
    "profile_left",
    "profile_right",
    "unknown",
}


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasPortraitInputEvidence:
    evidence_id: str
    media_kind: str
    view_type: str
    width: int
    height: int
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        evidence_id = self._normalize_evidence_id(
            self.evidence_id
        )
        media_kind = self._normalize_choice(
            self.media_kind,
            name="media_kind",
            allowed=_ALLOWED_MEDIA_KINDS,
        )
        view_type = self._normalize_choice(
            self.view_type,
            name="view_type",
            allowed=_ALLOWED_VIEW_TYPES,
        )
        width = self._normalize_dimension(
            self.width,
            name="width",
        )
        height = self._normalize_dimension(
            self.height,
            name="height",
        )
        metadata = self._normalize_metadata(
            self.metadata
        )

        object.__setattr__(
            self,
            "evidence_id",
            evidence_id,
        )
        object.__setattr__(
            self,
            "media_kind",
            media_kind,
        )
        object.__setattr__(
            self,
            "view_type",
            view_type,
        )
        object.__setattr__(
            self,
            "width",
            width,
        )
        object.__setattr__(
            self,
            "height",
            height,
        )
        object.__setattr__(
            self,
            "metadata",
            metadata,
        )

    @staticmethod
    def _normalize_evidence_id(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError(
                "evidence_id must be a string."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "evidence_id must not be blank."
            )

        return normalized

    @staticmethod
    def _normalize_choice(
        value: Any,
        *,
        name: str,
        allowed: set[str],
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{name} must be a string."
            )

        normalized = value.strip().lower()

        if normalized not in allowed:
            raise ValueError(
                f"{name} must be one of: "
                + ", ".join(sorted(allowed))
                + "."
            )

        return normalized

    @staticmethod
    def _normalize_dimension(
        value: Any,
        *,
        name: str,
    ) -> int:
        if isinstance(value, bool):
            raise TypeError(
                f"{name} must be an integer."
            )

        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if not numeric.is_integer():
            raise ValueError(
                f"{name} must be an integer."
            )

        integer = int(numeric)

        if integer <= 0:
            raise ValueError(
                f"{name} must be greater than zero."
            )

        return integer

    @staticmethod
    def _normalize_metadata(
        value: Any,
    ) -> Mapping[str, Any]:
        if not isinstance(value, Mapping):
            raise TypeError(
                "metadata must be a mapping."
            )

        return MappingProxyType(
            dict(value)
        )
