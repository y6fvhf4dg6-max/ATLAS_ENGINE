from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Sequence

import numpy as np

from CORE.atlas_portrait_flame_barycentric_landmark_evaluator import (
    AtlasPortraitFlameBarycentricEmbedding,
    AtlasPortraitFlameBarycentricLandmarkEvaluator,
)
from CORE.atlas_portrait_flame_identity_geometry_evaluator import (
    AtlasPortraitFlameIdentityGeometryEvaluator,
)
from CORE.atlas_portrait_identity_recovery_v2_optimizer import (
    AtlasPortraitIdentityRecoveryV2ViewState,
)
from CORE.atlas_portrait_perspective_camera import (
    AtlasPortraitPerspectiveCamera,
)


@dataclass(frozen=True)
class AtlasPortraitMediaPipeLandmarkObservation:
    image_width: int
    image_height: int
    landmark_ids: np.ndarray
    pixel_xy: np.ndarray
    provider_id: str

    def __post_init__(self) -> None:
        if self.image_width <= 1 or self.image_height <= 1:
            raise ValueError(
                "image dimensions must both exceed one pixel."
            )

        ids = np.asarray(
            self.landmark_ids,
            dtype=np.int64,
        )
        xy = np.asarray(
            self.pixel_xy,
            dtype=np.float64,
        )

        if ids.ndim != 1 or ids.size == 0:
            raise ValueError(
                "landmark_ids must be a non-empty 1D array."
            )

        if xy.shape != (ids.size, 2):
            raise ValueError(
                "pixel_xy must have shape (N, 2)."
            )

        if len(np.unique(ids)) != ids.size:
            raise ValueError(
                "landmark_ids must be unique."
            )

        if np.any(ids < 0):
            raise ValueError(
                "landmark_ids must be non-negative."
            )

        if not np.all(np.isfinite(xy)):
            raise ValueError(
                "pixel_xy must contain only finite values."
            )

        if not str(self.provider_id).strip():
            raise ValueError(
                "provider_id must not be empty."
            )

        ids = ids.copy()
        xy = xy.copy()
        ids.setflags(write=False)
        xy.setflags(write=False)

        object.__setattr__(self, "landmark_ids", ids)
        object.__setattr__(self, "pixel_xy", xy)

    @classmethod
    def from_json_file(
        cls,
        path: str | Path,
    ) -> "AtlasPortraitMediaPipeLandmarkObservation":
        payload = json.loads(
            Path(path).read_text(
                encoding="utf-8",
            )
        )

        landmarks = payload["landmarks"]

        ids = np.asarray(
            [int(item["id"]) for item in landmarks],
            dtype=np.int64,
        )

        width = int(payload["image_width"])
        height = int(payload["image_height"])

        # ATLAS MediaPipe pixel contract:
        # normalized coordinates map onto [0, W-1] and [0, H-1].
        pixel_xy = np.asarray(
            [
                [
                    float(item["x"]) * (width - 1),
                    float(item["y"]) * (height - 1),
                ]
                for item in landmarks
            ],
            dtype=np.float64,
        )

        return cls(
            image_width=width,
            image_height=height,
            landmark_ids=ids,
            pixel_xy=pixel_xy,
            provider_id=str(payload["provider_id"]),
        )

    def select(
        self,
        requested_ids: np.ndarray,
    ) -> np.ndarray:
        requested = np.asarray(
            requested_ids,
            dtype=np.int64,
        )

        if requested.ndim != 1:
            raise ValueError(
                "requested_ids must be one-dimensional."
            )

        lookup = {
            int(identifier): index
            for index, identifier in enumerate(
                self.landmark_ids
            )
        }

        missing = [
            int(identifier)
            for identifier in requested
            if int(identifier) not in lookup
        ]

        if missing:
            raise ValueError(
                "observation is missing requested landmark ids: "
                + ", ".join(str(x) for x in missing)
            )

        selected = np.asarray(
            [
                self.pixel_xy[
                    lookup[int(identifier)]
                ]
                for identifier in requested
            ],
            dtype=np.float64,
        )
        selected.setflags(write=False)
        return selected


