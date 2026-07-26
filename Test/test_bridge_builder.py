from CORE.atlas_bridge_builder import AtlasBridgeBuilder
from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_type import AtlasLandmarkType


def test_bridge_builder_uses_default_height_and_preserves_geometry():
    landmark = AtlasLandmark(
        id=101,
        landmark_type=AtlasLandmarkType.BRIDGE,
        geometry=((0.0, 0.0), (10.0, 0.0)),
        tags={"bridge": "yes"},
        source="osm",
    )

    result = AtlasBridgeBuilder.build(landmark)

    assert result.landmark_kind == "bridge"
    assert result.footprint == landmark.geometry
    assert result.height_m == AtlasBridgeBuilder.DEFAULT_HEIGHT_M
    assert result.metadata["bridge_span_m"] == AtlasBridgeBuilder.DEFAULT_SPAN_M
    assert result.metadata["bridge_width_m"] == AtlasBridgeBuilder.DEFAULT_WIDTH_M
