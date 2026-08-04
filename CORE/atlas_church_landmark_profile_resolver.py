from __future__ import annotations

from CORE.atlas_church_landmark_profile import (
    AtlasChurchLandmarkProfile,
)
from CORE.atlas_landmark_type import AtlasLandmarkType


class AtlasChurchLandmarkProfileResolver:
    BONNER_MUENSTER_OSM_ID = 112526702

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

        landmark_id = int(landmark.id)

        has_apse = (
            landmark_id
            != cls.BONNER_MUENSTER_OSM_ID
        )

        return AtlasChurchLandmarkProfile(
            landmark_class=landmark_class,
            tower_count=(
                2
                if landmark_class == "cathedral"
                else 1
            ),
            has_apse=has_apse,
            scale_ratio=scale_ratio,
            nozzle_diameter_mm=nozzle_diameter_mm,
        )
