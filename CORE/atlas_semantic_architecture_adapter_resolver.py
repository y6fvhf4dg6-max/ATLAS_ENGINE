from __future__ import annotations

from CORE.atlas_bridge_builder import (
    AtlasBridgeGeometry,
)
from CORE.atlas_bridge_semantic_architecture_adapter import (
    AtlasBridgeSemanticArchitectureAdapter,
)
from CORE.atlas_castle_semantic_architecture_adapter import (
    AtlasCastleSemanticArchitectureAdapter,
)
from CORE.atlas_church_landmark_builder import (
    AtlasChurchLandmarkGeometry,
)
from CORE.atlas_church_semantic_architecture_adapter import (
    AtlasChurchSemanticArchitectureAdapter,
)
from CORE.atlas_mosque_landmark_builder import (
    AtlasMosqueLandmarkGeometry,
)
from CORE.atlas_mosque_semantic_architecture_adapter import (
    AtlasMosqueSemanticArchitectureAdapter,
)
from CORE.atlas_semantic_architecture_model import (
    AtlasSemanticArchitectureModel,
)


class AtlasSemanticArchitectureAdapterResolver:
    _CASTLE_CLASSIFICATION_KEYS = {
        "shell_castles",
        "independent_castle_walls",
        "relation_castle_walls",
        "inferred_perimeter_walls",
        "unknown_castles",
    }

    @classmethod
    def resolve(
        cls,
        source,
    ) -> AtlasSemanticArchitectureModel:
        if isinstance(
            source,
            AtlasChurchLandmarkGeometry,
        ):
            return (
                AtlasChurchSemanticArchitectureAdapter
                .adapt(source)
            )

        if isinstance(
            source,
            AtlasMosqueLandmarkGeometry,
        ):
            return (
                AtlasMosqueSemanticArchitectureAdapter
                .adapt(source)
            )

        if isinstance(
            source,
            AtlasBridgeGeometry,
        ):
            return (
                AtlasBridgeSemanticArchitectureAdapter
                .adapt(source)
            )

        if (
            isinstance(source, dict)
            and cls._CASTLE_CLASSIFICATION_KEYS
            .issubset(source)
        ):
            return (
                AtlasCastleSemanticArchitectureAdapter
                .adapt(source)
            )

        raise TypeError(
            "unsupported semantic architecture source"
        )
