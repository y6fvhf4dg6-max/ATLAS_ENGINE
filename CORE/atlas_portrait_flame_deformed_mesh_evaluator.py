from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasPortraitFlameDeformedMesh:
    """
    Immutable deformed FLAME triangle-mesh contract.

    Vertex coordinates and triangle indices are stored as
    independent, read-only NumPy arrays.
    """

    vertices: np.ndarray
    triangle_faces: np.ndarray

    def __post_init__(
        self,
    ) -> None:
        normalized_vertices = np.asarray(
            self.vertices,
            dtype=np.float64,
        ).copy()
        normalized_faces = np.asarray(
            self.triangle_faces,
            dtype=np.int64,
        ).copy()

        if (
            normalized_vertices.ndim != 2
            or normalized_vertices.shape[1] != 3
        ):
            raise ValueError(
                "vertices must have shape (N, 3)."
            )

        if (
            normalized_faces.ndim != 2
            or normalized_faces.shape[1] != 3
        ):
            raise ValueError(
                "triangle_faces must have shape (F, 3)."
            )

        if not np.isfinite(
            normalized_vertices,
        ).all():
            raise ValueError(
                "vertices contains non-finite values."
            )

        if normalized_faces.size:
            if np.any(
                normalized_faces < 0,
            ):
                raise ValueError(
                    "triangle_faces contains negative indices."
                )

            if np.any(
                normalized_faces
                >= normalized_vertices.shape[0],
            ):
                raise ValueError(
                    "triangle_faces contains indices outside "
                    "the vertex array."
                )

        normalized_vertices.setflags(
            write=False,
        )
        normalized_faces.setflags(
            write=False,
        )

        object.__setattr__(
            self,
            "vertices",
            normalized_vertices,
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
            self.vertices.shape[0]
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
            "vertices": self.vertices.copy(),
            "triangle_faces": self.triangle_faces.copy(),
            "vertex_count": self.vertex_count,
            "face_count": self.face_count,
        }


class AtlasPortraitFlameDeformedMeshEvaluator:
    """
    Combines deformed FLAME vertices with canonical triangle faces.

    This evaluator performs no camera projection, normal
    calculation, visibility evaluation, fitting, rendering,
    preview generation, or STL generation.
    """

    @classmethod
    def evaluate(
        cls,
        model: AtlasPortraitFlameCanonicalModel,
        *,
        skinned_vertices: Any,
    ) -> AtlasPortraitFlameDeformedMesh:
        if not isinstance(
            model,
            AtlasPortraitFlameCanonicalModel,
        ):
            raise TypeError(
                "model must be an "
                "AtlasPortraitFlameCanonicalModel instance."
            )

        normalized_vertices = cls._normalize_skinned_vertices(
            skinned_vertices,
            expected_vertex_count=model.vertex_count,
        )

        return AtlasPortraitFlameDeformedMesh(
            vertices=normalized_vertices,
            triangle_faces=np.asarray(
                model.triangle_faces,
                dtype=np.int64,
            ).copy(),
        )

    @staticmethod
    def _normalize_skinned_vertices(
        value: Any,
        *,
        expected_vertex_count: int,
    ) -> np.ndarray:
        try:
            vertices = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "skinned_vertices must be numeric."
            ) from exc

        expected_shape = (
            expected_vertex_count,
            3,
        )

        if vertices.shape != expected_shape:
            raise ValueError(
                "skinned_vertices must have shape "
                f"{expected_shape}."
            )

        if not np.isfinite(
            vertices,
        ).all():
            raise ValueError(
                "skinned_vertices contains non-finite values."
            )

        return vertices.astype(
            np.float64,
            copy=True,
        )
