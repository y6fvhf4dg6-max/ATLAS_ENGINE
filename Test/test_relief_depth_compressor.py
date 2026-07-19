import numpy as np
import pytest

from CORE.atlas_relief_depth_compressor import (
    AtlasReliefDepthCompressor,
)


def test_compresses_depth_candidate_to_normalized_range():
    values = np.array(
        [
            [-2.0, -1.0, 0.0],
            [1.0, 2.0, 3.0],
        ],
        dtype=np.float64,
    )

    result = AtlasReliefDepthCompressor.compress(
        values,
        lower_percentile=0.0,
        upper_percentile=100.0,
    )

    compressed = result["compressed_depth"]

    assert compressed.dtype == np.float64
    assert compressed.min() == pytest.approx(0.0)
    assert compressed.max() == pytest.approx(1.0)


def test_percentile_clipping_limits_extreme_outlier():
    values = np.array(
        [
            [0.0, 0.1, 0.2, 0.3, 100.0],
        ],
        dtype=np.float64,
    )

    full_range = AtlasReliefDepthCompressor.compress(
        values,
        lower_percentile=0.0,
        upper_percentile=100.0,
    )

    robust = AtlasReliefDepthCompressor.compress(
        values,
        lower_percentile=0.0,
        upper_percentile=80.0,
    )

    assert robust["upper_bound"] < 100.0
    assert (
        robust["compressed_depth"][0, 3]
        > full_range["compressed_depth"][0, 3]
    )
    assert robust["compressed_depth"][0, 4] == 1.0


def test_gamma_above_one_suppresses_mid_depth():
    values = np.array(
        [[0.0, 0.5, 1.0]],
        dtype=np.float64,
    )

    result = AtlasReliefDepthCompressor.compress(
        values,
        lower_percentile=0.0,
        upper_percentile=100.0,
        gamma=2.0,
    )

    assert result["compressed_depth"][0, 1] == (
        pytest.approx(0.25)
    )


def test_constant_input_produces_zero_depth():
    values = np.full(
        (4, 5),
        0.7,
        dtype=np.float64,
    )

    result = AtlasReliefDepthCompressor.compress(values)

    assert np.array_equal(
        result["compressed_depth"],
        np.zeros_like(values),
    )


def test_compression_preserves_value_order():
    values = np.array(
        [
            [0.0, 0.2, 0.4],
            [0.6, 0.8, 1.0],
        ],
        dtype=np.float64,
    )

    result = AtlasReliefDepthCompressor.compress(
        values,
        lower_percentile=0.0,
        upper_percentile=100.0,
        gamma=0.8,
    )

    flattened = result[
        "compressed_depth"
    ].reshape(-1)

    assert np.all(
        np.diff(flattened) >= 0.0
    )


def test_result_records_effective_bounds():
    values = np.arange(
        100,
        dtype=np.float64,
    ).reshape(10, 10)

    result = AtlasReliefDepthCompressor.compress(
        values,
        lower_percentile=10.0,
        upper_percentile=90.0,
    )

    assert result["lower_percentile"] == 10.0
    assert result["upper_percentile"] == 90.0
    assert result["lower_bound"] == pytest.approx(
        np.percentile(values, 10.0)
    )
    assert result["upper_bound"] == pytest.approx(
        np.percentile(values, 90.0)
    )


@pytest.mark.parametrize(
    "lower_percentile,upper_percentile,gamma",
    [
        (-0.1, 100.0, 1.0),
        (0.0, 100.1, 1.0),
        (50.0, 50.0, 1.0),
        (80.0, 20.0, 1.0),
        (float("nan"), 100.0, 1.0),
        (0.0, float("inf"), 1.0),
        ("invalid", 100.0, 1.0),
        (0.0, None, 1.0),
        (0.0, 100.0, 0.0),
        (0.0, 100.0, -1.0),
        (0.0, 100.0, float("nan")),
    ],
)
def test_rejects_invalid_compression_parameters(
    lower_percentile,
    upper_percentile,
    gamma,
):
    values = np.zeros(
        (3, 3),
        dtype=np.float64,
    )

    with pytest.raises(ValueError):
        AtlasReliefDepthCompressor.compress(
            values,
            lower_percentile=lower_percentile,
            upper_percentile=upper_percentile,
            gamma=gamma,
        )


@pytest.mark.parametrize(
    "values",
    [
        [],
        [1.0, 2.0],
        [[[1.0]]],
        [[0.0, float("nan")]],
        [["invalid"]],
    ],
)
def test_rejects_invalid_depth_arrays(values):
    with pytest.raises(ValueError):
        AtlasReliefDepthCompressor.compress(values)


def test_compression_is_deterministic():
    values = np.arange(
        64,
        dtype=np.float64,
    ).reshape(8, 8)

    first = AtlasReliefDepthCompressor.compress(
        values,
        lower_percentile=2.0,
        upper_percentile=98.0,
        gamma=0.9,
    )
    second = AtlasReliefDepthCompressor.compress(
        values,
        lower_percentile=2.0,
        upper_percentile=98.0,
        gamma=0.9,
    )

    assert np.array_equal(
        first["compressed_depth"],
        second["compressed_depth"],
    )


def test_compression_does_not_mutate_input():
    values = np.arange(
        16,
        dtype=np.float64,
    ).reshape(4, 4)
    original = values.copy()

    AtlasReliefDepthCompressor.compress(values)

    assert np.array_equal(
        values,
        original,
    )
