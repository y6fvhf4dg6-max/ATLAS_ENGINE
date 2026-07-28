from __future__ import annotations

from copy import deepcopy

from CORE.atlas_label_plate_spec import AtlasLabelPlateSpec
from CORE.atlas_label_text_spec import AtlasLabelTextSpec
from CORE.atlas_product_preview_material_profile import (
    AtlasProductPreviewMaterialProfile,
)
from CORE.atlas_wall_collection_product_builder import (
    AtlasWallCollectionProductBuilder,
)
from CORE.atlas_wall_frame_hanger_mesher import (
    AtlasWallFrameHangerMesher,
)
from CORE.atlas_wall_hanger_spec import AtlasWallHangerSpec
from CORE.atlas_wall_frame_spec import AtlasWallFrameSpec


class AtlasProductColorPreviewRenderer:
    GROUP_TO_BATCH = {
        "terrain": "terrain",
        "buildings": "buildings",
        "roads": "roads",
        "parks": "parks",
        "trees": "trees",
        "waters": "water",
    }

    @staticmethod
    def _translate_mesh(
        mesh: dict,
        offset_x_mm: float,
        offset_y_mm: float,
    ) -> dict:
        translated = deepcopy(mesh)

        if "triangles" in translated:
            translated["triangles"] = [
                tuple(
                    (
                        float(x) + offset_x_mm,
                        float(y) + offset_y_mm,
                        float(z),
                    )
                    for x, y, z in triangle
                )
                for triangle in translated["triangles"]
            ]

        return translated

    @classmethod
    def build_scene(
        cls,
        *,
        city_result: dict,
        frame_spec: AtlasWallFrameSpec,
        frame_depth_mm: float,
        material_profile: AtlasProductPreviewMaterialProfile,
        label_plate_spec: AtlasLabelPlateSpec | None = None,
        label_text_spec: AtlasLabelTextSpec | None = None,
    ) -> dict:
        terrain_size_x_mm = float(city_result["terrain_size_x_mm"])
        terrain_size_y_mm = float(city_result["terrain_size_y_mm"])

        city_offset_x_mm = -(terrain_size_x_mm / 2.0)
        city_offset_y_mm = -(terrain_size_y_mm / 2.0)

        hanger_spec = AtlasWallHangerSpec.for_product_size(
            outer_width_mm=frame_spec.outer_width_mm,
            outer_height_mm=frame_spec.outer_height_mm,
            frame_width_mm=frame_spec.frame_width_mm,
            frame_depth_mm=frame_depth_mm,
        )

        frame_mesh = AtlasWallFrameHangerMesher.build(
            frame_spec=frame_spec,
            hanger_spec=hanger_spec,
            frame_depth_mm=frame_depth_mm,
        )

        material_batches = {
            "frame": {
                "rgb": material_profile.frame_rgb,
                "meshes": [frame_mesh],
            },
            "terrain": {
                "rgb": material_profile.terrain_rgb,
                "meshes": [],
            },
            "buildings": {
                "rgb": material_profile.building_rgb,
                "meshes": [],
            },
            "building_walls": {
                "rgb": material_profile.building_wall_rgb,
                "meshes": [],
            },
            "building_roofs": {
                "rgb": material_profile.building_roof_rgb,
                "meshes": [],
            },
            "roads": {
                "rgb": material_profile.road_rgb,
                "meshes": [],
            },
            "parks": {
                "rgb": material_profile.green_rgb,
                "meshes": [],
            },
            "trees": {
                "rgb": material_profile.tree_rgb,
                "meshes": [],
            },
            "water": {
                "rgb": material_profile.water_rgb,
                "meshes": [],
            },
            "label_plate": {
                "rgb": material_profile.label_plate_rgb,
                "meshes": [],
            },
            "label_text": {
                "rgb": material_profile.label_text_rgb,
                "meshes": [],
            },
        }

        mesh_groups = city_result.get("mesh_groups", {})

        for group_name, batch_name in cls.GROUP_TO_BATCH.items():
            for mesh in mesh_groups.get(group_name, []):
                if (
                    group_name == "buildings"
                    and "building_wall_triangles" in mesh
                    and "building_roof_triangles" in mesh
                ):
                    wall_mesh = {
                        "type": mesh.get("type", "building"),
                        "triangles": mesh["building_wall_triangles"],
                    }
                    roof_mesh = {
                        "type": mesh.get("type", "building"),
                        "triangles": mesh["building_roof_triangles"],
                    }

                    material_batches["building_walls"]["meshes"].append(
                        cls._translate_mesh(
                            wall_mesh,
                            city_offset_x_mm,
                            city_offset_y_mm,
                        )
                    )
                    material_batches["building_roofs"]["meshes"].append(
                        cls._translate_mesh(
                            roof_mesh,
                            city_offset_x_mm,
                            city_offset_y_mm,
                        )
                    )
                    continue

                material_batches[batch_name]["meshes"].append(
                    cls._translate_mesh(
                        mesh,
                        city_offset_x_mm,
                        city_offset_y_mm,
                    )
                )

        if label_plate_spec is not None or label_text_spec is not None:
            product = AtlasWallCollectionProductBuilder.build(
                city_result=city_result,
                frame_spec=frame_spec,
                frame_depth_mm=frame_depth_mm,
                label_plate_spec=label_plate_spec,
                label_text_spec=label_text_spec,
            )
            material_batches["label_plate"]["meshes"].extend(
                product["label_plate_meshes"]
            )
            material_batches["label_text"]["meshes"].extend(
                product["label_text_meshes"]
            )

        return {
            "type": "product_color_preview_scene",
            "profile_name": material_profile.name,
            "outer_width_mm": frame_spec.outer_width_mm,
            "outer_height_mm": frame_spec.outer_height_mm,
            "opening_width_mm": frame_spec.inner_width_mm,
            "opening_height_mm": frame_spec.inner_height_mm,
            "frame_depth_mm": float(frame_depth_mm),
            "city_offset_x_mm": city_offset_x_mm,
            "city_offset_y_mm": city_offset_y_mm,
            "material_batches": material_batches,
        }
