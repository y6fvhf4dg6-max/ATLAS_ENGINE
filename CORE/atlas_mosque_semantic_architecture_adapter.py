from __future__ import annotations

from CORE.atlas_mosque_landmark_builder import (
    AtlasMosqueLandmarkGeometry,
)
from CORE.atlas_semantic_architecture_component import (
    AtlasSemanticArchitectureComponent,
)
from CORE.atlas_semantic_architecture_model import (
    AtlasSemanticArchitectureModel,
)


class AtlasMosqueSemanticArchitectureAdapter:
    _GEOMETRY_KINDS = {
        "prayer_hall": "polygon_extrusion",
        "dome_drum": "drum_volume",
        "main_dome": "dome_surface",
        "minaret_body": "minaret_shaft",
        "minaret_balcony": "balcony_ring",
        "minaret_cap": "minaret_cap",
    }

    _PARENT_ROLES = {
        "prayer_hall": None,
        "dome_drum": "prayer_hall",
        "main_dome": "dome_drum",
        "minaret_body": "prayer_hall",
        "minaret_balcony": "minaret_body",
        "minaret_cap": "minaret_body",
    }

    @classmethod
    def adapt(
        cls,
        geometry,
    ) -> AtlasSemanticArchitectureModel:
        if not isinstance(
            geometry,
            AtlasMosqueLandmarkGeometry,
        ):
            raise TypeError(
                "geometry must be AtlasMosqueLandmarkGeometry"
            )

        components = tuple(
            AtlasSemanticArchitectureComponent(
                landmark_family="mosque",
                role=component.component_type,
                geometry_kind=(
                    cls._GEOMETRY_KINDS[
                        component.component_type
                    ]
                ),
                parent_role=(
                    cls._PARENT_ROLES[
                        component.component_type
                    ]
                ),
                instance_index=component.index,
            )
            for component in geometry.components
        )

        flags = ()

        if geometry.profile.uses_real_footprint:
            flags = (
                "uses_real_footprint",
            )

        return AtlasSemanticArchitectureModel(
            landmark_family="mosque",
            grammar_name=geometry.grammar_name,
            components=components,
            flags=flags,
        )
