import math

import pytest

from CORE.atlas_frontal_face_measurements import (
    AtlasFrontalFaceMeasurements,
)
from CORE.atlas_frontal_face_measurer import (
    AtlasFrontalFaceMeasurer,
)
from CORE.atlas_portrait_landmark_result import (
    AtlasPortraitLandmarkResult,
)


def _landmark_result(
    **landmark_overrides,
) -> AtlasPortraitLandmarkResult:
    landmarks = {
        "left_face_edge": (
            0.80,
            0.45,
        ),
        "right_face_edge": (
            0.20,
            0.45,
        ),
        "hairline_center": (
            0.50,
            0.10,
        ),
        "left_eye_center": (
            0.62,
            0.35,
        ),
        "right_eye_center": (
            0.38,
            0.35,
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
            0.58,
        ),
        "nose_right": (
            0.55,
            0.55,
        ),
        "mouth_left": (
            0.40,
            0.70,
        ),
        "mouth_right": (
            0.60,
            0.70,
        ),
        "left_jaw": (
            0.72,
            0.78,
        ),
        "chin_tip": (
            0.50,
            0.88,
        ),
        "right_jaw": (
            0.28,
            0.78,
        ),
    }

    landmarks.update(
        landmark_overrides,
    )

    return AtlasPortraitLandmarkResult(
        image_width=1000,
        image_height=1200,
        landmarks=landmarks,
        confidence=1.0,
        provider_id="test-provider",
        metadata={
            "view_type": "front",
        },
    )


def test_measurer_returns_frontal_face_measurements():
    result = _landmark_result()

    measurements = AtlasFrontalFaceMeasurer.measure(
        result,
    )

    assert isinstance(
        measurements,
        AtlasFrontalFaceMeasurements,
    )


def test_measurer_calculates_face_center():
    measurements = AtlasFrontalFaceMeasurer.measure(
        _landmark_result(),
    )

    assert measurements.center_x == pytest.approx(
        0.50,
    )
    assert measurements.center_y == pytest.approx(
        0.49,
    )


def test_measurer_calculates_face_dimensions():
    measurements = AtlasFrontalFaceMeasurer.measure(
        _landmark_result(),
    )

    assert measurements.face_width == pytest.approx(
        0.60,
    )
    assert measurements.face_height == pytest.approx(
        0.78,
    )
    assert measurements.reference_scale == pytest.approx(
        measurements.face_height,
    )


def test_measurer_calculates_eye_geometry():
    measurements = AtlasFrontalFaceMeasurer.measure(
        _landmark_result(),
    )

    assert measurements.eye_spacing == pytest.approx(
        0.24,
    )
    assert measurements.eye_line_angle_degrees == pytest.approx(
        0.0,
    )


def test_measurer_calculates_nose_geometry():
    measurements = AtlasFrontalFaceMeasurer.measure(
        _landmark_result(),
    )

    assert measurements.nose_width == pytest.approx(
        0.10,
    )
    assert measurements.nose_length == pytest.approx(
        0.18,
    )


def test_measurer_calculates_mouth_and_jaw_width():
    measurements = AtlasFrontalFaceMeasurer.measure(
        _landmark_result(),
    )

    assert measurements.mouth_width == pytest.approx(
        0.20,
    )
    assert measurements.jaw_width == pytest.approx(
        0.44,
    )


def test_measurer_calculates_forehead_height():
    measurements = AtlasFrontalFaceMeasurer.measure(
        _landmark_result(),
    )

    assert measurements.forehead_height == pytest.approx(
        0.30,
    )


def test_measurer_calculates_signed_eye_line_angle():
    result = _landmark_result(
        left_eye_center=(
            0.62,
            0.33,
        ),
        right_eye_center=(
            0.38,
            0.37,
        ),
    )

    measurements = AtlasFrontalFaceMeasurer.measure(
        result,
    )

    expected_angle = math.degrees(
        math.atan2(
            -0.04,
            0.24,
        )
    )

    assert measurements.eye_line_angle_degrees == pytest.approx(
        expected_angle,
    )


def test_measurer_rejects_wrong_input_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitLandmarkResult",
    ):
        AtlasFrontalFaceMeasurer.measure(
            object(),
        )


def test_measurer_rejects_missing_required_landmark():
    result = _landmark_result()

    incomplete_landmarks = dict(
        result.landmarks,
    )
    del incomplete_landmarks["nose_tip"]

    incomplete_result = AtlasPortraitLandmarkResult(
        image_width=result.image_width,
        image_height=result.image_height,
        landmarks=incomplete_landmarks,
        confidence=result.confidence,
        provider_id=result.provider_id,
        metadata=result.metadata,
    )

    with pytest.raises(
        ValueError,
        match="nose_tip",
    ):
        AtlasFrontalFaceMeasurer.measure(
            incomplete_result,
        )


def test_measurer_rejects_zero_face_width():
    result = _landmark_result(
        left_face_edge=(
            0.50,
            0.45,
        ),
        right_face_edge=(
            0.50,
            0.45,
        ),
    )

    with pytest.raises(
        ValueError,
        match="face_width",
    ):
        AtlasFrontalFaceMeasurer.measure(
            result,
        )


def test_measurer_is_deterministic():
    result = _landmark_result()

    first = AtlasFrontalFaceMeasurer.measure(
        result,
    )
    second = AtlasFrontalFaceMeasurer.measure(
        result,
    )

    assert first == second
    assert first is not second
