from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_type import AtlasLandmarkType


class AtlasTowerSampler:
    @staticmethod
    def sample(ways):
        landmarks = []

        for way in ways:
            if way.tags.get("man_made") != "tower":
                continue

            landmarks.append(
                AtlasLandmark(
                    id=way.id,
                    landmark_type=AtlasLandmarkType.TOWER,
                    geometry=way.geometry,
                    tags=dict(way.tags),
                    source="OSM",
                )
            )

        return landmarks
