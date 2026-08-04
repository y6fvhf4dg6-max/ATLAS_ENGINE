from __future__ import annotations

from CORE.atlas_semantic_architecture_component import (
    AtlasSemanticArchitectureComponent,
)
from CORE.atlas_semantic_architecture_model import (
    AtlasSemanticArchitectureModel,
)


class AtlasCastleSemanticArchitectureAdapter:
    _REQUIRED_KEYS = {
        "shell_castles",
        "independent_castle_walls",
        "relation_castle_walls",
        "inferred_perimeter_walls",
        "unknown_castles",
    }

    @classmethod
    def adapt(
        cls,
        classification,
    ) -> AtlasSemanticArchitectureModel:
        if not isinstance(
            classification,
            dict,
        ):
            raise TypeError(
                "classification must be a dict"
            )

        if not cls._REQUIRED_KEYS.issubset(
            classification
        ):
            raise TypeError(
                "classification must contain castle classifier keys"
            )

        shell_castles = tuple(
            classification[
                "shell_castles"
            ]
        )
        independent_walls = tuple(
            classification[
                "independent_castle_walls"
            ]
        )
        relation_walls = tuple(
            classification[
                "relation_castle_walls"
            ]
        )
        inferred_walls = tuple(
            classification[
                "inferred_perimeter_walls"
            ]
        )
        unknown_castles = tuple(
            classification[
                "unknown_castles"
            ]
        )

        inferred_ids = {
            wall.get("id")
            for wall in inferred_walls
        }

        components = []

        for index, _ in enumerate(
            shell_castles
        ):
            components.append(
                AtlasSemanticArchitectureComponent(
                    landmark_family="castle",
                    role="shell",
                    geometry_kind="courtyard_shell",
                    instance_index=index,
                )
            )

        for index, wall in enumerate(
            independent_walls
        ):
            flags = ()

            if wall.get("id") in inferred_ids:
                flags = (
                    "inferred",
                )

            components.append(
                AtlasSemanticArchitectureComponent(
                    landmark_family="castle",
                    role="perimeter_wall",
                    geometry_kind="fortification_wall",
                    instance_index=index,
                    flags=flags,
                )
            )

        for index, _ in enumerate(
            relation_walls
        ):
            components.append(
                AtlasSemanticArchitectureComponent(
                    landmark_family="castle",
                    role="relation_wall",
                    geometry_kind="fortification_wall",
                    parent_role="shell",
                    instance_index=index,
                )
            )

        for index, _ in enumerate(
            unknown_castles
        ):
            components.append(
                AtlasSemanticArchitectureComponent(
                    landmark_family="castle",
                    role="unknown_site",
                    geometry_kind="unresolved_footprint",
                    instance_index=index,
                    flags=(
                        "unresolved",
                    ),
                )
            )

        if not components:
            raise ValueError(
                "classification contains no castle components"
            )

        has_shell = bool(
            shell_castles
        )
        has_perimeter_walls = bool(
            independent_walls
        )

        if has_shell and has_perimeter_walls:
            grammar_name = (
                "mixed_castle_complex"
            )
        elif has_shell:
            grammar_name = (
                "shell_complex"
            )
        elif has_perimeter_walls:
            grammar_name = (
                "perimeter_fortification"
            )
        else:
            grammar_name = (
                "unresolved_castle_site"
            )

        return AtlasSemanticArchitectureModel(
            landmark_family="castle",
            grammar_name=grammar_name,
            components=tuple(
                components
            ),
        )
