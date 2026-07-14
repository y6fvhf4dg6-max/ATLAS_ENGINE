"""
ATLAS Ancient Theatre Profiler v0.1

OSM verisindeki antik tiyatro yapılarını genel ve kimlikten bağımsız
olarak sınıflandırır.

Bu modül geometri üretmez.
Yalnızca yapının standart bina akışından ayrılması gerekip gerekmediğini
ve eşleşme nedenini belirler.
"""


class AtlasAncientTheatreProfiler:
    THEATRE_VALUES = {
        "theatre",
        "amphitheatre",
    }

    ANCIENT_CIVILIZATIONS = {
        "ancient_greek",
        "ancient_roman",
        "greek",
        "roman",
    }

    @staticmethod
    def profile(raw_building):
        tags = raw_building.get(
            "tags",
            {},
        )

        historic = AtlasAncientTheatreProfiler._normalize(
            tags.get("historic")
        )

        archaeological_site = AtlasAncientTheatreProfiler._normalize(
            tags.get("archaeological_site")
        )

        civilization = AtlasAncientTheatreProfiler._normalize(
            tags.get("historic:civilization")
        )

        ruins = AtlasAncientTheatreProfiler._is_yes(
            tags.get("ruins")
        )

        matched_by = []

        if historic in AtlasAncientTheatreProfiler.THEATRE_VALUES:
            matched_by.append("historic")

        if (
            archaeological_site
            in AtlasAncientTheatreProfiler.THEATRE_VALUES
        ):
            matched_by.append("archaeological_site")

        is_ancient_theatre = bool(matched_by)

        return {
            "is_ancient_theatre": is_ancient_theatre,
            "replace_standard_building_mesh": is_ancient_theatre,
            "matched_by": tuple(matched_by),
            "historic": historic or None,
            "archaeological_site": archaeological_site or None,
            "civilization": civilization or None,
            "is_ancient_civilization": (
                civilization
                in AtlasAncientTheatreProfiler.ANCIENT_CIVILIZATIONS
            ),
            "is_ruin": ruins,
            "preserve_component_heights": is_ancient_theatre,
        }

    @staticmethod
    def apply_to_building(
        atlas_building,
        raw_building,
    ):
        profile = AtlasAncientTheatreProfiler.profile(
            raw_building
        )

        atlas_building.is_ancient_theatre = profile[
            "is_ancient_theatre"
        ]

        atlas_building.ancient_theatre_profile = profile

        if atlas_building.is_ancient_theatre:
            atlas_building.tags[
                "atlas:ancient_theatre"
            ] = "yes"

            atlas_building.tags[
                "atlas:replace_standard_building_mesh"
            ] = "yes"

        return atlas_building

    @staticmethod
    def _normalize(value):
        if value is None:
            return ""

        return str(value).strip().lower()

    @staticmethod
    def _is_yes(value):
        return AtlasAncientTheatreProfiler._normalize(
            value
        ) in {
            "yes",
            "true",
            "1",
        }
