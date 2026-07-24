from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_obelisk_builder import AtlasObeliskBuilder


def test_builder_prefers_osm_height_when_available():
    landmark = AtlasLandmark(
        id=1,
        landmark_type=AtlasLandmarkType.OBELISK,
        geometry=(
            (0.0, 0.0),
            (1.0, 0.0),
            (1.0, 1.0),
            (0.0, 1.0),
        ),
        tags={
            "height": "82.5",
        },
        source="OSM",
    )

    geometry = AtlasObeliskBuilder.build(landmark)

    assert geometry.height_m == 82.5


def test_builder_uses_default_height_when_missing():
    landmark = AtlasLandmark(
        id=2,
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

    geometry = AtlasObeliskBuilder.build(landmark)

    assert geometry.height_m == AtlasObeliskBuilder.DEFAULT_HEIGHT_M
