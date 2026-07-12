"""
ATLAS Castle Building Profiler v0.1

Kale sınırı içinde bulunan binaları sınıflandırır ve OSM yükseklik
verisi eksik olduğunda baskıya uygun genel yükseklik profili üretir.

Bu modül belirli bir kaleye bağlı değildir.
"""

import unicodedata

from shapely.geometry import Point
from shapely.geometry import Polygon


class AtlasCastleBuildingProfiler:
    PROFILE_HEIGHTS_M = {
        "main_tower": 28.0,
        "defensive_tower": 22.0,
        "gate_tower": 20.0,
        "chapel": 16.0,
        "castle_wing": 12.0,
        "service_building": 6.0,
        "unknown_castle_building": 8.0,
    }

    MAIN_TOWER_WORDS = (
        "kaiserturm",
        "hauptturm",
        "main tower",
        "keep",
        "donjon",
        "bergfried",
        "ana kule",
    )

    TOWER_WORDS = (
        "turm",
        "tower",
        "kule",
        "bastion",
        "burc",
        "burç",
    )

    GATE_WORDS = (
        "torturm",
        "gate tower",
        "gatehouse",
        "torhaus",
        "kapı kulesi",
        "kapi kulesi",
    )

    CHAPEL_WORDS = (
        "kapelle",
        "chapel",
        "kirche",
        "church",
        "basilica",
        "mosque",
        "cami",
        "şapel",
        "sapel",
        "kilise",
    )

    SERVICE_BUILDING_TYPES = {
        "kiosk",
        "shed",
        "garage",
        "service",
        "toilets",
    }

    RELIGIOUS_BUILDING_TYPES = {
        "chapel",
        "church",
        "cathedral",
        "mosque",
        "synagogue",
        "temple",
    }

    @staticmethod
    def profile(
        raw_building,
        castles,
    ):
        tags = raw_building.get(
            "tags",
            {},
        )

        inside_castle = AtlasCastleBuildingProfiler._is_inside_any_castle(
            raw_building=raw_building,
            castles=castles,
        )

        if not inside_castle:
            return {
                "inside_castle": False,
                "profile": None,
                "fallback_height_m": None,
                "roof_profile": None,
            }

        profile_name = AtlasCastleBuildingProfiler._classify(raw_building)

        fallback_height_m = AtlasCastleBuildingProfiler.PROFILE_HEIGHTS_M[profile_name]

        roof_profile = AtlasCastleBuildingProfiler._roof_profile(
            profile_name=profile_name,
            raw_building=raw_building,
        )

        return {
            "inside_castle": True,
            "profile": profile_name,
            "fallback_height_m": fallback_height_m,
            "roof_profile": roof_profile,
            "name": tags.get("name"),
        }

    @staticmethod
    def apply_to_building(
        atlas_building,
        raw_building,
        castles,
    ):
        profile = AtlasCastleBuildingProfiler.profile(
            raw_building=raw_building,
            castles=castles,
        )

        atlas_building.castle_profile = profile.get("profile")

        atlas_building.castle_roof_profile = profile.get("roof_profile")

        atlas_building.is_castle_building = profile.get(
            "inside_castle",
            False,
        )

        if not atlas_building.is_castle_building:
            return atlas_building

        # Gerçek height veya building:levels varsa
        # AtlasHeightEngine tarafından hesaplanan değer korunur.
        if atlas_building.height is None and atlas_building.levels is None:
            atlas_building.estimated_height = profile["fallback_height_m"]

        atlas_building.tags["atlas:castle_profile"] = profile["profile"]

        atlas_building.tags["atlas:roof_profile"] = profile["roof_profile"]

        return atlas_building

    @staticmethod
    def _classify(
        raw_building,
    ):
        tags = raw_building.get(
            "tags",
            {},
        )

        name = AtlasCastleBuildingProfiler._normalize_text(
            tags.get(
                "name",
                "",
            )
        )

        building_type = AtlasCastleBuildingProfiler._normalize_text(
            tags.get(
                "building",
                "",
            )
        )

        man_made = AtlasCastleBuildingProfiler._normalize_text(
            tags.get(
                "man_made",
                "",
            )
        )

        tower_type = AtlasCastleBuildingProfiler._normalize_text(
            tags.get(
                "tower:type",
                "",
            )
        )

        if AtlasCastleBuildingProfiler._contains_any(
            name,
            AtlasCastleBuildingProfiler.MAIN_TOWER_WORDS,
        ):
            return "main_tower"

        if AtlasCastleBuildingProfiler._contains_any(
            name,
            AtlasCastleBuildingProfiler.GATE_WORDS,
        ):
            return "gate_tower"

        if (
            man_made == "tower"
            or tower_type == "defensive"
            or AtlasCastleBuildingProfiler._contains_any(
                name,
                AtlasCastleBuildingProfiler.TOWER_WORDS,
            )
        ):
            return "defensive_tower"

        if (
            building_type in AtlasCastleBuildingProfiler.RELIGIOUS_BUILDING_TYPES
            or AtlasCastleBuildingProfiler._contains_any(
                name,
                AtlasCastleBuildingProfiler.CHAPEL_WORDS,
            )
        ):
            return "chapel"

        if building_type in AtlasCastleBuildingProfiler.SERVICE_BUILDING_TYPES:
            return "service_building"

        area_m2 = AtlasCastleBuildingProfiler._building_area_m2(raw_building)

        if area_m2 >= 80.0:
            return "castle_wing"

        return "unknown_castle_building"

    @staticmethod
    def _roof_profile(
        profile_name,
        raw_building,
    ):
        tags = raw_building.get(
            "tags",
            {},
        )

        explicit_roof = tags.get("roof:shape")

        if explicit_roof:
            return explicit_roof

        if profile_name in (
            "main_tower",
            "defensive_tower",
            "gate_tower",
        ):
            return "tower_spire"

        if profile_name == "chapel":
            return "chapel_roof"

        if profile_name == "castle_wing":
            return "pitched"

        return "flat"

    @staticmethod
    def _is_inside_any_castle(
        raw_building,
        castles,
    ):
        geometry = raw_building.get(
            "geometry",
            [],
        )

        if len(geometry) < 3:
            return False

        building_polygon = AtlasCastleBuildingProfiler._polygon_from_geometry(geometry)

        if building_polygon is None:
            return False

        representative_point = building_polygon.representative_point()

        for castle in castles:
            outer_geometries = castle.get(
                "outer_geometries",
                [],
            )

            if not outer_geometries:
                geometry = castle.get(
                    "geometry",
                    [],
                )

                if geometry:
                    outer_geometries = [geometry]

            for outer_geometry in outer_geometries:
                castle_polygon = AtlasCastleBuildingProfiler._polygon_from_geometry(
                    outer_geometry
                )

                if castle_polygon is None:
                    continue

                if castle_polygon.covers(representative_point):
                    return True

        return False

    @staticmethod
    def _polygon_from_geometry(
        geometry,
    ):
        if len(geometry) < 3:
            return None

        coordinates = [
            (
                float(lon),
                float(lat),
            )
            for lat, lon in geometry
        ]

        polygon = Polygon(coordinates)

        if polygon.is_empty:
            return None

        if not polygon.is_valid:
            polygon = polygon.buffer(0)

        if polygon.is_empty or not polygon.is_valid:
            return None

        return polygon

    @staticmethod
    def _building_area_m2(
        raw_building,
    ):
        geometry = raw_building.get(
            "geometry",
            [],
        )

        polygon = AtlasCastleBuildingProfiler._polygon_from_geometry(geometry)

        if polygon is None:
            return 0.0

        # Bu değer yalnız büyük/küçük footprint ayrımı
        # için yaklaşık karşılaştırmada kullanılır.
        return polygon.area * 8_000_000_000.0

    @staticmethod
    def _normalize_text(
        value,
    ):
        text = str(value or "").lower()

        normalized = unicodedata.normalize(
            "NFKD",
            text,
        )

        return "".join(
            character
            for character in normalized
            if not unicodedata.combining(character)
        )

    @staticmethod
    def _contains_any(
        text,
        words,
    ):
        return any(
            AtlasCastleBuildingProfiler._normalize_text(word) in text for word in words
        )
