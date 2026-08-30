from __future__ import annotations

import numpy as np

from CORE.atlas_canonical_head_geometry import (
    AtlasCanonicalHeadGeometry,
)


class AtlasCanonicalHeadVertexNormalEvaluator:
    @classmethod
    def evaluate(
        cls,
        geometry: AtlasCanonicalHeadGeometry,
    ) -> np.ndarray:
        if not isinstance(
            geometry,
            AtlasCanonicalHeadGeometry,
        ):
            raise TypeError(
                "geometry must be an "
                "AtlasCanonicalHeadGeometry."
            )

        return cls._evaluate_indexed(
            vertices=geometry.vertices,
            faces=geometry.topology.faces,
        )

    @classmethod
    def evaluate_indexed_surface(
        cls,
        *,
        vertices,
        faces,
    ) -> np.ndarray:
        vertices = np.asarray(
            vertices,
            dtype=np.float64,
        )
        faces = tuple(
            tuple(face)
            for face in faces
        )

        if (
            vertices.ndim != 2
            or vertices.shape[1] != 3
            or not np.isfinite(vertices).all()
        ):
            raise ValueError(
                "vertices must have shape "
                "(vertex_count, 3) and be finite."
            )

        if not faces:
            raise ValueError(
                "faces must not be empty."
            )

        for face in faces:
            if len(face) != 3:
                raise ValueError(
                    "faces must contain triangles."
                )
            if any(
                isinstance(index, bool)
                or not isinstance(index, (int, np.integer))
                or index < 0
                or index >= len(vertices)
                for index in face
            ):
                raise ValueError(
                    "faces reference invalid vertices."
                )

        return cls._evaluate_indexed(
            vertices=vertices,
            faces=faces,
        )

    @staticmethod
    def _evaluate_indexed(
        *,
        vertices,
        faces,
    ) -> np.ndarray:
        accumulated = np.zeros(
            (
                len(vertices),
                3,
            ),
            dtype=np.float64,
        )

        for index_a, index_b, index_c in faces:
            point_a = vertices[index_a]
            point_b = vertices[index_b]
            point_c = vertices[index_c]

            face_normal = np.cross(
                point_b - point_a,
                point_c - point_a,
            )

            face_length = float(
                np.linalg.norm(
                    face_normal
                )
            )

            if (
                not np.isfinite(
                    face_length
                )
                or face_length <= 1e-12
            ):
                raise ValueError(
                    "canonical head surface contains "
                    "a degenerate face."
                )

            accumulated[index_a] += face_normal
            accumulated[index_b] += face_normal
            accumulated[index_c] += face_normal

        lengths = np.linalg.norm(
            accumulated,
            axis=1,
        )

        if (
            not np.all(
                np.isfinite(
                    lengths
                )
            )
            or np.any(
                lengths <= 1e-12
            )
        ):
            raise ValueError(
                "canonical head surface contains "
                "a degenerate vertex normal."
            )

        normals = (
            accumulated
            / lengths[:, np.newaxis]
        )

        normals = np.asarray(
            normals,
            dtype=np.float64,
        )
        normals.setflags(
            write=False
        )

        return normals
