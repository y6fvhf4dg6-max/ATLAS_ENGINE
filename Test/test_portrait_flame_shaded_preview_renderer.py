from __future__ import annotations

import math

import numpy as np
import pytest

from CORE.atlas_portrait_flame_shaded_preview_renderer import (
    AtlasPortraitFlameShadedPreviewRenderer,
)
from CORE.atlas_portrait_flame_shaded_preview_result import (
    AtlasPortraitFlameShadedPreviewResult,
)
from CORE.atlas_portrait_flame_triangle_rasterizer import (
    AtlasPortraitFlameTriangleRasterization,
)
from CORE.atlas_portrait_flame_vertex_normal_evaluator import (
    AtlasPortraitFlameNormalField,
)


def _rasterization() -> AtlasPortraitFlameTriangleRasterization:
    coverage_mask = np.array(
        [
            [False, False, False, False],
            [False, True, True, False],
            [False, True, True, False],
            [False, False, False, False],
        ],
        dtype=np.bool_,
    )

    triangle_index_buffer = np.array(
        [
            [-1, -1, -1, -1],
            [-1, 0, 0, -1],
            [-1, 1, 1, -1],
            [-1, -1, -1, -1],
        ],
        dtype=np.int64,
    )

    depth_buffer = np.full(
        (
            4,
            4,
        ),
        np.inf,
        dtype=np.float64,
    )
    depth_buffer[
        coverage_mask
    ] = np.array(
        [
            1.0,
            1.0,
            2.0,
            2.0,
        ],
        dtype=np.float64,
    )

    return AtlasPortraitFlameTriangleRasterization(
        image_width=4,
        image_height=4,
        coverage_mask=coverage_mask,
        triangle_index_buffer=triangle_index_buffer,
        depth_buffer=depth_buffer,
    )


def _normal_field() -> AtlasPortraitFlameNormalField:
    return AtlasPortraitFlameNormalField(
        face_normals=np.array(
            [
                [0.0, 0.0, 1.0],
                [0.0, 1.0, 0.0],
            ],
            dtype=np.float64,
        ),
        vertex_normals=np.array(
            [
                [0.0, 0.0, 1.0],
                [0.0, 0.0, 1.0],
                [0.0, 1.0, 0.0],
                [0.0, 1.0, 0.0],
            ],
            dtype=np.float64,
        ),
    )


def test_renderer_returns_shaded_preview_result():
    result = AtlasPortraitFlameShadedPreviewRenderer.render(
        _rasterization(),
        normal_field=_normal_field(),
    )

    assert isinstance(
        result,
        AtlasPortraitFlameShadedPreviewResult,
    )


def test_renderer_preserves_raster_dimensions():
    result = AtlasPortraitFlameShadedPreviewRenderer.render(
        _rasterization(),
        normal_field=_normal_field(),
    )

    assert result.shape == (
        4,
        4,
    )
    assert result.image_width == 4
    assert result.image_height == 4


def test_renderer_applies_face_normal_lighting():
    result = AtlasPortraitFlameShadedPreviewRenderer.render(
        _rasterization(),
        normal_field=_normal_field(),
        light_direction=(
            0.0,
            0.0,
            1.0,
        ),
        ambient_strength=0.20,
        diffuse_strength=0.80,
        background_intensity=0.10,
    )

    expected = np.array(
        [
            [0.10, 0.10, 0.10, 0.10],
            [0.10, 1.00, 1.00, 0.10],
            [0.10, 0.20, 0.20, 0.10],
            [0.10, 0.10, 0.10, 0.10],
        ],
        dtype=np.float64,
    )

    assert np.allclose(
        result.shading,
        expected,
        rtol=0.0,
        atol=1.0e-12,
    )


