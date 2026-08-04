from __future__ import annotations

from CORE.atlas_landmark_type import AtlasLandmarkType


class AtlasWorshipGrammarResolver:
    DEFAULT_GRAMMAR = "footprint_fallback"

    VALID_GRAMMARS = {
        AtlasLandmarkType.MOSQUE: {
            "footprint_fallback",
            "single_dome_single_minaret",
            "multi_dome_multi_minaret",
        },
        AtlasLandmarkType.SYNAGOGUE: {
            "footprint_fallback",
            "basilica_hall",
            "twin_tower_facade",
        },
    }

    @classmethod
    def resolve(cls, landmark) -> str:
        landmark_type = landmark.landmark_type

        if landmark_type not in cls.VALID_GRAMMARS:
            raise ValueError(
                "landmark must be mosque or synagogue"
            )

        tags = getattr(
            landmark,
            "tags",
            {},
        ) or {}

        explicit_grammar = tags.get(
            "atlas:worship_grammar"
        )

        if explicit_grammar is None:
            return cls.DEFAULT_GRAMMAR

        grammar_name = str(
            explicit_grammar
        ).strip().lower()

        if not grammar_name:
            return cls.DEFAULT_GRAMMAR

        valid_grammars = cls.VALID_GRAMMARS[
            landmark_type
        ]

        if grammar_name not in valid_grammars:
            landmark_name = (
                "mosque"
                if landmark_type is AtlasLandmarkType.MOSQUE
                else "synagogue"
            )

            raise ValueError(
                f"worship grammar {grammar_name!r} "
                f"is not valid for {landmark_name}"
            )

        return grammar_name
