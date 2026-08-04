from CORE.atlas_bridge_builder import AtlasBridgeBuilder
from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_type import AtlasLandmarkType


def test_bridge_builder_uses_default_height_and_width():
    landmark = AtlasLandmark(
        id=101,
        landmark_type=AtlasLandmarkType.BRIDGE,
        geometry=((0.0, 0.0), (10.0, 0.0)),
        tags={"bridge": "yes"},
        source="osm",
    )

    result = AtlasBridgeBuilder.build(landmark)

    assert result.landmark_kind == "bridge"
    assert result.footprint == (
        (0.0, -5.0),
        (10.0, -5.0),
        (10.0, 5.0),
        (0.0, 5.0),
    )
    assert result.height_m == AtlasBridgeBuilder.DEFAULT_HEIGHT_M
    assert result.metadata["bridge_span_m"] == 10.0
    assert result.metadata["bridge_width_m"] == AtlasBridgeBuilder.DEFAULT_WIDTH_M


def test_bridge_builder_expands_centerline_into_deck_footprint():
    landmark = AtlasLandmark(
        id=102,
        landmark_type=AtlasLandmarkType.BRIDGE,
        geometry=((0.0, 0.0), (20.0, 0.0)),
        tags={
            "bridge": "yes",
            "width": "6",
        },
        source="osm",
    )

    result = AtlasBridgeBuilder.build(landmark)

    assert result.footprint == (
        (0.0, -3.0),
        (20.0, -3.0),
        (20.0, 3.0),
        (0.0, 3.0),
    )
    assert result.metadata["bridge_span_m"] == 20.0
    assert result.metadata["bridge_width_m"] == 6.0

def test_bridge_builder_resolves_deck_thickness():
    default_landmark = AtlasLandmark(
        id=103,
        landmark_type=AtlasLandmarkType.BRIDGE,
        geometry=((0.0, 0.0), (10.0, 0.0)),
        tags={"bridge": "yes"},
        source="osm",
    )
    tagged_landmark = AtlasLandmark(
        id=104,
        landmark_type=AtlasLandmarkType.BRIDGE,
        geometry=((0.0, 0.0), (10.0, 0.0)),
        tags={
            "bridge": "yes",
            "bridge:deck_thickness": "1.5 m",
        },
        source="osm",
    )

    default_result = AtlasBridgeBuilder.build(default_landmark)
    tagged_result = AtlasBridgeBuilder.build(tagged_landmark)

    assert (
        default_result.metadata["bridge_deck_thickness_m"]
        == AtlasBridgeBuilder.DEFAULT_DECK_THICKNESS_M
    )
    assert tagged_result.metadata["bridge_deck_thickness_m"] == 1.5

def test_bridge_builder_places_requested_piers_evenly_along_centerline():
    landmark = AtlasLandmark(
        id=105,
        landmark_type=AtlasLandmarkType.BRIDGE,
        geometry=((0.0, 0.0), (20.0, 0.0)),
        tags={
            "bridge": "yes",
            "bridge:pier_count": "3",
        },
        source="osm",
    )

    result = AtlasBridgeBuilder.build(landmark)

    assert result.metadata["bridge_pier_count"] == 3
    assert result.metadata["bridge_pier_positions"] == (
        (5.0, 0.0),
        (10.0, 0.0),
        (15.0, 0.0),
    )

def test_bridge_builder_resolves_pier_dimensions():
    landmark = AtlasLandmark(
        id=106,
        landmark_type=AtlasLandmarkType.BRIDGE,
        geometry=((0.0, 0.0), (20.0, 0.0)),
        tags={
            "bridge": "yes",
            "bridge:pier_count": "2",
            "bridge:pier_width": "2.5",
            "bridge:pier_depth": "1.5",
        },
        source="osm",
    )

    result = AtlasBridgeBuilder.build(landmark)

    assert result.metadata["bridge_pier_width_m"] == 2.5
    assert result.metadata["bridge_pier_depth_m"] == 1.5

