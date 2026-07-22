from __future__ import annotations

from typing import Any

import numpy as np


class AtlasPortraitFlameImageCoordinateNormalizer:
    """
    Converts FLAME canonical coordinates to the
    normalized portrait image coordinate convention.

    FLAME uses a Y-up coordinate system. Portrait image
    coordinates use Y-down. The conversion therefore
    preserves X and Z while reversing Y:

        (x, y, z) -> (x, -y, z)

    It performs no camera estimation, rotation, pose
    fitting, FLAME deformation, projection, rendering,
    relief compression, or STL generation.
    """

    @staticmethod
    def normalize(
        source_points_3d: Any,
    ) -> np.ndarray:
        try:
            points = np.asarray(
                source_points_3d,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "source_points_3d must be numeric."
            ) from exc

        if (
            points.ndim != 2
            or points.shape[1] != 3
            or points.shape[0] < 1
        ):
            raise ValueError(
                "source_points_3d must have shape "
                "(N, 3) and contain at least one point."
            )

        if not np.isfinite(
            points,
        ).all():
            raise ValueError(
                "source_points_3d contains non-finite "
                "values."
            )

        normalized = points.astype(
            np.float64,
            copy=True,
        )

        normalized[
            :,
            1,
        ] *= -1.0

        normalized.setflags(
            write=False,
        )

        return normalized

    @classmethod
    def normalize_mesh(
        cls,
        *,
        vertices: Any,
        triangle_faces: Any,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Converts FLAME mesh geometry to image coordinates.

        Y reflection changes mesh handedness. Triangle
        winding is therefore reversed to preserve the
        original front-face orientation:

            vertices: (x, y, z) -> (x, -y, z)
            faces:    (a, b, c) -> (a, c, b)
        """

        normalized_vertices = cls.normalize(
            vertices
        )

        try:
            numeric_faces = np.asarray(
                triangle_faces,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "triangle_faces must be numeric."
            ) from exc

        if (
            numeric_faces.ndim != 2
            or numeric_faces.shape[1] != 3
            or numeric_faces.shape[0] < 1
        ):
            raise ValueError(
                "triangle_faces must have shape (F, 3) "
                "and contain at least one face."
            )

        if not np.isfinite(
            numeric_faces
        ).all():
            raise ValueError(
                "triangle_faces contains non-finite values."
            )

        if not np.equal(
            numeric_faces,
            np.rint(
                numeric_faces
            ),
        ).all():
            raise ValueError(
                "triangle_faces must contain integer indices."
            )

        normalized_faces = numeric_faces.astype(
            np.int64,
            copy=True,
        )

        vertex_count = int(
            normalized_vertices.shape[0]
        )

        if (
            np.any(
                normalized_faces < 0
            )
            or np.any(
                normalized_faces >= vertex_count
            )
        ):
            raise ValueError(
                "triangle face index is outside the vertex range."
            )

        normalized_faces = normalized_faces[
            :,
            [
                0,
                2,
                1,
            ],
        ].copy()

        normalized_faces.setflags(
            write=False
        )

        return (
            normalized_vertices,
            normalized_faces,
        )
