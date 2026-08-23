from __future__ import annotations

import numpy as np

from CORE.atlas_canonical_head_geometry import (
    AtlasCanonicalHeadGeometry,
)
from CORE.atlas_canonical_head_vertex_normal_evaluator import (
    AtlasCanonicalHeadVertexNormalEvaluator,
)


class AtlasCanonicalHeadNormalResidualDetailProjector:
    @classmethod
    def project(
        cls,
        geometry: AtlasCanonicalHeadGeometry,
        *,
        amplitudes: object,
    ) -> np.ndarray:
        if not isinstance(
            geometry,
            AtlasCanonicalHeadGeometry,
        ):
            raise TypeError(
                "geometry must be an "
                "AtlasCanonicalHeadGeometry."
            )

        try:
            normalized_amplitudes = np.asarray(
                amplitudes,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "amplitudes must be numeric."
            ) from exc

        expected_shape = (
            geometry.vertex_count,
        )

        if normalized_amplitudes.shape != expected_shape:
            raise ValueError(
                "amplitudes must have shape "
                f"{expected_shape}."
            )

        if not np.isfinite(
            normalized_amplitudes
        ).all():
            raise ValueError(
                "amplitudes must contain only finite values."
            )

        normals = (
            AtlasCanonicalHeadVertexNormalEvaluator
            .evaluate(
                geometry
            )
        )

        displacement = (
            normals
            * normalized_amplitudes[
                :,
                np.newaxis,
            ]
        )

        displacement = np.asarray(
            displacement,
            dtype=np.float64,
        )
        displacement.setflags(
            write=False
        )

        return displacement
