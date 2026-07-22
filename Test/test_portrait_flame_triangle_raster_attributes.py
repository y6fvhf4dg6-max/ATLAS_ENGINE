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


def _projection() -> AtlasPortraitFlameWeakPerspectiveProjection:
    return AtlasPortraitFlameWeakPerspectiveProjection(
        scale=1.0,
        translation_x=0.0,
        translation_y=0.0,
        projected_vertices_2d=np.array(
            [
                [1.0, 1.0],
                [4.0, 1.0],
                [1.0, 4.0],
            ],
            dtype=np.float64,
        ),
        triangle_faces=np.array(
            [
                [0, 1, 2],
            ],
            dtype=np.int64,
        ),
    )


def _visibility() -> AtlasPortraitFlameTriangleVisibility:
    return AtlasPortraitFlameTriangleVisibility(
        visible_triangle_mask=np.array(
            [
                True,
            ],
            dtype=np.bool_,
        ),
        front_facing_triangle_mask=np.array(
            [
                True,
            ],
            dtype=np.bool_,
        ),
        signed_projected_areas=np.array(
            [
                4.5,
            ],
            dtype=np.float64,
        ),
        mean_triangle_depths=np.array(
            [
                2.0,
            ],
            dtype=np.float64,
        ),
    )


def _rasterization() -> AtlasPortraitFlameTriangleRasterization:
    return AtlasPortraitFlameTriangleRasterizer.rasterize(
        _projection(),
        visibility=_visibility(),
        image_width=6,
        image_height=6,
    )


def test_rasterization_exposes_barycentric_coordinates():
    result = _rasterization()

    assert isinstance(
        result.barycentric_coordinates,
        np.ndarray,
    )


def test_barycentric_coordinates_have_expected_shape_and_dtype():
    result = _rasterization()

    assert result.barycentric_coordinates.shape == (
        6,
        6,
        3,
    )
    assert (
        result.barycentric_coordinates.dtype
        == np.float64
    )


def test_triangle_vertices_receive_exact_unit_weights():
    result = _rasterization()

    assert result.barycentric_coordinates[
        1,
        1,
    ] == pytest.approx(
        np.array(
            [
                1.0,
                0.0,
                0.0,
            ],
            dtype=np.float64,
        )
    )

    assert result.barycentric_coordinates[
        1,
        4,
    ] == pytest.approx(
        np.array(
            [
                0.0,
                1.0,
                0.0,
            ],
            dtype=np.float64,
        )
    )

    assert result.barycentric_coordinates[
        4,
        1,
    ] == pytest.approx(
        np.array(
            [
                0.0,
                0.0,
                1.0,
            ],
            dtype=np.float64,
        )
    )


def test_interior_pixel_receives_expected_weights():
    result = _rasterization()

    assert result.barycentric_coordinates[
        2,
        2,
    ] == pytest.approx(
        np.array(
            [
                1.0 / 3.0,
                1.0 / 3.0,
                1.0 / 3.0,
            ],
            dtype=np.float64,
        ),
        rel=0.0,
        abs=1.0e-12,
    )


def test_edge_pixel_receives_expected_weights():
    result = _rasterization()

    assert result.barycentric_coordinates[
        1,
        2,
    ] == pytest.approx(
        np.array(
            [
                2.0 / 3.0,
                1.0 / 3.0,
                0.0,
            ],
            dtype=np.float64,
        ),
        rel=0.0,
        abs=1.0e-12,
    )


def test_covered_barycentric_weights_sum_to_one():
    result = _rasterization()

    covered_weights = result.barycentric_coordinates[
        result.coverage_mask
    ]

    assert np.allclose(
        np.sum(
            covered_weights,
            axis=1,
            dtype=np.float64,
        ),
        np.ones(
            result.covered_pixel_count,
            dtype=np.float64,
        ),
        rtol=0.0,
        atol=1.0e-12,
    )


def test_covered_barycentric_weights_are_non_negative():
    result = _rasterization()

    covered_weights = result.barycentric_coordinates[
        result.coverage_mask
    ]

    assert np.all(
        covered_weights
        >= -1.0e-12
    )


def test_background_barycentric_weights_are_zero():
    result = _rasterization()

    assert np.array_equal(
        result.barycentric_coordinates[
            ~result.coverage_mask
        ],
        np.zeros(
            (
                result.background_pixel_count,
                3,
            ),
            dtype=np.float64,
        ),
    )


