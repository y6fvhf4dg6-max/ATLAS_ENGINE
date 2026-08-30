from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_relief_normal_height_integrator import (
    AtlasReliefNormalHeightIntegrator,
)


def _normalize_normals(normals: np.ndarray) -> np.ndarray:
    lengths = np.linalg.norm(normals, axis=2, keepdims=True)
    return normals / np.maximum(lengths, 1e-12)


def test_flat_normal_field_produces_flat_height_map() -> None:
    normals = np.zeros((24, 32, 3), dtype=np.float64)
    normals[..., 2] = 1.0

    result = AtlasReliefNormalHeightIntegrator.integrate(normals)

    assert result.shape == (24, 32)
    assert result.dtype == np.float64
    assert np.all(np.isfinite(result))
    assert np.ptp(result) == pytest.approx(0.0, abs=1e-10)


def test_constant_x_slope_produces_monotonic_height_change() -> None:
    normals = np.zeros((20, 30, 3), dtype=np.float64)
    normals[..., 0] = -0.25
    normals[..., 2] = 1.0
    normals = _normalize_normals(normals)

    result = AtlasReliefNormalHeightIntegrator.integrate(
        normals,
        normalize_output=False,
    )

    center_row = result[result.shape[0] // 2]
    differences = np.diff(center_row)

    assert np.all(np.isfinite(result))
    assert np.all(differences > 0.0)
    assert np.std(differences) < 1e-8


def test_constant_y_slope_produces_monotonic_height_change() -> None:
    normals = np.zeros((24, 18, 3), dtype=np.float64)
    normals[..., 1] = -0.20
    normals[..., 2] = 1.0
    normals = _normalize_normals(normals)

    result = AtlasReliefNormalHeightIntegrator.integrate(
        normals,
        normalize_output=False,
    )

    center_column = result[:, result.shape[1] // 2]
    differences = np.diff(center_column)

    assert np.all(np.isfinite(result))
    assert np.all(differences > 0.0)
    assert np.std(differences) < 1e-8


def test_convex_synthetic_surface_reconstructs_higher_center() -> None:
    rows = 51
    columns = 51

    y, x = np.mgrid[
        -1.0:1.0:complex(rows),
        -1.0:1.0:complex(columns),
    ]

    source_height = np.exp(-4.0 * (x * x + y * y))

    dz_dy, dz_dx = np.gradient(source_height)

    normals = np.stack(
        [
            -dz_dx,
            -dz_dy,
            np.ones_like(source_height),
        ],
        axis=2,
    )
    normals = _normalize_normals(normals)

    result = AtlasReliefNormalHeightIntegrator.integrate(normals)

    center = result[rows // 2, columns // 2]
    corners = np.array(
        [
            result[0, 0],
            result[0, -1],
            result[-1, 0],
            result[-1, -1],
        ]
    )

    assert result.min() == pytest.approx(0.0, abs=1e-10)
    assert result.max() == pytest.approx(1.0, abs=1e-10)
    assert center > 0.90
    assert np.all(corners < 0.10)


def test_mask_excludes_outside_region_from_normalization() -> None:
    rows = 30
    columns = 40

    normals = np.zeros((rows, columns, 3), dtype=np.float64)
    normals[..., 0] = -0.15
    normals[..., 2] = 1.0
    normals = _normalize_normals(normals)

    mask = np.zeros((rows, columns), dtype=np.float64)
    mask[5:25, 10:30] = 1.0

    result = AtlasReliefNormalHeightIntegrator.integrate(
        normals,
        mask=mask,
    )

    inside = result[mask > 0.5]
    outside = result[mask <= 0.5]

    assert inside.min() == pytest.approx(0.0, abs=1e-10)
    assert inside.max() == pytest.approx(1.0, abs=1e-10)
    assert np.allclose(outside, 0.0)


def test_small_nz_values_are_clamped_and_remain_finite() -> None:
    normals = np.zeros((16, 16, 3), dtype=np.float64)
    normals[..., 0] = 1.0
    normals[..., 1] = -1.0
    normals[..., 2] = 1e-12
    normals = _normalize_normals(normals)

    result = AtlasReliefNormalHeightIntegrator.integrate(
        normals,
        minimum_nz=0.10,
    )

    assert result.shape == (16, 16)
    assert np.all(np.isfinite(result))
    assert result.min() >= 0.0
    assert result.max() <= 1.0


@pytest.mark.parametrize(
    "invalid_normals",
    [
        np.zeros((16, 16), dtype=np.float64),
        np.zeros((16, 16, 2), dtype=np.float64),
        np.zeros((16, 16, 4), dtype=np.float64),
    ],
)
def test_invalid_normal_shape_is_rejected(
    invalid_normals: np.ndarray,
) -> None:
    with pytest.raises(ValueError, match="normals"):
        AtlasReliefNormalHeightIntegrator.integrate(invalid_normals)


def test_mask_shape_must_match_normal_field() -> None:
    normals = np.zeros((16, 20, 3), dtype=np.float64)
    normals[..., 2] = 1.0

    wrong_mask = np.ones((15, 20), dtype=np.float64)

    with pytest.raises(ValueError, match="mask"):
        AtlasReliefNormalHeightIntegrator.integrate(
            normals,
            mask=wrong_mask,
        )


def test_confidence_map_zeroes_gradients_outside_active_region() -> None:
    rows = 40
    columns = 48

    normals = np.zeros((rows, columns, 3), dtype=np.float64)
    normals[..., 0] = -0.25
    normals[..., 2] = 1.0
    normals = _normalize_normals(normals)

    confidence = np.zeros((rows, columns), dtype=np.float64)
    confidence[:, 12:36] = 1.0

    result = AtlasReliefNormalHeightIntegrator.integrate(
        normals,
        confidence_map=confidence,
        normalize_output=False,
    )

    left_region = result[:, :10]
    center_region = result[:, 14:34]
    right_region = result[:, 38:]

    assert np.ptp(left_region) < 1e-8
    assert np.ptp(right_region) < 1e-8
    assert np.ptp(center_region) > 1.0


def test_half_confidence_reduces_integrated_slope() -> None:
    rows = 24
    columns = 32

    normals = np.zeros((rows, columns, 3), dtype=np.float64)
    normals[..., 0] = -0.20
    normals[..., 2] = 1.0
    normals = _normalize_normals(normals)

    full = AtlasReliefNormalHeightIntegrator.integrate(
        normals,
        confidence_map=np.ones((rows, columns), dtype=np.float64),
        normalize_output=False,
    )

    half = AtlasReliefNormalHeightIntegrator.integrate(
        normals,
        confidence_map=np.full(
            (rows, columns),
            0.5,
            dtype=np.float64,
        ),
        normalize_output=False,
    )

    full_range = float(np.ptp(full))
    half_range = float(np.ptp(half))

    assert half_range == pytest.approx(
        0.5 * full_range,
        rel=1e-6,
        abs=1e-8,
    )


def test_confidence_map_is_clamped_to_unit_interval() -> None:
    normals = np.zeros((18, 22, 3), dtype=np.float64)
    normals[..., 0] = -0.15
    normals[..., 2] = 1.0
    normals = _normalize_normals(normals)

    raw_confidence = np.linspace(
        -1.0,
        2.0,
        18 * 22,
        dtype=np.float64,
    ).reshape(18, 22)

    clipped_confidence = np.clip(
        raw_confidence,
        0.0,
        1.0,
    )

    raw_result = AtlasReliefNormalHeightIntegrator.integrate(
        normals,
        confidence_map=raw_confidence,
        normalize_output=False,
    )

    clipped_result = AtlasReliefNormalHeightIntegrator.integrate(
        normals,
        confidence_map=clipped_confidence,
        normalize_output=False,
    )

    assert np.allclose(
        raw_result,
        clipped_result,
        atol=1e-10,
    )


def test_confidence_map_shape_must_match_normal_field() -> None:
    normals = np.zeros((16, 20, 3), dtype=np.float64)
    normals[..., 2] = 1.0

    wrong_confidence = np.ones(
        (15, 20),
        dtype=np.float64,
    )

    with pytest.raises(ValueError, match="confidence_map"):
        AtlasReliefNormalHeightIntegrator.integrate(
            normals,
            confidence_map=wrong_confidence,
        )


def test_confidence_map_must_be_finite() -> None:
    normals = np.zeros((16, 20, 3), dtype=np.float64)
    normals[..., 2] = 1.0

    confidence = np.ones(
        (16, 20),
        dtype=np.float64,
    )
    confidence[5, 7] = np.nan

    with pytest.raises(ValueError, match="confidence_map"):
        AtlasReliefNormalHeightIntegrator.integrate(
            normals,
            confidence_map=confidence,
        )


def test_zero_confidence_produces_flat_height_map() -> None:
    normals = np.zeros((20, 24, 3), dtype=np.float64)
    normals[..., 0] = -0.30
    normals[..., 1] = 0.12
    normals[..., 2] = 1.0
    normals = _normalize_normals(normals)

    confidence = np.zeros(
        (20, 24),
        dtype=np.float64,
    )

    result = AtlasReliefNormalHeightIntegrator.integrate(
        normals,
        confidence_map=confidence,
    )

    assert np.ptp(result) == pytest.approx(
        0.0,
        abs=1e-10,
    )


def test_sample_spacing_scales_unnormalized_physical_height() -> None:
    normals = np.zeros((12, 20, 3), dtype=np.float64)
    normals[..., 0] = -0.25
    normals[..., 2] = 1.0
    normals = _normalize_normals(normals)

    unit_spacing = AtlasReliefNormalHeightIntegrator.integrate(
        normals,
        normalize_output=False,
    )
    physical_spacing = AtlasReliefNormalHeightIntegrator.integrate(
        normals,
        sample_spacing_mm=0.25,
        normalize_output=False,
    )

    unit_range = float(np.ptp(unit_spacing))
    physical_range = float(np.ptp(physical_spacing))

    assert unit_range > 0.0
    assert physical_range == pytest.approx(
        unit_range * 0.25,
        rel=1e-10,
        abs=1e-10,
    )
