from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from CORE.atlas_portrait_flame_deformed_mesh_evaluator import (
    AtlasPortraitFlameDeformedMesh,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasPortraitFlameNormalField:
    """
    Immutable FLAME face-normal and vertex-normal contract.
    """

    face_normals: np.ndarray
    vertex_normals: np.ndarray

    def __post_init__(
        self,
    ) -> None:
        normalized_face_normals = np.asarray(
            self.face_normals,
            dtype=np.float64,
        ).copy()
        normalized_vertex_normals = np.asarray(
            self.vertex_normals,
            dtype=np.float64,
        ).copy()

        if (
            normalized_face_normals.ndim != 2
            or normalized_face_normals.shape[1] != 3
        ):
            raise ValueError(
                "face_normals must have shape (F, 3)."
            )

        if (
            normalized_vertex_normals.ndim != 2
            or normalized_vertex_normals.shape[1] != 3
        ):
            raise ValueError(
                "vertex_normals must have shape (N, 3)."
            )

        if not np.isfinite(
            normalized_face_normals,
        ).all():
            raise ValueError(
                "face_normals contains non-finite values."
            )

        if not np.isfinite(
            normalized_vertex_normals,
        ).all():
            raise ValueError(
                "vertex_normals contains non-finite values."
            )

        normalized_face_normals.setflags(
            write=False,
        )
        normalized_vertex_normals.setflags(
            write=False,
        )

        object.__setattr__(
            self,
            "face_normals",
            normalized_face_normals,
        )
        object.__setattr__(
            self,
            "vertex_normals",
            normalized_vertex_normals,
        )

    @property
    def face_count(
        self,
    ) -> int:
        return int(
            self.face_normals.shape[0]
        )

    @property
    def vertex_count(
        self,
    ) -> int:
        return int(
            self.vertex_normals.shape[0]
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "face_normals": self.face_normals.copy(),
            "vertex_normals": self.vertex_normals.copy(),
            "face_count": self.face_count,
            "vertex_count": self.vertex_count,
        }


class AtlasPortraitFlameVertexNormalEvaluator:
    """
    Evaluates area-weighted FLAME face and vertex normals.

    Face normals follow canonical triangle winding. Vertex normals
    are normalized sums of adjacent unnormalized face normals.

    This evaluator performs no camera projection, visibility
    classification, fitting, rendering, or preview generation.
    """

    _DEGENERATE_THRESHOLD = 1.0e-12

    @classmethod
    def evaluate(
        cls,
        mesh: AtlasPortraitFlameDeformedMesh,
    ) -> AtlasPortraitFlameNormalField:
        if not isinstance(
            mesh,
            AtlasPortraitFlameDeformedMesh,
        ):
            raise TypeError(
                "mesh must be an "
                "AtlasPortraitFlameDeformedMesh instance."
            )

        vertices = np.asarray(
            mesh.vertices,
            dtype=np.float64,
        )
        faces = np.asarray(
            mesh.triangle_faces,
            dtype=np.int64,
        )

        first_vertices = vertices[
            faces[
                :,
                0,
            ]
        ]
        second_vertices = vertices[
            faces[
                :,
                1,
            ]
        ]
        third_vertices = vertices[
            faces[
                :,
                2,
            ]
        ]

        first_edges = (
            second_vertices
            - first_vertices
        )
        second_edges = (
            third_vertices
            - first_vertices
        )

        unnormalized_face_normals = np.cross(
            first_edges,
            second_edges,
        )
        face_lengths = np.linalg.norm(
            unnormalized_face_normals,
            axis=1,
        )

        if np.any(
            face_lengths
            <= cls._DEGENERATE_THRESHOLD
        ):
            raise ValueError(
                "mesh contains a degenerate triangle."
            )

        face_normals = (
            unnormalized_face_normals
            / face_lengths[
                :,
                None,
            ]
        )

        accumulated_vertex_normals = np.zeros(
            (
                mesh.vertex_count,
                3,
            ),
            dtype=np.float64,
        )

        for corner_index in range(
            3,
        ):
            np.add.at(
                accumulated_vertex_normals,
                faces[
                    :,
                    corner_index,
                ],
                unnormalized_face_normals,
            )

        vertex_lengths = np.linalg.norm(
            accumulated_vertex_normals,
            axis=1,
        )

        if np.any(
            vertex_lengths
            <= cls._DEGENERATE_THRESHOLD
        ):
            raise ValueError(
                "mesh contains an unreferenced vertex."
            )

        vertex_normals = (
            accumulated_vertex_normals
            / vertex_lengths[
                :,
                None,
            ]
        )

        return AtlasPortraitFlameNormalField(
            face_normals=face_normals,
            vertex_normals=vertex_normals,
        )
