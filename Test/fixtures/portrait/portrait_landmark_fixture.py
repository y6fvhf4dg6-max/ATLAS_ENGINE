from __future__ import annotations

from CORE.atlas_portrait_landmark_result import (
    AtlasPortraitLandmarkResult,
)

_FIXTURE_LANDMARKS = {
    "left_eye_outer": (
        0.30,
        0.34,
    ),
    "left_eye_inner": (
        0.44,
        0.34,
    ),
    "right_eye_inner": (
        0.56,
        0.34,
    ),
    "right_eye_outer": (
        0.70,
        0.34,
    ),
    "nose_root": (
        0.50,
        0.40,
    ),
    "nose_left": (
        0.45,
        0.55,
    ),
    "nose_tip": (
        0.50,
        0.55,
    ),
    "nose_right": (
        0.55,
        0.55,
    ),
    "mouth_left": (
        0.41,
        0.69,
    ),
    "mouth_right": (
        0.59,
        0.69,
    ),
    "chin_tip": (
        0.50,
        0.88,
    ),
}


def fixture_landmark_names() -> tuple[str, ...]:
    """
    Returns all synthetic fixture landmark names
    in deterministic order.
    """

    return tuple(sorted(_FIXTURE_LANDMARKS))


def load_frontal_portrait_landmark_fixture() -> AtlasPortraitLandmarkResult:
    """
    Returns a deterministic synthetic frontal
    portrait landmark result.

    The fixture is intended for provider, fitting,
    projection, and serialization tests without
    depending on private portrait images or ML models.
    """

    return AtlasPortraitLandmarkResult(
        image_width=1000,
        image_height=1200,
        landmarks=dict(_FIXTURE_LANDMARKS),
        confidence=1.0,
        provider_id=("synthetic-frontal-fixture"),
        metadata={
            "fixture_name": ("synthetic_frontal_portrait_v1"),
            "view_type": "front",
            "synthetic": True,
        },
    )
