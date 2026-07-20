import math

import pytest

from CORE.atlas_portrait_landmark_result import (
    AtlasPortraitLandmarkResult,
)


def _make_result(**overrides):
    arguments = {
        "image_width": 1000,
        "image_height": 800,
        "landmarks": {
            "left_eye_outer": (0.30, 0.35),
            "right_eye_outer": (0.70, 0.35),
            "nose_tip": (0.50, 0.55),
            "mouth_left": (0.42, 0.70),
            "mouth_right": (0.58, 0.70),
            "chin_tip": (0.50, 0.90),
        },
        "confidence": 0.95,
        "provider_id": "fixture-provider",
        "metadata": {
            "view_type": "front",
        },
    }
    arguments.update(overrides)

    return AtlasPortraitLandmarkResult(
        **arguments,
    )


def test_result_preserves_normalized_landmarks():
    result = _make_result()

    assert result.image_width == 1000
    assert result.image_height == 800
    assert result.landmarks["nose_tip"] == (
        0.50,
        0.55,
    )
    assert result.confidence == 0.95
    assert result.provider_id == "fixture-provider"
    assert result.metadata == {
        "view_type": "front",
    }


def test_result_converts_numeric_values():
    result = _make_result(
        image_width=1000.0,
        image_height=800.0,
        landmarks={
            "nose_tip": (1 / 2, 11 / 20),
        },
        confidence=1,
    )

    assert result.image_width == 1000
    assert result.image_height == 800
    assert result.landmarks["nose_tip"] == (
        0.5,
        0.55,
    )
    assert result.confidence == 1.0


def test_result_strips_provider_id_whitespace():
    result = _make_result(
        provider_id="  fixture-provider  ",
    )

    assert result.provider_id == "fixture-provider"


def test_result_returns_pixel_coordinates():
    result = _make_result(
        image_width=1001,
        image_height=801,
        landmarks={
            "top_left": (0.0, 0.0),
            "center": (0.5, 0.5),
            "bottom_right": (1.0, 1.0),
        },
    )

    assert result.pixel_landmark(
        "top_left",
    ) == (
        0.0,
        0.0,
    )
    assert result.pixel_landmark(
        "center",
    ) == (
        500.0,
        400.0,
    )
    assert result.pixel_landmark(
        "bottom_right",
    ) == (
        1000.0,
        800.0,
    )


def test_result_rejects_unknown_pixel_landmark():
    result = _make_result()

    with pytest.raises(
        KeyError,
    ):
        result.pixel_landmark(
            "unknown",
        )


def test_result_is_immutable():
    result = _make_result()

    with pytest.raises(
        AttributeError,
    ):
        result.confidence = 0.50


def test_result_landmarks_are_immutable_snapshot():
    source_landmarks = {
        "nose_tip": (0.50, 0.55),
    }

    result = _make_result(
        landmarks=source_landmarks,
    )

    source_landmarks["nose_tip"] = (
        0.10,
        0.10,
    )

    assert result.landmarks["nose_tip"] == (
        0.50,
        0.55,
    )

    with pytest.raises(
        TypeError,
    ):
        result.landmarks["nose_tip"] = (
            0.20,
            0.20,
        )


def test_result_metadata_is_immutable_snapshot():
    source_metadata = {
        "view_type": "front",
    }

    result = _make_result(
        metadata=source_metadata,
    )

    source_metadata["view_type"] = "profile"

    assert result.metadata["view_type"] == "front"

    with pytest.raises(
        TypeError,
    ):
        result.metadata["view_type"] = "profile"


@pytest.mark.parametrize(
    "arguments",
    [
        {
            "image_width": 0,
        },
        {
            "image_width": -1,
        },
        {
            "image_width": 1000.5,
        },
        {
            "image_width": math.nan,
        },
        {
            "image_height": 0,
        },
        {
            "image_height": -1,
        },
        {
            "image_height": 800.5,
        },
        {
            "image_height": math.inf,
        },
        {
            "landmarks": {},
        },
        {
            "landmarks": {
                "": (0.50, 0.50),
            },
        },
        {
            "landmarks": {
                "   ": (0.50, 0.50),
            },
        },
        {
            "landmarks": {
                123: (0.50, 0.50),
            },
        },
        {
            "landmarks": {
                "nose_tip": (0.50,),
            },
        },
        {
            "landmarks": {
                "nose_tip": (
                    0.50,
                    0.55,
                    0.60,
                ),
            },
        },
        {
            "landmarks": {
                "nose_tip": (
                    -0.01,
                    0.55,
                ),
            },
        },
        {
            "landmarks": {
                "nose_tip": (
                    1.01,
                    0.55,
                ),
            },
        },
        {
            "landmarks": {
                "nose_tip": (
                    0.50,
                    math.nan,
                ),
            },
        },
        {
            "landmarks": {
                "nose_tip": (
                    0.50,
                    math.inf,
                ),
            },
        },
        {
            "confidence": -0.01,
        },
        {
            "confidence": 1.01,
        },
        {
            "confidence": math.nan,
        },
        {
            "confidence": math.inf,
        },
        {
            "provider_id": "",
        },
        {
            "provider_id": "   ",
        },
        {
            "provider_id": 123,
        },
        {
            "metadata": None,
        },
        {
            "metadata": [],
        },
    ],
)
def test_result_rejects_invalid_values(
    arguments,
):
    with pytest.raises(
        ValueError,
    ):
        _make_result(
            **arguments,
        )
