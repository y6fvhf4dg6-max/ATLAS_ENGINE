from __future__ import annotations

from copy import deepcopy

from CORE.atlas_lod_component_mesh_group_mapper import (
    AtlasLoDComponentMeshGroupMapper,
)
from CORE.atlas_lod_component_visibility_policy import (
    AtlasLoDComponentVisibilityPolicy,
)
from CORE.atlas_lod_level_catalog import (
    AtlasLoDLevel,
)
from CORE.atlas_semantic_architecture_model import (
    AtlasSemanticArchitectureModel,
)


class AtlasLoDMeshFilter:
    @classmethod
    def filter(
        cls,
        *,
        mesh,
        semantic_model,
        level,
    ) -> dict:
        if not isinstance(
            mesh,
            dict,
        ):
            raise TypeError(
                "mesh must be a dictionary"
            )

        if not isinstance(
            semantic_model,
            AtlasSemanticArchitectureModel,
        ):
            raise TypeError(
                "semantic_model must be an "
                "AtlasSemanticArchitectureModel"
            )

        if not isinstance(
            level,
            AtlasLoDLevel,
        ):
            raise TypeError(
                "level must be an AtlasLoDLevel"
            )

        result = deepcopy(
            mesh
        )

        mapped_group_keys = cls._mapped_group_keys(
            semantic_model
        )
        visible_group_keys = (
            cls._visible_group_keys(
                semantic_model=semantic_model,
                level=level,
            )
        )

        for group_key in mapped_group_keys:
            source_group = mesh.get(
                group_key,
                [],
            )

            if not isinstance(
                source_group,
                (list, tuple),
            ):
                raise ValueError(
                    f"mesh group {group_key} must "
                    "be a list or tuple"
                )

            result[group_key] = (
                deepcopy(
                    source_group
                )
                if group_key in visible_group_keys
                else []
            )

        result["triangles"] = [
            triangle
            for group_key in mapped_group_keys
            for component_mesh in result.get(
                group_key,
                (),
            )
            for triangle in component_mesh.get(
                "triangles",
                (),
            )
        ]

        result["lod_level"] = level
        result["lod_visible_mesh_groups"] = tuple(
            group_key
            for group_key in mapped_group_keys
            if group_key in visible_group_keys
        )

        return result

    @staticmethod
    def _mapped_group_keys(
        semantic_model,
    ) -> tuple[str, ...]:
        ordered = []

        for component in semantic_model.components:
            for group_key in (
                AtlasLoDComponentMeshGroupMapper
                .mesh_group_keys(
                    component
                )
            ):
                if group_key not in ordered:
                    ordered.append(
                        group_key
                    )

        return tuple(
            ordered
        )

    @staticmethod
    def _visible_group_keys(
        *,
        semantic_model,
        level,
    ) -> frozenset[str]:
        visible_components = (
            AtlasLoDComponentVisibilityPolicy
            .visible_components(
                model=semantic_model,
                level=level,
            )
        )

        return frozenset(
            group_key
            for component in visible_components
            for group_key in (
                AtlasLoDComponentMeshGroupMapper
                .mesh_group_keys(
                    component
                )
            )
        )
