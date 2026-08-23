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

        vertices = geometry.vertices
        faces = geometry.topology.faces

        accumulated = np.zeros(
            (
                geometry.vertex_count,
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