def _flame_to_camera_axes(
    points: np.ndarray,
) -> np.ndarray:
    """
    Convert FLAME canonical coordinates to the ATLAS camera convention.

    FLAME frontal geometry uses X-Y as the image-facing plane, with +Y
    anatomically upward and the facial surface on the +Z side.

    ATLAS pinhole camera coordinates use +X right, +Y down and +Z
    forward from the camera into the scene. To place the FLAME facial
    surface toward the camera while preserving image vertical semantics,
    the canonical conversion is:

        (x, y, z) -> (x, -y, -z)

    The conversion is applied exactly once after canonical root rotation
    and before camera translation/projection.
    """

    points = np.asarray(
        points,
        dtype=np.float64,
    )

    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError(
            "points must have shape (N, 3)."
        )

    if not np.all(np.isfinite(points)):
        raise ValueError(
            "points must contain only finite values."
        )

    converted = points.copy()
    converted[:, 1] *= -1.0
    converted[:, 2] *= -1.0
    converted.setflags(write=False)
    return converted



def _axis_angle_rotation_matrix(
    rotation_vector: np.ndarray,
) -> np.ndarray:
    vector = np.asarray(
        rotation_vector,
        dtype=np.float64,
    )

    if vector.shape != (3,):
        raise ValueError(
            "rotation_vector must have shape (3,)."
        )

    theta = float(np.linalg.norm(vector))

    if theta < 1.0e-15:
        return np.eye(3, dtype=np.float64)

    axis = vector / theta

    x, y, z = axis

    skew = np.array(
        [
            [0.0, -z, y],
            [z, 0.0, -x],
            [-y, x, 0.0],
        ],
        dtype=np.float64,
    )

    return (
        np.eye(3, dtype=np.float64)
        + np.sin(theta) * skew
        + (1.0 - np.cos(theta)) * (skew @ skew)
    )


@dataclass(frozen=True)
class AtlasPortraitFlameMultiviewLandmarkResidual:
    geometry_evaluator: AtlasPortraitFlameIdentityGeometryEvaluator
    embedding: AtlasPortraitFlameBarycentricEmbedding
    observations: tuple[AtlasPortraitMediaPipeLandmarkObservation, ...]
    base_focal_pixels: tuple[float, ...]

    def __post_init__(self) -> None:
        observations = tuple(self.observations)
        focals = tuple(float(x) for x in self.base_focal_pixels)

        if not observations:
            raise ValueError(
                "at least one observation is required."
            )

        if len(focals) != len(observations):
            raise ValueError(
                "base_focal_pixels count must match observations."
            )

        if not np.all(np.isfinite(focals)):
            raise ValueError(
                "base_focal_pixels must be finite."
            )

        if any(value <= 0.0 for value in focals):
            raise ValueError(
                "base_focal_pixels must be positive."
            )

        object.__setattr__(
            self,
            "observations",
            observations,
        )
        object.__setattr__(
            self,
            "base_focal_pixels",
            focals,
        )

    def evaluate(
        self,
        identity_vector: np.ndarray,
        view_states: Sequence[
            AtlasPortraitIdentityRecoveryV2ViewState
        ],
    ) -> dict[str, np.ndarray]:
        states = tuple(view_states)

        if len(states) != len(self.observations):
            raise ValueError(
                "view state count must match observations."
            )

        geometry = self.geometry_evaluator.evaluate(
            identity_vector=identity_vector,
        )

        model_points = (
            AtlasPortraitFlameBarycentricLandmarkEvaluator.evaluate(
                vertices=geometry.vertices,
                faces=geometry.faces,
                embedding=self.embedding,
            )
        )

        residual_blocks = []

        for observation, base_focal, state in zip(
            self.observations,
            self.base_focal_pixels,
            states,
            strict=True,
        ):
            rotation = _axis_angle_rotation_matrix(
                state.pose_radians
            )

            rotated_points = (
                model_points @ rotation.T
            )

            camera_points = (
                _flame_to_camera_axes(
                    rotated_points
                )
                + state.translation_xyz[None, :]
            )

            focal_scale = state.focal_scale_xy

            camera = AtlasPortraitPerspectiveCamera(
                fx=base_focal * float(focal_scale[0]),
                fy=base_focal * float(focal_scale[1]),
                cx=(observation.image_width - 1) / 2.0,
                cy=(observation.image_height - 1) / 2.0,
            )

            predicted = camera.project(
                camera_points
            )

            observed = observation.select(
                self.embedding.landmark_indices
            )

            # Normalize by image diagonal so differently sized images
            # contribute in the same dimensionless image-space scale.
            image_diagonal = float(
                np.hypot(
                    observation.image_width - 1,
                    observation.image_height - 1,
                )
            )

            residual_blocks.append(
                (
                    predicted - observed
                ).reshape(-1)
                / image_diagonal
            )

        residual = np.concatenate(
            residual_blocks
        ).astype(
            np.float64,
            copy=False,
        )
        residual.setflags(write=False)

        return {
            "static_landmarks": residual,
        }
