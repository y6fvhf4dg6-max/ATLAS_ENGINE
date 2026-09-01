from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class AtlasPortraitPerspectiveCamera:
    """
    ATLAS-owned pinhole perspective camera.

    Input points are expected in camera coordinates:
        +X right
        +Y down
        +Z forward

    Projection:
        u = fx * X / Z + cx
        v = fy * Y / Z + cy

    This class performs projection only. Head pose and camera translation
    remain explicit optimizer parameters outside this object.
    """

    fx: float
    fy: float
    cx: float
    cy: float
    near_z: float = 1.0e-6

    def __post_init__(self) -> None:
        values = np.asarray(
            [self.fx, self.fy, self.cx, self.cy, self.near_z],
            dtype=np.float64,
        )

        if not np.all(np.isfinite(values)):
            raise ValueError("camera parameters must be finite.")

        if self.fx <= 0.0:
            raise ValueError("fx must be positive.")

        if self.fy <= 0.0:
            raise ValueError("fy must be positive.")

        if self.near_z <= 0.0:
            raise ValueError("near_z must be positive.")

    def project(
        self,
        points_camera: np.ndarray,
    ) -> np.ndarray:
        points = np.asarray(
            points_camera,
            dtype=np.float64,
        )

        if points.ndim != 2 or points.shape[1] != 3:
            raise ValueError(
                "points_camera must have shape (N, 3)."
            )

        if points.shape[0] == 0:
            raise ValueError(
                "points_camera must not be empty."
            )

        if not np.all(np.isfinite(points)):
            raise ValueError(
                "points_camera must contain only finite values."
            )

        z = points[:, 2]

        if np.any(z <= self.near_z):
            raise ValueError(
                "all points must lie in front of the perspective "
                "camera near plane."
            )

        projected = np.empty(
            (points.shape[0], 2),
            dtype=np.float64,
        )

        projected[:, 0] = (
            self.fx * points[:, 0] / z + self.cx
        )
        projected[:, 1] = (
            self.fy * points[:, 1] / z + self.cy
        )

        projected.setflags(write=False)
        return projected

    def normalized_image_coordinates(
        self,
        pixels: np.ndarray,
    ) -> np.ndarray:
        pixels = np.asarray(
            pixels,
            dtype=np.float64,
        )

        if pixels.ndim != 2 or pixels.shape[1] != 2:
            raise ValueError(
                "pixels must have shape (N, 2)."
            )

        if pixels.shape[0] == 0:
            raise ValueError(
                "pixels must not be empty."
            )

        if not np.all(np.isfinite(pixels)):
            raise ValueError(
                "pixels must contain only finite values."
            )

        normalized = np.empty_like(
            pixels,
            dtype=np.float64,
        )

        normalized[:, 0] = (
            pixels[:, 0] - self.cx
        ) / self.fx
        normalized[:, 1] = (
            pixels[:, 1] - self.cy
        ) / self.fy

        normalized.setflags(write=False)
        return normalized

    @property
    def intrinsic_matrix(self) -> np.ndarray:
        matrix = np.array(
            [
                [self.fx, 0.0, self.cx],
                [0.0, self.fy, self.cy],
                [0.0, 0.0, 1.0],
            ],
            dtype=np.float64,
        )
        matrix.setflags(write=False)
        return matrix
