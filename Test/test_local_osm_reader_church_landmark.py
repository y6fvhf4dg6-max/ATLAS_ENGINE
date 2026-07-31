from CORE.atlas_local_osm_reader import AtlasLocalOSMReader


def test_church_building_is_landmark():
    tags = {
        "building": "church",
        "amenity": "place_of_worship",
        "religion": "christian",
    }

    assert AtlasLocalOSMReader._is_landmark(tags) is True


def test_cathedral_building_is_landmark():
    tags = {
        "building": "cathedral",
        "amenity": "place_of_worship",
        "religion": "christian",
    }

    assert AtlasLocalOSMReader._is_landmark(tags) is True


def test_generic_place_of_worship_is_not_promoted_to_landmark():
    tags = {
        "amenity": "place_of_worship",
        "religion": "christian",
    }

    assert AtlasLocalOSMReader._is_landmark(tags) is False


def test_non_christian_religious_building_is_not_promoted_by_church_rule():
    tags = {
        "building": "church",
        "amenity": "place_of_worship",
        "religion": "muslim",
    }

    assert AtlasLocalOSMReader._is_landmark(tags) is False
