import pytest

from CORE.atlas_frontal_face_measurements import (
    AtlasFrontalFaceMeasurements,
)
from CORE.atlas_frontal_face_parameter_initializer import (
    AtlasFrontalFaceParameterInitializer,
)
from CORE.atlas_parametric_face_parameters import (
    AtlasParametricFaceParameters,
)
from CORE.atlas_frontal_face_reference_profile import (
    AtlasFrontalFaceReferenceProfile,
)
from CORE.atlas_frontal_face_reference_profile_catalog import (
    AtlasFrontalFaceReferenceProfileCatalog,
)


def _measurements(
    **overrides,
) -> AtlasFrontalFaceMeasurements:
    values = {
        "center_x": 0.50,
        "center_y": 0.50,
        "reference_scale": 0.80,
        "face_width": 0.60,
        "face_height": 0.80,
        "eye_spacing": 0.26,
        "eye_line_angle_degrees": 0.0,
        "nose_width": 0.10,
        "nose_length": 0.15,
        "mouth_width": 0.18,
        "jaw_width": 0.44,
        "forehead_height": 0.30,
    }

    values.update(
        overrides,
    )

    return AtlasFrontalFaceMeasurements(
        **values,
    )


def test_initializer_returns_parametric_face_parameters():
    parameters = AtlasFrontalFaceParameterInitializer.initialize(
        _measurements(),
    )

    assert isinstance(
        parameters,
        AtlasParametricFaceParameters,
    )


def test_neutral_measurements_produce_neutral_parameters():
    parameters = AtlasFrontalFaceParameterInitializer.initialize(
        _measurements(),
    )

    assert parameters.scale == pytest.approx(
        0.80,
    )
    assert parameters.translation_x == pytest.approx(
        0.0,
    )
    assert parameters.translation_y == pytest.approx(
        0.0,
    )
    assert parameters.rotation_degrees == pytest.approx(
        0.0,
    )

    assert parameters.face_width == pytest.approx(
        1.0,
    )
    assert parameters.face_height == pytest.approx(
        1.0,
    )
    assert parameters.eye_spacing == pytest.approx(
        1.0,
    )
    assert parameters.eye_height == pytest.approx(
        1.0,
    )
    assert parameters.nose_width == pytest.approx(
        1.0,
    )
    assert parameters.nose_length == pytest.approx(
        1.0,
    )
    assert parameters.mouth_width == pytest.approx(
        1.0,
    )
    assert parameters.chin_width == pytest.approx(
        1.0,
    )
    assert parameters.chin_length == pytest.approx(
        1.0,
    )
    assert parameters.jaw_width == pytest.approx(
        1.0,
    )
    assert parameters.forehead_height == pytest.approx(
        1.0,
    )


def test_initializer_preserves_pose_measurements():
    parameters = AtlasFrontalFaceParameterInitializer.initialize(
        _measurements(
            center_x=0.54,
            center_y=0.47,
            eye_line_angle_degrees=-3.5,
        ),
    )

    assert parameters.translation_x == pytest.approx(
        0.04,
    )
    assert parameters.translation_y == pytest.approx(
        -0.03,
    )
    assert parameters.rotation_degrees == pytest.approx(
        -3.5,
    )


def test_initializer_normalizes_width_measurements():
    parameters = AtlasFrontalFaceParameterInitializer.initialize(
        _measurements(
            face_width=0.66,
            eye_spacing=0.286,
            nose_width=0.11,
            mouth_width=0.198,
            jaw_width=0.484,
        ),
    )

    assert parameters.face_width == pytest.approx(
        1.10,
    )
    assert parameters.eye_spacing == pytest.approx(
        1.10,
    )
    assert parameters.nose_width == pytest.approx(
        1.10,
    )
    assert parameters.mouth_width == pytest.approx(
        1.10,
    )
    assert parameters.jaw_width == pytest.approx(
        1.10,
    )


def test_initializer_normalizes_vertical_measurements():
    parameters = AtlasFrontalFaceParameterInitializer.initialize(
        _measurements(
            nose_length=0.165,
            forehead_height=0.33,
        ),
    )

    assert parameters.nose_length == pytest.approx(
        1.10,
    )
    assert parameters.forehead_height == pytest.approx(
        1.10,
    )


def test_initializer_uses_face_height_as_reference():
    parameters = AtlasFrontalFaceParameterInitializer.initialize(
        _measurements(
            reference_scale=0.40,
            face_width=0.30,
            face_height=0.40,
            eye_spacing=0.13,
            nose_width=0.05,
            nose_length=0.075,
            mouth_width=0.09,
            jaw_width=0.22,
            forehead_height=0.15,
        ),
    )

    assert parameters.scale == pytest.approx(
        0.40,
    )
    assert parameters.face_width == pytest.approx(
        1.0,
    )
    assert parameters.eye_spacing == pytest.approx(
        1.0,
    )
    assert parameters.nose_width == pytest.approx(
        1.0,
    )
    assert parameters.nose_length == pytest.approx(
        1.0,
    )
    assert parameters.mouth_width == pytest.approx(
        1.0,
    )
    assert parameters.jaw_width == pytest.approx(
        1.0,
    )
    assert parameters.forehead_height == pytest.approx(
        1.0,
    )


