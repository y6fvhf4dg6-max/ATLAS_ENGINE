import numpy as np
import pytest

from CORE.atlas_height_map_engine import (
    AtlasHeightMapEngine,
)


def test_normalize_maps_values_to_unit_range():
    result = AtlasHeightMapEngine.normalize(
        [
            [10.0, 20.0],
            [30.0, 40.0],
        ]
    )

    assert result.dtype == np.float64
    assert result.min() == pytest.approx(0.0)
    assert result.max() == pytest.approx(1.0)
    assert result[0, 1] == pytest.approx(
        1.0 / 3.0
    )


def test_normalize_preserves_shape():
    result = AtlasHeightMapEngine.normalize(
        np.arange(12).reshape(3, 4)
    )

    assert result.shape == (3, 4)


def test_normalize_supports_inversion():
    normal = AtlasHeightMapEngine.normalize(
        [[0.0, 1.0]]
    )

    inverted = AtlasHeightMapEngine.normalize(
        [[0.0, 1.0]],
        invert=True,
    )

    assert inverted[0, 0] == pytest.approx(
        1.0
    )
    assert inverted[0, 1] == pytest.approx(
        0.0
    )
    assert np.allclose(
        inverted,
        1.0 - normal,
    )


def test_constant_input_returns_zero_map():
    result = AtlasHeightMapEngine.normalize(
        [
            [5.0, 5.0],
            [5.0, 5.0],
        ]
    )

    assert np.array_equal(
        result,
        np.zeros((2, 2)),
    )


@pytest.mark.parametrize(
    "values",
    [
        [],
        [1.0, 2.0, 3.0],
        np.zeros((2, 2, 2)),
    ],
)
def test_rejects_invalid_dimensions(values):
    with pytest.raises(ValueError):
        AtlasHeightMapEngine.normalize(values)


@pytest.mark.parametrize(
    "invalid_value",
    [
        np.nan,
        np.inf,
        -np.inf,
    ],
)
def test_rejects_non_finite_values(
    invalid_value,
):
    with pytest.raises(ValueError):
        AtlasHeightMapEngine.normalize(
            [
                [0.0, invalid_value],
                [1.0, 2.0],
            ]
        )


def test_output_is_deterministic():
    values = np.array(
        [
            [7.0, 2.0, 9.0],
            [4.0, 8.0, 1.0],
        ]
    )

    first = AtlasHeightMapEngine.normalize(
        values
    )
    second = AtlasHeightMapEngine.normalize(
        values
    )

    assert np.array_equal(first, second)


def test_gaussian_smoothing_preserves_shape():
    values = np.arange(
        20,
        dtype=np.float64,
    ).reshape(4, 5)

    result = (
        AtlasHeightMapEngine
        .smooth_gaussian(
            values,
            sigma=1.0,
        )
    )

    assert result.shape == values.shape
    assert result.dtype == np.float64


def test_gaussian_smoothing_preserves_constant_map():
    values = np.full(
        (5, 7),
        0.42,
        dtype=np.float64,
    )

    result = (
        AtlasHeightMapEngine
        .smooth_gaussian(
            values,
            sigma=1.25,
        )
    )

    assert np.allclose(
        result,
        values,
    )


def test_gaussian_smoothing_reduces_impulse_peak():
    values = np.zeros(
        (7, 7),
        dtype=np.float64,
    )

    values[3, 3] = 1.0

    result = (
        AtlasHeightMapEngine
        .smooth_gaussian(
            values,
            sigma=1.0,
        )
    )

    assert 0.0 < result[3, 3] < 1.0
    assert result[3, 2] > 0.0
    assert result[2, 3] > 0.0


def test_gaussian_smoothing_is_symmetric():
    values = np.zeros(
        (7, 7),
        dtype=np.float64,
    )

    values[3, 3] = 1.0

    result = (
        AtlasHeightMapEngine
        .smooth_gaussian(
            values,
            sigma=1.0,
        )
    )

    assert result[3, 2] == pytest.approx(
        result[3, 4]
    )

    assert result[2, 3] == pytest.approx(
        result[4, 3]
    )

    assert result[2, 2] == pytest.approx(
        result[4, 4]
    )


def test_gaussian_smoothing_preserves_total_impulse_mass():
    values = np.zeros(
        (15, 15),
        dtype=np.float64,
    )

    values[7, 7] = 1.0

    result = (
        AtlasHeightMapEngine
        .smooth_gaussian(
            values,
            sigma=1.0,
            radius=3,
        )
    )

    assert result.sum() == pytest.approx(
        1.0,
        abs=1e-12,
    )


