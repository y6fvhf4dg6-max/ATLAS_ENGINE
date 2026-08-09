from __future__ import annotations

from CORE.atlas_city_composition_lod_resolver import (
    AtlasCityCompositionLoDResolver,
)
from CORE.atlas_urban_fabric_scene_contract import (
    AtlasUrbanFabricElement,
    AtlasUrbanFabricScene,
)


class AtlasCityCompositionSceneAdapter:
    @staticmethod
    def _element(
        *,
        prefix,
        source,
        semantic_class,
    ):
        source_id = source.get("id")

        if source_id is None:
            raise ValueError(
                "city composition source requires id"
            )

        return AtlasUrbanFabricElement(
            element_id=(
                f"{prefix}_{source_id}"
            ),
            semantic_class=semantic_class,
            source_id=source_id,
            source_type=prefix,
            product_priority=(
                AtlasCityCompositionLoDResolver
                .resolve_semantic_narrative_priority(
                    semantic_class
                )
            ),
            lod_eligible=True,
        )

    @staticmethod
    def _road_semantic_class(source):
        tags = source.get("tags", {}) or {}

        highway = str(
            source.get("road_type")
            or tags.get("highway")
            or ""
        ).strip().lower()

        if highway in {
            "motorway",
            "trunk",
            "primary",
            "secondary",
            "tertiary",
        }:
            return "major_road"

        if highway == "service":
            return "service_road"

        if highway in {
            "footway",
            "path",
            "pedestrian",
            "steps",
        }:
            return "pedestrian_path"

        return "local_road"

    @classmethod
    def build_scene(
        cls,
        *,
        landmarks=(),
        roads=(),
        buildings=(),
        parks=(),
        waters=(),
        linear_infrastructure=(),
    ):
        elements = []

        for source in landmarks or ():
            elements.append(
                cls._element(
                    prefix="landmark",
                    source=source,
                    semantic_class="landmark",
                )
            )

        for source in roads or ():
            elements.append(
                cls._element(
                    prefix="road",
                    source=source,
                    semantic_class=(
                        cls._road_semantic_class(
                            source
                        )
                    ),
                )
            )

        for source in buildings or ():
            elements.append(
                cls._element(
                    prefix="building",
                    source=source,
                    semantic_class=(
                        "generic_building"
                    ),
                )
            )

        for source in parks or ():
            elements.append(
                cls._element(
                    prefix="park",
                    source=source,
                    semantic_class="park",
                )
            )

        for source in waters or ():
            elements.append(
                cls._element(
                    prefix="water",
                    source=source,
                    semantic_class="water",
                )
            )

        for source in linear_infrastructure or ():
            semantic_class = str(
                source.get(
                    "semantic_class",
                    "infrastructure_corridor",
                )
            ).strip().lower()

            if not semantic_class:
                semantic_class = (
                    "infrastructure_corridor"
                )

            elements.append(
                cls._element(
                    prefix="infrastructure",
                    source=source,
                    semantic_class=semantic_class,
                )
            )

        return AtlasUrbanFabricScene(
            elements=tuple(elements),
        )
