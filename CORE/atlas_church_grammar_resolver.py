from __future__ import annotations

from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_master_landmark_catalog import (
    AtlasMasterLandmarkCatalog,
)


class AtlasChurchGrammarResolver:
    DEFAULT_GRAMMARS = {
        AtlasLandmarkType.CHURCH: "single_west_tower",
        AtlasLandmarkType.CATHEDRAL: "twin_west_towers",
    }

    @classmethod
    def resolve(
        cls,
        landmark,
        *,
        hierarchy_context=None,
    ) -> str:
        landmark_type = landmark.landmark_type

        if landmark_type not in cls.DEFAULT_GRAMMARS:
            raise ValueError(
                "landmark must be church or cathedral"
            )

        tags = getattr(
            landmark,
            "tags",
            {},
        ) or {}

        catalog_entry = (
            AtlasMasterLandmarkCatalog.resolve(
                wikidata_id=tags.get("wikidata"),
                osm_id=getattr(
                    landmark,
                    "id",
                    None,
                ),
            )
        )

        if (
            catalog_entry is not None
            and catalog_entry.landmark_family
            == "church"
            and catalog_entry.grammar_name
            is not None
        ):
            return catalog_entry.grammar_name

        bell_tower_count = (
            cls._resolve_bell_tower_count(
                landmark=landmark,
                hierarchy_context=(
                    hierarchy_context
                ),
            )
        )

        if bell_tower_count == 1:
            return "single_west_tower"

        if bell_tower_count == 2:
            return "twin_west_towers"

        return cls.DEFAULT_GRAMMARS[
            landmark_type
        ]

    @staticmethod
    def _resolve_bell_tower_count(
        *,
        landmark,
        hierarchy_context,
    ) -> int:
        if not hierarchy_context:
            return 0

        parents = hierarchy_context.get(
            "parents",
            {},
        ) or {}

        parent_data = parents.get(
            getattr(
                landmark,
                "id",
                None,
            )
        )

        if not parent_data:
            return 0

        parts = tuple(
            parent_data.get(
                "parts",
                (),
            )
            or ()
        )

        bell_tower_ids = {
            (
                part.get("id")
                if part.get("id") is not None
                else (
                    "anonymous",
                    index,
                )
            )
            for index, part in enumerate(parts)
            if (
                str(
                    (
                        part.get(
                            "tags",
                            {},
                        )
                        or {}
                    ).get(
                        "tower:type",
                        "",
                    )
                ).strip().lower()
                == "bell_tower"
            )
        }

        return len(
            bell_tower_ids
        )
