from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_image_coordinate_normalizer import (
    AtlasPortraitFlameImageCoordinateNormalizer,
)


def _points() -> np.ndarray:
    return np.array(
        [
            [0.10, 0.20, 0.30],
            [-0.40, 0.50, 0.60],
            [0.70, -0.80, 0.90],
        ],
        dtype=np.float64,
    )


def test_normalizer_preserves_x_coordinates():
    result = (
        AtlasPortraitFlameImageCoordinateNormalizer
        .normalize(
            _points()
        )
    )

    np.testing.assert_allclose(
        result[:, 0],
        _points()[:, 0],
    )


def test_normalizer_flips_y_coordinates():
    result = (
        AtlasPortraitFlameImageCoordinateNormalizer
        .normalize(
            _points()
        )
    )

    np.testing.assert_allclose(
        result[:, 1],
        -_points()[:, 1],
    )


def test_normalizer_preserves_z_coordinates():
    result = (
        AtlasPortraitFlameImageCoordinateNormalizer
        .normalize(
            _points()
        )
    )

    np.testing.assert_allclose(
        result[:, 2],
        _points()[:, 2],
    )


def test_normalizer_returns_float64_copy():
    source = _points().astype(
        np.float32
    )

    result = (
        AtlasPortraitFlameImageCoordinateNormalizer
        .normalize(
            source
        )
    )

    assert result.dtype == np.float64
    assert result is not source
    assert not np.shares_memory(
        result,
        source,
    )


def test_normalizer_returns_read_only_array():
    result = (
        AtlasPortraitFlameImageCoordinateNormalizer
        .normalize(
            _points()
        )
    )

    assert not result.flags.writeable


def test_normalizer_does_not_modify_source():
    source = _points()
    before = source.copy()

    AtlasPortraitFlameImageCoordinateNormalizer.normalize(
        source
    )

    np.testing.assert_array_equal(
        source,
        before,
    )


@pytest.mark.parametrize(
    "value",
    [
        np.zeros(
            (3,),
            dtype=np.float64,
        ),
        np.zeros(
            (3, 2),
            dtype=np.float64,
        ),
        np.zeros(
            (0, 3),
            dtype=np.float64,
        ),
    ],
)
def test_normalizer_rejects_invalid_shape(
    value,
):
    with pytest.raises(
        ValueError,
        match=r"shape \(N, 3\)",
    ):
        AtlasPortraitFlameImageCoordinateNormalizer.normalize(
            value
        )


def test_normalizer_rejects_non_numeric_values():
    with pytest.raises(
        ValueError,
        match="numeric",
    ):
        AtlasPortraitFlameImageCoordinateNormalizer.normalize(
            [
                [
                    "invalid",
                    0.0,
                    0.0,
                ],
            ]
        )


def test_normalizer_rejects_non_finite_values():
    value = _points()
    value[
        1,
        2,
    ] = np.nan

    with pytest.raises(
        ValueError,
        match="non-finite",
    ):
        AtlasPortraitFlameImageCoordinateNormalizer.normalize(
            value
        )
