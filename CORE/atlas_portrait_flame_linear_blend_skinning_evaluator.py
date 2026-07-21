from __future__ import annotations

from typing import Any

import numpy as np

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)


class AtlasPortraitFlameLinearBlendSkinningEvaluator:
    """
    Applies FLAME linear blend skinning.

    Each posed vertex is converted to homogeneous coordinates,
    transformed by every joint transform, and blended using the
    model skinning weights.

    This evaluator performs no camera projection, fitting,
    rendering, preview generation, or STL generation.
    """

    @classmethod
    def evaluate(
        cls,
        model: AtlasPortraitFlameCanonicalModel,
        *,
        posed_vertices: Any,
        joint_transforms: Any,
    ) -> np.ndarray:
        if not isinstance(
            model,
            AtlasPortraitFlameCanonicalModel,
        ):
            raise TypeError(
                "model must be an "
                "AtlasPortraitFlameCanonicalModel instance."
            )

        normalized_vertices = cls._normalize_posed_vertices(
            posed_vertices,
            expected_vertex_count=model.vertex_count,
        )
        normalized_transforms = cls._normalize_joint_transforms(
            joint_transforms,
            expected_joint_count=model.joint_count,
        )

        homogeneous_vertices = np.concatenate(
            [
                normalized_vertices,
                np.ones(
                    (
                        model.vertex_count,
                        1,
                    ),
                    dtype=np.float64,
                ),
            ],
            axis=1,
        )

        transformed_vertices = np.einsum(
            "jab,nb->nja",
            normalized_transforms,
            homogeneous_vertices,
        )

        blended_homogeneous_vertices = np.einsum(
            "nj,nja->na",
            model.skinning_weights,
            transformed_vertices,
        )

        skinned_vertices = np.asarray(
            blended_homogeneous_vertices[
                :,
                :3,
            ],
            dtype=np.float64,
        ).copy()

        skinned_vertices.setflags(
            write=False,
        )

        return skinned_vertices

    @staticmethod
    def _normalize_posed_vertices(
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
                "posed_vertices must be numeric."
            ) from exc

        expected_shape = (
            expected_vertex_count,
            3,
        )

        if vertices.shape != expected_shape:
            raise ValueError(
                "posed_vertices must have shape "
                f"{expected_shape}."
            )

        if not np.isfinite(
            vertices,
        ).all():
            raise ValueError(
                "posed_vertices contains non-finite values."
            )

        return vertices.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _normalize_joint_transforms(
        value: Any,
        *,
        expected_joint_count: int,
    ) -> np.ndarray:
        try:
            transforms = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "joint_transforms must be numeric."
            ) from exc

        expected_shape = (
            expected_joint_count,
            4,
            4,
        )

        if transforms.shape != expected_shape:
            raise ValueError(
                "joint_transforms must have shape "
                f"{expected_shape}."
            )

        if not np.isfinite(
            transforms,
        ).all():
            raise ValueError(
                "joint_transforms contains non-finite values."
            )

        expected_bottom_rows = np.repeat(
            np.array(
                [
                    [
                        0.0,
                        0.0,
                        0.0,
                        1.0,
                    ],
                ],
                dtype=np.float64,
            ),
            repeats=expected_joint_count,
            axis=0,
        )

        if not np.allclose(
            transforms[
                :,
                3,
                :,
            ],
            expected_bottom_rows,
            rtol=0.0,
            atol=1.0e-12,
        ):
            raise ValueError(
                "joint_transforms must contain valid "
                "homogeneous bottom rows."
            )

        return transforms.astype(
            np.float64,
            copy=True,
        )
