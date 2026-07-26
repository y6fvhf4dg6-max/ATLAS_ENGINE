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
