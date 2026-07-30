import numpy as np

from CORE.atlas_rock_relief_illumination_normalizer import (
    AtlasRockReliefIlluminationNormalizer,
)


def test_normalizer_reduces_broad_lighting_gradient():
    height, width = 48, 96

    broad_gradient = np.tile(
        np.linspace(
            0.20,
            0.90,
            width,
            dtype=np.float64,
        ),
        (height, 1),
    )

    result = (
        AtlasRockReliefIlluminationNormalizer.normalize(
            broad_gradient,
            illumination_sigma=12.0,
            detail_strength=0.70,
        )
    )

    input_column_means = np.mean(
        broad_gradient,
        axis=0,
    )
    output_column_means = np.mean(
        result,
        axis=0,
    )

    assert result.shape == broad_gradient.shape
    assert result.dtype == np.float64
    assert np.all(np.isfinite(result))
    assert float(np.min(result)) >= 0.0
    assert float(np.max(result)) <= 1.0

    assert (
        float(np.ptp(output_column_means))
        <
        float(np.ptp(input_column_means)) * 0.25
    )


def test_normalizer_preserves_local_carved_edge():
    image = np.full(
        (64, 96),
        0.45,
        dtype=np.float64,
    )

    image[:, 48:] += 0.20

    result = (
        AtlasRockReliefIlluminationNormalizer.normalize(
            image,
            illumination_sigma=14.0,
            detail_strength=0.80,
        )
    )

    left = float(np.mean(result[:, 44:47]))
    right = float(np.mean(result[:, 49:52]))

    assert right - left > 0.08


def test_normalizer_rejects_non_2d_input():
    values = np.zeros(
        (8, 8, 3),
        dtype=np.float64,
    )

    try:
        AtlasRockReliefIlluminationNormalizer.normalize(
            values
        )
    except ValueError as exc:
        assert "two-dimensional" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError."
        )
