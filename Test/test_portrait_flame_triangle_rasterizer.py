from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_triangle_rasterizer import (
    AtlasPortraitFlameTriangleRasterization,
    AtlasPortraitFlameTriangleRasterizer,
)
from CORE.atlas_portrait_flame_triangle_visibility_evaluator import (
    AtlasPortraitFlameTriangleVisibility,
)
from CORE.atlas_portrait_flame_weak_perspective_projection_evaluator import (
    AtlasPortraitFlameWeakPerspectiveProjection,
)


def _single_triangle_projection(
    *,
    triangle_faces: np.ndarray | None = None,
) -> AtlasPortraitFlameWeakPerspectiveProjection:
    if triangle_faces is None:
        triangle_faces = np.array(
            [
                [0, 1, 2],
            ],
            dtype=np.int64,
        )

    return AtlasPortraitFlameWeakPerspectiveProjection(
        scale=1.0,
        translation_x=0.0,
        translation_y=0.0,
        projected_vertices_2d=np.array(
            [
                [1.0, 1.0],
                [3.0, 1.0],
                [1.0, 3.0],
            ],
            dtype=np.float64,
        ),
        triangle_faces=triangle_faces,
    )


def _single_triangle_visibility(
    *,
    visible: bool = True,
    depth: float = 2.0,
) -> AtlasPortraitFlameTriangleVisibility:
    return AtlasPortraitFlameTriangleVisibility(
        visible_triangle_mask=np.array(
            [
                visible,
            ],
            dtype=np.bool_,
        ),
        front_facing_triangle_mask=np.array(
            [
                visible,
            ],
            dtype=np.bool_,
        ),
        signed_projected_areas=np.array(
            [
                2.0 if visible else -2.0,
            ],
            dtype=np.float64,
        ),
        mean_triangle_depths=np.array(
            [
                depth,
            ],
            dtype=np.float64,
        ),
    )


def _overlapping_projection() -> (
    AtlasPortraitFlameWeakPerspectiveProjection
):
    return AtlasPortraitFlameWeakPerspectiveProjection(
        scale=1.0,
        translation_x=0.0,
        translation_y=0.0,
        projected_vertices_2d=np.array(
            [
                [1.0, 1.0],
                [3.0, 1.0],
                [1.0, 3.0],
            ],
            dtype=np.float64,
        ),
        triangle_faces=np.array(
            [
                [0, 1, 2],
                [0, 1, 2],
            ],
            dtype=np.int64,
        ),
    )


def _overlapping_visibility() -> (
    AtlasPortraitFlameTriangleVisibility
):
    return AtlasPortraitFlameTriangleVisibility(
        visible_triangle_mask=np.array(
            [
                True,
                True,
            ],
            dtype=np.bool_,
        ),
        front_facing_triangle_mask=np.array(
            [
                True,
                True,
            ],
            dtype=np.bool_,
        ),
        signed_projected_areas=np.array(
            [
                2.0,
                2.0,
            ],
            dtype=np.float64,
        ),
        mean_triangle_depths=np.array(
            [
                3.0,
                1.0,
            ],
            dtype=np.float64,
        ),
    )


def test_rasterizer_returns_rasterization_contract():
    result = AtlasPortraitFlameTriangleRasterizer.rasterize(
        _single_triangle_projection(),
        visibility=_single_triangle_visibility(),
        image_width=5,
        image_height=5,
    )

    assert isinstance(
        result,
        AtlasPortraitFlameTriangleRasterization,
    )


def test_rasterizer_marks_expected_triangle_coverage():
    result = AtlasPortraitFlameTriangleRasterizer.rasterize(
        _single_triangle_projection(),
        visibility=_single_triangle_visibility(),
        image_width=5,
        image_height=5,
    )

    expected = np.zeros(
        (
            5,
            5,
        ),
        dtype=np.bool_,
    )

    expected[
        1,
        1,
    ] = True
    expected[
        1,
        2,
    ] = True
    expected[
        1,
        3,
    ] = True
    expected[
        2,
        1,
    ] = True
    expected[
        2,
        2,
    ] = True
    expected[
        3,
        1,
    ] = True

    assert np.array_equal(
        result.coverage_mask,
        expected,
    )


