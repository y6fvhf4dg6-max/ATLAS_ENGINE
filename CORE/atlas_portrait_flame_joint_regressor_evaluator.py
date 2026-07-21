from __future__ import annotations

from typing import Any

import numpy as np

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)


class AtlasPortraitFlameJointRegressorEvaluator:
    """
    Evaluates canonical FLAME joint positions.

    The evaluator multiplies the canonical model's joint
    regressor by a validated shaped-vertex array.

    It performs no pose corrective deformation, kinematic
    transformation, linear blend skinning, fitting,
    rendering, or STL generation.
    """

    @classmethod
    def evaluate(
        cls,
        model: AtlasPortraitFlameCanonicalModel,
        *,
        shaped_vertices: Any,
    ) -> np.ndarray:
        if not isinstance(
            model,
            AtlasPortraitFlameCanonicalModel,
        ):
            raise TypeError(
                "model must be an "
                "AtlasPortraitFlameCanonicalModel instance."
            )

        normalized_vertices = cls._normalize_shaped_vertices(
            shaped_vertices,
            expected_vertex_count=model.vertex_count,
        )

        joint_positions = np.asarray(
            model.joint_regressor
            @ normalized_vertices,
            dtype=np.float64,
        ).copy()

        joint_positions.setflags(
            write=False,
        )

        return joint_positions

    @staticmethod
    def _normalize_shaped_vertices(
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
                "shaped_vertices must be numeric."
            ) from exc

        expected_shape = (
            expected_vertex_count,
            3,
        )

        if vertices.shape != expected_shape:
            raise ValueError(
                "shaped_vertices must have shape "
                f"{expected_shape}."
            )

        if not np.isfinite(
            vertices,
        ).all():
            raise ValueError(
                "shaped_vertices contains non-finite "
                "values."
            )

        return vertices.astype(
            np.float64,
            copy=True,
        )
