from CORE.atlas_local_osm_reader import AtlasLocalOSMReader


def test_statue_artwork_is_classified():
    tags = {
        "tourism": "artwork",
        "artwork_type": "statue",
        "statue": "animal",
    }

    assert AtlasLocalOSMReader._is_artwork(tags)


def test_sculpture_artwork_is_classified():
    tags = {
        "tourism": "artwork",
        "artwork_type": "sculpture",
    }

    assert AtlasLocalOSMReader._is_artwork(tags)


def test_unrelated_artwork_type_is_not_classified():
    tags = {
        "tourism": "artwork",
        "artwork_type": "mural",
    }

    assert not AtlasLocalOSMReader._is_artwork(tags)


def test_anitkabir_fixture_reads_lion_statues():
    data = AtlasLocalOSMReader.read(
        "Data/OSM/anitkabir-test.osm.pbf",
        (
            39.92180,
            32.83280,
            39.92830,
            32.84110,
        ),
    )

    animal_statues = [
        item
        for item in data["artworks"]
        if item["statue_type"] == "animal"
    ]

    assert len(data["artworks"]) == 26
    assert len(animal_statues) == 24

    assert all(
        item["geometry_type"] == "node"
        for item in animal_statues
    )
