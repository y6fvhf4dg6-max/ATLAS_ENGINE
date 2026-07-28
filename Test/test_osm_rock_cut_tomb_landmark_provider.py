from CORE.atlas_landmark_provider_osm import AtlasLandmarkProviderOsm
from CORE.atlas_landmark_type import AtlasLandmarkType


def test_osm_rock_cut_tomb_maps_to_rock_cut_tomb_landmark_type():
    source = {
        "id": 5825276872,
        "geometry": (),
        "tags": {
            "historic": "tomb",
            "tomb": "rock-cut",
            "tourism": "attraction",
        },
    }

    landmark = AtlasLandmarkProviderOsm.from_source(source)

    assert landmark.landmark_type is AtlasLandmarkType.ROCK_CUT_TOMB