def test_renderer_generates_uint8_preview():
    result = AtlasPortraitFlameShadedPreviewRenderer.render(
        _rasterization(),
        normal_field=_normal_field(),
        light_direction=(
            0.0,
            0.0,
            1.0,
        ),
        ambient_strength=0.20,
        diffuse_strength=0.80,
        background_intensity=0.10,
    )

    expected = np.rint(
        result.shading * 255.0,
    ).astype(
        np.uint8,
    )

    assert result.preview.dtype == np.uint8
    assert np.array_equal(
        result.preview,
        expected,
    )


def test_zero_diffuse_strength_produces_ambient_foreground():
    result = AtlasPortraitFlameShadedPreviewRenderer.render(
        _rasterization(),
        normal_field=_normal_field(),
        light_direction=(
            0.0,
            0.0,
            1.0,
        ),
        ambient_strength=0.35,
        diffuse_strength=0.0,
        background_intensity=0.05,
    )

    assert np.allclose(
        result.shading[
            result.coverage_mask
        ],
        np.full(
            result.covered_pixel_count,
            0.35,
            dtype=np.float64,
        ),
        rtol=0.0,
        atol=1.0e-12,
    )


def test_back_facing_light_produces_ambient_only():
    result = AtlasPortraitFlameShadedPreviewRenderer.render(
        _rasterization(),
        normal_field=_normal_field(),
        light_direction=(
            0.0,
            0.0,
            -1.0,
        ),
        ambient_strength=0.25,
        diffuse_strength=0.75,
        background_intensity=0.0,
    )

    assert np.allclose(
        result.shading[
            1,
            1:3,
        ],
        np.array(
            [
                0.25,
                0.25,
            ],
            dtype=np.float64,
        ),
        rtol=0.0,
        atol=1.0e-12,
    )


def test_default_light_direction_is_normalized():
    result = AtlasPortraitFlameShadedPreviewRenderer.render(
        _rasterization(),
        normal_field=_normal_field(),
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


def test_result_reports_coverage_counts():
    result = AtlasPortraitFlameShadedPreviewRenderer.render(
        _rasterization(),
        normal_field=_normal_field(),
    )

    assert result.covered_pixel_count == 4
    assert result.background_pixel_count == 12


def test_result_arrays_are_read_only():
    result = AtlasPortraitFlameShadedPreviewRenderer.render(
        _rasterization(),
        normal_field=_normal_field(),
    )

    assert result.shading.flags.writeable is False
    assert result.preview.flags.writeable is False
    assert result.coverage_mask.flags.writeable is False

    with pytest.raises(
        ValueError,
    ):
        result.shading[
            0,
            0,
        ] = 1.0

    with pytest.raises(
        ValueError,
    ):
        result.preview[
            0,
            0,
        ] = 255

    with pytest.raises(
        ValueError,
    ):
        result.coverage_mask[
            0,
            0,
        ] = True


def test_renderer_returns_independent_results():
    rasterization = _rasterization()
    normal_field = _normal_field()

    first = AtlasPortraitFlameShadedPreviewRenderer.render(
        rasterization,
        normal_field=normal_field,
    )
    second = AtlasPortraitFlameShadedPreviewRenderer.render(
        rasterization,
        normal_field=normal_field,
    )

    assert first is not second
    assert not np.shares_memory(
        first.shading,
        second.shading,
    )
    assert not np.shares_memory(
        first.preview,
        second.preview,
    )
    assert not np.shares_memory(
        first.coverage_mask,
        second.coverage_mask,
    )


def test_renderer_does_not_modify_inputs():
    rasterization = _rasterization()
    normal_field = _normal_field()

    rasterization_before = rasterization.to_dict()
    normal_field_before = normal_field.to_dict()

    AtlasPortraitFlameShadedPreviewRenderer.render(
        rasterization,
        normal_field=normal_field,
    )

    assert rasterization.to_dict() == rasterization_before

    assert np.array_equal(
        normal_field.face_normals,
        normal_field_before[
            "face_normals"
        ],
    )
    assert np.array_equal(
        normal_field.vertex_normals,
        normal_field_before[
            "vertex_normals"
        ],
    )


def test_result_to_dict_returns_plain_values():
    result = AtlasPortraitFlameShadedPreviewRenderer.render(
        _rasterization(),
        normal_field=_normal_field(),
        light_direction=(
            0.0,
            0.0,
            1.0,
        ),
        ambient_strength=0.20,
        diffuse_strength=0.80,
        background_intensity=0.10,
    )

    payload = result.to_dict()

    assert set(
        payload,
    ) == {
        "image_width",
        "image_height",
        "covered_pixel_count",
        "background_pixel_count",
        "minimum_intensity",
        "maximum_intensity",
        "light_direction",
        "ambient_strength",
        "diffuse_strength",
        "background_intensity",
        "shading",
        "preview",
        "coverage_mask",
    }

    assert payload["image_width"] == 4
    assert payload["image_height"] == 4
    assert payload["covered_pixel_count"] == 4
    assert payload["background_pixel_count"] == 12
    assert payload["light_direction"] == [
        0.0,
        0.0,
        1.0,
    ]
    assert payload["ambient_strength"] == pytest.approx(
        0.20,
    )
    assert payload["diffuse_strength"] == pytest.approx(
        0.80,
    )
    assert payload["background_intensity"] == pytest.approx(
        0.10,
    )
    assert payload["shading"] == result.shading.tolist()
    assert payload["preview"] == result.preview.tolist()
    assert payload["coverage_mask"] == (
        result.coverage_mask.tolist()
    )


def test_renderer_rejects_wrong_rasterization_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameTriangleRasterization",
    ):
        AtlasPortraitFlameShadedPreviewRenderer.render(
            object(),
            normal_field=_normal_field(),
        )