def test_barycentric_coordinates_are_read_only():
    result = _rasterization()

    assert (
        result.barycentric_coordinates.flags.writeable
        is False
    )

    with pytest.raises(
        ValueError,
    ):
        result.barycentric_coordinates[
            1,
            1,
            0,
        ] = 0.0


def test_independent_rasterizations_do_not_share_barycentric_memory():
    first = _rasterization()
    second = _rasterization()

    assert not np.shares_memory(
        first.barycentric_coordinates,
        second.barycentric_coordinates,
    )


def test_rasterization_to_dict_includes_plain_barycentric_coordinates():
    result = _rasterization()

    payload = result.to_dict()

    assert "barycentric_coordinates" in payload
    assert payload[
        "barycentric_coordinates"
    ] == result.barycentric_coordinates.tolist()


def test_contract_rejects_wrong_barycentric_shape():
    with pytest.raises(
        ValueError,
        match="barycentric_coordinates",
    ):
        AtlasPortraitFlameTriangleRasterization(
            image_width=3,
            image_height=2,
            coverage_mask=np.zeros(
                (
                    2,
                    3,
                ),
                dtype=np.bool_,
            ),
            triangle_index_buffer=np.full(
                (
                    2,
                    3,
                ),
                -1,
                dtype=np.int64,
            ),
            depth_buffer=np.full(
                (
                    2,
                    3,
                ),
                np.inf,
                dtype=np.float64,
            ),
            barycentric_coordinates=np.zeros(
                (
                    2,
                    3,
                    2,
                ),
                dtype=np.float64,
            ),
        )


def test_contract_rejects_non_finite_barycentric_coordinates():
    coordinates = np.zeros(
        (
            2,
            3,
            3,
        ),
        dtype=np.float64,
    )
    coordinates[
        0,
        0,
        0,
    ] = np.nan

    with pytest.raises(
        ValueError,
        match="barycentric_coordinates",
    ):
        AtlasPortraitFlameTriangleRasterization(
            image_width=3,
            image_height=2,
            coverage_mask=np.zeros(
                (
                    2,
                    3,
                ),
                dtype=np.bool_,
            ),
            triangle_index_buffer=np.full(
                (
                    2,
                    3,
                ),
                -1,
                dtype=np.int64,
            ),
            depth_buffer=np.full(
                (
                    2,
                    3,
                ),
                np.inf,
                dtype=np.float64,
            ),
            barycentric_coordinates=coordinates,
        )


def test_contract_rejects_nonzero_background_weights():
    coverage_mask = np.zeros(
        (
            2,
            3,
        ),
        dtype=np.bool_,
    )

    coordinates = np.zeros(
        (
            2,
            3,
            3,
        ),
        dtype=np.float64,
    )
    coordinates[
        0,
        0,
    ] = np.array(
        [
            1.0,
            0.0,
            0.0,
        ],
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="Background barycentric",
    ):
        AtlasPortraitFlameTriangleRasterization(
            image_width=3,
            image_height=2,
            coverage_mask=coverage_mask,
            triangle_index_buffer=np.full(
                (
                    2,
                    3,
                ),
                -1,
                dtype=np.int64,
            ),
            depth_buffer=np.full(
                (
                    2,
                    3,
                ),
                np.inf,
                dtype=np.float64,
            ),
            barycentric_coordinates=coordinates,
        )


def test_contract_rejects_covered_weights_not_summing_to_one():
    coverage_mask = np.zeros(
        (
            2,
            3,
        ),
        dtype=np.bool_,
    )
    coverage_mask[
        0,
        0,
    ] = True

    triangle_indices = np.full(
        (
            2,
            3,
        ),
        -1,
        dtype=np.int64,
    )
    triangle_indices[
        0,
        0,
    ] = 0

    depth_buffer = np.full(
        (
            2,
            3,
        ),
        np.inf,
        dtype=np.float64,
    )
    depth_buffer[
        0,
        0,
    ] = 1.0

    coordinates = np.zeros(
        (
            2,
            3,
            3,
        ),
        dtype=np.float64,
    )
    coordinates[
        0,
        0,
    ] = np.array(
        [
            0.25,
            0.25,
            0.25,
        ],
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="sum to 1.0",
    ):
        AtlasPortraitFlameTriangleRasterization(
            image_width=3,
            image_height=2,
            coverage_mask=coverage_mask,
            triangle_index_buffer=triangle_indices,
            depth_buffer=depth_buffer,
            barycentric_coordinates=coordinates,
        )
