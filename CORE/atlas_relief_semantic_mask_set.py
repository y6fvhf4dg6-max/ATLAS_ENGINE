from __future__ import annotations

from collections.abc import Mapping

from CORE.atlas_relief_semantic_mask_input import (
    AtlasReliefSemanticMaskInput,
)
from CORE.atlas_relief_semantic_material_map import (
    AtlasReliefSemanticMaterialMap,
)


class AtlasReliefSemanticMaskSet:
    @classmethod
    def load(
        cls,
        *,
        mask_paths: Mapping[str, object],
        expected_shape,
        default_material: str,
        threshold: int = 128,
    ) -> dict:
        if not isinstance(mask_paths, Mapping):
            raise TypeError(
                "mask_paths must be a mapping"
            )

        if not mask_paths:
            raise ValueError(
                "mask_paths must not be empty"
            )

        region_masks = {}
        normalized_paths = {}

        for material_name, path in mask_paths.items():
            mask_input = AtlasReliefSemanticMaskInput.load(
                path,
                threshold=threshold,
                expected_shape=expected_shape,
            )

            region_masks[material_name] = mask_input[
                "mask"
            ]
            normalized_paths[material_name] = mask_input[
                "path"
            ]

        material_map = AtlasReliefSemanticMaterialMap.build(
            shape=expected_shape,
            region_masks=region_masks,
            default_material=default_material,
        )

        return {
            "type": "relief_semantic_mask_set",
            "shape": material_map["shape"],
            "material_names": material_map[
                "material_names"
            ],
            "mask_paths": normalized_paths,
            "region_masks": region_masks,
            "material_id_map": material_map[
                "material_id_map"
            ],
        }
