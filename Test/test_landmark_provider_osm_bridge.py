from CORE.atlas_landmark_provider_osm import AtlasLandmarkProviderOsm
from CORE.atlas_landmark_type import AtlasLandmarkType


def test_osm_provider_classifies_bridge_landmark():
    osm = {
        "id": 301,
        "geometry": ((0.0, 0.0), (20.0, 0.0)),
        "tags": {
            "bridge": "yes",
            "man_made": "bridge",
        },
    }

    landmark = AtlasLandmarkProviderOsm.from_osm(osm)

    assert landmark.landmark_type is AtlasLandmarkType.BRIDGE
