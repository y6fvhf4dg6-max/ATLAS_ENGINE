from __future__ import annotations

from CORE.atlas_church_grammar_resolver import (
    AtlasChurchGrammarResolver,
)
from CORE.atlas_church_landmark_profile import (
    AtlasChurchLandmarkProfile,
)
from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_master_landmark_catalog import (
    AtlasMasterLandmarkCatalog,
)


class AtlasChurchLandmarkProfileResolver:
    @classmethod
    def resolve(
        cls,
        landmark,
        *,
        hierarchy_context=None,
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    ) -> AtlasChurchLandmarkProfile:
        landmark_type = landmark.landmark_type

        if landmark_type not in {
            AtlasLandmarkType.CHURCH,
            AtlasLandmarkType.CATHEDRAL,
        }:
            raise ValueError(
                "landmark must be church or cathedral"
            )

        landmark_class = (
            "cathedral"
            if landmark_type is AtlasLandmarkType.CATHEDRAL
            else "church"
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

        church_catalog_entry = (
            catalog_entry
            if (
                catalog_entry is not None
                and catalog_entry.landmark_family
                == "church"
            )
            else None
        )

        has_apse = not (
            church_catalog_entry is not None
            and "disable_synthetic_apse"
            in church_catalog_entry.geometry_overrides
        )

        profile_name = (
            church_catalog_entry.profile_name
            if (
                church_catalog_entry is not None
                and church_catalog_entry.profile_name
                is not None
            )
            else "generic_church"
        )

        grammar_name = (
            AtlasChurchGrammarResolver.resolve(
                landmark,
                hierarchy_context=(
                    hierarchy_context
                ),
            )
        )

        if grammar_name == "single_west_tower":
            tower_count = 1
        elif grammar_name == "twin_west_towers":
            tower_count = 2
        else:
            tower_count = (
                2
                if landmark_class == "cathedral"
                else 1
            )

        return AtlasChurchLandmarkProfile(
            landmark_class=landmark_class,
            grammar_name=grammar_name,
            profile_name=profile_name,
            tower_count=tower_count,
            has_apse=has_apse,
            scale_ratio=scale_ratio,
            nozzle_diameter_mm=nozzle_diameter_mm,
        )
