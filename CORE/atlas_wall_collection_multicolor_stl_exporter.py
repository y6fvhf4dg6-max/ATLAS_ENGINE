from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

from EXPORT.atlas_stl_writer import AtlasSTLWriter


class AtlasWallCollectionMulticolorSTLExporter:
    BATCH_TO_COLOR_NAME = {
        "building_roofs": "red",
        "parks": "green",
        "trees": "green",
        "label_plate": "black",
        "water": "blue",
    }

    COLOR_ORDER = (
        "white",
        "red",
        "green",
        "black",
        "blue",
    )

    @classmethod
    def _resolve_color_name(
        cls,
        *,
        batch_name: str,
    ) -> str:
        return cls.BATCH_TO_COLOR_NAME.get(
            str(batch_name),
            "white",
        )

    @classmethod
    def export_scene(
        cls,
        *,
        scene: dict,
        output_directory,
        product_name: str,
    ) -> dict:
        output_directory = Path(output_directory)
        product_name = str(product_name).strip()

        if not product_name:
            raise ValueError("product_name must not be empty")

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        material_batches = scene.get(
            "material_batches",
            {},
        )

        color_groups = OrderedDict(
            (
                color_name,
                {
                    "rgb": None,
                    "meshes": [],
                    "source_batches": [],
                },
            )
            for color_name in cls.COLOR_ORDER
        )

        for batch_name, batch in material_batches.items():
            meshes = list(batch.get("meshes", []))

            if not meshes:
                continue

            color_name = cls._resolve_color_name(
                batch_name=batch_name,
            )
            rgb = tuple(batch["rgb"])
            group = color_groups[color_name]

            if group["rgb"] is None:
                group["rgb"] = rgb
            elif group["rgb"] != rgb:
                raise ValueError(
                    f"{color_name} batches use conflicting RGB values"
                )

            group["meshes"].extend(meshes)
            group["source_batches"].append(
                str(batch_name)
            )

        parts = {}

        for color_name in cls.COLOR_ORDER:
            group = color_groups[color_name]

            if not group["meshes"]:
                continue

            rgb = group["rgb"]
            output_path = (
                output_directory
                / f"{product_name}__{color_name}.stl"
            )

            solid_name = (
                "ATLAS_WALL_COLLECTION_"
                f"{color_name.upper()}"
            )

            AtlasSTLWriter.write(
                meshes=group["meshes"],
                output_path=output_path,
                solid_name=solid_name,
            )

            parts[color_name] = {
                "rgb": rgb,
                "output_path": output_path,
                "mesh_count": len(group["meshes"]),
                "source_batches": tuple(
                    group["source_batches"]
                ),
            }

        return {
            "type": (
                "wall_collection_multicolor_stl_package"
            ),
            "profile_name": scene.get("profile_name"),
            "color_count": len(parts),
            "part_count": len(parts),
            "parts": parts,
        }
