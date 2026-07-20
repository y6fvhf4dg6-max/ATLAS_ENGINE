import pytest

from CORE.atlas_frontal_face_measurements import (
    AtlasFrontalFaceMeasurements,
)
from CORE.atlas_frontal_face_parameter_initializer import (
    AtlasFrontalFaceParameterInitializer,
)
from CORE.atlas_frontal_face_reference_profile import (
    AtlasFrontalFaceReferenceProfile,
)
from CORE.atlas_frontal_face_surface_comparison_builder import (
    AtlasFrontalFaceSurfaceComparisonBuilder,
)
from CORE.atlas_neutral_parametric_face_surface_builder import (
    AtlasNeutralParametricFaceSurfaceBuilder,
)
from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)
from CORE.atlas_parametric_face_surface_comparison_builder import (
    AtlasParametricFaceSurfaceComparisonBuilder,
)
from CORE.atlas_parametric_face_surface_comparison_result import (
    AtlasParametricFaceSurfaceComparisonResult,
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


def _reference_profile(
    **overrides,
) -> AtlasFrontalFaceReferenceProfile:
    values = {
        "name": "synthetic-neutral",
        "face_width_ratio": 0.7500,
        "eye_spacing_ratio": 0.3250,
        "nose_width_ratio": 0.1250,
        "nose_length_ratio": 0.1875,
        "mouth_width_ratio": 0.2250,
        "jaw_width_ratio": 0.5500,
        "forehead_height_ratio": 0.3750,
    }

    values.update(
        overrides,
    )

    return AtlasFrontalFaceReferenceProfile(
        **values,
    )


def _surface() -> AtlasParametricFaceSurface:
    return AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=41,
        column_count=41,
    )


def test_builder_returns_surface_comparison_result():
    result = AtlasFrontalFaceSurfaceComparisonBuilder.build(
        _surface(),
        measurements=_measurements(),
        reference_profile=_reference_profile(),
    )

    assert isinstance(
        result,
        AtlasParametricFaceSurfaceComparisonResult,
    )


def test_builder_preserves_neutral_surface_reference():
    neutral_surface = _surface()

    result = AtlasFrontalFaceSurfaceComparisonBuilder.build(
        neutral_surface,
        measurements=_measurements(),
        reference_profile=_reference_profile(),
    )

    assert result.neutral_surface is neutral_surface


def test_builder_parameters_match_initializer_output():
    measurements = _measurements(
        center_x=0.53,
        center_y=0.47,
        eye_line_angle_degrees=-3.0,
        face_width=0.66,
        nose_width=0.11,
        forehead_height=0.33,
    )
    reference_profile = _reference_profile()

    expected_parameters = (
        AtlasFrontalFaceParameterInitializer.initialize(
            measurements,
            reference_profile=reference_profile,
        )
    )

    result = AtlasFrontalFaceSurfaceComparisonBuilder.build(
        _surface(),
        measurements=measurements,
        reference_profile=reference_profile,
    )

    assert result.parameters == expected_parameters


def test_builder_matches_explicit_initializer_and_surface_builder_chain():
    neutral_surface = _surface()
    measurements = _measurements(
        center_x=0.52,
        center_y=0.48,
        reference_scale=0.76,
        face_width=0.63,
        eye_spacing=0.28,
        eye_line_angle_degrees=4.0,
        nose_width=0.11,
        nose_length=0.16,
        mouth_width=0.19,
        jaw_width=0.47,
        forehead_height=0.32,
    )
    reference_profile = _reference_profile()

    parameters = AtlasFrontalFaceParameterInitializer.initialize(
        measurements,
        reference_profile=reference_profile,
    )

    expected = AtlasParametricFaceSurfaceComparisonBuilder.build(
        neutral_surface,
        parameters=parameters,
    )

    result = AtlasFrontalFaceSurfaceComparisonBuilder.build(
        neutral_surface,
        measurements=measurements,
        reference_profile=reference_profile,
    )

    assert result.parameters == expected.parameters
    assert result.adapted_surface.x_coordinates == pytest.approx(
        expected.adapted_surface.x_coordinates,
    )
    assert result.adapted_surface.y_coordinates == pytest.approx(
        expected.adapted_surface.y_coordinates,
    )
    assert result.adapted_surface.z_coordinates == pytest.approx(
        expected.adapted_surface.z_coordinates,
    )
    assert result.x_deltas == pytest.approx(
        expected.x_deltas,
    )
    assert result.y_deltas == pytest.approx(
        expected.y_deltas,
    )
    assert result.z_deltas == pytest.approx(
        expected.z_deltas,
    )


