from __future__ import annotations

from copy import deepcopy

from CORE.atlas_product_preview_material_profile import (
    AtlasProductPreviewMaterialProfile,
)
from CORE.atlas_wall_frame_mesher import AtlasWallFrameMesher
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
    ) -> dict:
        terrain_size_x_mm = float(city_result["terrain_size_x_mm"])
        terrain_size_y_mm = float(city_result["terrain_size_y_mm"])

        city_offset_x_mm = -(terrain_size_x_mm / 2.0)
        city_offset_y_mm = -(terrain_size_y_mm / 2.0)

        frame_mesh = AtlasWallFrameMesher.build(
            spec=frame_spec,
            depth_mm=frame_depth_mm,
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
        }

        mesh_groups = city_result.get("mesh_groups", {})

        for group_name, batch_name in cls.GROUP_TO_BATCH.items():
            for mesh in mesh_groups.get(group_name, []):
                material_batches[batch_name]["meshes"].append(
                    cls._translate_mesh(
                        mesh,
                        city_offset_x_mm,
                        city_offset_y_mm,
                    )
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
