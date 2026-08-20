from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_canonical_head_camera_observation import (
    AtlasCanonicalHeadCameraObservation,
)
from CORE.atlas_canonical_head_pose_observation import (
    AtlasCanonicalHeadPoseObservation,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadPoseNormalization:
    normalization_id: str
    observed_pose: AtlasCanonicalHeadPoseObservation
    camera_observation: AtlasCanonicalHeadCameraObservation

    def __post_init__(self) -> None:
        normalization_id = self._normalize_identifier(
            self.normalization_id,
            name="normalization_id",
        )

        if not isinstance(
            self.observed_pose,
            AtlasCanonicalHeadPoseObservation,
        ):
            raise TypeError(
                "observed_pose must be an "
                "AtlasCanonicalHeadPoseObservation."
            )

        if not isinstance(
            self.camera_observation,
            AtlasCanonicalHeadCameraObservation,
        ):
            raise TypeError(
                "camera_observation must be an "
                "AtlasCanonicalHeadCameraObservation."
            )

        object.__setattr__(
            self,
            "normalization_id",
            normalization_id,
        )

    @property
    def inverse_yaw_deg(
        self,
    ) -> float:
        return -self.observed_pose.yaw_deg

    @property
    def inverse_pitch_deg(
        self,
    ) -> float:
        return -self.observed_pose.pitch_deg

    @property
    def inverse_roll_deg(
        self,
    ) -> float:
        return -self.observed_pose.roll_deg

    @property
    def inverse_rotation_deg(
        self,
    ) -> tuple[float, float, float]:
        return (
            self.inverse_yaw_deg,
            self.inverse_pitch_deg,
            self.inverse_roll_deg,
        )

    @property
    def target_yaw_deg(
        self,
    ) -> float:
        return 0.0

    @property
    def target_pitch_deg(
        self,
    ) -> float:
        return 0.0

    @property
    def target_roll_deg(
        self,
    ) -> float:
        return 0.0

    @property
    def normalizes_to_canonical_neutral(
        self,
    ) -> bool:
        return True

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