def test_renderer_rejects_wrong_normal_field_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameNormalField",
    ):
        AtlasPortraitFlameShadedPreviewRenderer.render(
            _rasterization(),
            normal_field=object(),
        )


def test_renderer_rejects_triangle_index_outside_normal_field():
    rasterization = _rasterization()

    triangle_indices = (
        rasterization.triangle_index_buffer.copy()
    )
    triangle_indices[
        1,
        1,
    ] = 2

    invalid = AtlasPortraitFlameTriangleRasterization(
        image_width=rasterization.image_width,
        image_height=rasterization.image_height,
        coverage_mask=rasterization.coverage_mask,
        triangle_index_buffer=triangle_indices,
        depth_buffer=rasterization.depth_buffer,
    )

    with pytest.raises(
        ValueError,
        match="triangle_index_buffer",
    ):
        AtlasPortraitFlameShadedPreviewRenderer.render(
            invalid,
            normal_field=_normal_field(),
        )


@pytest.mark.parametrize(
    "light_direction",
    [
        (
            0.0,
            1.0,
        ),
        (
            0.0,
            0.0,
            0.0,
        ),
        (
            0.0,
            np.nan,
            1.0,
        ),
    ],
)
def test_renderer_rejects_invalid_light_direction(
    light_direction,
):
    with pytest.raises(
        ValueError,
        match="light_direction",
    ):
        AtlasPortraitFlameShadedPreviewRenderer.render(
            _rasterization(),
            normal_field=_normal_field(),
            light_direction=light_direction,
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "value",
    ),
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
            "ambient_strength",
            np.nan,
        ),
        (
            "diffuse_strength",
            -0.01,
        ),
        (
            "diffuse_strength",
            1.01,
        ),
        (
            "diffuse_strength",
            np.inf,
        ),
        (
            "background_intensity",
            -0.01,
        ),
        (
            "background_intensity",
            1.01,
        ),
        (
            "background_intensity",
            None,
        ),
    ],
)
def test_renderer_rejects_invalid_strengths(
    field_name,
    value,
):
    values = {
        "ambient_strength": 0.25,
        "diffuse_strength": 0.75,
        "background_intensity": 0.0,
    }
    values[
        field_name
    ] = value

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        AtlasPortraitFlameShadedPreviewRenderer.render(
            _rasterization(),
            normal_field=_normal_field(),
            **values,
        )
