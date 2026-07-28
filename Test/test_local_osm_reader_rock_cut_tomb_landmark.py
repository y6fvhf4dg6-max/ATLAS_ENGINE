from CORE.atlas_local_osm_reader import AtlasLocalOSMReader


def test_rock_cut_tomb_node_is_landmark():
    tags = {
        "historic": "tomb",
        "tomb": "rock-cut",
        "tourism": "attraction",
    }

    assert AtlasLocalOSMReader._is_landmark(tags) is True


def test_generic_tomb_without_rock_cut_type_is_not_landmark():
    tags = {
        "historic": "tomb",
    }

    assert AtlasLocalOSMReader._is_landmark(tags) is False