def test_gaussian_smoothing_is_deterministic():
    values = np.array(
        [
            [0.0, 1.0, 0.0],
            [0.5, 0.2, 0.8],
            [1.0, 0.0, 0.4],
        ],
        dtype=np.float64,
    )

    first = (
        AtlasHeightMapEngine
        .smooth_gaussian(
            values,
            sigma=0.8,
            radius=2,
        )
    )

    second = (
        AtlasHeightMapEngine
        .smooth_gaussian(
            values,
            sigma=0.8,
            radius=2,
        )
    )

    assert np.array_equal(
        first,
        second,
    )


@pytest.mark.parametrize(
    "sigma",
    [
        0.0,
        -1.0,
        np.nan,
        np.inf,
    ],
)
def test_gaussian_smoothing_rejects_invalid_sigma(
    sigma,
):
    with pytest.raises(ValueError):
        (
            AtlasHeightMapEngine
            .smooth_gaussian(
                [[0.0, 1.0], [1.0, 0.0]],
                sigma=sigma,
            )
        )


@pytest.mark.parametrize(
    "radius",
    [
        0,
        -1,
        1.5,
        True,
        "invalid",
    ],
)
def test_gaussian_smoothing_rejects_invalid_radius(
    radius,
):
    with pytest.raises(ValueError):
        (
            AtlasHeightMapEngine
            .smooth_gaussian(
                [[0.0, 1.0], [1.0, 0.0]],
                sigma=1.0,
                radius=radius,
            )
        )


def test_bilinear_resampling_preserves_corners():
    values = np.array(
        [
            [0.0, 1.0],
            [2.0, 3.0],
        ],
        dtype=np.float64,
    )

    result = (
        AtlasHeightMapEngine
        .resample_bilinear(
            values,
            target_rows=5,
            target_columns=7,
        )
    )

    assert result[0, 0] == pytest.approx(0.0)
    assert result[0, -1] == pytest.approx(1.0)
    assert result[-1, 0] == pytest.approx(2.0)
    assert result[-1, -1] == pytest.approx(
        3.0
    )


def test_bilinear_resampling_interpolates_center():
    values = np.array(
        [
            [0.0, 2.0],
            [2.0, 4.0],
        ],
        dtype=np.float64,
    )

    result = (
        AtlasHeightMapEngine
        .resample_bilinear(
            values,
            target_rows=3,
            target_columns=3,
        )
    )

    assert result[1, 1] == pytest.approx(2.0)


def test_bilinear_resampling_preserves_constant_map():
    values = np.full(
        (4, 6),
        0.37,
        dtype=np.float64,
    )

    result = (
        AtlasHeightMapEngine
        .resample_bilinear(
            values,
            target_rows=9,
            target_columns=11,
        )
    )

    assert np.allclose(
        result,
        0.37,
    )


def test_bilinear_resampling_supports_downsampling():
    values = np.arange(
        25,
        dtype=np.float64,
    ).reshape(5, 5)

    result = (
        AtlasHeightMapEngine
        .resample_bilinear(
            values,
            target_rows=3,
            target_columns=3,
        )
    )

    assert result.shape == (3, 3)
    assert result[1, 1] == pytest.approx(
        values[2, 2]
    )


def test_bilinear_resampling_same_size_returns_copy():
    values = np.array(
        [
            [0.0, 1.0],
            [1.0, 0.0],
        ],
        dtype=np.float64,
    )

    result = (
        AtlasHeightMapEngine
        .resample_bilinear(
            values,
            target_rows=2,
            target_columns=2,
        )
    )

    assert np.array_equal(
        result,
        values,
    )
    assert result is not values


def test_bilinear_resampling_is_deterministic():
    values = np.array(
        [
            [0.0, 0.4, 1.0],
            [0.3, 0.8, 0.2],
        ],
        dtype=np.float64,
    )

    first = (
        AtlasHeightMapEngine
        .resample_bilinear(
            values,
            target_rows=7,
            target_columns=8,
        )
    )

    second = (
        AtlasHeightMapEngine
        .resample_bilinear(
            values,
            target_rows=7,
            target_columns=8,
        )
    )

    assert np.array_equal(first, second)


@pytest.mark.parametrize(
    "target_rows,target_columns",
    [
        (1, 2),
        (2, 1),
        (0, 2),
        (2, 0),
        (-1, 2),
        (2, -1),
        (2.5, 3),
        (3, 2.5),
        (True, 3),
        (3, False),
        ("invalid", 3),
        (3, "invalid"),
    ],
)
def test_bilinear_resampling_rejects_invalid_size(
    target_rows,
    target_columns,
):
    with pytest.raises(ValueError):
        (
            AtlasHeightMapEngine
            .resample_bilinear(
                [
                    [0.0, 1.0],
                    [1.0, 0.0],
                ],
                target_rows=target_rows,
                target_columns=target_columns,
            )
        )
