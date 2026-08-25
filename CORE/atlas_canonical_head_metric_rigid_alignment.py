from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadMetricRigidAlignmentResult:
    aligned_source_points: np.ndarray
    rotation: np.ndarray
    translation: np.ndarray
    scale_factor: float

    def __post_init__(self) -> None:
        aligned = np.asarray(
            self.aligned_source_points,
            dtype=np.float64,
        )
        rotation = np.asarray(
            self.rotation,
            dtype=np.float64,
        )
        translation = np.asarray(
            self.translation,
            dtype=np.float64,
        )

        if (
            aligned.ndim != 2
            or aligned.shape[1] != 3
            or aligned.shape[0] == 0
        ):
            raise ValueError(
                "aligned_source_points must have shape (N, 3)."
            )

        if rotation.shape != (3, 3):
            raise ValueError(
                "rotation must have shape (3, 3)."
            )

        if translation.shape != (3,):
            raise ValueError(
                "translation must have shape (3,)."
            )

        if not (
            np.all(np.isfinite(aligned))
            and np.all(np.isfinite(rotation))
            and np.all(np.isfinite(translation))
        ):
            raise ValueError(
                "alignment result values must be finite."
            )

        aligned = aligned.copy()
        rotation = rotation.copy()
        translation = translation.copy()

        aligned.setflags(write=False)
        rotation.setflags(write=False)
        translation.setflags(write=False)

        object.__setattr__(
            self,
            "aligned_source_points",
            aligned,
        )
        object.__setattr__(
            self,
            "rotation",
            rotation,
        )
        object.__setattr__(
            self,
            "translation",
            translation,
        )

        scale_factor = float(
            self.scale_factor
        )

        if (
            not np.isfinite(scale_factor)
            or scale_factor != 1.0
        ):
            raise ValueError(
                "scale_factor must be exactly 1.0 "
                "for rigid alignment."
            )

        object.__setattr__(
            self,
            "scale_factor",
            scale_factor,
        )


class AtlasCanonicalHeadMetricRigidAlignment:
    @classmethod
    def solve(
        cls,
        *,
        source_points: object,
        target_points: object,
    ) -> AtlasCanonicalHeadMetricRigidAlignmentResult:
        source = cls._normalize_points(
            source_points,
            name="source_points",
        )
        target = cls._normalize_points(
            target_points,
            name="target_points",
        )

        if source.shape != target.shape:
            raise ValueError(
                "source_points and target_points "
                "must have the same shape."
            )

        if source.shape[0] < 3:
            raise ValueError(
                "at least three point correspondences are required."
            )

        source_centroid = source.mean(
            axis=0
        )
        target_centroid = target.mean(
            axis=0
        )

        source_centered = (
            source
            - source_centroid
        )
        target_centered = (
            target
            - target_centroid
        )

        covariance = (
            source_centered.T
            @ target_centered
        )

        u, _, vt = np.linalg.svd(
            covariance
        )

        rotation = (
            vt.T
            @ u.T
        )

        if np.linalg.det(rotation) < 0.0:
            vt = vt.copy()
            vt[-1, :] *= -1.0
            rotation = (
                vt.T
                @ u.T
            )

        translation = (
            target_centroid
            - source_centroid @ rotation.T
        )

        aligned = (
            source @ rotation.T
            + translation
        )

        return AtlasCanonicalHeadMetricRigidAlignmentResult(
            aligned_source_points=aligned,
            rotation=rotation,
            translation=translation,
            scale_factor=1.0,
        )

    @staticmethod
    def _normalize_points(
        value: object,
        *,
        name: str,
    ) -> np.ndarray:
        points = np.asarray(
            value,
            dtype=np.float64,
        )

        if (
            points.ndim != 2
            or points.shape[1] != 3
            or points.shape[0] == 0
        ):
            raise ValueError(
                f"{name} must have shape (N, 3)."
            )

        if not np.all(
            np.isfinite(points)
        ):
            raise ValueError(
                f"{name} must contain only finite values."
            )

        return points.copy()
