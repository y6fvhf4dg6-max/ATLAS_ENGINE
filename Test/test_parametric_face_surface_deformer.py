import numpy as np
import pytest

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
    return AtlasParametricFaceSurface(
        x_coordinates=[
            [-1.0, 0.0, 1.0],
            [-1.0, 0.0, 1.0],
        ],
        y_coordinates=[
            [-0.5, -0.5, -0.5],
            [0.5, 0.5, 0.5],
        ],
        z_coordinates=[
            [0.0, 0.4, 0.0],
            [0.1, 0.8, 0.1],
        ],
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


def test_deformer_returns_parametric_face_surface():
    result = AtlasParametricFaceSurfaceDeformer.deform(
        _surface(),
        parameters=_parameters(),
    )

    assert isinstance(
        result,
        AtlasParametricFaceSurface,
    )


def test_identity_parameters_preserve_coordinates():
    source = _surface()

    result = AtlasParametricFaceSurfaceDeformer.deform(
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


def test_deformer_returns_independent_surface():
    source = _surface()

    result = AtlasParametricFaceSurfaceDeformer.deform(
        source,
        parameters=_parameters(),
    )

    assert result is not source
    assert result.x_coordinates is not source.x_coordinates
    assert result.y_coordinates is not source.y_coordinates
    assert result.z_coordinates is not source.z_coordinates


def test_face_width_scales_x_coordinates_only():
    source = _surface()

    result = AtlasParametricFaceSurfaceDeformer.deform(
        source,
        parameters=_parameters(
            face_width=1.25,
        ),
    )

    assert result.x_coordinates == pytest.approx(
        source.x_coordinates * 1.25,
    )
    assert result.y_coordinates == pytest.approx(
        source.y_coordinates,
    )
    assert result.z_coordinates == pytest.approx(
        source.z_coordinates,
    )


def test_face_height_scales_y_coordinates_only():
    source = _surface()

    result = AtlasParametricFaceSurfaceDeformer.deform(
        source,
        parameters=_parameters(
            face_height=0.80,
        ),
    )

    assert result.x_coordinates == pytest.approx(
        source.x_coordinates,
    )
    assert result.y_coordinates == pytest.approx(
        source.y_coordinates * 0.80,
    )
    assert result.z_coordinates == pytest.approx(
        source.z_coordinates,
    )


def test_global_scale_scales_xyz_coordinates():
    source = _surface()

    result = AtlasParametricFaceSurfaceDeformer.deform(
        source,
        parameters=_parameters(
            scale=1.50,
        ),
    )

    assert result.x_coordinates == pytest.approx(
        source.x_coordinates * 1.50,
    )
    assert result.y_coordinates == pytest.approx(
        source.y_coordinates * 1.50,
    )
    assert result.z_coordinates == pytest.approx(
        source.z_coordinates * 1.50,
    )


def test_translation_offsets_xy_coordinates_only():
    source = _surface()

    result = AtlasParametricFaceSurfaceDeformer.deform(
        source,
        parameters=_parameters(
            translation_x=0.25,
            translation_y=-0.40,
        ),
    )

    assert result.x_coordinates == pytest.approx(
        source.x_coordinates + 0.25,
    )
    assert result.y_coordinates == pytest.approx(
        source.y_coordinates - 0.40,
    )
    assert result.z_coordinates == pytest.approx(
        source.z_coordinates,
    )


def test_rotation_applies_counterclockwise_in_xy_plane():
    source = AtlasParametricFaceSurface(
        x_coordinates=[
            [1.0, 0.0],
            [-1.0, 0.0],
        ],
        y_coordinates=[
            [0.0, 1.0],
            [0.0, -1.0],
        ],
        z_coordinates=[
            [0.1, 0.2],
            [0.3, 0.4],
        ],
    )

    result = AtlasParametricFaceSurfaceDeformer.deform(
        source,
        parameters=_parameters(
            rotation_degrees=90.0,
        ),
    )

    assert result.x_coordinates == pytest.approx(
        np.array(
            [
                [0.0, -1.0],
                [0.0, 1.0],
            ],
            dtype=np.float64,
        ),
        abs=1e-12,
    )
    assert result.y_coordinates == pytest.approx(
        np.array(
            [
                [1.0, 0.0],
                [-1.0, 0.0],
            ],
            dtype=np.float64,
        ),
        abs=1e-12,
    )
    assert result.z_coordinates == pytest.approx(
        source.z_coordinates,
    )


def test_deformation_order_is_local_scale_global_scale_rotation_translation():
    source = AtlasParametricFaceSurface(
        x_coordinates=[
            [1.0, 0.0],
            [-1.0, 0.0],
        ],
        y_coordinates=[
            [0.0, 1.0],
            [0.0, -1.0],
        ],
        z_coordinates=[
            [0.5, 0.5],
            [0.5, 0.5],
        ],
    )

    result = AtlasParametricFaceSurfaceDeformer.deform(
        source,
        parameters=_parameters(
            face_width=2.0,
            face_height=3.0,
            scale=0.5,
            rotation_degrees=90.0,
            translation_x=0.25,
            translation_y=-0.50,
        ),
    )

    assert result.x_coordinates == pytest.approx(
        np.array(
            [
                [0.25, -1.25],
                [0.25, 1.75],
            ],
            dtype=np.float64,
        ),
        abs=1e-12,
    )
    assert result.y_coordinates == pytest.approx(
        np.array(
            [
                [0.50, -0.50],
                [-1.50, -0.50],
            ],
            dtype=np.float64,
        ),
        abs=1e-12,
    )
    assert result.z_coordinates == pytest.approx(
        np.array(
            [
                [0.25, 0.25],
                [0.25, 0.25],
            ],
            dtype=np.float64,
        ),
    )


def test_deformer_does_not_modify_source_surface():
    source = _surface()

    original_x = source.x_coordinates.copy()
    original_y = source.y_coordinates.copy()
    original_z = source.z_coordinates.copy()

    AtlasParametricFaceSurfaceDeformer.deform(
        source,
        parameters=_parameters(
            face_width=1.20,
            face_height=0.90,
            scale=1.30,
            rotation_degrees=12.0,
            translation_x=0.10,
            translation_y=-0.05,
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


def test_deformer_is_deterministic():
    source = _surface()
    parameters = _parameters(
        face_width=1.15,
        face_height=0.95,
        scale=1.10,
        rotation_degrees=-7.5,
        translation_x=0.03,
        translation_y=-0.04,
    )

    first = AtlasParametricFaceSurfaceDeformer.deform(
        source,
        parameters=parameters,
    )
    second = AtlasParametricFaceSurfaceDeformer.deform(
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

    assert first is not second


def test_deformer_rejects_wrong_surface_type():
    with pytest.raises(
        TypeError,
        match="AtlasParametricFaceSurface",
    ):
        AtlasParametricFaceSurfaceDeformer.deform(
            object(),
            parameters=_parameters(),
        )


def test_deformer_rejects_wrong_parameters_type():
    with pytest.raises(
        TypeError,
        match="AtlasParametricFaceParameters",
    ):
        AtlasParametricFaceSurfaceDeformer.deform(
            _surface(),
            parameters=object(),
        )
