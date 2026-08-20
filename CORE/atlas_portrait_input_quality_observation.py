from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasPortraitInputQualityObservation:
    evidence_id: str
    face_detected: bool
    face_coverage_ratio: float
    occlusion_ratio: float
    blur_score: float
    perspective_distortion_score: float

    def __post_init__(self) -> None:
        evidence_id = self._normalize_evidence_id(
            self.evidence_id
        )
        face_detected = self._normalize_face_detected(
            self.face_detected
        )
        face_coverage_ratio = self._normalize_ratio(
            self.face_coverage_ratio,
            name="face_coverage_ratio",
        )
        occlusion_ratio = self._normalize_ratio(
            self.occlusion_ratio,
            name="occlusion_ratio",
        )
        blur_score = self._normalize_ratio(
            self.blur_score,
            name="blur_score",
        )
        perspective_distortion_score = self._normalize_ratio(
            self.perspective_distortion_score,
            name="perspective_distortion_score",
        )

        object.__setattr__(
            self,
            "evidence_id",
            evidence_id,
        )
        object.__setattr__(
            self,
            "face_detected",
            face_detected,
        )
        object.__setattr__(
            self,
            "face_coverage_ratio",
            face_coverage_ratio,
        )
        object.__setattr__(
            self,
            "occlusion_ratio",
            occlusion_ratio,
        )
        object.__setattr__(
            self,
            "blur_score",
            blur_score,
        )
        object.__setattr__(
            self,
            "perspective_distortion_score",
            perspective_distortion_score,
        )

    @staticmethod
    def _normalize_evidence_id(
        value: Any,
    ) -> str:
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
    def _normalize_face_detected(
        value: Any,
    ) -> bool:
        if not isinstance(value, bool):
            raise TypeError(
                "face_detected must be a boolean."
            )

        return value

    @staticmethod
    def _normalize_ratio(
        value: Any,
        *,
        name: str,
    ) -> float:
        try:
            numeric = float(value)
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if not math.isfinite(numeric):
            raise ValueError(
                f"{name} must be finite."
            )

        if not (
            0.0
            <= numeric
            <= 1.0
        ):
            raise ValueError(
                f"{name} must be in the 0.0..1.0 range."
            )

        return numeric
