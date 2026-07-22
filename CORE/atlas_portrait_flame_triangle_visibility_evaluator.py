from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from CORE.atlas_portrait_flame_deformed_mesh_evaluator import (
    AtlasPortraitFlameDeformedMesh,
)
from CORE.atlas_portrait_flame_weak_perspective_projection_evaluator import (
    AtlasPortraitFlameWeakPerspectiveProjection,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasPortraitFlameTriangleVisibility:
    """
    Immutable projected-triangle visibility contract.

    Visibility currently represents projected front-facing
    classification only. It does not include occlusion or
    pixel-level depth testing.
    """

    visible_triangle_mask: np.ndarray
    front_facing_triangle_mask: np.ndarray
    signed_projected_areas: np.ndarray
    mean_triangle_depths: np.ndarray

    def __post_init__(
        self,
    ) -> None:
        visible_mask = np.asarray(
            self.visible_triangle_mask,
            dtype=np.bool_,
        ).copy()
        front_facing_mask = np.asarray(
            self.front_facing_triangle_mask,
            dtype=np.bool_,
        ).copy()
        signed_areas = np.asarray(
            self.signed_projected_areas,
            dtype=np.float64,
        ).copy()
        mean_depths = np.asarray(
            self.mean_triangle_depths,
            dtype=np.float64,
        ).copy()

        arrays = {
            "visible_triangle_mask": visible_mask,
            "front_facing_triangle_mask": front_facing_mask,
            "signed_projected_areas": signed_areas,
            "mean_triangle_depths": mean_depths,
        }

        triangle_count = visible_mask.shape[0]

        for name, array in arrays.items():
            if (
                array.ndim != 1
                or array.shape[0] != triangle_count
            ):
                raise ValueError(
                    f"{name} must have shape "
                    f"({triangle_count},)."
                )

        if not np.isfinite(
            signed_areas,
        ).all():
            raise ValueError(
                "signed_projected_areas contains "
                "non-finite values."
            )

        if not np.isfinite(
            mean_depths,
        ).all():
            raise ValueError(
                "mean_triangle_depths contains "
                "non-finite values."
            )

        visible_mask.setflags(
            write=False,
        )
        front_facing_mask.setflags(
            write=False,
        )
        signed_areas.setflags(
            write=False,
        )
        mean_depths.setflags(
            write=False,
        )

        object.__setattr__(
            self,
            "visible_triangle_mask",
            visible_mask,
        )
        object.__setattr__(
            self,
            "front_facing_triangle_mask",
            front_facing_mask,
        )
        object.__setattr__(
            self,
            "signed_projected_areas",
            signed_areas,
        )
        object.__setattr__(
            self,
            "mean_triangle_depths",
            mean_depths,
        )

    @property
    def triangle_count(
        self,
    ) -> int:
        return int(
            self.visible_triangle_mask.shape[0]
        )

    @property
    def visible_triangle_count(
        self,
    ) -> int:
        return int(
            np.count_nonzero(
                self.visible_triangle_mask,
            )
        )

    @property
    def hidden_triangle_count(
        self,
    ) -> int:
        return (
            self.triangle_count
            - self.visible_triangle_count
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "triangle_count": self.triangle_count,
            "visible_triangle_count": (
                self.visible_triangle_count
            ),
            "hidden_triangle_count": (
                self.hidden_triangle_count
            ),
            "visible_triangle_mask": (
                self.visible_triangle_mask.tolist()
            ),
            "front_facing_triangle_mask": (
                self.front_facing_triangle_mask.tolist()
            ),
            "signed_projected_areas": (
                self.signed_projected_areas.tolist()
            ),
            "mean_triangle_depths": (
                self.mean_triangle_depths.tolist()
            ),
        }


class AtlasPortraitFlameTriangleVisibilityEvaluator:
    """
    Classifies projected FLAME triangles by winding.

    Positive signed projected area is front-facing.
    Negative signed projected area is back-facing.
    Degenerate projected triangles are rejected.

    Mean deformed-mesh Z depth is retained for each triangle
    for use by a later rasterizer or z-buffer stage.

    This evaluator performs no triangle-triangle occlusion,
    pixel rasterization, shading, or preview generation.
    """

    _DEGENERATE_AREA_THRESHOLD = 1.0e-15

    @classmethod
    def evaluate(
        cls,
        mesh: AtlasPortraitFlameDeformedMesh,
        *,
        projection: (
            AtlasPortraitFlameWeakPerspectiveProjection
        ),
    ) -> AtlasPortraitFlameTriangleVisibility:
        if not isinstance(
            mesh,
            AtlasPortraitFlameDeformedMesh,
        ):
            raise TypeError(
                "mesh must be an "
                "AtlasPortraitFlameDeformedMesh instance."
            )

        if not isinstance(
            projection,
            AtlasPortraitFlameWeakPerspectiveProjection,
        ):
            raise TypeError(
                "projection must be an "
                "AtlasPortraitFlameWeakPerspectiveProjection "
                "instance."
            )

        if not np.array_equal(
            mesh.triangle_faces,
            projection.triangle_faces,
        ):
            raise ValueError(
                "mesh and projection triangle_faces "
                "must match exactly."
            )

        faces = np.asarray(
            mesh.triangle_faces,
            dtype=np.int64,
        )
        projected_vertices = np.asarray(
            projection.projected_vertices_2d,
            dtype=np.float64,
        )

        first_points = projected_vertices[
            faces[
                :,
                0,
            ]
        ]
        second_points = projected_vertices[
            faces[
                :,
                1,
            ]
        ]
        third_points = projected_vertices[
            faces[
                :,
                2,
            ]
        ]

        first_edges = (
            second_points
            - first_points
        )
        second_edges = (
            third_points
            - first_points
        )

        signed_double_areas = (
            first_edges[
                :,
                0,
            ]
            * second_edges[
                :,
                1,
            ]
            - first_edges[
                :,
                1,
            ]
            * second_edges[
                :,
                0,
            ]
        )

        signed_projected_areas = (
            0.5
            * signed_double_areas
        )

        if np.any(
            np.abs(
                signed_projected_areas,
            )
            <= cls._DEGENERATE_AREA_THRESHOLD
        ):
            raise ValueError(
                "projection contains a degenerate triangle."
            )

        front_facing_mask = (
            signed_projected_areas
            > 0.0
        )

        visible_mask = front_facing_mask.copy()

        vertex_depths = np.asarray(
            mesh.vertices[
                :,
                2,
            ],
            dtype=np.float64,
        )

        mean_triangle_depths = np.mean(
            vertex_depths[
                faces
            ],
            axis=1,
            dtype=np.float64,
        )

        return AtlasPortraitFlameTriangleVisibility(
            visible_triangle_mask=visible_mask,
            front_facing_triangle_mask=(
                front_facing_mask
            ),
            signed_projected_areas=(
                signed_projected_areas
            ),
            mean_triangle_depths=(
                mean_triangle_depths
            ),
        )