def test_initializer_keeps_unmeasured_parameters_neutral():
    parameters = AtlasFrontalFaceParameterInitializer.initialize(
        _measurements(
            face_width=0.72,
            nose_width=0.12,
        ),
    )

    assert parameters.eye_height == 1.0
    assert parameters.chin_width == 1.0
    assert parameters.chin_length == 1.0


def test_initializer_rejects_wrong_input_type():
    with pytest.raises(
        TypeError,
        match="AtlasFrontalFaceMeasurements",
    ):
        AtlasFrontalFaceParameterInitializer.initialize(
            object(),
        )


def test_initializer_is_deterministic():
    measurements = _measurements(
        center_x=0.52,
        face_width=0.63,
        nose_length=0.16,
    )

    first = AtlasFrontalFaceParameterInitializer.initialize(
        measurements,
    )

    second = AtlasFrontalFaceParameterInitializer.initialize(
        measurements,
    )

    assert first == second
    assert first is not second


def _reference_profile(
    **overrides,
) -> AtlasFrontalFaceReferenceProfile:
    values = {
        "name": "custom-reference",
        "face_width_ratio": 0.60,
        "eye_spacing_ratio": 0.26,
        "nose_width_ratio": 0.10,
        "nose_length_ratio": 0.15,
        "mouth_width_ratio": 0.18,
        "jaw_width_ratio": 0.44,
        "forehead_height_ratio": 0.30,
    }

    values.update(
        overrides,
    )

    return AtlasFrontalFaceReferenceProfile(
        **values,
    )


def test_initializer_accepts_reference_profile():
    parameters = AtlasFrontalFaceParameterInitializer.initialize(
        _measurements(),
        reference_profile=_reference_profile(),
    )

    assert isinstance(
        parameters,
        AtlasParametricFaceParameters,
    )


def test_custom_reference_profile_controls_ratios():
    parameters = AtlasFrontalFaceParameterInitializer.initialize(
        _measurements(),
        reference_profile=_reference_profile(),
    )

    assert parameters.face_width == pytest.approx(
        1.25,
    )
    assert parameters.eye_spacing == pytest.approx(
        1.25,
    )
    assert parameters.nose_width == pytest.approx(
        1.25,
    )
    assert parameters.nose_length == pytest.approx(
        1.25,
    )
    assert parameters.mouth_width == pytest.approx(
        1.25,
    )
    assert parameters.jaw_width == pytest.approx(
        1.25,
    )
    assert parameters.forehead_height == pytest.approx(
        1.25,
    )


def test_equivalent_reference_profile_produces_neutral_parameters():
    profile = _reference_profile(
        face_width_ratio=0.7500,
        eye_spacing_ratio=0.3250,
        nose_width_ratio=0.1250,
        nose_length_ratio=0.1875,
        mouth_width_ratio=0.2250,
        jaw_width_ratio=0.5500,
        forehead_height_ratio=0.3750,
    )

    parameters = AtlasFrontalFaceParameterInitializer.initialize(
        _measurements(),
        reference_profile=profile,
    )

    assert parameters.face_width == pytest.approx(
        1.0,
    )
    assert parameters.eye_spacing == pytest.approx(
        1.0,
    )
    assert parameters.nose_width == pytest.approx(
        1.0,
    )
    assert parameters.nose_length == pytest.approx(
        1.0,
    )
    assert parameters.mouth_width == pytest.approx(
        1.0,
    )
    assert parameters.jaw_width == pytest.approx(
        1.0,
    )
    assert parameters.forehead_height == pytest.approx(
        1.0,
    )


def test_initializer_rejects_wrong_reference_profile_type():
    with pytest.raises(
        TypeError,
        match="AtlasFrontalFaceReferenceProfile",
    ):
        AtlasFrontalFaceParameterInitializer.initialize(
            _measurements(),
            reference_profile=object(),
        )


def test_default_reference_profile_is_value_equivalent():
    explicit_profile = AtlasFrontalFaceReferenceProfile(
        name="synthetic-neutral",
        face_width_ratio=0.7500,
        eye_spacing_ratio=0.3250,
        nose_width_ratio=0.1250,
        nose_length_ratio=0.1875,
        mouth_width_ratio=0.2250,
        jaw_width_ratio=0.5500,
        forehead_height_ratio=0.3750,
    )

    implicit = AtlasFrontalFaceParameterInitializer.initialize(
        _measurements(),
    )
    explicit = AtlasFrontalFaceParameterInitializer.initialize(
        _measurements(),
        reference_profile=explicit_profile,
    )

    assert implicit == explicit
    assert implicit is not explicit


def test_default_reference_profile_uses_catalog_instance():
    assert (
        AtlasFrontalFaceParameterInitializer.DEFAULT_REFERENCE_PROFILE
        is AtlasFrontalFaceReferenceProfileCatalog.SYNTHETIC_NEUTRAL
    )
