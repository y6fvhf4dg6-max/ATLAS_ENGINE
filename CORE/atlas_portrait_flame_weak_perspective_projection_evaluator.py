from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from CORE.atlas_portrait_flame_deformed_mesh_evaluator import (
    AtlasPortraitFlameDeformedMesh,
)
from CORE.atlas_portrait_weak_perspective_camera import (
    AtlasPortraitWeakPerspectiveCamera,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasPortraitFlameWeakPerspectiveProjection:
    """
    Immutable weak-perspective projection of a deformed FLAME mesh.
    """

    scale: float
    translation_x: float
    translation_y: float
    projected_vertices_2d: np.ndarray
    triangle_faces: np.ndarray

    def __post_init__(
        self,
    ) -> None:
        normalized_projected_vertices = np.asarray(
            self.projected_vertices_2d,
            dtype=np.float64,
        ).copy()
        normalized_faces = np.asarray(
            self.triangle_faces,
            dtype=np.int64,
        ).copy()

        if (
            normalized_projected_vertices.ndim != 2
            or normalized_projected_vertices.shape[1] != 2
        ):
            raise ValueError(
                "projected_vertices_2d must have shape (N, 2)."
            )

        if (
            normalized_faces.ndim != 2
            or normalized_faces.shape[1] != 3
        ):
            raise ValueError(
                "triangle_faces must have shape (F, 3)."
            )

        if not np.isfinite(
            normalized_projected_vertices,
        ).all():
            raise ValueError(
                "projected_vertices_2d contains non-finite values."
            )

        normalized_projected_vertices.setflags(
            write=False,
        )
        normalized_faces.setflags(
            write=False,
        )

        object.__setattr__(
            self,
            "projected_vertices_2d",
            normalized_projected_vertices,
        )
        object.__setattr__(
            self,
            "triangle_faces",
            normalized_faces,
        )

    @property
    def vertex_count(
        self,
    ) -> int:
        return int(
            self.projected_vertices_2d.shape[0]
        )

    @property
    def face_count(
        self,
    ) -> int:
        return int(
            self.triangle_faces.shape[0]
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "scale": float(
                self.scale,
            ),
            "translation_x": float(
                self.translation_x,
            ),
            "translation_y": float(
                self.translation_y,
            ),
            "projected_vertices_2d": (
                self.projected_vertices_2d.tolist()
            ),
            "triangle_faces": self.triangle_faces.tolist(),
            "vertex_count": self.vertex_count,
            "face_count": self.face_count,
        }


class AtlasPortraitFlameWeakPerspectiveProjectionEvaluator:
    """
    Projects deformed FLAME mesh vertices into 2D image space.

    Projection model:

        u = scale * x + translation_x
        v = scale * y + translation_y

    Vertex depth is intentionally ignored.

    This evaluator performs no rasterization, visibility
    classification, shading, fitting, or preview generation.
    """

    @classmethod
    def evaluate(
        cls,
        mesh: AtlasPortraitFlameDeformedMesh,
        *,
        camera: AtlasPortraitWeakPerspectiveCamera,
    ) -> AtlasPortraitFlameWeakPerspectiveProjection:
        if not isinstance(
            mesh,
            AtlasPortraitFlameDeformedMesh,
        ):
            raise TypeError(
                "mesh must be an "
                "AtlasPortraitFlameDeformedMesh instance."
            )

        if not isinstance(
            camera,
            AtlasPortraitWeakPerspectiveCamera,
        ):
            raise TypeError(
                "camera must be an "
                "AtlasPortraitWeakPerspectiveCamera instance."
            )

        projected_vertices_2d = np.asarray(
            camera.scale
            * mesh.vertices[
                :,
                :2,
            ]
            + np.array(
                [
                    camera.translation_x,
                    camera.translation_y,
                ],
                dtype=np.float64,
            ),
            dtype=np.float64,
        ).copy()

        return AtlasPortraitFlameWeakPerspectiveProjection(
            scale=camera.scale,
            translation_x=camera.translation_x,
            translation_y=camera.translation_y,
            projected_vertices_2d=projected_vertices_2d,
            triangle_faces=np.asarray(
                mesh.triangle_faces,
                dtype=np.int64,
            ).copy(),
        )
