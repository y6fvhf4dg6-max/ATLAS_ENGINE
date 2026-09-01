from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Any

import numpy as np


@dataclass(frozen=True)
class AtlasPortraitFlameBarycentricEmbedding:
    landmark_indices: np.ndarray
    face_indices: np.ndarray
    barycentric_coordinates: np.ndarray

    def __post_init__(self) -> None:
        landmark_indices = np.asarray(
            self.landmark_indices,
            dtype=np.int64,
        )
        face_indices = np.asarray(
            self.face_indices,
            dtype=np.int64,
        )
        barycentric = np.asarray(
            self.barycentric_coordinates,
            dtype=np.float64,
        )

        if landmark_indices.ndim != 1:
            raise ValueError(
                "landmark_indices must be one-dimensional."
            )

        if face_indices.shape != landmark_indices.shape:
            raise ValueError(
                "face_indices must match landmark_indices shape."
            )

        if barycentric.shape != (
            landmark_indices.size,
            3,
        ):
            raise ValueError(
                "barycentric_coordinates must have shape (N, 3)."
            )

        if landmark_indices.size == 0:
            raise ValueError(
                "embedding must contain at least one landmark."
            )

        if np.any(landmark_indices < 0):
            raise ValueError(
                "landmark_indices must be non-negative."
            )

        if len(np.unique(landmark_indices)) != landmark_indices.size:
            raise ValueError(
                "landmark_indices must be unique."
            )

        if np.any(face_indices < 0):
            raise ValueError(
                "face_indices must be non-negative."
            )

        if not np.all(np.isfinite(barycentric)):
            raise ValueError(
                "barycentric_coordinates must contain only finite values."
            )

        if not np.allclose(
            barycentric.sum(axis=1),
            1.0,
            atol=1.0e-10,
            rtol=0.0,
        ):
            raise ValueError(
                "each barycentric coordinate row must sum to 1."
            )

        landmark_indices = landmark_indices.copy()
        face_indices = face_indices.copy()
        barycentric = barycentric.copy()

        landmark_indices.setflags(write=False)
        face_indices.setflags(write=False)
        barycentric.setflags(write=False)

        object.__setattr__(
            self,
            "landmark_indices",
            landmark_indices,
        )
        object.__setattr__(
            self,
            "face_indices",
            face_indices,
        )
        object.__setattr__(
            self,
            "barycentric_coordinates",
            barycentric,
        )

    @classmethod
    def from_npz_mapping(
        cls,
        mapping: Mapping[str, Any],
    ) -> "AtlasPortraitFlameBarycentricEmbedding":
        required = (
            "landmark_indices",
            "lmk_face_idx",
            "lmk_b_coords",
        )

        missing = [
            key
            for key in required
            if key not in mapping
        ]

        if missing:
            raise ValueError(
                "embedding mapping missing required fields: "
                + ", ".join(missing)
            )

        return cls(
            landmark_indices=np.asarray(
                mapping["landmark_indices"],
                dtype=np.int64,
            ),
            face_indices=np.asarray(
                mapping["lmk_face_idx"],
                dtype=np.int64,
            ),
            barycentric_coordinates=np.asarray(
                mapping["lmk_b_coords"],
                dtype=np.float64,
            ),
        )

    @property
    def landmark_count(self) -> int:
        return int(self.landmark_indices.size)


class AtlasPortraitFlameBarycentricLandmarkEvaluator:
    """
    Evaluate MediaPipe landmark positions on FLAME surface triangles.

    No correspondence inference occurs here. The evaluator consumes a
    verified embedding and computes exact barycentric surface positions.
    """

    @staticmethod
    def evaluate(
        *,
        vertices: np.ndarray,
        faces: np.ndarray,
        embedding: AtlasPortraitFlameBarycentricEmbedding,
    ) -> np.ndarray:
        vertices = np.asarray(
            vertices,
            dtype=np.float64,
        )
        faces = np.asarray(
            faces,
            dtype=np.int64,
        )

        if vertices.ndim != 2 or vertices.shape[1] != 3:
            raise ValueError(
                "vertices must have shape (N, 3)."
            )

        if faces.ndim != 2 or faces.shape[1] != 3:
            raise ValueError(
                "faces must have shape (F, 3)."
            )

        if not np.all(np.isfinite(vertices)):
            raise ValueError(
                "vertices must contain only finite values."
            )

        if np.any(faces < 0) or np.any(faces >= vertices.shape[0]):
            raise ValueError(
                "faces contain invalid vertex indices."
            )

        if np.any(embedding.face_indices >= faces.shape[0]):
            raise ValueError(
                "embedding contains face indices outside mesh topology."
            )

        triangle_vertex_indices = faces[
            embedding.face_indices
        ]

        triangle_vertices = vertices[
            triangle_vertex_indices
        ]

        points = np.sum(
            triangle_vertices
            * embedding.barycentric_coordinates[:, :, None],
            axis=1,
        )

        points = np.asarray(
            points,
            dtype=np.float64,
        )
        points.setflags(write=False)

        return points
