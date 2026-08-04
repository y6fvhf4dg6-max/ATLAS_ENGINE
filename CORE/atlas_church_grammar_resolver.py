from __future__ import annotations

from CORE.atlas_landmark_type import AtlasLandmarkType


class AtlasChurchGrammarResolver:
    CATALOG_GRAMMARS = {
        "Q686664": "bonn_muenster_catalog",
        "Q1788329": "single_west_tower",
    }

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

        wikidata = str(
            tags.get("wikidata", "")
        ).strip()

        catalog_grammar = cls.CATALOG_GRAMMARS.get(
            wikidata
        )

        if catalog_grammar is not None:
            return catalog_grammar

        return cls.DEFAULT_GRAMMARS[
            landmark_type
        ]
