import pytest

from CORE.atlas_neutral_parametric_face_surface_builder import (
    AtlasNeutralParametricFaceSurfaceBuilder,
)
from CORE.atlas_parametric_face_deformation_pipeline import (
    AtlasParametricFaceDeformationPipeline,
)
from CORE.atlas_parametric_face_parameters import (
    AtlasParametricFaceParameters,
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


def _surface() -> AtlasParametricFaceSurface:
    return AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=41,
        column_count=41,
    )


def _parameters(
    **overrides,
) -> AtlasParametricFaceParameters:
    values = {
        "scale": 1.0,
        "translation_x": 0.0,
        "translation_y": 0.0,
        "rotation_degrees": 0.0,
        "face_width": 1.0,
        "face_height": 1.0,
        "eye_spacing": 1.0,
        "eye_height": 1.0,
        "nose_width": 1.0,
        "nose_length": 1.0,
        "mouth_width": 1.0,
        "chin_width": 1.0,
        "chin_length": 1.0,
        "jaw_width": 1.0,
        "forehead_height": 1.0,
    }

    values.update(
        overrides,
    )

    return AtlasParametricFaceParameters(
        **values,
    )


def test_builder_returns_surface_comparison_result():
    result = AtlasParametricFaceSurfaceComparisonBuilder.build(
        _surface(),
        parameters=_parameters(),
    )

    assert isinstance(
        result,
        AtlasParametricFaceSurfaceComparisonResult,
    )


def test_builder_preserves_neutral_surface_reference():
    neutral = _surface()

    result = AtlasParametricFaceSurfaceComparisonBuilder.build(
        neutral,
        parameters=_parameters(),
    )

    assert result.neutral_surface is neutral


def test_builder_preserves_parameters_reference():
    parameters = _parameters(
        nose_width=1.20,
    )

    result = AtlasParametricFaceSurfaceComparisonBuilder.build(
        _surface(),
        parameters=parameters,
    )

    assert result.parameters is parameters


def test_builder_adapted_surface_matches_deformation_pipeline():
    neutral = _surface()
    parameters = _parameters(
        scale=0.86,
        translation_x=0.08,
        translation_y=-0.05,
        rotation_degrees=6.0,
        face_width=1.12,
        face_height=0.94,
        eye_spacing=1.18,
        eye_height=0.90,
        nose_width=1.24,
        nose_length=1.16,
        mouth_width=0.92,
        chin_width=1.08,
        chin_length=1.10,
        jaw_width=1.06,
        forehead_height=1.14,
    )

    expected = AtlasParametricFaceDeformationPipeline.deform(
        neutral,
        parameters=parameters,
    )

    result = AtlasParametricFaceSurfaceComparisonBuilder.build(
        neutral,
        parameters=parameters,
    )

    assert result.adapted_surface.x_coordinates == pytest.approx(
        expected.x_coordinates,
    )
    assert result.adapted_surface.y_coordinates == pytest.approx(
        expected.y_coordinates,
    )
    assert result.adapted_surface.z_coordinates == pytest.approx(
        expected.z_coordinates,
    )


def test_identity_parameters_report_no_coordinate_change():
    result = AtlasParametricFaceSurfaceComparisonBuilder.build(
        _surface(),
        parameters=_parameters(),
    )

    assert not result.has_coordinate_change
    assert result.maximum_absolute_x_delta == pytest.approx(
        0.0,
    )
    assert result.maximum_absolute_y_delta == pytest.approx(
        0.0,
    )
    assert result.maximum_absolute_z_delta == pytest.approx(
        0.0,
    )


def test_non_identity_parameters_report_coordinate_change():
    result = AtlasParametricFaceSurfaceComparisonBuilder.build(
        _surface(),
        parameters=_parameters(
            nose_width=1.25,
            jaw_width=1.12,
            forehead_height=1.10,
        ),
    )

    assert result.has_coordinate_change
    assert result.maximum_absolute_x_delta > 0.0
    assert result.maximum_absolute_y_delta > 0.0


def test_builder_does_not_modify_neutral_surface():
    neutral = _surface()

    original_x = neutral.x_coordinates.copy()
    original_y = neutral.y_coordinates.copy()
    original_z = neutral.z_coordinates.copy()

    AtlasParametricFaceSurfaceComparisonBuilder.build(
        neutral,
        parameters=_parameters(
            scale=0.90,
            rotation_degrees=5.0,
            eye_spacing=1.15,
            chin_length=1.12,
        ),
    )

    assert neutral.x_coordinates == pytest.approx(
        original_x,
    )
    assert neutral.y_coordinates == pytest.approx(
        original_y,
    )
    assert neutral.z_coordinates == pytest.approx(
        original_z,
    )


def test_builder_is_deterministic():
    neutral = _surface()
    parameters = _parameters(
        scale=0.88,
        translation_x=0.03,
        translation_y=-0.02,
        rotation_degrees=-4.0,
        nose_length=1.14,
        mouth_width=0.94,
        jaw_width=1.08,
    )

    first = AtlasParametricFaceSurfaceComparisonBuilder.build(
        neutral,
        parameters=parameters,
    )
    second = AtlasParametricFaceSurfaceComparisonBuilder.build(
        neutral,
        parameters=parameters,
    )

    assert first.adapted_surface.x_coordinates == pytest.approx(
        second.adapted_surface.x_coordinates,
    )
    assert first.adapted_surface.y_coordinates == pytest.approx(
        second.adapted_surface.y_coordinates,
    )
    assert first.adapted_surface.z_coordinates == pytest.approx(
        second.adapted_surface.z_coordinates,
    )

    assert first.x_deltas == pytest.approx(
        second.x_deltas,
    )
    assert first.y_deltas == pytest.approx(
        second.y_deltas,
    )
    assert first.z_deltas == pytest.approx(
        second.z_deltas,
    )


def test_builder_rejects_wrong_surface_type():
    with pytest.raises(
        TypeError,
        match="AtlasParametricFaceSurface",
    ):
        AtlasParametricFaceSurfaceComparisonBuilder.build(
            object(),
            parameters=_parameters(),
        )


def test_builder_rejects_wrong_parameters_type():
    with pytest.raises(
        TypeError,
        match="AtlasParametricFaceParameters",
    ):
        AtlasParametricFaceSurfaceComparisonBuilder.build(
            _surface(),
            parameters=object(),
        )
