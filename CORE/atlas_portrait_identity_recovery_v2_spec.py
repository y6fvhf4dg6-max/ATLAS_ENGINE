from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class AtlasPortraitIdentityRecoveryV2Spec:
    """
    Production contract for ATLAS portrait identity recovery V2.

    This contract defines which evidence channels participate in
    identity recovery. It does not perform fitting, rendering,
    camera estimation, or mesh deformation.
    """

    shared_identity_across_views: bool = True
    separate_pose_per_view: bool = True
    separate_camera_per_view: bool = True
    neutral_expression_for_identity_fit: bool = True

    use_static_landmarks: bool = True
    use_dense_landmarks: bool = True
    use_face_oval: bool = True
    use_silhouette: bool = True
    use_photometric: bool = True
    use_surface_normals: bool = True
    use_identity_prior: bool = True

    camera_model: str = "perspective"

    static_landmark_weight: float = 1.0
    dense_landmark_weight: float = 1.0
    face_oval_weight: float = 1.0
    silhouette_weight: float = 1.0
    photometric_weight: float = 1.0
    surface_normal_weight: float = 1.0
    identity_prior_weight: float = 1.0

    def __post_init__(self) -> None:
        if self.camera_model not in {"perspective", "weak_perspective"}:
            raise ValueError(
                "camera_model must be 'perspective' or 'weak_perspective'."
            )

        for name, value in self.weights.items():
            if value < 0.0:
                raise ValueError(
                    f"{name} must be non-negative."
                )

        if not self.shared_identity_across_views:
            raise ValueError(
                "Identity Recovery V2 requires one shared identity across views."
            )

        if not self.neutral_expression_for_identity_fit:
            raise ValueError(
                "Identity Recovery V2 requires neutral expression during identity fit."
            )

    @property
    def weights(self) -> Mapping[str, float]:
        return {
            "static_landmarks": self.static_landmark_weight,
            "dense_landmarks": self.dense_landmark_weight,
            "face_oval": self.face_oval_weight,
            "silhouette": self.silhouette_weight,
            "photometric": self.photometric_weight,
            "surface_normals": self.surface_normal_weight,
            "identity_prior": self.identity_prior_weight,
        }

    @property
    def enabled_channels(self) -> tuple[str, ...]:
        channels = []

        if self.use_static_landmarks:
            channels.append("static_landmarks")
        if self.use_dense_landmarks:
            channels.append("dense_landmarks")
        if self.use_face_oval:
            channels.append("face_oval")
        if self.use_silhouette:
            channels.append("silhouette")
        if self.use_photometric:
            channels.append("photometric")
        if self.use_surface_normals:
            channels.append("surface_normals")
        if self.use_identity_prior:
            channels.append("identity_prior")

        return tuple(channels)
