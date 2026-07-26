from CORE.atlas_local_osm_reader import AtlasLocalOSMReader


def test_primary_highway_bridge_is_landmark():
    tags = {
        "bridge": "yes",
        "highway": "primary",
    }

    assert AtlasLocalOSMReader._is_landmark(tags) is True


def test_man_made_bridge_is_landmark():
    tags = {
        "man_made": "bridge",
    }

    assert AtlasLocalOSMReader._is_landmark(tags) is True


def test_bridge_steps_are_not_independent_landmark():
    tags = {
        "bridge": "yes",
        "highway": "steps",
    }

    assert AtlasLocalOSMReader._is_landmark(tags) is False


def test_bridge_footway_is_not_independent_landmark():
    tags = {
        "bridge": "yes",
        "highway": "footway",
    }

    assert AtlasLocalOSMReader._is_landmark(tags) is False


def test_bridge_tram_is_not_independent_landmark():
    tags = {
        "bridge": "yes",
        "railway": "tram",
    }

    assert AtlasLocalOSMReader._is_landmark(tags) is False


def test_bridge_subway_is_not_independent_landmark():
    tags = {
        "bridge": "yes",
        "railway": "subway",
    }

    assert AtlasLocalOSMReader._is_landmark(tags) is False
