from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np


class AtlasReliefSemanticHeightAdjuster:
    @classmethod
    def apply(
        cls,
        *,
        height_map,
        material_id_map,
        material_names: Sequence[str],
        height_scales: Mapping[str, float],
    ) -> np.ndarray:
        heights = np.asarray(
            height_map,
            dtype=np.float64,
        )

        material_ids = np.asarray(
            material_id_map,
        )

        if heights.shape != material_ids.shape:
            raise ValueError(
                "height_map and material_id_map "
                "must have the same shape"
            )

        result = heights.copy()

        for material_id, material_name in enumerate(
            material_names
        ):
            scale = float(
                height_scales.get(
                    material_name,
                    1.0,
                )
            )

            result[
                material_ids == material_id
            ] *= scale

        return result