def test_rasterizer_writes_triangle_indices():
    result = AtlasPortraitFlameTriangleRasterizer.rasterize(
        _single_triangle_projection(),
        visibility=_single_triangle_visibility(),
        image_width=5,
        image_height=5,
    )

    assert np.all(
        result.triangle_index_buffer[
            result.coverage_mask
        ]
        == 0
    )

    assert np.all(
        result.triangle_index_buffer[
            ~result.coverage_mask
        ]
        == -1
    )


def test_rasterizer_writes_triangle_depths():
    result = AtlasPortraitFlameTriangleRasterizer.rasterize(
        _single_triangle_projection(),
        visibility=_single_triangle_visibility(
            depth=2.5,
        ),
        image_width=5,
        image_height=5,
    )

    assert np.allclose(
        result.depth_buffer[
            result.coverage_mask
        ],
        np.full(
            result.covered_pixel_count,
            2.5,
            dtype=np.float64,
        ),
        rtol=0.0,
        atol=1.0e-12,
    )

    assert np.all(
        np.isposinf(
            result.depth_buffer[
                ~result.coverage_mask
            ]
        )
    )


def test_rasterizer_uses_nearest_triangle_depth():
    result = AtlasPortraitFlameTriangleRasterizer.rasterize(
        _overlapping_projection(),
        visibility=_overlapping_visibility(),
        image_width=5,
        image_height=5,
    )

    assert np.all(
        result.triangle_index_buffer[
            result.coverage_mask
        ]
        == 1
    )

    assert np.allclose(
        result.depth_buffer[
            result.coverage_mask
        ],
        np.ones(
            result.covered_pixel_count,
            dtype=np.float64,
        ),
        rtol=0.0,
        atol=1.0e-12,
    )


def test_rasterizer_skips_hidden_triangles():
    result = AtlasPortraitFlameTriangleRasterizer.rasterize(
        _single_triangle_projection(),
        visibility=_single_triangle_visibility(
            visible=False,
        ),
        image_width=5,
        image_height=5,
    )

    assert not np.any(
        result.coverage_mask,
    )
    assert np.all(
        result.triangle_index_buffer == -1
    )
    assert np.all(
        np.isposinf(
            result.depth_buffer,
        )
    )


def test_rasterization_reports_dimensions_and_counts():
    result = AtlasPortraitFlameTriangleRasterizer.rasterize(
        _single_triangle_projection(),
        visibility=_single_triangle_visibility(),
        image_width=5,
        image_height=5,
    )

    assert result.image_width == 5
    assert result.image_height == 5
    assert result.covered_pixel_count == 6
    assert result.background_pixel_count == 19


def test_rasterization_arrays_use_expected_dtypes():
    result = AtlasPortraitFlameTriangleRasterizer.rasterize(
        _single_triangle_projection(),
        visibility=_single_triangle_visibility(),
        image_width=5,
        image_height=5,
    )

    assert result.coverage_mask.dtype == np.bool_
    assert result.triangle_index_buffer.dtype == np.int64
    assert result.depth_buffer.dtype == np.float64


def test_rasterization_arrays_are_read_only():
    result = AtlasPortraitFlameTriangleRasterizer.rasterize(
        _single_triangle_projection(),
        visibility=_single_triangle_visibility(),
        image_width=5,
        image_height=5,
    )

    assert result.coverage_mask.flags.writeable is False
    assert result.triangle_index_buffer.flags.writeable is False
    assert result.depth_buffer.flags.writeable is False

    with pytest.raises(
        ValueError,
    ):
        result.coverage_mask[
            0,
            0,
        ] = True

    with pytest.raises(
        ValueError,
    ):
        result.triangle_index_buffer[
            0,
            0,
        ] = 0

    with pytest.raises(
        ValueError,
    ):
        result.depth_buffer[
            0,
            0,
        ] = 0.0


