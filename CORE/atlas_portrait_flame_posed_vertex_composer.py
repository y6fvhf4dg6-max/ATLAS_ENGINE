from __future__ import annotations

from typing import Any

import numpy as np

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)


class AtlasPortraitFlamePosedVertexComposer:
    """
    Composes FLAME shaped vertices with pose corrective offsets.

    The composer performs element-wise addition only.

    It performs no joint regression, kinematic transformation,
    linear blend skinning, fitting, rendering, or STL generation.
    """

    @classmethod
    def compose(
        cls,
        model: AtlasPortraitFlameCanonicalModel,
        *,
        shaped_vertices: Any,
        pose_corrective_offsets: Any,
    ) -> np.ndarray:
        if not isinstance(
            model,
            AtlasPortraitFlameCanonicalModel,
        ):
            raise TypeError(
                "model must be an "
                "AtlasPortraitFlameCanonicalModel instance."
            )

        expected_shape = (
            model.vertex_count,
            3,
        )

        normalized_shaped_vertices = cls._normalize_vertex_array(
            shaped_vertices,
            argument_name="shaped_vertices",
            expected_shape=expected_shape,
        )
        normalized_pose_corrective_offsets = cls._normalize_vertex_array(
            pose_corrective_offsets,
            argument_name="pose_corrective_offsets",
            expected_shape=expected_shape,
        )

        posed_vertices = np.asarray(
            normalized_shaped_vertices
            + normalized_pose_corrective_offsets,
            dtype=np.float64,
        ).copy()

        posed_vertices.setflags(
            write=False,
        )

        return posed_vertices

    @staticmethod
    def _normalize_vertex_array(
        value: Any,
        *,
        argument_name: str,
        expected_shape: tuple[int, int],
    ) -> np.ndarray:
        try:
            array = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{argument_name} must be numeric."
            ) from exc

        if array.shape != expected_shape:
            raise ValueError(
                f"{argument_name} must have shape "
                f"{expected_shape}."
            )

        if not np.isfinite(
            array,
        ).all():
            raise ValueError(
                f"{argument_name} contains non-finite values."
            )

        return array.astype(
            np.float64,
            copy=True,
        )
