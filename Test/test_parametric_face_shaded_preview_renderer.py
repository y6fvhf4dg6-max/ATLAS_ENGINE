import math

import numpy as np
import pytest

from CORE.atlas_neutral_parametric_face_surface_builder import (
    AtlasNeutralParametricFaceSurfaceBuilder,
)
from CORE.atlas_parametric_face_shaded_preview_renderer import (
    AtlasParametricFaceShadedPreviewRenderer,
)
from CORE.atlas_parametric_face_shaded_preview_result import (
    AtlasParametricFaceShadedPreviewResult,
)
from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)


def _flat_surface(
    *,
    row_count=5,
    column_count=7,
) -> AtlasParametricFaceSurface:
    x_axis = np.linspace(
        -1.0,
        1.0,
        column_count,
        dtype=np.float64,
    )
    y_axis = np.linspace(
        -1.0,
        1.0,
        row_count,
        dtype=np.float64,
    )

    x_coordinates, y_coordinates = np.meshgrid(
        x_axis,
        y_axis,
    )

    return AtlasParametricFaceSurface(
        x_coordinates=x_coordinates,
        y_coordinates=y_coordinates,
        z_coordinates=np.zeros_like(
            x_coordinates,
        ),
    )


def _sloped_surface() -> AtlasParametricFaceSurface:
    x_axis = np.linspace(
        -1.0,
        1.0,
        7,
        dtype=np.float64,
    )
    y_axis = np.linspace(
        -1.0,
        1.0,
        5,
        dtype=np.float64,
    )

    x_coordinates, y_coordinates = np.meshgrid(
        x_axis,
        y_axis,
    )

    z_coordinates = (
        0.25 * x_coordinates
        - 0.15 * y_coordinates
    )

    return AtlasParametricFaceSurface(
        x_coordinates=x_coordinates,
        y_coordinates=y_coordinates,
        z_coordinates=z_coordinates,
    )


def test_renderer_returns_shaded_preview_result():
    result = AtlasParametricFaceShadedPreviewRenderer.render(
        _flat_surface(),
    )

    assert isinstance(
        result,
        AtlasParametricFaceShadedPreviewResult,
    )


def test_renderer_preserves_surface_shape():
    surface = _flat_surface(
        row_count=6,
        column_count=8,
    )

    result = AtlasParametricFaceShadedPreviewRenderer.render(
        surface,
    )

    assert result.shape == surface.shape


def test_default_light_direction_is_normalized():
    result = AtlasParametricFaceShadedPreviewRenderer.render(
        _flat_surface(),
    )

    magnitude = math.sqrt(
        sum(
            component * component
            for component in result.light_direction
        )
    )

    assert magnitude == pytest.approx(
        1.0,
    )


def test_flat_surface_facing_light_has_uniform_shading():
    result = AtlasParametricFaceShadedPreviewRenderer.render(
        _flat_surface(),
        light_direction=(
            0.0,
            0.0,
            1.0,
        ),
        ambient_strength=0.20,
        diffuse_strength=0.80,
    )

    assert result.shading == pytest.approx(
        np.ones(
            result.shape,
            dtype=np.float64,
        )
    )

    assert np.all(
        result.preview == 255
    )


def test_flat_surface_back_facing_light_receives_ambient_only():
    result = AtlasParametricFaceShadedPreviewRenderer.render(
        _flat_surface(),
        light_direction=(
            0.0,
            0.0,
            -1.0,
        ),
        ambient_strength=0.20,
        diffuse_strength=0.80,
    )

    assert result.shading == pytest.approx(
        np.full(
            result.shape,
            0.20,
            dtype=np.float64,
        )
    )

    assert np.all(
        result.preview == 51
    )


