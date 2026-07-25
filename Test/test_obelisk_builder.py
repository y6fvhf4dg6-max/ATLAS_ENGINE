from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_geometry import AtlasLandmarkGeometry
from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_obelisk_builder import AtlasObeliskBuilder


def test_builder_returns_landmark_geometry():
    landmark = AtlasLandmark(
        id=1,
        landmark_type=AtlasLandmarkType.OBELISK,
        geometry=(
            (0.0, 0.0),
            (1.0, 0.0),
            (1.0, 1.0),
            (0.0, 1.0),
        ),
        tags={},
        source="OSM",
    )

    result = AtlasObeliskBuilder.build(landmark)

    assert isinstance(result, AtlasLandmarkGeometry)


def test_builder_preserves_footprint_and_real_world_height():
    landmark = AtlasLandmark(
        id=1,
        landmark_type=AtlasLandmarkType.OBELISK,
        geometry=(
            (0.0, 0.0),
            (1.0, 0.0),
            (1.0, 1.0),
            (0.0, 1.0),
        ),
        tags={},
        source="OSM",
    )

    result = AtlasObeliskBuilder.build(landmark)

    assert result.footprint == landmark.geometry
    assert result.height_m > 0.0
