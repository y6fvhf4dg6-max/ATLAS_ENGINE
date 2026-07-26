from CORE.atlas_bridge_builder import AtlasBridgeBuilder
from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_builder_factory import AtlasLandmarkBuilderFactory
from CORE.atlas_landmark_type import AtlasLandmarkType


def test_factory_returns_bridge_builder_for_bridge_landmark():
    landmark = AtlasLandmark(
        id=201,
        landmark_type=AtlasLandmarkType.BRIDGE,
        geometry=((0.0, 0.0), (10.0, 0.0)),
        tags={"bridge": "yes"},
        source="osm",
    )

    assert AtlasLandmarkBuilderFactory.get_builder(landmark) is AtlasBridgeBuilder
