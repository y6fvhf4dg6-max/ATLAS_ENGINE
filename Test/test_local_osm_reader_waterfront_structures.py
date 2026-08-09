from CORE.atlas_local_osm_reader import AtlasLocalOSMReader


def test_reader_recognizes_waterfront_structure_tags():
    assert (
        AtlasLocalOSMReader._waterfront_structure_type(
            {"man_made": "quay"}
        )
        == "quay"
    )

    assert (
        AtlasLocalOSMReader._waterfront_structure_type(
            {"man_made": "pier"}
        )
        == "waterfront_pier"
    )

    assert (
        AtlasLocalOSMReader._waterfront_structure_type(
            {"leisure": "marina"}
        )
        == "marina"
    )


def test_reader_does_not_misclassify_bridge_pier_metadata():
    assert (
        AtlasLocalOSMReader._waterfront_structure_type(
            {
                "bridge": "yes",
                "bridge:pier_count": "3",
            }
        )
        is None
    )


def test_reader_rejects_unrelated_tags_as_waterfront_structure():
    assert (
        AtlasLocalOSMReader._waterfront_structure_type(
            {"amenity": "bench"}
        )
        is None
    )


class _Location:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def valid(self):
        return True


class _Node:
    def __init__(self, lat, lon):
        self.location = _Location(lat, lon)


class _Way:
    def __init__(self, way_id, tags, geometry):
        self.id = way_id
        self.tags = tags
        self.nodes = [
            _Node(lat, lon)
            for lat, lon in geometry
        ]


def test_reader_collects_quay_as_waterfront_structure():
    reader = AtlasLocalOSMReader(
        bbox=(
            49.0,
            7.0,
            51.0,
            9.0,
        )
    )

    way = _Way(
        1001,
        {"man_made": "quay"},
        (
            (50.0, 8.0),
            (50.0, 8.1),
        ),
    )

    reader.way(way)

    assert len(reader.waterfront_structures) == 1

    item = reader.waterfront_structures[0]

    assert item["id"] == 1001
    assert item["waterfront_type"] == "quay"
    assert item["geometry"] == [
        (50.0, 8.0),
        (50.0, 8.1),
    ]


def test_reader_collects_pier_and_marina_without_bridge_pier_confusion():
    reader = AtlasLocalOSMReader(
        bbox=(
            49.0,
            7.0,
            51.0,
            9.0,
        )
    )

    reader.way(
        _Way(
            1002,
            {"man_made": "pier"},
            (
                (50.0, 8.0),
                (50.0, 8.1),
            ),
        )
    )

    reader.way(
        _Way(
            1003,
            {"leisure": "marina"},
            (
                (50.0, 8.0),
                (50.0, 8.1),
                (50.1, 8.1),
                (50.1, 8.0),
                (50.0, 8.0),
            ),
        )
    )

    reader.way(
        _Way(
            1004,
            {
                "bridge": "yes",
                "bridge:pier_count": "3",
            },
            (
                (50.0, 8.0),
                (50.0, 8.1),
            ),
        )
    )

    assert [
        item["waterfront_type"]
        for item in reader.waterfront_structures
    ] == [
        "waterfront_pier",
        "marina",
    ]


def test_reader_collects_open_linear_waterways_for_product_geometry():
    reader = AtlasLocalOSMReader(
        bbox=(
            49.0,
            7.0,
            51.0,
            9.0,
        )
    )

    for way_id, waterway in (
        (1101, "stream"),
        (1102, "river"),
        (1103, "canal"),
    ):
        reader.way(
            _Way(
                way_id,
                {
                    "waterway": waterway,
                    "width": "1.5",
                },
                (
                    (50.0, 8.0),
                    (50.0, 8.1),
                ),
            )
        )

    assert [
        item["id"]
        for item in reader.waters
    ] == [
        1101,
        1102,
        1103,
    ]

    assert [
        item["tags"]["waterway"]
        for item in reader.waters
    ] == [
        "stream",
        "river",
        "canal",
    ]

    for item in reader.waters:
        assert len(item["geometry"]) == 2
