from CORE.atlas_landmark_provider_osm import AtlasLandmarkProviderOsm
from CORE.atlas_landmark_type import AtlasLandmarkType


def test_memorial_conversion():
    osm = {
        "id": 10,
        "geometry": (
            (39.0, 32.0),
            (39.0, 32.1),
        ),
        "tags": {
            "historic": "memorial",
            "name": "Anıt",
        },
    }

    landmark = AtlasLandmarkProviderOsm.from_osm(osm)

    assert landmark.id == 10
    assert landmark.landmark_type is AtlasLandmarkType.MEMORIAL
    assert landmark.geometry == osm["geometry"]
    assert landmark.tags == osm["tags"]
    assert landmark.source == "OSM"


def test_unknown_conversion():
    osm = {
        "id": 20,
        "geometry": (),
        "tags": {},
    }

    landmark = AtlasLandmarkProviderOsm.from_osm(osm)

    assert landmark.landmark_type is AtlasLandmarkType.UNKNOWN
