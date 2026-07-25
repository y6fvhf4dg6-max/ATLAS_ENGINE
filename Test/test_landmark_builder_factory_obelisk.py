from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_builder_factory import AtlasLandmarkBuilderFactory
from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_obelisk_builder import AtlasObeliskBuilder


def test_factory_returns_obelisk_builder():
    landmark = AtlasLandmark(
        id=1,
        landmark_type=AtlasLandmarkType.OBELISK,
        geometry=(),
        tags={},
        source="OSM",
    )

    builder = AtlasLandmarkBuilderFactory.get_builder(landmark)

    assert builder is AtlasObeliskBuilder
