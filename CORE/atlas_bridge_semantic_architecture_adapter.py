from __future__ import annotations

from CORE.atlas_bridge_builder import (
    AtlasBridgeGeometry,
)
from CORE.atlas_semantic_architecture_component import (
    AtlasSemanticArchitectureComponent,
)
from CORE.atlas_semantic_architecture_model import (
    AtlasSemanticArchitectureModel,
)


class AtlasBridgeSemanticArchitectureAdapter:
    @classmethod
    def adapt(
        cls,
        geometry,
    ) -> AtlasSemanticArchitectureModel:
        if not isinstance(
            geometry,
            AtlasBridgeGeometry,
        ):
            raise TypeError(
                "geometry must be AtlasBridgeGeometry"
            )

        metadata = geometry.metadata

        components = [
            AtlasSemanticArchitectureComponent(
                landmark_family="bridge",
                role="deck",
                geometry_kind="deck_volume",
            ),
        ]

        pier_positions = tuple(
            metadata.get(
                "bridge_pier_positions",
                (),
            )
        )

        for index, _ in enumerate(
            pier_positions
        ):
            components.append(
                AtlasSemanticArchitectureComponent(
                    landmark_family="bridge",
                    role="pier",
                    geometry_kind="support_prism",
                    parent_role="deck",
                    instance_index=index,
                )
            )

        flags = []

        if metadata.get(
            "bridge_approach_profile",
            False,
        ):
            flags.append(
                "approach_profile"
            )

        if metadata.get(
            "bridge_segmented_deck",
            False,
        ):
            flags.append(
                "segmented_deck"
            )

        if metadata.get(
            "bridge_full_span_convex",
            False,
        ):
            flags.append(
                "full_span_convex"
            )

        grammar_name = (
            "full_span_convex"
            if "full_span_convex" in flags
            else "flat_deck"
        )

        return AtlasSemanticArchitectureModel(
            landmark_family="bridge",
            grammar_name=grammar_name,
            components=tuple(
                components
            ),
            flags=tuple(
                flags
            ),
        )
