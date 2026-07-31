from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_relief_normal_confidence_applier import (
    AtlasReliefNormalConfidenceApplier,
)


def _gradient_to_normal(
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

    lengths = np.linalg.norm(
        normals,
        axis=2,
        keepdims=True,
    )

    return np.asarray(
        normals / np.maximum(lengths, 1.0e-12),
        dtype=np.float64,
    )


def _normal_to_gradients(
    normals: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    nz = np.maximum(
        normals[..., 2],
        0.05,
    )

    return (
        -normals[..., 0] / nz,
        -normals[..., 1] / nz,
    )


def _normals() -> np.ndarray:
    gradient_x = np.full(
        (40, 50),
        0.40,
        dtype=np.float64,
    )
    gradient_y = np.full(
        (40, 50),
        -0.20,
        dtype=np.float64,
    )

    return _gradient_to_normal(
        gradient_x,
        gradient_y,
    )


def test_output_contract() -> None:
    result = AtlasReliefNormalConfidenceApplier.apply(
        _normals(),
        confidence_map=np.ones(
            (40, 50),
            dtype=np.float64,
        ),
    )

    assert result.shape == (40, 50, 3)
    assert result.dtype == np.float64
    assert np.all(np.isfinite(result))

    lengths = np.linalg.norm(
        result,
        axis=2,
    )

    assert np.allclose(
        lengths,
        1.0,
        atol=1.0e-12,
    )


def test_unit_confidence_preserves_normals() -> None:
    normals = _normals()

    result = AtlasReliefNormalConfidenceApplier.apply(
        normals,
        confidence_map=np.ones(
            normals.shape[:2],
            dtype=np.float64,
        ),
    )

    assert np.allclose(
        result,
        normals,
        atol=1.0e-12,
    )


def test_zero_confidence_flattens_normals() -> None:
    normals = _normals()

    result = AtlasReliefNormalConfidenceApplier.apply(
        normals,
        confidence_map=np.zeros(
            normals.shape[:2],
            dtype=np.float64,
        ),
    )

    expected = np.zeros_like(normals)
    expected[..., 2] = 1.0

    assert np.allclose(
        result,
        expected,
        atol=1.0e-12,
    )


def test_half_confidence_halves_gradient_magnitude() -> None:
    normals = _normals()

    result = AtlasReliefNormalConfidenceApplier.apply(
        normals,
        confidence_map=np.full(
            normals.shape[:2],
            0.50,
            dtype=np.float64,
        ),
    )

    input_x, input_y = _normal_to_gradients(
        normals
    )
    result_x, result_y = _normal_to_gradients(
        result
    )

    assert np.allclose(
        result_x,
        0.50 * input_x,
        atol=1.0e-12,
    )
    assert np.allclose(
        result_y,
        0.50 * input_y,
        atol=1.0e-12,
    )


def test_gradient_direction_is_preserved() -> None:
    normals = _normals()

    confidence = np.linspace(
        0.10,
        1.0,
        normals.shape[1],
        dtype=np.float64,
    )[None, :]

    confidence = np.repeat(
        confidence,
        normals.shape[0],
        axis=0,
    )

    result = AtlasReliefNormalConfidenceApplier.apply(
        normals,
        confidence_map=confidence,
    )

    input_x, input_y = _normal_to_gradients(
        normals
    )
    result_x, result_y = _normal_to_gradients(
        result
    )

    input_ratio = input_y / input_x
    result_ratio = result_y / result_x

    assert np.allclose(
        result_ratio,
        input_ratio,
        atol=1.0e-12,
    )


def test_soft_confidence_does_not_create_hard_gradient_jump() -> None:
    rows = 40
    columns = 50

    normals = _normals()

    confidence = np.linspace(
        0.0,
        1.0,
        columns,
        dtype=np.float64,
    )[None, :]

    confidence = np.repeat(
        confidence,
        rows,
        axis=0,
    )

    result = AtlasReliefNormalConfidenceApplier.apply(
        normals,
        confidence_map=confidence,
    )

    gradient_x, _ = _normal_to_gradients(
        result
    )

    horizontal_changes = np.abs(
        np.diff(
            gradient_x,
            axis=1,
        )
    )

    assert float(
        np.max(horizontal_changes)
    ) < 0.02


def test_optional_mask_flattens_normals_outside_mask() -> None:
    normals = _normals()

    mask = np.zeros(
        normals.shape[:2],
        dtype=np.float64,
    )
    mask[10:30, 12:38] = 1.0

    result = AtlasReliefNormalConfidenceApplier.apply(
        normals,
        confidence_map=np.ones(
            normals.shape[:2],
            dtype=np.float64,
        ),
        mask=mask,
    )

    outside = mask <= 0.0
    inside = mask > 0.0

    assert np.allclose(
        result[outside, 0],
        0.0,
        atol=1.0e-12,
    )
    assert np.allclose(
        result[outside, 1],
        0.0,
        atol=1.0e-12,
    )
    assert np.allclose(
        result[outside, 2],
        1.0,
        atol=1.0e-12,
    )

    assert np.allclose(
        result[inside],
        normals[inside],
        atol=1.0e-12,
    )


def test_confidence_values_are_clipped_to_unit_interval() -> None:
    normals = _normals()

    confidence = np.ones(
        normals.shape[:2],
        dtype=np.float64,
    )
    confidence[:, :25] = -1.0
    confidence[:, 25:] = 2.0

    result = AtlasReliefNormalConfidenceApplier.apply(
        normals,
        confidence_map=confidence,
    )

    flat = result[:, :25]
    preserved = result[:, 25:]

    assert np.allclose(
        flat[..., 0],
        0.0,
        atol=1.0e-12,
    )
    assert np.allclose(
        flat[..., 1],
        0.0,
        atol=1.0e-12,
    )
    assert np.allclose(
        flat[..., 2],
        1.0,
        atol=1.0e-12,
    )
    assert np.allclose(
        preserved,
        normals[:, 25:],
        atol=1.0e-12,
    )


def test_wrong_normal_shape_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="normals",
    ):
        AtlasReliefNormalConfidenceApplier.apply(
            np.zeros(
                (40, 50),
                dtype=np.float64,
            ),
            confidence_map=np.ones(
                (40, 50),
                dtype=np.float64,
            ),
        )


def test_wrong_confidence_shape_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="confidence_map",
    ):
        AtlasReliefNormalConfidenceApplier.apply(
            _normals(),
            confidence_map=np.ones(
                (20, 25),
                dtype=np.float64,
            ),
        )


