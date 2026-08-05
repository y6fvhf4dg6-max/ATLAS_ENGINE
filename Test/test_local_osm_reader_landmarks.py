from CORE.atlas_local_osm_reader import AtlasLocalOSMReader


PBF_PATH = "Data/OSM/galata-tower-test.osm.pbf"
BBOX = (
    41.0160,
    28.9610,
    41.0350,
    28.9870,
)


def test_reader_collects_galata_tower_as_landmark():
    data = AtlasLocalOSMReader.read(
        PBF_PATH,
        BBOX,
    )

    landmarks = data["landmarks"]

    galata = next(
        landmark
        for landmark in landmarks
        if landmark["id"] == 23236783
    )

    assert galata["geometry_type"] == "way"
    assert galata["tags"]["man_made"] == "tower"
    assert galata["tags"]["historic"] == "tower"
    assert (
        galata["tags"]["tower:type"]
        == "observation;museum_and_observation"
    )
    assert len(galata["geometry"]) >= 3

def test_reader_collects_catalog_verified_conflicting_worship_landmark():
    data = AtlasLocalOSMReader.read(
        "Data/OSM/ankara-kalesi-test.osm.pbf",
        (
            39.9351328,
            32.8582838,
            39.9521044,
            32.8780862,
        ),
    )

    cenabi = next(
        landmark
        for landmark in data["landmarks"]
        if landmark["id"] == 322722702
    )

    assert cenabi["tags"]["building"] == "church"
    assert cenabi["tags"]["religion"] == "muslim"
    assert cenabi["tags"]["wikidata"] == "Q96278624"
    assert len(cenabi["geometry"]) >= 3
