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
