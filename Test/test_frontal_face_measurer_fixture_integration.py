import pytest

from CORE.atlas_frontal_face_measurer import (
    AtlasFrontalFaceMeasurer,
)
from Test.fixtures.portrait.portrait_landmark_fixture import (
    load_frontal_portrait_landmark_fixture,
)


def test_synthetic_fixture_supports_frontal_measurement():
    landmark_result = load_frontal_portrait_landmark_fixture()

    measurements = AtlasFrontalFaceMeasurer.measure(
        landmark_result,
    )

    assert measurements.center_x == pytest.approx(
        0.50,
    )
    assert measurements.center_y == pytest.approx(
        0.50,
    )
    assert measurements.face_width == pytest.approx(
        0.60,
    )
    assert measurements.face_height == pytest.approx(
        0.80,
    )
    assert measurements.eye_spacing == pytest.approx(
        0.26,
    )
    assert measurements.eye_line_angle_degrees == pytest.approx(
        0.0,
    )
    assert measurements.nose_width == pytest.approx(
        0.10,
    )
    assert measurements.nose_length == pytest.approx(
        0.15,
    )
    assert measurements.mouth_width == pytest.approx(
        0.18,
    )
    assert measurements.jaw_width == pytest.approx(
        0.44,
    )
    assert measurements.forehead_height == pytest.approx(
        0.30,
    )


def test_synthetic_fixture_measurement_is_deterministic():
    landmark_result = load_frontal_portrait_landmark_fixture()

    first = AtlasFrontalFaceMeasurer.measure(
        landmark_result,
    )
    second = AtlasFrontalFaceMeasurer.measure(
        landmark_result,
    )

    assert first == second
    assert first is not second
