from __future__ import annotations


class AtlasCustomerPreviewParity:
    REQUIRED_SEMANTIC_ROLES = frozenset(
        {
            "generic_building",
            "landmark_wall",
            "vegetation",
            "water",
            "roads_hardscape",
            "terrain",
        }
    )

    @staticmethod
    def _same(left, right):
        return left == right

    @classmethod
    def resolve(
        cls,
        *,
        production_result,
        preview_scene,
    ):
        if not isinstance(
            production_result,
            dict,
        ):
            raise TypeError(
                "production_result must be a dict"
            )

        if not isinstance(
            preview_scene,
            dict,
        ):
            raise TypeError(
                "preview_scene must be a dict"
            )

        production_lod = production_result.get(
            "city_composition_lod"
        )

        preview_lod = preview_scene.get(
            "city_composition_lod"
        )

        production_product_size = None

        if isinstance(
            production_lod,
            dict,
        ):
            production_product_size = (
                production_lod.get(
                    "product_size_mm"
                )
            )

        preview_product_size = (
            preview_scene.get(
                "opening_width_mm"
            )
        )

        semantic_hierarchy = (
            preview_scene.get(
                "semantic_material_hierarchy",
                {},
            )
        )

        roles = semantic_hierarchy.get(
            "roles",
            {},
        )

        checks = {
            "scene_morphology": cls._same(
                production_result.get(
                    "effective_scene_morphology"
                ),
                preview_scene.get(
                    "effective_scene_morphology"
                ),
            ),
            "composition_policy": cls._same(
                production_result.get(
                    "morphology_composition_policy"
                ),
                preview_scene.get(
                    "morphology_composition_policy"
                ),
            ),
            "city_composition_lod": cls._same(
                production_lod,
                preview_lod,
            ),
            "suppressed_mesh_count": cls._same(
                production_result.get(
                    "city_composition_suppressed_meshes",
                    0,
                ),
                preview_scene.get(
                    "city_composition_suppressed_meshes",
                    0,
                ),
            ),
            "product_size": cls._same(
                production_product_size,
                preview_product_size,
            ),
            "semantic_material_roles": (
                cls.REQUIRED_SEMANTIC_ROLES
                .issubset(
                    set(roles)
                )
            ),
        }

        mismatches = tuple(
            name
            for name, matched in checks.items()
            if not matched
        )

        return {
            "type": "customer_preview_parity",
            "matches": not mismatches,
            "checks": checks,
            "mismatches": mismatches,
        }
