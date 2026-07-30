from __future__ import annotations

from collections.abc import Mapping

import numpy as np


class AtlasReliefSemanticMaterialMap:
    @staticmethod
    def _normalize_shape(shape) -> tuple[int, int]:
        try:
            rows, columns = shape
        except (TypeError, ValueError) as error:
            raise ValueError(
                "shape must contain exactly two dimensions"
            ) from error

        rows = int(rows)
        columns = int(columns)

        if rows <= 0 or columns <= 0:
            raise ValueError(
                "shape dimensions must be positive"
            )

        return rows, columns

    @staticmethod
    def _normalize_material_name(
        value,
        *,
        field_name: str,
    ) -> str:
        name = str(value).strip()

        if not name:
            raise ValueError(
                f"{field_name} must not be empty"
            )

        return name

    @classmethod
    def build(
        cls,
        *,
        shape,
        region_masks: Mapping[str, object],
        default_material: str,
    ) -> dict:
        normalized_shape = cls._normalize_shape(shape)
        default_name = cls._normalize_material_name(
            default_material,
            field_name="default_material",
        )

        if not isinstance(region_masks, Mapping):
            raise TypeError(
                "region_masks must be a mapping"
            )

        material_names = [default_name]
        material_id_map = np.zeros(
            normalized_shape,
            dtype=np.uint8,
        )
        occupied = np.zeros(
            normalized_shape,
            dtype=bool,
        )

        for material_id, (raw_name, raw_mask) in enumerate(
            region_masks.items(),
            start=1,
        ):
            material_name = cls._normalize_material_name(
                raw_name,
                field_name="material name",
            )

            if material_name in material_names:
                raise ValueError(
                    f"duplicate material name: {material_name}"
                )

            mask = np.asarray(
                raw_mask,
                dtype=bool,
            )

            if mask.shape != normalized_shape:
                raise ValueError(
                    "region mask shape does not match "
                    f"expected shape {normalized_shape}: "
                    f"{mask.shape}"
                )

            if np.any(occupied & mask):
                raise ValueError(
                    "region masks overlap"
                )

            if material_id > np.iinfo(
                np.uint8
            ).max:
                raise ValueError(
                    "too many materials for uint8 map"
                )

            material_id_map[mask] = material_id
            occupied |= mask
            material_names.append(material_name)

        return {
            "type": "relief_semantic_material_map",
            "shape": normalized_shape,
            "material_names": tuple(
                material_names
            ),
            "material_id_map": material_id_map,
        }
