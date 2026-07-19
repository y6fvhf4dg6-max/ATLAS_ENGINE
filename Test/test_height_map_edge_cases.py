import numpy as np
import pytest

from CORE.atlas_height_map_engine import (
    AtlasHeightMapEngine,
)
from fixtures.relief.relief_fixture_catalog import (
    load_fixture,
)


def test_normalize_handles_tiny_positive_dynamic_range():
    values = np.array(
        [
            [1.0, 1.0 + 1e-12],
            [1.0 + 2e-12, 1.0 + 3e-12],
        ],
        dtype=np.float64,
    )

    result = AtlasHeightMapEngine.normalize(values)

    assert result.dtype == np.float64
    assert np.all(np.isfinite(result))
    assert result.min() == pytest.approx(0.0)
    assert result.max() == pytest.approx(1.0)
    assert np.all(np.diff(result.ravel()) >= 0.0)


def test_normalize_handles_large_offset_with_small_range():
    values = np.array(
        [
            [1_000_000.0, 1_000_000.25],
            [1_000_000.50, 1_000_000.75],
        ],
        dtype=np.float64,
    )

    result = AtlasHeightMapEngine.normalize(values)

    assert result[0, 0] == pytest.approx(0.0)
    assert result[-1, -1] == pytest.approx(1.0)
    assert result[0, 1] == pytest.approx(1.0 / 3.0)
    assert result[1, 0] == pytest.approx(2.0 / 3.0)


@pytest.mark.parametrize(
    "shape",
    [
        (2, 2),
        (2, 3),
        (3, 2),
    ],
)
def test_gaussian_smoothing_supports_small_grids(
    shape,
):
    values = np.arange(
        shape[0] * shape[1],
        dtype=np.float64,
    ).reshape(shape)

    result = AtlasHeightMapEngine.smooth_gaussian(
        values,
        sigma=0.8,
        radius=2,
    )

    assert result.shape == shape
    assert result.dtype == np.float64
    assert np.all(np.isfinite(result))


@pytest.mark.parametrize(
    "fixture_name",
    [
        "small_reflect_2x3",
        "horizontal_ramp_3x3",
    ],
)
def test_gaussian_smoothing_supports_radius_larger_than_grid(
    fixture_name,
):
    values = load_fixture(fixture_name)

    result = AtlasHeightMapEngine.smooth_gaussian(
        values,
        sigma=2.0,
        radius=7,
    )

    assert result.shape == values.shape
    assert result.dtype == np.float64
    assert np.all(np.isfinite(result))


def test_gaussian_smoothing_large_radius_is_deterministic():
    values = load_fixture("small_reflect_2x3")

    first = AtlasHeightMapEngine.smooth_gaussian(
        values,
        sigma=2.0,
        radius=7,
    )

    second = AtlasHeightMapEngine.smooth_gaussian(
        values,
        sigma=2.0,
        radius=7,
    )

    assert np.array_equal(first, second)


@pytest.mark.parametrize(
    "values",
    [
        np.array(
            [
                [0.0, 0.25, 0.50, 1.0],
                [1.0, 0.50, 0.25, 0.0],
            ],
            dtype=np.float64,
        ),
        np.array(
            [
                [0.0, 1.0],
                [0.25, 0.75],
                [0.50, 0.50],
                [1.0, 0.0],
            ],
            dtype=np.float64,
        ),
    ],
)
def test_gaussian_smoothing_supports_thin_grids(
    values,
):
    result = AtlasHeightMapEngine.smooth_gaussian(
        values,
        sigma=1.25,
        radius=4,
    )

    assert result.shape == values.shape
    assert np.all(np.isfinite(result))
    assert result.min() >= values.min()
    assert result.max() <= values.max()


def test_gaussian_smoothing_preserves_small_constant_grid():
    values = np.full(
        (2, 2),
        0.375,
        dtype=np.float64,
    )

    result = AtlasHeightMapEngine.smooth_gaussian(
        values,
        sigma=2.0,
        radius=7,
    )

    assert np.allclose(
        result,
        values,
        rtol=0.0,
        atol=1e-15,
    )


def test_gaussian_smoothing_remains_within_input_range():
    values = load_fixture("small_reflect_2x3")

    result = AtlasHeightMapEngine.smooth_gaussian(
        values,
        sigma=1.5,
        radius=5,
    )

    assert result.min() >= values.min()
    assert result.max() <= values.max()


@pytest.mark.parametrize(
    "target_rows,target_columns",
    [
        (2, 2),
        (2, 9),
        (9, 2),
    ],
)
def test_bilinear_resampling_small_targets_are_finite(
    target_rows,
    target_columns,
):
    values = load_fixture("asymmetric_surface_3x4")

    result = AtlasHeightMapEngine.resample_bilinear(
        values,
        target_rows=target_rows,
        target_columns=target_columns,
    )

    assert result.shape == (
        target_rows,
        target_columns,
    )
    assert result.dtype == np.float64
    assert np.all(np.isfinite(result))


def test_bilinear_resampling_stays_within_source_range():
    values = load_fixture("asymmetric_surface_3x4")

    result = AtlasHeightMapEngine.resample_bilinear(
        values,
        target_rows=17,
        target_columns=19,
    )

    assert result.min() >= values.min()
    assert result.max() <= values.max()


def test_bilinear_resampling_preserves_edge_endpoints_on_thin_grid():
    values = load_fixture("small_reflect_2x3")

    result = AtlasHeightMapEngine.resample_bilinear(
        values,
        target_rows=11,
        target_columns=13,
    )

    assert result[0, 0] == pytest.approx(values[0, 0])
    assert result[0, -1] == pytest.approx(values[0, -1])
    assert result[-1, 0] == pytest.approx(values[-1, 0])
    assert result[-1, -1] == pytest.approx(values[-1, -1])
