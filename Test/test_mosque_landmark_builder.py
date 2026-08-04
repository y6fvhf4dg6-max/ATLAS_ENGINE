import pytest

from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_mosque_landmark_builder import (
    AtlasMosqueLandmarkBuilder,
)
from CORE.atlas_mosque_landmark_profile import (
    AtlasMosqueLandmarkProfile,
)


def _landmark(
    *,
    landmark_type=AtlasLandmarkType.MOSQUE,
    tags=None,
):
    return AtlasLandmark(
        id=1101,
        landmark_type=landmark_type,
        geometry=(
            (0.0, 0.0),
            (24.0, 0.0),
            (24.0, 36.0),
            (0.0, 36.0),
        ),
        tags=tags or {
            "building": "mosque",
            "religion": "muslim",
        },
        source="OSM",
    )


def test_builder_creates_single_dome_single_minaret_plan():
    result = AtlasMosqueLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasMosqueLandmarkProfile(),
    )

    assert result.landmark_id == 1101
    assert result.grammar_name == (
        "single_dome_single_minaret"
    )
    assert result.footprint == (
        (0.0, 0.0),
        (24.0, 0.0),
        (24.0, 36.0),
        (0.0, 36.0),
    )

    assert tuple(
        component.component_type
        for component in result.components
    ) == (
        "prayer_hall",
        "dome_drum",
        "main_dome",
        "minaret_body",
        "minaret_balcony",
        "minaret_cap",
    )


def test_builder_uses_osm_height():
    result = AtlasMosqueLandmarkBuilder.build(
        landmark=_landmark(
            tags={
                "building": "mosque",
                "religion": "muslim",
                "height": "27.5 m",
            },
        ),
        profile=AtlasMosqueLandmarkProfile(),
    )

    assert result.height_m == pytest.approx(
        27.5
    )


def test_builder_uses_default_height():
    result = AtlasMosqueLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasMosqueLandmarkProfile(),
    )

    assert result.height_m == pytest.approx(
        AtlasMosqueLandmarkBuilder
        .DEFAULT_MOSQUE_HEIGHT_M
    )


def test_builder_rejects_non_mosque_landmark():
    with pytest.raises(
        ValueError,
        match="mosque",
    ):
        AtlasMosqueLandmarkBuilder.build(
            landmark=_landmark(
                landmark_type=AtlasLandmarkType.CHURCH,
            ),
            profile=AtlasMosqueLandmarkProfile(),
        )


def test_builder_rejects_wrong_profile_type():
    with pytest.raises(
        TypeError,
        match="AtlasMosqueLandmarkProfile",
    ):
        AtlasMosqueLandmarkBuilder.build(
            landmark=_landmark(),
            profile=object(),
        )


def test_builder_rejects_invalid_footprint():
    landmark = AtlasLandmark(
        id=1102,
        landmark_type=AtlasLandmarkType.MOSQUE,
        geometry=(
            (0.0, 0.0),
            (1.0, 0.0),
        ),
        tags={
            "building": "mosque",
        },
        source="OSM",
    )

    with pytest.raises(
        ValueError,
        match="three footprint points",
    ):
        AtlasMosqueLandmarkBuilder.build(
            landmark=landmark,
            profile=AtlasMosqueLandmarkProfile(),
        )
