import numpy as np
import pytest

from CORE.atlas_neutral_parametric_face_surface_builder import (
    AtlasNeutralParametricFaceSurfaceBuilder,
)
from CORE.atlas_parametric_face_deformation_pipeline import (
    AtlasParametricFaceDeformationPipeline,
)
from CORE.atlas_parametric_face_local_deformer import (
    AtlasParametricFaceLocalDeformer,
)
from CORE.atlas_parametric_face_parameters import (
    AtlasParametricFaceParameters,
)
from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)
from CORE.atlas_parametric_face_surface_deformer import (
    AtlasParametricFaceSurfaceDeformer,
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


def test_pipeline_returns_parametric_face_surface():
    result = AtlasParametricFaceDeformationPipeline.deform(
        _surface(),
        parameters=_parameters(),
    )

    assert isinstance(
        result,
        AtlasParametricFaceSurface,
    )


def test_identity_parameters_preserve_surface():
    source = _surface()

    result = AtlasParametricFaceDeformationPipeline.deform(
        source,
        parameters=_parameters(),
    )

    assert result.x_coordinates == pytest.approx(
        source.x_coordinates,
    )
    assert result.y_coordinates == pytest.approx(
        source.y_coordinates,
    )
    assert result.z_coordinates == pytest.approx(
        source.z_coordinates,
    )


def test_pipeline_matches_explicit_local_then_global_order():
    source = _surface()
    parameters = _parameters(
        scale=0.85,
        translation_x=0.12,
        translation_y=-0.08,
        rotation_degrees=7.5,
        face_width=1.15,
        face_height=0.92,
        eye_spacing=1.20,
        eye_height=0.88,
        nose_width=1.25,
        nose_length=1.18,
        mouth_width=0.90,
        chin_width=1.10,
        chin_length=1.12,
        jaw_width=1.08,
        forehead_height=1.16,
    )

    locally_deformed = AtlasParametricFaceLocalDeformer.deform(
        source,
        parameters=parameters,
    )

    expected = AtlasParametricFaceSurfaceDeformer.deform(
        locally_deformed,
        parameters=parameters,
    )

    result = AtlasParametricFaceDeformationPipeline.deform(
        source,
        parameters=parameters,
    )

    assert result.x_coordinates == pytest.approx(
        expected.x_coordinates,
    )
    assert result.y_coordinates == pytest.approx(
        expected.y_coordinates,
    )
    assert result.z_coordinates == pytest.approx(
        expected.z_coordinates,
    )


def test_pipeline_does_not_match_global_then_local_order():
    source = _surface()
    parameters = _parameters(
        scale=0.90,
        translation_x=0.10,
        translation_y=-0.06,
        rotation_degrees=9.0,
        face_width=1.12,
        face_height=0.94,
        eye_spacing=1.22,
        nose_width=1.28,
        mouth_width=0.88,
        jaw_width=1.10,
        forehead_height=1.14,
    )

    globally_deformed = AtlasParametricFaceSurfaceDeformer.deform(
        source,
        parameters=parameters,
    )

    wrong_order = AtlasParametricFaceLocalDeformer.deform(
        globally_deformed,
        parameters=parameters,
    )

    result = AtlasParametricFaceDeformationPipeline.deform(
        source,
        parameters=parameters,
    )

    assert not np.allclose(
        result.x_coordinates,
        wrong_order.x_coordinates,
    )
    assert not np.allclose(
        result.y_coordinates,
        wrong_order.y_coordinates,
    )


def test_pipeline_preserves_source_surface():
    source = _surface()

    original_x = source.x_coordinates.copy()
    original_y = source.y_coordinates.copy()
    original_z = source.z_coordinates.copy()

    AtlasParametricFaceDeformationPipeline.deform(
        source,
        parameters=_parameters(
            scale=0.90,
            rotation_degrees=5.0,
            nose_width=1.20,
            jaw_width=1.15,
        ),
    )

    assert source.x_coordinates == pytest.approx(
        original_x,
    )
    assert source.y_coordinates == pytest.approx(
        original_y,
    )
    assert source.z_coordinates == pytest.approx(
        original_z,
    )


def test_pipeline_is_deterministic():
    source = _surface()
    parameters = _parameters(
        scale=0.88,
        translation_x=0.04,
        translation_y=-0.03,
        rotation_degrees=-4.0,
        eye_spacing=1.12,
        nose_length=1.15,
        chin_length=1.08,
    )

    first = AtlasParametricFaceDeformationPipeline.deform(
        source,
        parameters=parameters,
    )
    second = AtlasParametricFaceDeformationPipeline.deform(
        source,
        parameters=parameters,
    )

    assert first.x_coordinates == pytest.approx(
        second.x_coordinates,
    )
    assert first.y_coordinates == pytest.approx(
        second.y_coordinates,
    )
    assert first.z_coordinates == pytest.approx(
        second.z_coordinates,
    )


def test_pipeline_rejects_wrong_surface_type():
    with pytest.raises(
        TypeError,
        match="AtlasParametricFaceSurface",
    ):
        AtlasParametricFaceDeformationPipeline.deform(
            object(),
            parameters=_parameters(),
        )


def test_pipeline_rejects_wrong_parameters_type():
    with pytest.raises(
        TypeError,
        match="AtlasParametricFaceParameters",
    ):
        AtlasParametricFaceDeformationPipeline.deform(
            _surface(),
            parameters=object(),
        )
