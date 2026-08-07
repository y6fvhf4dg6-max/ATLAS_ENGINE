from CORE.atlas_local_osm_reader import AtlasLocalOSMReader


class _Location:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def valid(self):
        return True


class _NodeRef:
    def __init__(self, lat, lon):
        self.location = _Location(lat, lon)


class _Way:
    def __init__(self, way_id, tags, geometry):
        self.id = way_id
        self.tags = tags
        self.nodes = [
            _NodeRef(lat, lon)
            for lat, lon in geometry
        ]


def _reader():
    return AtlasLocalOSMReader(
        bbox=(50.0, 7.0, 51.0, 8.0)
    )


def test_reader_collects_surface_railway_as_linear_infrastructure():
    reader = _reader()

    way = _Way(
        101,
        {"railway": "rail"},
        [
            (50.5, 7.5),
            (50.6, 7.6),
        ],
    )

    reader.way(way)

    assert len(reader.linear_infrastructure) == 1

    item = reader.linear_infrastructure[0]

    assert item["id"] == 101
    assert item["geometry"] == [
        (50.5, 7.5),
        (50.6, 7.6),
    ]
    assert item["tags"]["railway"] == "rail"


def test_reader_collects_tram_and_preserves_source_tags():
    reader = _reader()

    way = _Way(
        102,
        {
            "railway": "tram",
            "bridge": "yes",
            "name": "Test Tram",
        },
        [
            (50.5, 7.5),
            (50.6, 7.6),
        ],
    )

    reader.way(way)

    assert len(reader.linear_infrastructure) == 1

    item = reader.linear_infrastructure[0]

    assert item["tags"]["railway"] == "tram"
    assert item["tags"]["bridge"] == "yes"
    assert item["tags"]["name"] == "Test Tram"


def test_reader_collects_cycleway_as_linear_infrastructure():
    reader = _reader()

    way = _Way(
        103,
        {"highway": "cycleway"},
        [
            (50.5, 7.5),
            (50.6, 7.6),
        ],
    )

    reader.way(way)

    assert len(reader.linear_infrastructure) == 1
    assert (
        reader.linear_infrastructure[0]["tags"]["highway"]
        == "cycleway"
    )


def test_reader_does_not_duplicate_cycleway_into_pedestrian_paths():
    reader = _reader()

    way = _Way(
        104,
        {"highway": "cycleway"},
        [
            (50.5, 7.5),
            (50.6, 7.6),
        ],
    )

    reader.way(way)

    assert len(reader.linear_infrastructure) == 1
    assert reader.pedestrian_paths == []


def test_reader_attaches_resolved_linear_infrastructure_metadata():
    reader = _reader()

    way = _Way(
        105,
        {
            "railway": "tram",
            "tunnel": "yes",
            "disused": "yes",
        },
        [
            (50.5, 7.5),
            (50.6, 7.6),
        ],
    )

    reader.way(way)

    item = reader.linear_infrastructure[0]

    assert item["semantic_class"] == "tram"
    assert item["operational_state"] == "disused"
    assert item["surface_visible"] is False




def test_reader_keeps_regular_pedestrian_path_in_existing_bucket():
    reader = _reader()

    way = _Way(
        106,
        {"highway": "footway"},
        [
            (50.5, 7.5),
            (50.6, 7.6),
        ],
    )

    reader.way(way)

    assert len(reader.pedestrian_paths) == 1
    assert reader.linear_infrastructure == []


def test_read_result_exposes_anitkabir_cycle_corridor():
    data = AtlasLocalOSMReader.read(
        "Data/OSM/anitkabir-test.osm.pbf",
        (
            39.92180,
            32.83280,
            39.92830,
            32.84110,
        ),
    )

    assert "linear_infrastructure" in data

    items = data["linear_infrastructure"]

    assert any(
        item["id"] == 883691085
        and item["semantic_class"] == "cycle_corridor"
        for item in items
    )