def test_nonfinite_confidence_is_rejected() -> None:
    confidence = np.ones(
        (40, 50),
        dtype=np.float64,
    )
    confidence[10, 20] = np.nan

    with pytest.raises(
        ValueError,
        match="confidence_map",
    ):
        AtlasReliefNormalConfidenceApplier.apply(
            _normals(),
            confidence_map=confidence,
        )


def test_wrong_mask_shape_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="mask",
    ):
        AtlasReliefNormalConfidenceApplier.apply(
            _normals(),
            confidence_map=np.ones(
                (40, 50),
                dtype=np.float64,
            ),
            mask=np.ones(
                (20, 25),
                dtype=np.float64,
            ),
        )


def test_invalid_minimum_nz_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="minimum_nz",
    ):
        AtlasReliefNormalConfidenceApplier.apply(
            _normals(),
            confidence_map=np.ones(
                (40, 50),
                dtype=np.float64,
            ),
            minimum_nz=0.0,
        )


def test_minimum_retention_limits_maximum_gradient_reduction() -> None:
    normals = _normals()

    result = AtlasReliefNormalConfidenceApplier.apply(
        normals,
        confidence_map=np.zeros(
            normals.shape[:2],
            dtype=np.float64,
        ),
        minimum_retention=0.65,
    )

    input_x, input_y = _normal_to_gradients(
        normals
    )
    result_x, result_y = _normal_to_gradients(
        result
    )

    assert np.allclose(
        result_x,
        0.65 * input_x,
        atol=1.0e-12,
    )
    assert np.allclose(
        result_y,
        0.65 * input_y,
        atol=1.0e-12,
    )


def test_minimum_retention_blends_soft_confidence() -> None:
    normals = _normals()

    result = AtlasReliefNormalConfidenceApplier.apply(
        normals,
        confidence_map=np.full(
            normals.shape[:2],
            0.40,
            dtype=np.float64,
        ),
        minimum_retention=0.65,
    )

    input_x, input_y = _normal_to_gradients(
        normals
    )
    result_x, result_y = _normal_to_gradients(
        result
    )

    expected_scale = (
        0.65
        + (1.0 - 0.65) * 0.40
    )

    assert np.allclose(
        result_x,
        expected_scale * input_x,
        atol=1.0e-12,
    )
    assert np.allclose(
        result_y,
        expected_scale * input_y,
        atol=1.0e-12,
    )


