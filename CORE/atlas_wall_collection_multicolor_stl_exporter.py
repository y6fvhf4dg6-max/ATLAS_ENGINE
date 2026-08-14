from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

from EXPORT.atlas_stl_writer import AtlasSTLWriter


class AtlasWallCollectionMulticolorSTLExporter:
    PHYSICAL_PALETTE_NAME_BY_RGB = {
        (20, 20, 20): "black",
        (245, 245, 240): "white",
        (205, 190, 160): "desert_tan",
        (156, 48, 42): "brick_red",
        (73, 105, 58): "dark_green",
        (70, 140, 180): "blue",
    }

    BATCH_TO_COLOR_NAME = {
        "frame": "black",
        "roads": "black",
        "label_text": "black",
        "terrain": "desert_tan",
        "buildings": "desert_tan",
        "building_walls": "desert_tan",
        "landmarks": "desert_tan",
        "landmark_roofs": "brick_red",
        "label_plate": "desert_tan",
        "building_roofs": "brick_red",
        "parks": "dark_green",
        "trees": "dark_green",
        "water": "blue",
    }

    BATCH_TO_SEMANTIC_ROLE = {
        "frame": "frame",
        "terrain": "terrain",
        "building_walls": "generic_building",
        "building_roofs": "generic_building_roof",
        "landmark_roofs": "landmark_roof",
        "parks": "vegetation",
        "trees": "vegetation",
        "water": "water",
        "label_plate": "label_plate",
        "label_text": "label_text",
        "roads": "roads_hardscape",
    }

    COLOR_ORDER = (
        "black",
        "desert_tan",
        "brick_red",
        "dark_green",
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
        maximum_physical_color_count=None,
    ) -> dict:
        output_directory = Path(output_directory)
        product_name = str(product_name).strip()

        if not product_name:
            raise ValueError("product_name must not be empty")

        if maximum_physical_color_count is not None:
            if (
                isinstance(
                    maximum_physical_color_count,
                    bool,
                )
                or not isinstance(
                    maximum_physical_color_count,
                    int,
                )
                or maximum_physical_color_count <= 0
            ):
                raise ValueError(
                    "maximum_physical_color_count "
                    "must be a positive integer"
                )

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        material_batches = scene.get(
            "material_batches",
            {},
        )

        color_groups = OrderedDict()

        for batch_name, batch in material_batches.items():
            meshes = list(batch.get("meshes", []))

            if not meshes:
                continue

            batch_name = str(batch_name)
            legacy_color_name = cls._resolve_color_name(
                batch_name=batch_name,
            )

            physical_material = str(
                batch.get(
                    "physical_material",
                    "",
                )
            ).strip()

            if physical_material:
                group_key = (
                    "physical_material",
                    physical_material,
                )
            else:
                group_key = (
                    "legacy_color",
                    legacy_color_name,
                )

            group = color_groups.setdefault(
                group_key,
                {
                    "rgb": None,
                    "meshes": [],
                    "source_batches": [],
                    "semantic_roles": [],
                    "legacy_color_names": [],
                    "physical_material": (
                        physical_material or None
                    ),
                },
            )

            rgb = tuple(batch["rgb"])

            if group["rgb"] is None:
                group["rgb"] = rgb
            elif group["rgb"] != rgb:
                raise ValueError(
                    "physical material batches use "
                    "conflicting RGB values"
                )

            group["meshes"].extend(meshes)
            group["source_batches"].append(
                batch_name
            )

            if (
                legacy_color_name
                not in group["legacy_color_names"]
            ):
                group["legacy_color_names"].append(
                    legacy_color_name
                )

            semantic_role = batch.get(
                "semantic_role"
            )

            if semantic_role is None:
                semantic_role = (
                    cls.BATCH_TO_SEMANTIC_ROLE.get(
                        batch_name
                    )
                )

            if (
                semantic_role is not None
                and semantic_role
                not in group["semantic_roles"]
            ):
                group["semantic_roles"].append(
                    semantic_role
                )

        physical_color_count = sum(
            1
            for group in color_groups.values()
            if group["meshes"]
        )

        if (
            maximum_physical_color_count is not None
            and physical_color_count
            > maximum_physical_color_count
        ):
            raise ValueError(
                "physical color count exceeds "
                "maximum_physical_color_count"
            )

        parts = {}
        used_part_names = set()

        for group in color_groups.values():
            if not group["meshes"]:
                continue

            legacy_color_names = tuple(
                group["legacy_color_names"]
            )

            physical_palette_name = (
                cls.PHYSICAL_PALETTE_NAME_BY_RGB.get(
                    tuple(group["rgb"])
                )
            )

            if physical_palette_name is not None:
                part_name = physical_palette_name
            elif len(legacy_color_names) == 1:
                part_name = legacy_color_names[0]
            elif group["physical_material"]:
                part_name = group[
                    "physical_material"
                ]
            else:
                part_name = "material"

            part_name = "".join(
                character
                if (
                    character.isalnum()
                    or character in {"_", "-"}
                )
                else "_"
                for character in str(part_name)
            ).strip("_")

            if not part_name:
                part_name = "material"

            base_part_name = part_name
            suffix = 2

            while part_name in used_part_names:
                part_name = (
                    f"{base_part_name}_{suffix}"
                )
                suffix += 1

            used_part_names.add(part_name)

            rgb = group["rgb"]
            output_path = (
                output_directory
                / f"{product_name}__{part_name}.stl"
            )

            solid_name = (
                "ATLAS_WALL_COLLECTION_"
                f"{part_name.upper()}"
            )

            merged_triangles = []
            seen_triangle_keys = set()

            for mesh in group["meshes"]:
                for triangle in mesh.get("triangles", []):
                    triangle_key = tuple(
                        sorted(
                            tuple(
                                round(float(value), 6)
                                for value in point
                            )
                            for point in triangle
                        )
                    )

                    if triangle_key in seen_triangle_keys:
                        continue

                    seen_triangle_keys.add(triangle_key)
                    merged_triangles.append(triangle)

            AtlasSTLWriter.write(
                meshes=[
                    {
                        "type": "multicolor_merged_color_mesh",
                        "triangles": merged_triangles,
                    }
                ],
                output_path=output_path,
                solid_name=solid_name,
            )

            parts[part_name] = {
                "rgb": rgb,
                "physical_material": (
                    group["physical_material"]
                    or part_name
                ),
                "output_path": output_path,
                "mesh_count": len(group["meshes"]),
                "source_batches": tuple(
                    group["source_batches"]
                ),
                "semantic_roles": tuple(
                    group["semantic_roles"]
                ),
            }

        return {
            "type": (
                "wall_collection_multicolor_stl_package"
            ),
            "profile_name": scene.get("profile_name"),
            "color_count": len(parts),
            "physical_color_count": len(parts),
            "maximum_physical_color_count": (
                maximum_physical_color_count
            ),
            "part_count": len(parts),
            "parts": parts,
        }
