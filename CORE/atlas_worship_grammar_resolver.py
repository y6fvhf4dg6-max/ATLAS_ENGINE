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
    def resolve(
        cls,
        landmark,
        *,
        hierarchy_context=None,
    ) -> str:
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
            if (
                landmark_type
                is AtlasLandmarkType.MOSQUE
            ):
                inferred_grammar = (
                    cls._infer_mosque_grammar(
                        landmark=landmark,
                        hierarchy_context=(
                            hierarchy_context
                        ),
                    )
                )

                if inferred_grammar is not None:
                    return inferred_grammar

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

    @staticmethod
    def _infer_mosque_grammar(
        *,
        landmark,
        hierarchy_context,
    ):
        if not hierarchy_context:
            return None

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
            return None

        parts = tuple(
            parent_data.get(
                "parts",
                (),
            )
            or ()
        )

        minaret_ids = {
            part.get("id")
            for part in parts
            if (
                (
                    part.get(
                        "tags",
                        {},
                    )
                    or {}
                ).get("tower:type")
                == "minaret"
            )
        }

        dome_ids = {
            part.get("id")
            for part in parts
            if (
                str(
                    (
                        part.get(
                            "tags",
                            {},
                        )
                        or {}
                    ).get(
                        "roof:shape",
                        "",
                    )
                ).strip().lower()
                == "dome"
            )
        }

        minaret_count = len(
            minaret_ids
        )
        dome_count = len(
            dome_ids
        )

        if minaret_count >= 2:
            if dome_count >= 2:
                return (
                    "multi_dome_multi_minaret"
                )

            return (
                AtlasWorshipGrammarResolver
                .DEFAULT_GRAMMAR
            )

        if minaret_count == 1:
            return (
                "single_dome_single_minaret"
            )

        return None