def test_unit_confidence_remains_unit_with_minimum_retention() -> None:
    normals = _normals()

    result = AtlasReliefNormalConfidenceApplier.apply(
        normals,
        confidence_map=np.ones(
            normals.shape[:2],
            dtype=np.float64,
        ),
        minimum_retention=0.65,
    )

    assert np.allclose(
        result,
        normals,
        atol=1.0e-12,
    )


@pytest.mark.parametrize(
    "minimum_retention",
    [
        -0.1,
        1.1,
        np.nan,
        np.inf,
    ],
)
def test_invalid_minimum_retention_is_rejected(
    minimum_retention: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="minimum_retention",
    ):
        AtlasReliefNormalConfidenceApplier.apply(
            _normals(),
            confidence_map=np.ones(
                (40, 50),
                dtype=np.float64,
            ),
            minimum_retention=minimum_retention,
        )


def test_minimum_retention_map_controls_local_gradient_reduction() -> None:
    normals = _normals()
    rows, columns = normals.shape[:2]

    confidence = np.full(
        (rows, columns),
        0.20,
        dtype=np.float64,
    )

    retention_map = np.full(
        (rows, columns),
        0.65,
        dtype=np.float64,
    )
    retention_map[10:20, 15:30] = 0.40

    result = AtlasReliefNormalConfidenceApplier.apply(
        normals,
        confidence_map=confidence,
        minimum_retention=0.65,
        minimum_retention_map=retention_map,
    )

    input_x, input_y = _normal_to_gradients(
        normals
    )
    result_x, result_y = _normal_to_gradients(
        result
    )

    expected_scale = (
        retention_map
        + (
            1.0 - retention_map
        )
        * confidence
    )

    assert np.allclose(
        result_x,
        expected_scale * input_x,
        atol=1.0e-12,
    )
    assert np.allclose(
        result_y,
        expected_scale * input_y,
        atol=1.0e-12,
    )


def test_minimum_retention_map_leaves_unmodified_regions_at_scalar_value() -> None:
    normals = _normals()
    rows, columns = normals.shape[:2]

    confidence = np.full(
        (rows, columns),
        0.30,
        dtype=np.float64,
    )

    scalar_result = AtlasReliefNormalConfidenceApplier.apply(
        normals,
        confidence_map=confidence,
        minimum_retention=0.65,
    )

    retention_map = np.full(
        (rows, columns),
        0.65,
        dtype=np.float64,
    )
    retention_map[10:20, 15:30] = 0.40

    mapped_result = AtlasReliefNormalConfidenceApplier.apply(
        normals,
        confidence_map=confidence,
        minimum_retention=0.65,
        minimum_retention_map=retention_map,
    )

    clear_region = np.ones(
        (rows, columns),
        dtype=bool,
    )
    clear_region[10:20, 15:30] = False

    assert np.allclose(
        mapped_result[clear_region],
        scalar_result[clear_region],
        atol=1.0e-12,
    )


def test_wrong_minimum_retention_map_shape_is_rejected() -> None:
    normals = _normals()

    with pytest.raises(
        ValueError,
        match="minimum_retention_map",
    ):
        AtlasReliefNormalConfidenceApplier.apply(
            normals,
            confidence_map=np.ones(
                normals.shape[:2],
                dtype=np.float64,
            ),
            minimum_retention_map=np.ones(
                (3, 4),
                dtype=np.float64,
            ),
        )


@pytest.mark.parametrize(
    "invalid_value",
    [
        -0.1,
        1.1,
        np.nan,
        np.inf,
    ],
)
def test_invalid_minimum_retention_map_values_are_rejected(
    invalid_value: float,
) -> None:
    normals = _normals()

    retention_map = np.full(
        normals.shape[:2],
        0.65,
        dtype=np.float64,
    )
    retention_map[0, 0] = invalid_value

    with pytest.raises(
        ValueError,
        match="minimum_retention_map",
    ):
        AtlasReliefNormalConfidenceApplier.apply(
            normals,
            confidence_map=np.ones(
                normals.shape[:2],
                dtype=np.float64,
            ),
            minimum_retention_map=retention_map,
        )