def test_bridge_builder_resolves_pier_vertical_extent():
    landmark = AtlasLandmark(
        id=107,
        landmark_type=AtlasLandmarkType.BRIDGE,
        geometry=((0.0, 0.0), (20.0, 0.0)),
        tags={
            "bridge": "yes",
            "height": "8.0",
            "bridge:deck_thickness": "1.0",
            "bridge:pier_count": "2",
        },
        source="osm",
    )

    result = AtlasBridgeBuilder.build(landmark)

    assert result.metadata["bridge_pier_base_m"] == 0.0
    assert result.metadata["bridge_pier_top_m"] == 7.0
    assert result.metadata["bridge_pier_height_m"] == 7.0

def test_bridge_builder_rejects_invalid_pier_counts():
    for index, invalid_value in enumerate(("0", "-2", "2.5", "invalid"), start=108):
        landmark = AtlasLandmark(
            id=index,
            landmark_type=AtlasLandmarkType.BRIDGE,
            geometry=((0.0, 0.0), (12.0, 0.0)),
            tags={
                "bridge": "yes",
                "bridge:pier_count": invalid_value,
            },
            source="osm",
        )

        result = AtlasBridgeBuilder.build(landmark)

        assert result.metadata["bridge_pier_count"] == 0
        assert result.metadata["bridge_pier_positions"] == ()

def test_bridge_builder_falls_back_for_invalid_pier_dimensions():
    landmark = AtlasLandmark(
        id=112,
        landmark_type=AtlasLandmarkType.BRIDGE,
        geometry=((0.0, 0.0), (20.0, 0.0)),
        tags={
            "bridge": "yes",
            "bridge:pier_count": "2",
            "bridge:pier_width": "0",
            "bridge:pier_depth": "-1",
        },
        source="osm",
    )

    result = AtlasBridgeBuilder.build(landmark)

    assert (
        result.metadata["bridge_pier_width_m"]
        == AtlasBridgeBuilder.DEFAULT_PIER_WIDTH_M
    )
    assert (
        result.metadata["bridge_pier_depth_m"]
        == AtlasBridgeBuilder.DEFAULT_PIER_DEPTH_M
    )


def test_bridge_builder_keeps_galata_deck_continuous():
    landmark = AtlasLandmark(
        id=280961352,
        landmark_type=AtlasLandmarkType.BRIDGE,
        geometry=(
            (0.0, -5.0),
            (80.0, -5.0),
            (80.0, 5.0),
            (0.0, 5.0),
        ),
        tags={
            "man_made": "bridge",
            "name": "Galata Köprüsü",
            "wikidata": "Q81523",
        },
        source="osm",
    )

    result = AtlasBridgeBuilder.build(landmark)

    assert result.metadata["bridge_approach_profile"] is False
    assert result.metadata["bridge_segmented_deck"] is False
    assert result.metadata["bridge_shore_top_m"] == 6.0
    assert result.metadata["bridge_approach_ratio"] == 0.20


def test_bridge_builder_does_not_assign_galata_profile_to_generic_bridge():
    landmark = AtlasLandmark(
        id=999,
        landmark_type=AtlasLandmarkType.BRIDGE,
        geometry=(
            (0.0, -5.0),
            (80.0, -5.0),
            (80.0, 5.0),
            (0.0, 5.0),
        ),
        tags={
            "man_made": "bridge",
            "name": "Generic Bridge",
        },
        source="osm",
    )

    result = AtlasBridgeBuilder.build(landmark)

    assert result.metadata["bridge_approach_profile"] is False


def test_galata_bridge_catalog_matching_is_normalized():
    landmark = AtlasLandmark(
        id=280961352,
        landmark_type=AtlasLandmarkType.BRIDGE,
        geometry=(
            (0.0, -5.0),
            (80.0, -5.0),
            (80.0, 5.0),
            (0.0, 5.0),
        ),
        tags={
            "man_made": "bridge",
            "name": "Galata Köprüsü",
            "wikidata": " q81523 ",
        },
        source="osm",
    )

    result = AtlasBridgeBuilder.build(landmark)

    assert result.metadata["bridge_full_span_convex"] is True
    assert result.metadata["bridge_shore_top_m"] == 6.0
