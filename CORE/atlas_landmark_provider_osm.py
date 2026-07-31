from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_provider import AtlasLandmarkProvider
from CORE.atlas_landmark_type import AtlasLandmarkType


class AtlasLandmarkProviderOsm(AtlasLandmarkProvider):
    @classmethod
    def from_source(cls, source):
        return cls.from_osm(source)

    @classmethod
    def from_osm(cls, osm):
        tags = dict(osm.get("tags", {}))

        if tags.get("bridge") == "yes" or tags.get("man_made") == "bridge":
            landmark_type = AtlasLandmarkType.BRIDGE
        elif (
            tags.get("man_made") == "tower"
            or tags.get("historic") == "tower"
        ):
            landmark_type = AtlasLandmarkType.TOWER
        elif tags.get("historic") == "memorial":
            landmark_type = AtlasLandmarkType.MEMORIAL
        elif (
            tags.get("historic") == "tomb"
            and tags.get("tomb") == "rock-cut"
        ):
            landmark_type = AtlasLandmarkType.ROCK_CUT_TOMB
        elif tags.get("building") == "cathedral":
            landmark_type = AtlasLandmarkType.CATHEDRAL
        elif tags.get("building") == "church":
            landmark_type = AtlasLandmarkType.CHURCH
        else:
            landmark_type = AtlasLandmarkType.UNKNOWN

        return AtlasLandmark(
            id=osm["id"],
            landmark_type=landmark_type,
            geometry=tuple(osm.get("geometry", ())),
            tags=tags,
            source="OSM",
        )
