from CORE.atlas_local_osm_reader import AtlasLocalOSMReader


def main():
    pbf_path = "Data/OSM/hessen-latest.osm.pbf"

    bbox = (
        50.1000,
        8.6500,
        50.1300,
        8.6900,
    )

    data = AtlasLocalOSMReader.read(pbf_path, bbox)

    print()
    print("=" * 60)
    print("LOCAL OSM DATABASE TEST")
    print("=" * 60)
    print("Buildings:", len(data["buildings"]))
    print("Trees    :", len(data["trees"]))

    print()
    print("First trees:")
    for tree in data["trees"][:5]:
        print(tree)


if __name__ == "__main__":
    main()


class _FakeLocation:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def valid(self):
        return True


class _FakeNodeRef:
    def __init__(self, lat, lon):
        self.location = _FakeLocation(lat, lon)


class _FakeWay:
    def __init__(self, way_id, geometry, tags):
        self.id = way_id
        self.nodes = [
            _FakeNodeRef(lat, lon)
            for lat, lon in geometry
        ]
        self.tags = tags


def test_reader_collects_natural_tree_row_way():
    reader = AtlasLocalOSMReader(
        bbox=(49.0, 6.0, 51.0, 8.0)
    )

    way = _FakeWay(
        way_id=123,
        geometry=(
            (50.0000, 7.0000),
            (50.0001, 7.0001),
            (50.0002, 7.0002),
        ),
        tags={
            "natural": "tree_row",
            "name": "Formal avenue",
        },
    )

    reader.way(way)

    assert len(reader.tree_rows) == 1
    assert reader.trees == []

    row = reader.tree_rows[0]

    assert row["id"] == 123
    assert row["tree_type"] == "tree_row"
    assert row["geometry"] == [
        (50.0000, 7.0000),
        (50.0001, 7.0001),
        (50.0002, 7.0002),
    ]
    assert row["tags"]["natural"] == "tree_row"


def test_reader_result_contract_exposes_tree_rows_key():
    reader = AtlasLocalOSMReader(
        bbox=(49.0, 6.0, 51.0, 8.0)
    )

    assert hasattr(reader, "tree_rows")
    assert reader.tree_rows == []