def test_rasterizer_returns_independent_results():
    projection = _single_triangle_projection()
    visibility = _single_triangle_visibility()

    first = AtlasPortraitFlameTriangleRasterizer.rasterize(
        projection,
        visibility=visibility,
        image_width=5,
        image_height=5,
    )
    second = AtlasPortraitFlameTriangleRasterizer.rasterize(
        projection,
        visibility=visibility,
        image_width=5,
        image_height=5,
    )

    assert first is not second

    assert not np.shares_memory(
        first.coverage_mask,
        second.coverage_mask,
    )
    assert not np.shares_memory(
        first.triangle_index_buffer,
        second.triangle_index_buffer,
    )
    assert not np.shares_memory(
        first.depth_buffer,
        second.depth_buffer,
    )


def test_rasterizer_does_not_modify_inputs():
    projection = _single_triangle_projection()
    visibility = _single_triangle_visibility()

    projection_before = projection.to_dict()
    visibility_before = visibility.to_dict()

    AtlasPortraitFlameTriangleRasterizer.rasterize(
        projection,
        visibility=visibility,
        image_width=5,
        image_height=5,
    )

    assert projection.to_dict() == projection_before
    assert visibility.to_dict() == visibility_before


def test_rasterization_to_dict_returns_plain_values():
    result = AtlasPortraitFlameTriangleRasterizer.rasterize(
        _single_triangle_projection(),
        visibility=_single_triangle_visibility(),
        image_width=5,
        image_height=5,
    )

    payload = result.to_dict()

    assert set(
        payload,
    ) == {
        "image_width",
        "image_height",
        "covered_pixel_count",
        "background_pixel_count",
        "coverage_mask",
        "triangle_index_buffer",
        "depth_buffer",
    }

    assert payload["image_width"] == 5
    assert payload["image_height"] == 5
    assert payload["covered_pixel_count"] == 6
    assert payload["background_pixel_count"] == 19
    assert payload["coverage_mask"] == (
        result.coverage_mask.tolist()
    )
    assert payload["triangle_index_buffer"] == (
        result.triangle_index_buffer.tolist()
    )
    assert payload["depth_buffer"] == (
        result.depth_buffer.tolist()
    )


def test_rasterizer_rejects_wrong_projection_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameWeakPerspectiveProjection",
    ):
        AtlasPortraitFlameTriangleRasterizer.rasterize(
            object(),
            visibility=_single_triangle_visibility(),
            image_width=5,
            image_height=5,
        )


def test_rasterizer_rejects_wrong_visibility_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameTriangleVisibility",
    ):
        AtlasPortraitFlameTriangleRasterizer.rasterize(
            _single_triangle_projection(),
            visibility=object(),
            image_width=5,
            image_height=5,
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "value",
    ),
    [
        (
            "image_width",
            0,
        ),
        (
            "image_width",
            -1,
        ),
        (
            "image_width",
            5.5,
        ),
        (
            "image_width",
            None,
        ),
        (
            "image_height",
            0,
        ),
        (
            "image_height",
            -1,
        ),
        (
            "image_height",
            5.5,
        ),
        (
            "image_height",
            None,
        ),
    ],
)
def test_rasterizer_rejects_invalid_dimensions(
    field_name,
    value,
):
    values = {
        "image_width": 5,
        "image_height": 5,
    }
    values[
        field_name
    ] = value

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        AtlasPortraitFlameTriangleRasterizer.rasterize(
            _single_triangle_projection(),
            visibility=_single_triangle_visibility(),
            **values,
        )


def test_rasterizer_rejects_triangle_count_mismatch():
    projection = _overlapping_projection()

    with pytest.raises(
        ValueError,
        match="triangle_count",
    ):
        AtlasPortraitFlameTriangleRasterizer.rasterize(
            projection,
            visibility=_single_triangle_visibility(),
            image_width=5,
            image_height=5,
        )
