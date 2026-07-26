from CORE.atlas_landmark_provider_osm import AtlasLandmarkProviderOsm
from CORE.atlas_landmark_type import AtlasLandmarkType


def test_osm_provider_classifies_man_made_tower():
    osm = {
        "id": 23236783,
        "geometry": (
            (41.02561, 28.97413),
            (41.02562, 28.97418),
            (41.02558, 28.97421),
        ),
        "tags": {
            "building": "yes",
            "historic": "tower",
            "man_made": "tower",
            "tower:type": "observation;museum_and_observation",
        },
    }

    landmark = AtlasLandmarkProviderOsm.from_osm(osm)

    assert landmark.landmark_type is AtlasLandmarkType.TOWER
