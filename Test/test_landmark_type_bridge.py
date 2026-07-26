from CORE.atlas_landmark_type import AtlasLandmarkType


def test_landmark_type_includes_bridge():
    assert AtlasLandmarkType.BRIDGE.name == "BRIDGE"
