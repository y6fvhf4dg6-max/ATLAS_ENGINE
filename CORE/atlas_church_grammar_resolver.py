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
    def resolve(cls, landmark) -> str:
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

        return cls.DEFAULT_GRAMMARS[
            landmark_type
        ]
