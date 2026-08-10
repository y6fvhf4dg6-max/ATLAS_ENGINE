from __future__ import annotations

from collections import OrderedDict

from CORE.atlas_product_preview_material_profile import (
    AtlasProductPreviewMaterialProfile,
)


class AtlasSemanticMaterialHierarchy:
    ROLE_PRESENTATION = {
        "generic_building": {
            "surface_treatment": "building_mass",
            "relief_priority": 0.55,
            "readability_priority": 0.60,
        },
        "generic_building_roof": {
            "surface_treatment": "roof_plane",
            "relief_priority": 0.65,
            "readability_priority": 0.68,
        },
        "landmark_wall": {
            "surface_treatment": "landmark_wall",
            "relief_priority": 0.85,
            "readability_priority": 0.95,
        },
        "landmark_roof": {
            "surface_treatment": "landmark_roof",
            "relief_priority": 0.90,
            "readability_priority": 1.00,
        },
        "vegetation": {
            "surface_treatment": "vegetation_texture",
            "relief_priority": 0.55,
            "readability_priority": 0.65,
        },
        "water": {
            "surface_treatment": "water_surface",
            "relief_priority": 0.45,
            "readability_priority": 0.75,
        },
        "roads_hardscape": {
            "surface_treatment": "hardscape_linear",
            "relief_priority": 0.40,
            "readability_priority": 0.72,
        },
        "terrain": {
            "surface_treatment": "terrain_relief",
            "relief_priority": 0.70,
            "readability_priority": 0.70,
        },
        "frame": {
            "surface_treatment": "frame_finish",
            "relief_priority": 0.20,
            "readability_priority": 0.90,
        },
        "label_plate": {
            "surface_treatment": "label_plate",
            "relief_priority": 0.35,
            "readability_priority": 0.95,
        },
        "label_text": {
            "surface_treatment": "label_text",
            "relief_priority": 1.00,
            "readability_priority": 1.00,
        },
    }

    ROLE_RGB_FIELDS = OrderedDict(
        (
            ("generic_building", "building_rgb"),
            ("generic_building_roof", "building_roof_rgb"),
            ("landmark_wall", "landmark_rgb"),
            ("landmark_roof", "building_roof_rgb"),
            ("vegetation", "green_rgb"),
            ("water", "water_rgb"),
            ("roads_hardscape", "road_rgb"),
            ("terrain", "terrain_rgb"),
            ("frame", "frame_rgb"),
            ("label_plate", "label_plate_rgb"),
            ("label_text", "label_text_rgb"),
        )
    )

    @staticmethod
    def _validate_color_limit(
        maximum_physical_color_count,
    ):
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

        return maximum_physical_color_count

    @classmethod
    def resolve(
        cls,
        *,
        material_profile,
        maximum_physical_color_count,
    ):
        if not isinstance(
            material_profile,
            AtlasProductPreviewMaterialProfile,
        ):
            raise TypeError(
                "material_profile must be an "
                "AtlasProductPreviewMaterialProfile"
            )

        if maximum_physical_color_count is not None:
            maximum_physical_color_count = (
                cls._validate_color_limit(
                    maximum_physical_color_count
                )
            )

        physical_material_by_rgb = {}
        roles = OrderedDict()

        for semantic_role, field_name in (
            cls.ROLE_RGB_FIELDS.items()
        ):
            rgb = tuple(
                getattr(
                    material_profile,
                    field_name,
                )
            )

            if rgb not in physical_material_by_rgb:
                physical_material_by_rgb[
                    rgb
                ] = (
                    f"material_"
                    f"{len(physical_material_by_rgb) + 1}"
                )

            presentation = dict(
                cls.ROLE_PRESENTATION[
                    semantic_role
                ]
            )

            roles[semantic_role] = {
                "semantic_role": semantic_role,
                "rgb": rgb,
                "physical_material": (
                    physical_material_by_rgb[rgb]
                ),
                **presentation,
            }

        physical_color_count = len(
            physical_material_by_rgb
        )

        if (
            maximum_physical_color_count is not None
            and physical_color_count
            > maximum_physical_color_count
        ):
            raise ValueError(
                "material profile requires more "
                "physical colors than "
                "maximum_physical_color_count"
            )

        physical_materials = tuple(
            {
                "physical_material": material_name,
                "rgb": rgb,
            }
            for rgb, material_name in (
                physical_material_by_rgb.items()
            )
        )

        return {
            "profile_name": material_profile.name,
            "maximum_physical_color_count": (
                maximum_physical_color_count
            ),
            "physical_color_count": (
                physical_color_count
            ),
            "roles": roles,
            "physical_materials": (
                physical_materials
            ),
        }
