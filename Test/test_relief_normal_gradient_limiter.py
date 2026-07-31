from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_relief_normal_gradient_limiter import (
    AtlasReliefNormalGradientLimiter,
)


def _normalize(
    normals: np.ndarray,
) -> np.ndarray:
    lengths = np.linalg.norm(
        normals,
        axis=2,
        keepdims=True,
    )

    return normals / np.maximum(
        lengths,
        1e-12,
    )


def _normals_from_gradients(
    gradient_x: np.ndarray,
    gradient_y: np.ndarray,
) -> np.ndarray:
    normals = np.stack(
        [
            -gradient_x,
            -gradient_y,
            np.ones_like(gradient_x),
        ],
        axis=2,
    )

    return _normalize(normals)


def _gradient_magnitude(
    normals: np.ndarray,
    *,
    minimum_nz: float = 0.05,
) -> np.ndarray:
    nz = np.maximum(
        normals[..., 2],
        minimum_nz,
    )

    gradient_x = (
        -normals[..., 0]
        / nz
    )
    gradient_y = (
        -normals[..., 1]
        / nz
    )

    return np.sqrt(
        gradient_x * gradient_x
        + gradient_y * gradient_y
    )


def test_output_shape_and_dtype_are_preserved() -> None:
    normals = np.zeros(
        (40, 52, 3),
        dtype=np.float32,
    )
    normals[..., 2] = 1.0

    result = AtlasReliefNormalGradientLimiter.limit(
        normals,
    )

    assert result.shape == normals.shape
    assert result.dtype == np.float64


def test_output_normals_are_unit_length() -> None:
    rows = 42
    columns = 50

    gradient_x = np.full(
        (rows, columns),
        0.20,
        dtype=np.float64,
    )
    gradient_y = np.full(
        (rows, columns),
        -0.10,
        dtype=np.float64,
    )

    normals = _normals_from_gradients(
        gradient_x,
        gradient_y,
    )

    result = AtlasReliefNormalGradientLimiter.limit(
        normals,
        maximum_gradient=0.12,
    )

    lengths = np.linalg.norm(
        result,
        axis=2,
    )

    assert np.allclose(
        lengths,
        1.0,
        atol=1e-8,
    )


def test_flat_normals_remain_flat() -> None:
    normals = np.zeros(
        (36, 44, 3),
        dtype=np.float64,
    )
    normals[..., 2] = 1.0

    result = AtlasReliefNormalGradientLimiter.limit(
        normals,
    )

    assert np.allclose(
        result,
        normals,
        atol=1e-12,
    )


def test_explicit_maximum_limits_gradient_magnitude() -> None:
    rows = 32
    columns = 40

    gradient_x = np.full(
        (rows, columns),
        0.60,
        dtype=np.float64,
    )
    gradient_y = np.full(
        (rows, columns),
        0.80,
        dtype=np.float64,
    )

    normals = _normals_from_gradients(
        gradient_x,
        gradient_y,
    )

    result = AtlasReliefNormalGradientLimiter.limit(
        normals,
        maximum_gradient=0.25,
    )

    magnitude = _gradient_magnitude(
        result
    )

    assert float(
        magnitude.max()
    ) <= 0.25 + 1e-8


def test_gradient_direction_is_preserved_when_limited() -> None:
    gradient_x = np.array(
        [
            [0.30, -0.40],
            [0.50, -0.20],
        ],
        dtype=np.float64,
    )
    gradient_y = np.array(
        [
            [0.40, 0.30],
            [-0.20, -0.50],
        ],
        dtype=np.float64,
    )

    normals = _normals_from_gradients(
        gradient_x,
        gradient_y,
    )

    result = AtlasReliefNormalGradientLimiter.limit(
        normals,
        maximum_gradient=0.15,
    )

    nz = np.maximum(
        result[..., 2],
        0.05,
    )
    result_x = (
        -result[..., 0]
        / nz
    )
    result_y = (
        -result[..., 1]
        / nz
    )

    original_angle = np.arctan2(
        gradient_y,
        gradient_x,
    )
    result_angle = np.arctan2(
        result_y,
        result_x,
    )

    assert np.allclose(
        result_angle,
        original_angle,
        atol=1e-8,
    )


def test_small_gradients_are_not_changed_by_explicit_limit() -> None:
    rows = 36
    columns = 48

    gradient_x = np.full(
        (rows, columns),
        0.03,
        dtype=np.float64,
    )
    gradient_y = np.full(
        (rows, columns),
        -0.04,
        dtype=np.float64,
    )

    normals = _normals_from_gradients(
        gradient_x,
        gradient_y,
    )

    result = AtlasReliefNormalGradientLimiter.limit(
        normals,
        maximum_gradient=0.20,
    )

    assert np.allclose(
        result,
        normals,
        atol=1e-10,
    )


