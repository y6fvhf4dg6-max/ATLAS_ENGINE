from CORE.atlas_local_osm_reader import (
    AtlasLocalOSMReader,
)


class FakeLocation:
    def __init__(
        self,
        lat,
        lon,
        valid=True,
    ):
        self.lat = lat
        self.lon = lon
        self._valid = valid

    def valid(self):
        return self._valid


class FakeNode:
    def __init__(
        self,
        node_id,
        lat,
        lon,
        tags,
    ):
        self.id = node_id
        self.location = FakeLocation(
            lat=lat,
            lon=lon,
        )
        self.tags = tags


def test_castle_node_is_stored_as_metadata_only():
    reader = AtlasLocalOSMReader(
        bbox=(
            48.5520,
            9.3875,
            48.5595,
            9.3975,
        )
    )

    node = FakeNode(
        node_id=174509734,
        lat=48.5555559,
        lon=9.3924067,
        tags={
            "historic": "castle",
            "name": "Burg Hohenneuffen",
            "castle_type": "defensive",
            "ruins": "yes",
        },
    )

    reader.node(node)

    assert len(reader.castle_metadata) == 1
    assert len(reader.castles) == 0

    metadata = reader.castle_metadata[0]

    assert metadata["id"] == 174509734
    assert metadata["geometry_type"] == "node"
    assert metadata["name"] == "Burg Hohenneuffen"
    assert metadata["castle_type"] == "defensive"
    assert metadata["tags"]["ruins"] == "yes"


def test_regular_node_is_not_stored_as_castle_metadata():
    reader = AtlasLocalOSMReader(
        bbox=(
            48.5520,
            9.3875,
            48.5595,
            9.3975,
        )
    )

    node = FakeNode(
        node_id=1,
        lat=48.5555,
        lon=9.3924,
        tags={
            "amenity": "bench",
        },
    )

    reader.node(node)

    assert reader.castle_metadata == []
    assert reader.castles == []


def test_castle_node_outside_bbox_is_ignored():
    reader = AtlasLocalOSMReader(
        bbox=(
            48.5520,
            9.3875,
            48.5595,
            9.3975,
        )
    )

    node = FakeNode(
        node_id=2,
        lat=48.6000,
        lon=9.5000,
        tags={
            "historic": "castle",
            "name": "Outside Castle",
        },
    )

    reader.node(node)

    assert reader.castle_metadata == []
    assert reader.castles == []
