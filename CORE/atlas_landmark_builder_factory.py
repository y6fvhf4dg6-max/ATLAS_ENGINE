from CORE.atlas_bridge_builder import AtlasBridgeBuilder
from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_obelisk_builder import AtlasObeliskBuilder


class AtlasLandmarkBuilderFactory:
    _BUILDERS = {
        AtlasLandmarkType.OBELISK: AtlasObeliskBuilder,
        AtlasLandmarkType.BRIDGE: AtlasBridgeBuilder,
    }

    @classmethod
    def get_builder(cls, landmark):
        return cls._BUILDERS.get(landmark.landmark_type)
