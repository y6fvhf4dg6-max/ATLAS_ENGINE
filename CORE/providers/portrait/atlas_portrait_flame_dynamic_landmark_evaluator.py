from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np

from CORE.providers.portrait.atlas_portrait_flame_dynamic_landmark_selector import (
    AtlasPortraitFlameDynamicLandmarkSelection,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasPortraitFlameDynamicLandmarkEvaluation:
    """
    Immutable evaluated FLAME dynamic contour landmarks.
    """

    requested_yaw_degrees: float
    selected_yaw_degrees: float
    yaw_bin_index: int
    landmark_points: np.ndarray

    def __post_init__(
        self,
    ) -> None:
        requested_yaw = float(
            self.requested_yaw_degrees
        )
        selected_yaw = float(
            self.selected_yaw_degrees
        )
        yaw_bin_index = int(
            self.yaw_bin_index
        )

        landmark_points = np.asarray(
            self.landmark_points,
            dtype=np.float64,
        ).copy()

        if not math.isfinite(
            requested_yaw
        ):
            raise ValueError(
                "requested_yaw_degrees must be finite."
            )

        if not math.isfinite(
            selected_yaw
        ):
            raise ValueError(
                "selected_yaw_degrees must be finite."
            )

        if not 0 <= yaw_bin_index < 79:
            raise ValueError(
                "yaw_bin_index must be in the range 0..78."
            )

        if (
            landmark_points.ndim != 2
            or landmark_points.shape[0] == 0
            or landmark_points.shape[1] != 3
        ):
            raise ValueError(
                "landmark_points must have shape "
                "(L, 3) with L > 0."
            )

        if not np.isfinite(
            landmark_points
        ).all():
            raise ValueError(
                "landmark_points contains non-finite values."
            )

        landmark_points.setflags(
            write=False
        )

        object.__setattr__(
            self,
            "requested_yaw_degrees",
            requested_yaw,
        )
        object.__setattr__(
            self,
            "selected_yaw_degrees",
            selected_yaw,
        )
        object.__setattr__(
            self,
            "yaw_bin_index",
            yaw_bin_index,
        )
        object.__setattr__(
            self,
            "landmark_points",
            landmark_points,
        )

    @property
    def landmark_count(
        self,
    ) -> int:
        return int(
            self.landmark_points.shape[0]
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "requested_yaw_degrees": (
                self.requested_yaw_degrees
            ),
            "selected_yaw_degrees": (
                self.selected_yaw_degrees
            ),
            "yaw_bin_index": self.yaw_bin_index,
            "landmark_count": self.landmark_count,
            "landmark_points": (
                self.landmark_points.tolist()
            ),
        }


class AtlasPortraitFlameDynamicLandmarkEvaluator:
    """
    Evaluates selected FLAME contour landmarks on a mesh.

    Each selected landmark references one mesh triangle and one
    barycentric coordinate triplet. The evaluator computes the
    corresponding ordered 3D contour point.

    This class performs no yaw selection, camera projection,
    jaw correspondence, fitting, rendering, or STL generation.
    """

    @classmethod
    def evaluate(
        cls,
        selection: AtlasPortraitFlameDynamicLandmarkSelection,
        *,
        vertices: Any,
        triangles: Any,
    ) -> AtlasPortraitFlameDynamicLandmarkEvaluation:
        if not isinstance(
            selection,
            AtlasPortraitFlameDynamicLandmarkSelection,
        ):
            raise TypeError(
                "selection must be an "
                "AtlasPortraitFlameDynamicLandmarkSelection "
                "instance."
            )

        normalized_vertices = cls._normalize_vertices(
            vertices
        )
        normalized_triangles = cls._normalize_triangles(
            triangles,
            vertex_count=normalized_vertices.shape[0],
        )

        face_indices = selection.landmark_face_indices

        if np.any(
            face_indices >= normalized_triangles.shape[0]
        ):
            raise ValueError(
                "selection landmark_face_indices contains "
                "an index outside triangles."
            )

        selected_triangles = normalized_triangles[
            face_indices
        ]

        selected_triangle_vertices = normalized_vertices[
            selected_triangles
        ]

        landmark_points = np.sum(
            selected_triangle_vertices
            * selection.landmark_barycentric_coordinates[
                :,
                :,
                np.newaxis,
            ],
            axis=1,
            dtype=np.float64,
        )

        return AtlasPortraitFlameDynamicLandmarkEvaluation(
            requested_yaw_degrees=(
                selection.requested_yaw_degrees
            ),
            selected_yaw_degrees=(
                selection.selected_yaw_degrees
            ),
            yaw_bin_index=selection.yaw_bin_index,
            landmark_points=landmark_points,
        )

    @staticmethod
    def _normalize_vertices(
        value: Any,
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
                "vertices must be numeric."
            ) from exc

        if (
            vertices.ndim != 2
            or vertices.shape[0] == 0
            or vertices.shape[1] != 3
        ):
            raise ValueError(
                "vertices must have shape "
                "(V, 3) with V > 0."
            )

        if not np.isfinite(
            vertices
        ).all():
            raise ValueError(
                "vertices contains non-finite values."
            )

        return vertices.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _normalize_triangles(
        value: Any,
        *,
        vertex_count: int,
    ) -> np.ndarray:
        try:
            numeric_triangles = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "triangles must be numeric."
            ) from exc

        if (
            numeric_triangles.ndim != 2
            or numeric_triangles.shape[0] == 0
            or numeric_triangles.shape[1] != 3
        ):
            raise ValueError(
                "triangles must have shape "
                "(F, 3) with F > 0."
            )

        if not np.isfinite(
            numeric_triangles
        ).all():
            raise ValueError(
                "triangles contains non-finite values."
            )

        if not np.equal(
            numeric_triangles,
            np.rint(
                numeric_triangles
            ),
        ).all():
            raise ValueError(
                "triangles must contain integer values."
            )

        triangles = numeric_triangles.astype(
            np.int64,
            copy=True,
        )

        if np.any(
            triangles < 0
        ):
            raise ValueError(
                "triangles must not contain negative "
                "vertex indices."
            )

        if np.any(
            triangles >= vertex_count
        ):
            raise ValueError(
                "triangles contains a vertex index outside "
                "vertices."
            )

        return triangles
