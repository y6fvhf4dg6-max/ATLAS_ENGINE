from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_tower_builder import AtlasTowerBuilder


def test_builder_uses_min_height_when_height_non_numeric_and_levels_missing():
    lm = AtlasLandmark(
        id=104,
        landmark_type=AtlasLandmarkType.TOWER,
        geometry=((0, 0), (1, 0), (1, 1), (0, 1)),
        tags={
            "height": "approx 85m",  # sayısal değil
            "min_height": "90",
        },
        source="OSM",
    )
    geom = AtlasTowerBuilder.build(lm)
    assert geom.height_m == 90.0
