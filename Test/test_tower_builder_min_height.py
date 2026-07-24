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
def test_builder_uses_levels_when_height_non_numeric():
    lm = AtlasLandmark(
        id=105,
        landmark_type=AtlasLandmarkType.TOWER,
        geometry=((0, 0), (1, 0), (1, 1), (0, 1)),
        tags={
            "height": "unknown",
            "building:levels": "12",
        },
        source="OSM",
    )

    result = AtlasTowerBuilder.build(lm)

    assert result.height_m == 12 * AtlasTowerBuilder.FLOOR_HEIGHT_M
def test_builder_uses_default_height_when_no_valid_height_information():
    lm = AtlasLandmark(
        id=106,
        landmark_type=AtlasLandmarkType.TOWER,
        geometry=((0, 0), (1, 0), (1, 1), (0, 1)),
        tags={
            "height": "unknown",
            "building:levels": "many",
            "min_height": "invalid",
        },
        source="OSM",
    )

    result = AtlasTowerBuilder.build(lm)

    assert result.height_m == AtlasTowerBuilder.DEFAULT_HEIGHT_M
