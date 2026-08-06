from __future__ import annotations

from CORE.atlas_semantic_architecture_component import (
    AtlasSemanticArchitectureComponent,
)


class AtlasLoDComponentMeshGroupMapper:
    _FAMILY_ROLE_GROUPS = {
        "church": {
            "nave": (
                "outer_aisle_meshes",
                "main_nave_body_meshes",
            ),
            "transept": (
                "transept_meshes",
            ),
            "apse": (
                "apse_meshes",
            ),
            "tower": (
                "tower_meshes",
            ),
            "buttress_system": (
                "facade_meshes",
            ),
            "window_bay_system": (
                "facade_meshes",
                "tower_window_meshes",
            ),
            "roof_section": (
                "roof_meshes",
            ),
        },
        "mosque": {
            "prayer_hall": (
                "prayer_hall_meshes",
            ),
            "dome_drum": (
                "dome_drum_meshes",
            ),
            "main_dome": (
                "dome_meshes",
            ),
            "minaret_body": (
                "minaret_meshes",
            ),
            "minaret_balcony": (
                "minaret_balcony_meshes",
            ),
            "minaret_cap": (
                "minaret_cap_meshes",
            ),
        },
    }

    @classmethod
    def mesh_group_keys(
        cls,
        component: AtlasSemanticArchitectureComponent,
    ) -> tuple[str, ...]:
        if not isinstance(
            component,
            AtlasSemanticArchitectureComponent,
        ):
            raise TypeError(
                "component must be an "
                "AtlasSemanticArchitectureComponent"
            )

        family_mapping = (
            cls._FAMILY_ROLE_GROUPS.get(
                component.landmark_family,
                {},
            )
        )

        return family_mapping.get(
            component.role,
            (),
        )

    @classmethod
    def supported_families(
        cls,
    ) -> tuple[str, ...]:
        return tuple(
            cls._FAMILY_ROLE_GROUPS
        )