def test_zero_diffuse_strength_produces_uniform_ambient():
    result = AtlasParametricFaceShadedPreviewRenderer.render(
        _sloped_surface(),
        light_direction=(
            0.4,
            -0.5,
            0.7681145747868608,
        ),
        ambient_strength=0.30,
        diffuse_strength=0.0,
    )

    assert result.shading == pytest.approx(
        np.full(
            result.shape,
            0.30,
            dtype=np.float64,
        )
    )

    assert np.all(
        result.preview == 76
    )


def test_renderer_generates_uint8_preview_from_shading():
    result = AtlasParametricFaceShadedPreviewRenderer.render(
        _sloped_surface(),
        light_direction=(
            0.0,
            0.0,
            1.0,
        ),
        ambient_strength=0.25,
        diffuse_strength=0.75,
    )

    expected_preview = np.rint(
        result.shading * 255.0
    ).astype(
        np.uint8,
    )

    assert result.preview.dtype == np.uint8
    assert np.array_equal(
        result.preview,
        expected_preview,
    )


def test_renderer_produces_nonuniform_neutral_face_shading():
    surface = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=61,
        column_count=61,
    )

    result = AtlasParametricFaceShadedPreviewRenderer.render(
        surface,
    )

    assert result.maximum_intensity > result.minimum_intensity
    assert np.unique(
        result.preview,
    ).size > 10


def test_renderer_does_not_modify_surface():
    surface = _sloped_surface()

    original_x = surface.x_coordinates.copy()
    original_y = surface.y_coordinates.copy()
    original_z = surface.z_coordinates.copy()

    AtlasParametricFaceShadedPreviewRenderer.render(
        surface,
    )

    assert surface.x_coordinates == pytest.approx(
        original_x,
    )
    assert surface.y_coordinates == pytest.approx(
        original_y,
    )
    assert surface.z_coordinates == pytest.approx(
        original_z,
    )


def test_renderer_is_deterministic():
    surface = AtlasNeutralParametricFaceSurfaceBuilder.build(
        row_count=41,
        column_count=41,
    )

    first = AtlasParametricFaceShadedPreviewRenderer.render(
        surface,
        light_direction=(
            0.3,
            -0.4,
            0.8660254037844386,
        ),
        ambient_strength=0.24,
        diffuse_strength=0.76,
    )

    second = AtlasParametricFaceShadedPreviewRenderer.render(
        surface,
        light_direction=(
            0.3,
            -0.4,
            0.8660254037844386,
        ),
        ambient_strength=0.24,
        diffuse_strength=0.76,
    )

    assert first.shading == pytest.approx(
        second.shading,
    )
    assert np.array_equal(
        first.preview,
        second.preview,
    )


def test_renderer_rejects_wrong_surface_type():
    with pytest.raises(
        TypeError,
        match="AtlasParametricFaceSurface",
    ):
        AtlasParametricFaceShadedPreviewRenderer.render(
            object(),
        )


def test_renderer_rejects_invalid_light_direction_length():
    with pytest.raises(
        ValueError,
        match="three components",
    ):
        AtlasParametricFaceShadedPreviewRenderer.render(
            _flat_surface(),
            light_direction=(
                0.0,
                1.0,
            ),
        )


def test_renderer_rejects_zero_light_direction():
    with pytest.raises(
        ValueError,
        match="non-zero",
    ):
        AtlasParametricFaceShadedPreviewRenderer.render(
            _flat_surface(),
            light_direction=(
                0.0,
                0.0,
                0.0,
            ),
        )


@pytest.mark.parametrize(
    "field_name, value",
    [
        (
            "ambient_strength",
            -0.01,
        ),
        (
            "ambient_strength",
            1.01,
        ),
        (
            "diffuse_strength",
            -0.01,
        ),
        (
            "diffuse_strength",
            1.01,
        ),
    ],
)
def test_renderer_rejects_strength_outside_normalized_range(
    field_name,
    value,
):
    arguments = {
        "ambient_strength": 0.25,
        "diffuse_strength": 0.75,
    }
    arguments[field_name] = value

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        AtlasParametricFaceShadedPreviewRenderer.render(
            _flat_surface(),
            **arguments,
        )
