from __future__ import annotations

from CORE.atlas_church_landmark_builder import (
    AtlasChurchLandmarkGeometry,
)
from CORE.atlas_semantic_architecture_component import (
    AtlasSemanticArchitectureComponent,
)
from CORE.atlas_semantic_architecture_model import (
    AtlasSemanticArchitectureModel,
)


class AtlasChurchSemanticArchitectureAdapter:
    _GEOMETRY_KINDS = {
        "nave": "polygon_extrusion",
        "transept": "polygon_extrusion",
        "apse": "radial_extrusion",
        "tower": "tower_volume",
        "buttress_system": "linear_detail_system",
        "window_bay_system": "surface_detail_system",
        "roof_section": "roof_volume",
    }

    @classmethod
    def adapt(
        cls,
        geometry,
    ) -> AtlasSemanticArchitectureModel:
        if not isinstance(
            geometry,
            AtlasChurchLandmarkGeometry,
        ):
            raise TypeError(
                "geometry must be AtlasChurchLandmarkGeometry"
            )

        components = tuple(
            cls._adapt_component(
                component
            )
            for component in geometry.components
        )

        return AtlasSemanticArchitectureModel(
            landmark_family="church",
            grammar_name=geometry.profile.grammar_name,
            components=components,
            profile_name=geometry.profile.profile_name,
            flags=(
                f"class_{geometry.landmark_class}",
            ),
        )

    @classmethod
    def _adapt_component(
        cls,
        component,
    ) -> AtlasSemanticArchitectureComponent:
        role = component.component_type

        flags = []

        if component.section_name is not None:
            flags.append(
                f"section_{component.section_name}"
            )

        if component.physical_action is not None:
            flags.append(
                f"physical_{component.physical_action}"
            )

        parent_role = None

        if role == "tower":
            parent_role = "nave"
        elif role == "roof_section":
            parent_role = component.section_name

        return AtlasSemanticArchitectureComponent(
            landmark_family="church",
            role=role,
            geometry_kind=cls._GEOMETRY_KINDS[role],
            parent_role=parent_role,
            instance_index=component.index,
            flags=tuple(flags),
        )
