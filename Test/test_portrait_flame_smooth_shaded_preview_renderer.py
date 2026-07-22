from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_shaded_preview_renderer import (
    AtlasPortraitFlameShadedPreviewRenderer,
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
            [True, True, True],
        ],
        dtype=np.bool_,
    )

    return AtlasPortraitFlameTriangleRasterization(
        image_width=3,
        image_height=1,
        coverage_mask=coverage_mask,
        triangle_index_buffer=np.array(
            [
                [0, 0, 0],
            ],
            dtype=np.int64,
        ),
        depth_buffer=np.array(
            [
                [1.0, 1.0, 1.0],
            ],
            dtype=np.float64,
        ),
        barycentric_coordinates=np.array(
            [
                [
                    [1.0, 0.0, 0.0],
                    [0.5, 0.5, 0.0],
                    [0.0, 1.0, 0.0],
                ],
            ],
            dtype=np.float64,
        ),
    )


def _normal_field() -> AtlasPortraitFlameNormalField:
    diagonal = 1.0 / np.sqrt(
        2.0,
    )

    return AtlasPortraitFlameNormalField(
        face_normals=np.array(
            [
                [0.0, 0.0, 1.0],
            ],
            dtype=np.float64,
        ),
        vertex_normals=np.array(
            [
                [0.0, 0.0, 1.0],
                [0.0, 1.0, 0.0],
                [diagonal, 0.0, diagonal],
            ],
            dtype=np.float64,
        ),
    )


def _triangle_faces() -> np.ndarray:
    return np.array(
        [
            [0, 1, 2],
        ],
        dtype=np.int64,
    )


def test_renderer_accepts_triangle_faces_for_smooth_shading():
    result = AtlasPortraitFlameShadedPreviewRenderer.render(
        _rasterization(),
        normal_field=_normal_field(),
        triangle_faces=_triangle_faces(),
    )

    assert result.covered_pixel_count == 3


def test_renderer_interpolates_vertex_normals():
    result = AtlasPortraitFlameShadedPreviewRenderer.render(
        _rasterization(),
        normal_field=_normal_field(),
        triangle_faces=_triangle_faces(),
        light_direction=(
            0.0,
            0.0,
            1.0,
        ),
        ambient_strength=0.0,
        diffuse_strength=1.0,
        background_intensity=0.0,
    )

    assert result.shading[
        0,
        0,
    ] == pytest.approx(
        1.0,
    )

    assert result.shading[
        0,
        1,
    ] == pytest.approx(
        1.0 / np.sqrt(
            2.0,
        ),
        rel=0.0,
        abs=1.0e-12,
    )

    assert result.shading[
        0,
        2,
    ] == pytest.approx(
        0.0,
        rel=0.0,
        abs=1.0e-12,
    )


def test_interpolated_normals_are_renormalized():
    rasterization = AtlasPortraitFlameTriangleRasterization(
        image_width=1,
        image_height=1,
        coverage_mask=np.array(
            [
                [True],
            ],
            dtype=np.bool_,
        ),
        triangle_index_buffer=np.array(
            [
                [0],
            ],
            dtype=np.int64,
        ),
        depth_buffer=np.array(
            [
                [1.0],
            ],
            dtype=np.float64,
        ),
        barycentric_coordinates=np.array(
            [
                [
                    [
                        0.5,
                        0.5,
                        0.0,
                    ],
                ],
            ],
            dtype=np.float64,
        ),
    )

    result = AtlasPortraitFlameShadedPreviewRenderer.render(
        rasterization,
        normal_field=_normal_field(),
        triangle_faces=_triangle_faces(),
        light_direction=(
            0.0,
            0.0,
            1.0,
        ),
        ambient_strength=0.0,
        diffuse_strength=1.0,
        background_intensity=0.0,
    )

    assert result.shading[
        0,
        0,
    ] == pytest.approx(
        1.0 / np.sqrt(
            2.0,
        ),
        rel=0.0,
        abs=1.0e-12,
    )


def test_renderer_rejects_invalid_triangle_faces_shape():
    with pytest.raises(
        ValueError,
        match="triangle_faces",
    ):
        AtlasPortraitFlameShadedPreviewRenderer.render(
            _rasterization(),
            normal_field=_normal_field(),
            triangle_faces=np.zeros(
                (
                    1,
                    2,
                ),
                dtype=np.int64,
            ),
        )


def test_renderer_rejects_triangle_faces_outside_vertex_normals():
    with pytest.raises(
        ValueError,
        match="triangle_faces",
    ):
        AtlasPortraitFlameShadedPreviewRenderer.render(
            _rasterization(),
            normal_field=_normal_field(),
            triangle_faces=np.array(
                [
                    [0, 1, 3],
                ],
                dtype=np.int64,
            ),
        )


def test_renderer_rejects_triangle_face_count_mismatch():
    with pytest.raises(
        ValueError,
        match="triangle_faces",
    ):
        AtlasPortraitFlameShadedPreviewRenderer.render(
            _rasterization(),
            normal_field=_normal_field(),
            triangle_faces=np.array(
                [
                    [0, 1, 2],
                    [0, 2, 1],
                ],
                dtype=np.int64,
            ),
        )
