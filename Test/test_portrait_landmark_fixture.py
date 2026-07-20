import pytest

from CORE.atlas_portrait_landmark_result import (
    AtlasPortraitLandmarkResult,
)
from Test.fixtures.portrait.portrait_landmark_fixture import (
    fixture_landmark_names,
    load_frontal_portrait_landmark_fixture,
)

EXPECTED_LANDMARK_NAMES = (
    "chin_tip",
    "left_eye_inner",
    "left_eye_outer",
    "mouth_left",
    "mouth_right",
    "nose_left",
    "nose_right",
    "nose_root",
    "nose_tip",
    "right_eye_inner",
    "right_eye_outer",
)


def test_fixture_returns_landmark_result():
    result = load_frontal_portrait_landmark_fixture()

    assert isinstance(
        result,
        AtlasPortraitLandmarkResult,
    )


def test_fixture_uses_expected_image_dimensions():
    result = load_frontal_portrait_landmark_fixture()

    assert result.image_width == 1000
    assert result.image_height == 1200


def test_fixture_uses_deterministic_provider_id():
    result = load_frontal_portrait_landmark_fixture()

    assert result.provider_id == ("synthetic-frontal-fixture")


def test_fixture_has_full_confidence():
    result = load_frontal_portrait_landmark_fixture()

    assert result.confidence == 1.0


def test_fixture_landmark_names_are_complete():
    assert fixture_landmark_names() == (EXPECTED_LANDMARK_NAMES)


def test_fixture_landmarks_are_symmetric():
    result = load_frontal_portrait_landmark_fixture()

    left_eye_outer = result.landmarks["left_eye_outer"]
    right_eye_outer = result.landmarks["right_eye_outer"]

    assert left_eye_outer[0] == pytest.approx(1.0 - right_eye_outer[0])
    assert left_eye_outer[1] == (right_eye_outer[1])

    mouth_left = result.landmarks["mouth_left"]
    mouth_right = result.landmarks["mouth_right"]

    assert mouth_left[0] == pytest.approx(1.0 - mouth_right[0])
    assert mouth_left[1] == mouth_right[1]


def test_fixture_centerline_landmarks_are_centered():
    result = load_frontal_portrait_landmark_fixture()

    for name in (
        "nose_root",
        "nose_tip",
        "chin_tip",
    ):
        assert result.landmarks[name][0] == 0.5


def test_fixture_metadata_describes_front_view():
    result = load_frontal_portrait_landmark_fixture()

    assert result.metadata == {
        "fixture_name": ("synthetic_frontal_portrait_v1"),
        "view_type": "front",
        "synthetic": True,
    }


def test_fixture_returns_independent_results():
    first = load_frontal_portrait_landmark_fixture()
    second = load_frontal_portrait_landmark_fixture()

    assert first is not second
    assert first == second


def test_fixture_pixel_coordinates_are_deterministic():
    result = load_frontal_portrait_landmark_fixture()

    assert result.pixel_landmark(
        "nose_tip",
    ) == pytest.approx(
        (
            499.5,
            659.45,
        )
    )
