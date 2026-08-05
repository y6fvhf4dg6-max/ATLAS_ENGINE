from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AtlasMasterLandmarkCatalogEntry:
    key: str
    landmark_family: str
    wikidata_id: str | None = None
    osm_ids: tuple[int, ...] = ()
    grammar_name: str | None = None
    profile_name: str | None = None
    component_flags: tuple[str, ...] = ()
    geometry_overrides: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        key = str(self.key).strip().lower()
        landmark_family = str(
            self.landmark_family
        ).strip().lower()

        if not key:
            raise ValueError(
                "key must not be blank"
            )

        if not landmark_family:
            raise ValueError(
                "landmark_family must not be blank"
            )

        wikidata_id = self.wikidata_id

        if wikidata_id is not None:
            wikidata_id = str(
                wikidata_id
            ).strip().upper()

            if not wikidata_id:
                wikidata_id = None

        osm_ids = tuple(
            int(osm_id)
            for osm_id in self.osm_ids
        )

        grammar_name = self.grammar_name

        if grammar_name is not None:
            grammar_name = str(
                grammar_name
            ).strip().lower()

            if not grammar_name:
                grammar_name = None

        profile_name = self.profile_name

        if profile_name is not None:
            profile_name = str(
                profile_name
            ).strip().lower()

            if not profile_name:
                profile_name = None

        component_flags = tuple(
            str(flag).strip().lower()
            for flag in self.component_flags
            if str(flag).strip()
        )

        geometry_overrides = tuple(
            str(override).strip().lower()
            for override in self.geometry_overrides
            if str(override).strip()
        )

        object.__setattr__(
            self,
            "key",
            key,
        )
        object.__setattr__(
            self,
            "landmark_family",
            landmark_family,
        )
        object.__setattr__(
            self,
            "wikidata_id",
            wikidata_id,
        )
        object.__setattr__(
            self,
            "osm_ids",
            osm_ids,
        )
        object.__setattr__(
            self,
            "grammar_name",
            grammar_name,
        )
        object.__setattr__(
            self,
            "profile_name",
            profile_name,
        )
        object.__setattr__(
            self,
            "component_flags",
            component_flags,
        )
        object.__setattr__(
            self,
            "geometry_overrides",
            geometry_overrides,
        )


class AtlasMasterLandmarkCatalog:
    _ENTRIES = (
        AtlasMasterLandmarkCatalogEntry(
            key="bonn-muenster",
            landmark_family="church",
            wikidata_id="Q686664",
            osm_ids=(112526702,),
            grammar_name="bonn_muenster_catalog",
            profile_name="romanesque_cathedral",
            geometry_overrides=(
                "disable_synthetic_apse",
            ),
        ),
        AtlasMasterLandmarkCatalogEntry(
            key="kreuzkirche-bonn",
            landmark_family="church",
            wikidata_id="Q1788329",
            grammar_name="single_west_tower",
        ),
        AtlasMasterLandmarkCatalogEntry(
            key="cenabi-ahmet-pasha-mosque",
            landmark_family="mosque",
            wikidata_id="Q96278624",
            osm_ids=(322722702,),
            grammar_name="single_dome_single_minaret",
        ),
        AtlasMasterLandmarkCatalogEntry(
            key="kilic-ali-pasha-mosque",
            landmark_family="mosque",
            wikidata_id="Q862848",
            osm_ids=(165574748,),
            grammar_name="single_dome_single_minaret",
        ),
        AtlasMasterLandmarkCatalogEntry(
            key="galata-tower",
            landmark_family="tower",
            wikidata_id="Q91274",
            profile_name="galata",
        ),
        AtlasMasterLandmarkCatalogEntry(
            key="galata-bridge",
            landmark_family="bridge",
            wikidata_id="Q81523",
            profile_name="galata",
            component_flags=(
                "supports",
                "parapets",
            ),
        ),
    )

    @classmethod
    def entries(
        cls,
    ) -> tuple[AtlasMasterLandmarkCatalogEntry, ...]:
        return cls._ENTRIES

    @classmethod
    def resolve(
        cls,
        *,
        wikidata_id=None,
        osm_id=None,
    ) -> AtlasMasterLandmarkCatalogEntry | None:
        normalized_wikidata = cls._normalize_wikidata(
            wikidata_id
        )

        if normalized_wikidata is not None:
            for entry in cls._ENTRIES:
                if (
                    entry.wikidata_id
                    == normalized_wikidata
                ):
                    return entry

        normalized_osm_id = cls._normalize_osm_id(
            osm_id
        )

        if normalized_osm_id is not None:
            for entry in cls._ENTRIES:
                if normalized_osm_id in entry.osm_ids:
                    return entry

        return None

    @staticmethod
    def _normalize_wikidata(
        value,
    ) -> str | None:
        if value is None:
            return None

        normalized = str(
            value
        ).strip().upper()

        if not normalized:
            return None

        return normalized

    @staticmethod
    def _normalize_osm_id(
        value,
    ) -> int | None:
        if value is None or isinstance(value, bool):
            return None

        try:
            normalized = int(value)
        except (TypeError, ValueError):
            return None

        if normalized <= 0:
            return None

        return normalized
