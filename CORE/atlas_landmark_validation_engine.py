from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_master_landmark_catalog import (
    AtlasMasterLandmarkCatalog,
)
from CORE.atlas_place_of_worship_profile_resolver import (
    AtlasPlaceOfWorshipProfileResolver,
)


@dataclass(frozen=True, slots=True)
class AtlasLandmarkValidationResult:
    family: str
    confidence: str
    action: str
    evidence: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    catalog_key: str | None = None
    grammar_name: str | None = None

    @property
    def has_conflict(self) -> bool:
        return bool(self.conflicts)


class AtlasLandmarkValidationEngine:
    _EXPLICIT_RELIGIONS = {
        "church": "christian",
        "cathedral": "christian",
        "mosque": "muslim",
        "synagogue": "jewish",
    }

    @classmethod
    def validate(
        cls,
        source,
    ) -> AtlasLandmarkValidationResult:
        source = source or {}
        tags = dict(
            source.get("tags", {}) or {}
        )

        geometry = tuple(
            source.get("geometry", ()) or ()
        )

        building = str(
            tags.get("building", "")
        ).strip().lower()

        religion = str(
            tags.get("religion", "")
        ).strip().lower()

        catalog_entry = (
            AtlasMasterLandmarkCatalog.resolve(
                wikidata_id=tags.get("wikidata"),
                osm_id=source.get("id"),
            )
        )

        conflicts = []

        expected_religion = (
            cls._EXPLICIT_RELIGIONS.get(
                building
            )
        )

        if (
            expected_religion is not None
            and religion
            and religion != expected_religion
        ):
            conflicts.append(
                "building_religion_conflict"
            )

        if catalog_entry is not None:
            family = (
                catalog_entry.landmark_family
            )

            evidence = [
                "catalog_identity",
            ]

            if tags.get("wikidata"):
                evidence.append(
                    "wikidata_identity"
                )

            if len(geometry) < 3:
                conflicts.append(
                    "missing_footprint"
                )

            grammar_name = getattr(
                catalog_entry,
                "grammar_name",
                None,
            )
            profile_name = getattr(
                catalog_entry,
                "profile_name",
                None,
            )
            catalog_key = getattr(
                catalog_entry,
                "key",
                None,
            )

            if "missing_footprint" in conflicts:
                confidence = "low"
                action = "review"
            else:
                confidence = "high"
                action = (
                    "special"
                    if (
                        grammar_name is not None
                        or profile_name is not None
                    )
                    else "fallback"
                )

            return AtlasLandmarkValidationResult(
                family=family,
                confidence=confidence,
                action=action,
                evidence=tuple(evidence),
                conflicts=tuple(conflicts),
                catalog_key=catalog_key,
                grammar_name=grammar_name,
            )

        worship_profile = (
            AtlasPlaceOfWorshipProfileResolver.resolve(
                tags
            )
        )

        if conflicts:
            return AtlasLandmarkValidationResult(
                family="unknown",
                confidence="low",
                action="review",
                evidence=(
                    "osm_tags",
                ),
                conflicts=tuple(conflicts),
            )

        if worship_profile in {
            "church",
            "cathedral",
            "mosque",
            "synagogue",
        }:
            inferred = (
                building == "yes"
            )

            evidence = (
                ("religion_inference",)
                if inferred
                else ("explicit_building",)
            )

            if len(geometry) < 3:
                return AtlasLandmarkValidationResult(
                    family=worship_profile,
                    confidence="low",
                    action="review",
                    evidence=evidence,
                    conflicts=(
                        "missing_footprint",
                    ),
                )

            return AtlasLandmarkValidationResult(
                family=worship_profile,
                confidence=(
                    "medium"
                    if inferred
                    else "high"
                ),
                action="fallback",
                evidence=evidence,
            )

        if (
            worship_profile
            == "generic_place_of_worship"
        ):
            return AtlasLandmarkValidationResult(
                family="unknown",
                confidence="low",
                action="review",
                evidence=(
                    "generic_place_of_worship",
                ),
            )

        return AtlasLandmarkValidationResult(
            family="unknown",
            confidence="low",
            action="reject",
        )