def test_reference_profile_controls_adapted_surface():
    neutral_surface = _surface()
    measurements = _measurements()

    neutral_profile = _reference_profile()

    narrower_reference = _reference_profile(
        name="narrower-reference",
        face_width_ratio=0.60,
        eye_spacing_ratio=0.26,
        nose_width_ratio=0.10,
        nose_length_ratio=0.15,
        mouth_width_ratio=0.18,
        jaw_width_ratio=0.44,
        forehead_height_ratio=0.30,
    )

    neutral_result = AtlasFrontalFaceSurfaceComparisonBuilder.build(
        neutral_surface,
        measurements=measurements,
        reference_profile=neutral_profile,
    )

    adapted_result = AtlasFrontalFaceSurfaceComparisonBuilder.build(
        neutral_surface,
        measurements=measurements,
        reference_profile=narrower_reference,
    )

    assert neutral_result.parameters.face_width == pytest.approx(
        1.0,
    )
    assert adapted_result.parameters.face_width == pytest.approx(
        1.25,
    )

    assert not adapted_result.adapted_surface.x_coordinates == pytest.approx(
        neutral_result.adapted_surface.x_coordinates,
    )


def test_builder_does_not_modify_inputs():
    neutral_surface = _surface()
    measurements = _measurements()
    reference_profile = _reference_profile()

    original_x = neutral_surface.x_coordinates.copy()
    original_y = neutral_surface.y_coordinates.copy()
    original_z = neutral_surface.z_coordinates.copy()

    AtlasFrontalFaceSurfaceComparisonBuilder.build(
        neutral_surface,
        measurements=measurements,
        reference_profile=reference_profile,
    )

    assert neutral_surface.x_coordinates == pytest.approx(
        original_x,
    )
    assert neutral_surface.y_coordinates == pytest.approx(
        original_y,
    )
    assert neutral_surface.z_coordinates == pytest.approx(
        original_z,
    )

    assert measurements == _measurements()
    assert reference_profile == _reference_profile()


def test_builder_is_deterministic():
    neutral_surface = _surface()
    measurements = _measurements(
        center_x=0.51,
        face_width=0.64,
        nose_length=0.16,
        jaw_width=0.46,
    )
    reference_profile = _reference_profile()

    first = AtlasFrontalFaceSurfaceComparisonBuilder.build(
        neutral_surface,
        measurements=measurements,
        reference_profile=reference_profile,
    )

    second = AtlasFrontalFaceSurfaceComparisonBuilder.build(
        neutral_surface,
        measurements=measurements,
        reference_profile=reference_profile,
    )

    assert first.parameters == second.parameters
    assert first.adapted_surface.x_coordinates == pytest.approx(
        second.adapted_surface.x_coordinates,
    )
    assert first.adapted_surface.y_coordinates == pytest.approx(
        second.adapted_surface.y_coordinates,
    )
    assert first.adapted_surface.z_coordinates == pytest.approx(
        second.adapted_surface.z_coordinates,
    )


def test_builder_rejects_wrong_surface_type():
    with pytest.raises(
        TypeError,
        match="AtlasParametricFaceSurface",
    ):
        AtlasFrontalFaceSurfaceComparisonBuilder.build(
            object(),
            measurements=_measurements(),
            reference_profile=_reference_profile(),
        )


def test_builder_rejects_wrong_measurements_type():
    with pytest.raises(
        TypeError,
        match="AtlasFrontalFaceMeasurements",
    ):
        AtlasFrontalFaceSurfaceComparisonBuilder.build(
            _surface(),
            measurements=object(),
            reference_profile=_reference_profile(),
        )


def test_builder_rejects_wrong_reference_profile_type():
    with pytest.raises(
        TypeError,
        match="AtlasFrontalFaceReferenceProfile",
    ):
        AtlasFrontalFaceSurfaceComparisonBuilder.build(
            _surface(),
            measurements=_measurements(),
            reference_profile=object(),
        )
