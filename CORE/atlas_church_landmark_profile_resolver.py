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

        has_apse = not (
            catalog_entry is not None
            and catalog_entry.landmark_family
            == "church"
            and "disable_synthetic_apse"
            in catalog_entry.geometry_overrides
        )

        return AtlasChurchLandmarkProfile(
            landmark_class=landmark_class,
            grammar_name=(
                AtlasChurchGrammarResolver.resolve(
                    landmark
                )
            ),
            tower_count=(
                2
                if landmark_class == "cathedral"
                else 1
            ),
            has_apse=has_apse,
            scale_ratio=scale_ratio,
            nozzle_diameter_mm=nozzle_diameter_mm,
        )
