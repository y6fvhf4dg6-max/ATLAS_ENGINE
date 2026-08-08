from CORE.atlas_tree_row_member_producer import (
    AtlasTreeRowMemberProducer,
)


def test_producer_builds_controlled_tree_inputs_from_layout():
    layout = {
        "source_id": 123,
        "status": "resolved",
        "tree_count": 3,
        "placement_points": (
            (50.0000, 7.0000),
            (50.0001, 7.0000),
            (50.0002, 7.0000),
        ),
    }

    result = AtlasTreeRowMemberProducer.build(layout)

    assert len(result) == 3

    assert tuple(item["id"] for item in result) == (
        "tree_row_123_0",
        "tree_row_123_1",
        "tree_row_123_2",
    )

    assert all(
        item["tree_kind"] == "park_tree_symbol"
        for item in result
    )

    assert all(
        item["tags"]["source"] == "osm_tree_row"
        for item in result
    )

    assert tuple(
        (item["lat"], item["lon"])
        for item in result
    ) == layout["placement_points"]


def test_producer_returns_empty_for_skipped_layout():
    assert AtlasTreeRowMemberProducer.build(
        {
            "source_id": 124,
            "status": "skipped",
            "tree_count": 0,
            "placement_points": (),
        }
    ) == []


from CORE.atlas_tree_foundation_builder import (
    AtlasTreeFoundationBuilder,
)


class _CoordinateEngineStub:
    @staticmethod
    def latlon_to_stl_mm(lat, lon):
        return (
            (float(lon) - 7.0) * 100000.0,
            (float(lat) - 50.0) * 100000.0,
        )


def test_produced_row_members_build_controlled_tree_meshes():
    layout = {
        "source_id": 700,
        "status": "resolved",
        "tree_count": 3,
        "placement_points": (
            (50.00002, 7.00002),
            (50.00004, 7.00004),
            (50.00006, 7.00006),
        ),
    }

    members = AtlasTreeRowMemberProducer.build(layout)

    terrain_mesh = {
        "top_points": (
            (
                (0.0, 0.0, 1.0),
                (200.0, 0.0, 1.0),
            ),
            (
                (0.0, 200.0, 1.0),
                (200.0, 200.0, 1.0),
            ),
        ),
        "triangles": [
            (
                (0.0, 0.0, 1.0),
                (200.0, 0.0, 1.0),
                (200.0, 200.0, 1.0),
            ),
            (
                (0.0, 0.0, 1.0),
                (200.0, 200.0, 1.0),
                (0.0, 200.0, 1.0),
            ),
        ],
    }

    meshes = AtlasTreeFoundationBuilder.build_trees(
        trees=members,
        coordinate_engine=_CoordinateEngineStub(),
        terrain_mesh=terrain_mesh,
        debug=False,
    )

    assert len(meshes) == 3

    assert all(
        mesh["tree_type"] == "park_tree_symbol"
        for mesh in meshes
    )

    assert all(
        mesh["source"] == "osm_tree_row"
        for mesh in meshes
    )

    assert tuple(
        mesh["tree_id"]
        for mesh in meshes
    ) == (
        "tree_row_700_0",
        "tree_row_700_1",
        "tree_row_700_2",
    )
