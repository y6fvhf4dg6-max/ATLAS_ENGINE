from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadPoseObservation:
    pose_id: str
    yaw_deg: float
    pitch_deg: float
    roll_deg: float

    def __post_init__(self) -> None:
        pose_id = self._normalize_identifier(
            self.pose_id,
            name="pose_id",
        )
        yaw_deg = self._normalize_angle(
            self.yaw_deg,
            name="yaw_deg",
        )
        pitch_deg = self._normalize_angle(
            self.pitch_deg,
            name="pitch_deg",
        )
        roll_deg = self._normalize_angle(
            self.roll_deg,
            name="roll_deg",
        )

        object.__setattr__(
            self,
            "pose_id",
            pose_id,
        )
        object.__setattr__(
            self,
            "yaw_deg",
            yaw_deg,
        )
        object.__setattr__(
            self,
            "pitch_deg",
            pitch_deg,
        )
        object.__setattr__(
            self,
            "roll_deg",
            roll_deg,
        )

    @property
    def is_canonical_neutral(
        self,
    ) -> bool:
        return (
            self.yaw_deg == 0.0
            and self.pitch_deg == 0.0
            and self.roll_deg == 0.0
        )

    @staticmethod
    def _normalize_identifier(
        value: object,
        *,
        name: str,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{name} must be a string."
            )

        normalized = "_".join(
            value.strip().lower().split()
        )

        if not normalized:
            raise ValueError(
                f"{name} must not be blank."
            )

        return normalized

    @staticmethod
    def _normalize_angle(
        value: object,
        *,
        name: str,
    ) -> float:
        try:
            numeric = float(
                value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if not math.isfinite(
            numeric
        ):
            raise ValueError(
                f"{name} must be finite."
            )

        return numeric
