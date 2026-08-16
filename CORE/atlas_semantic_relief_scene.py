from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_semantic_relief_component import (
    AtlasSemanticReliefComponent,
    _normalize_identifier,
)


@dataclass(frozen=True, slots=True)
class AtlasSemanticReliefScene:
    scene_id: str
    components: tuple[AtlasSemanticReliefComponent, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "scene_id",
            _normalize_identifier(
                self.scene_id,
                field_name="scene_id",
            ),
        )
        components = tuple(self.components)

        if not components:
            raise ValueError(
                "components must not be empty"
            )

        if not all(
            isinstance(component, AtlasSemanticReliefComponent)
            for component in components
        ):
            raise TypeError(
                "components must contain only "
                "AtlasSemanticReliefComponent instances"
            )

        component_ids = tuple(
            component.component_id
            for component in components
        )

        component_id_set = set(component_ids)

        if len(component_ids) != len(component_id_set):
            raise ValueError(
                "duplicate component_id"
            )

        if any(
            component.parent_component_id is not None
            and component.parent_component_id not in component_id_set
            for component in components
        ):
            raise ValueError(
                "parent_component_id must reference a scene component"
            )

        if any(
            component.parent_component_id == component.component_id
            for component in components
        ):
            raise ValueError(
                "parent component must not reference itself"
            )

        parent_by_id = {
            component.component_id: component.parent_component_id
            for component in components
        }

        for component_id in component_ids:
            visited = set()
            current_id = component_id

            while current_id is not None:
                if current_id in visited:
                    raise ValueError(
                        "parent graph contains a cycle"
                    )

                visited.add(current_id)
                current_id = parent_by_id[current_id]

        if any(
            component.target_surface_id is not None
            and component.target_surface_id not in component_id_set
            for component in components
        ):
            raise ValueError(
                "target_surface_id must reference a scene component"
            )

        object.__setattr__(
            self,
            "components",
            components,
        )

    def component_for_id(
        self,
        component_id,
    ) -> AtlasSemanticReliefComponent:
        normalized_component_id = _normalize_identifier(
            component_id,
            field_name="component_id",
        )

        for component in self.components:
            if component.component_id == normalized_component_id:
                return component

        raise KeyError(
            f"unknown component_id: {normalized_component_id}"
        )

    def children_for_id(
        self,
        parent_component_id,
    ) -> tuple[AtlasSemanticReliefComponent, ...]:
        normalized_parent_id = _normalize_identifier(
            parent_component_id,
            field_name="parent_component_id",
        )
        self.component_for_id(
            normalized_parent_id
        )

        return tuple(
            component
            for component in self.components
            if component.parent_component_id == normalized_parent_id
        )

    def components_for_target_surface(
        self,
        target_surface_id,
    ) -> tuple[AtlasSemanticReliefComponent, ...]:
        normalized_target_id = _normalize_identifier(
            target_surface_id,
            field_name="target_surface_id",
        )
        self.component_for_id(
            normalized_target_id
        )

        return tuple(
            component
            for component in self.components
            if component.target_surface_id == normalized_target_id
        )

    def root_components(
        self,
    ) -> tuple[AtlasSemanticReliefComponent, ...]:
        return tuple(
            component
            for component in self.components
            if component.parent_component_id is None
        )
