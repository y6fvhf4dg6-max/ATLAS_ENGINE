from dataclasses import dataclass

from CORE.atlas_landmark_height_resolver import (
    AtlasLandmarkHeightResolver,
)


@dataclass(frozen=True)
class AtlasClockTowerGeometry:
    footprint: tuple
    height_m: float


class AtlasClockTowerBuilder:
    DEFAULT_HEIGHT_M = 40.0

    @staticmethod
    def build(landmark):
        height = AtlasLandmarkHeightResolver.resolve(
            getattr(landmark, "tags", {}),
            default_height_m=AtlasClockTowerBuilder.DEFAULT_HEIGHT_M,
            floor_height_m=AtlasClockTowerBuilder.FLOOR_HEIGHT_M,
        )

        return AtlasClockTowerGeometry(
            footprint=tuple(landmark.geometry),
            height_m=height,
        )

# AUTO-PATCH
if not hasattr(AtlasClockTowerBuilder, "FLOOR_HEIGHT_M"):
    AtlasClockTowerBuilder.FLOOR_HEIGHT_M = 3.0
