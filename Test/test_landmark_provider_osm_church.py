from CORE.atlas_landmark_provider_osm import (
    AtlasLandmarkProviderOsm,
)
from CORE.atlas_landmark_type import AtlasLandmarkType


def test_osm_provider_classifies_church_building():
    osm = {
        "id": 401,
        "geometry": (
            (50.0, 7.0),
            (50.0, 7.001),
            (50.001, 7.001),
            (50.001, 7.0),
        ),
        "tags": {
            "building": "church",
            "amenity": "place_of_worship",
            "religion": "christian",
            "name": "St. Martin",
        },
    }

    landmark = AtlasLandmarkProviderOsm.from_osm(osm)

    assert landmark.landmark_type is AtlasLandmarkType.CHURCH


def test_osm_provider_classifies_cathedral_building():
    osm = {
        "id": 402,
        "geometry": (
            (50.0, 7.0),
            (50.0, 7.002),
            (50.002, 7.002),
            (50.002, 7.0),
        ),
        "tags": {
            "building": "cathedral",
            "amenity": "place_of_worship",
            "religion": "christian",
            "name": "Example Cathedral",
        },
    }

    landmark = AtlasLandmarkProviderOsm.from_osm(osm)

    assert landmark.landmark_type is AtlasLandmarkType.CATHEDRAL


def test_osm_provider_does_not_promote_generic_place_of_worship():
    osm = {
        "id": 403,
        "geometry": (),
        "tags": {
            "amenity": "place_of_worship",
            "religion": "christian",
        },
    }

    landmark = AtlasLandmarkProviderOsm.from_osm(osm)

    assert landmark.landmark_type is AtlasLandmarkType.UNKNOWN


def test_osm_provider_classifies_mosque_building():
    osm = {
        "id": 404,
        "geometry": (
            (50.0, 7.0),
            (50.0, 7.001),
            (50.001, 7.001),
            (50.001, 7.0),
        ),
        "tags": {
            "building": "mosque",
            "amenity": "place_of_worship",
            "religion": "muslim",
        },
    }

    landmark = AtlasLandmarkProviderOsm.from_osm(osm)

    assert landmark.landmark_type is AtlasLandmarkType.MOSQUE


def test_osm_provider_classifies_synagogue_building():
    osm = {
        "id": 405,
        "geometry": (
            (50.0, 7.0),
            (50.0, 7.001),
            (50.001, 7.001),
            (50.001, 7.0),
        ),
        "tags": {
            "building": "synagogue",
            "amenity": "place_of_worship",
            "religion": "jewish",
        },
    }

    landmark = AtlasLandmarkProviderOsm.from_osm(osm)

    assert landmark.landmark_type is AtlasLandmarkType.SYNAGOGUE


def test_osm_provider_derives_synagogue_from_generic_building():
    osm = {
        "id": 406,
        "geometry": (),
        "tags": {
            "building": "yes",
            "amenity": "place_of_worship",
            "religion": "jewish",
        },
    }

    landmark = AtlasLandmarkProviderOsm.from_osm(osm)

    assert landmark.landmark_type is AtlasLandmarkType.SYNAGOGUE
