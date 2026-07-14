from CORE.atlas_local_osm_reader import AtlasLocalOSMReader


def test_closed_pedestrian_area_with_positive_height_is_elevated():
    tags = {
        "highway": "pedestrian",
        "area": "yes",
        "height": "4.25",
    }

    assert AtlasLocalOSMReader._is_elevated_area(tags)


def test_open_pedestrian_path_is_not_elevated():
    tags = {
        "highway": "pedestrian",
        "height": "4.25",
    }

    assert not AtlasLocalOSMReader._is_elevated_area(tags)


def test_pedestrian_area_without_height_is_not_elevated():
    tags = {
        "highway": "pedestrian",
        "area": "yes",
    }

    assert not AtlasLocalOSMReader._is_elevated_area(tags)


def test_invalid_or_non_positive_height_is_not_elevated():
    assert not AtlasLocalOSMReader._is_elevated_area(
        {
            "highway": "pedestrian",
            "area": "yes",
            "height": "unknown",
        }
    )

    assert not AtlasLocalOSMReader._is_elevated_area(
        {
            "highway": "pedestrian",
            "area": "yes",
            "height": "0",
        }
    )


def test_anitkabir_fixture_separates_elevated_areas_from_paths():
    data = AtlasLocalOSMReader.read(
        "Data/OSM/anitkabir-test.osm.pbf",
        (
            39.92180,
            32.83280,
            39.92830,
            32.84110,
        ),
    )

    assert len(data["elevated_areas"]) == 57
    assert len(data["pedestrian_paths"]) == 32

    assert all(
        item["area_type"] == "elevated_pedestrian_area"
        for item in data["elevated_areas"]
    )

    assert all(
        item["height_m"] > 0.0
        for item in data["elevated_areas"]
    )