def test_percentile_limit_reduces_only_outlier_gradients() -> None:
    rows = 50
    columns = 60

    gradient_x = np.full(
        (rows, columns),
        0.04,
        dtype=np.float64,
    )
    gradient_y = np.zeros(
        (rows, columns),
        dtype=np.float64,
    )

    gradient_x[10, 10] = 1.00
    gradient_x[20, 30] = -0.90
    gradient_y[35, 42] = 0.80

    normals = _normals_from_gradients(
        gradient_x,
        gradient_y,
    )

    result = AtlasReliefNormalGradientLimiter.limit(
        normals,
        magnitude_percentile=95.0,
    )

    input_magnitude = _gradient_magnitude(
        normals
    )
    output_magnitude = _gradient_magnitude(
        result
    )

    ordinary = input_magnitude < 0.10
    outliers = input_magnitude > 0.50

    assert np.allclose(
        output_magnitude[ordinary],
        input_magnitude[ordinary],
        atol=1e-10,
    )
    assert np.all(
        output_magnitude[outliers]
        < input_magnitude[outliers]
    )


def test_confidence_reduces_detail_in_low_confidence_region() -> None:
    rows = 40
    columns = 48

    gradient_x = np.full(
        (rows, columns),
        0.20,
        dtype=np.float64,
    )
    gradient_y = np.zeros(
        (rows, columns),
        dtype=np.float64,
    )

    normals = _normals_from_gradients(
        gradient_x,
        gradient_y,
    )

    confidence = np.ones(
        (rows, columns),
        dtype=np.float64,
    )
    confidence[:, :columns // 2] = 0.20

    result = AtlasReliefNormalGradientLimiter.limit(
        normals,
        confidence_map=confidence,
        maximum_gradient=0.20,
    )

    magnitude = _gradient_magnitude(
        result
    )

    low_confidence_mean = float(
        np.mean(
            magnitude[
                :,
                :columns // 2,
            ]
        )
    )
    high_confidence_mean = float(
        np.mean(
            magnitude[
                :,
                columns // 2:,
            ]
        )
    )

    assert low_confidence_mean < high_confidence_mean


def test_zero_confidence_returns_flat_normals() -> None:
    rows = 30
    columns = 38

    gradient_x = np.full(
        (rows, columns),
        0.25,
        dtype=np.float64,
    )
    gradient_y = np.full(
        (rows, columns),
        -0.15,
        dtype=np.float64,
    )

    normals = _normals_from_gradients(
        gradient_x,
        gradient_y,
    )

    confidence = np.zeros(
        (rows, columns),
        dtype=np.float64,
    )

    result = AtlasReliefNormalGradientLimiter.limit(
        normals,
        confidence_map=confidence,
        maximum_gradient=0.30,
    )

    expected = np.zeros_like(
        normals
    )
    expected[..., 2] = 1.0

    assert np.allclose(
        result,
        expected,
        atol=1e-12,
    )


def test_mask_makes_output_flat_outside_subject() -> None:
    rows = 34
    columns = 46

    gradient_x = np.full(
        (rows, columns),
        0.18,
        dtype=np.float64,
    )
    gradient_y = np.full(
        (rows, columns),
        0.10,
        dtype=np.float64,
    )

    normals = _normals_from_gradients(
        gradient_x,
        gradient_y,
    )

    mask = np.zeros(
        (rows, columns),
        dtype=np.float64,
    )
    mask[6:28, 8:38] = 1.0

    result = AtlasReliefNormalGradientLimiter.limit(
        normals,
        mask=mask,
        maximum_gradient=0.15,
    )

    outside = mask <= 0.0

    assert np.allclose(
        result[..., 0][outside],
        0.0,
        atol=1e-12,
    )
    assert np.allclose(
        result[..., 1][outside],
        0.0,
        atol=1e-12,
    )
    assert np.allclose(
        result[..., 2][outside],
        1.0,
        atol=1e-12,
    )


def test_invalid_normal_shape_is_rejected() -> None:
    normals = np.zeros(
        (30, 40, 2),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="normals",
    ):
        AtlasReliefNormalGradientLimiter.limit(
            normals,
        )


def test_confidence_shape_must_match_normal_field() -> None:
    normals = np.zeros(
        (30, 40, 3),
        dtype=np.float64,
    )
    normals[..., 2] = 1.0

    confidence = np.ones(
        (29, 40),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="confidence_map",
    ):
        AtlasReliefNormalGradientLimiter.limit(
            normals,
            confidence_map=confidence,
        )


@pytest.mark.parametrize(
    "magnitude_percentile",
    [
        0.0,
        100.0,
        -1.0,
        101.0,
        np.nan,
        np.inf,
    ],
)
def test_invalid_magnitude_percentile_is_rejected(
    magnitude_percentile: float,
) -> None:
    normals = np.zeros(
        (30, 40, 3),
        dtype=np.float64,
    )
    normals[..., 2] = 1.0

    with pytest.raises(
        ValueError,
        match="magnitude_percentile",
    ):
        AtlasReliefNormalGradientLimiter.limit(
            normals,
            magnitude_percentile=magnitude_percentile,
        )


@pytest.mark.parametrize(
    "maximum_gradient",
    [
        0.0,
        -0.1,
        np.nan,
        np.inf,
    ],
)
def test_invalid_maximum_gradient_is_rejected(
    maximum_gradient: float,
) -> None:
    normals = np.zeros(
        (30, 40, 3),
        dtype=np.float64,
    )
    normals[..., 2] = 1.0

    with pytest.raises(
        ValueError,
        match="maximum_gradient",
    ):
        AtlasReliefNormalGradientLimiter.limit(
            normals,
            maximum_gradient=maximum_gradient,
        )
