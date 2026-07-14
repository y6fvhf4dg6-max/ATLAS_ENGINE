from CORE.atlas_local_osm_reader import AtlasLocalOSMReader


class FakeLocation:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    @staticmethod
    def valid():
        return True


class FakeNode:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
        self.location = FakeLocation(
            lat,
            lon,
        )


class FakeWay:
    def __init__(self, way_id, tags, geometry):
        self.id = way_id
        self.tags = tags
        self.nodes = [
            FakeNode(lat, lon)
            for lat, lon in geometry
        ]


def _reader():
    reader = AtlasLocalOSMReader(
        bbox=(
            38.0,
            31.0,
            40.0,
            33.0,
        )
    )

    return reader


def test_building_part_way_is_read_as_building_record():
    reader = _reader()

    way = FakeWay(
        way_id=7001,
        tags={
            "building:part": "yes",
            "height": "22",
        },
        geometry=[
            (39.0, 32.0),
            (39.0, 32.0001),
            (39.0001, 32.0001),
            (39.0001, 32.0),
            (39.0, 32.0),
        ],
    )

    reader.way(way)

    assert len(reader.buildings) == 1

    record = reader.buildings[0]

    assert record["id"] == 7001
    assert record["tags"]["building:part"] == "yes"
    assert "building" not in record["tags"]


def test_regular_building_behavior_is_preserved():
    reader = _reader()

    way = FakeWay(
        way_id=7002,
        tags={
            "building": "yes",
            "height": "10",
        },
        geometry=[
            (39.0, 32.0),
            (39.0, 32.0001),
            (39.0001, 32.0001),
            (39.0001, 32.0),
            (39.0, 32.0),
        ],
    )

    reader.way(way)

    assert len(reader.buildings) == 1
    assert reader.buildings[0]["id"] == 7002
