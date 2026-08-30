from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_relief_normal_structure_detail_decomposer import (
    AtlasReliefNormalStructureDetailDecomposer,
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


def _normals_from_height(
    height: np.ndarray,
) -> np.ndarray:
    gradient_y, gradient_x = np.gradient(
        height
    )

    normals = np.stack(
        [
            -gradient_x,
            -gradient_y,
            np.ones_like(height),
        ],
        axis=2,
    )

    return _normalize(normals)


def _gradient_from_normals(
    normals: np.ndarray,
    *,
    minimum_nz: float = 0.05,
) -> tuple[np.ndarray, np.ndarray]:
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

    return gradient_x, gradient_y


def test_output_shapes_match_input() -> None:
    normals = np.zeros(
        (40, 52, 3),
        dtype=np.float64,
    )
    normals[..., 2] = 1.0

    structure, detail = (
        AtlasReliefNormalStructureDetailDecomposer.decompose(
            normals,
        )
    )

    assert structure.shape == normals.shape
    assert detail.shape == normals.shape


def test_outputs_are_float64() -> None:
    normals = np.zeros(
        (30, 36, 3),
        dtype=np.float32,
    )
    normals[..., 2] = 1.0

    structure, detail = (
        AtlasReliefNormalStructureDetailDecomposer.decompose(
            normals,
        )
    )

    assert structure.dtype == np.float64
    assert detail.dtype == np.float64


def test_outputs_are_unit_length_normals() -> None:
    rows = 48
    columns = 56

    y, x = np.mgrid[
        -1.0:1.0:complex(rows),
        -1.0:1.0:complex(columns),
    ]

    height = (
        0.50 * np.exp(
            -3.0 * (x * x + y * y)
        )
        + 0.02 * np.sin(
            18.0 * x
        )
    )

    normals = _normals_from_height(
        height
    )

    structure, detail = (
        AtlasReliefNormalStructureDetailDecomposer.decompose(
            normals,
            structure_radius=5,
        )
    )

    structure_lengths = np.linalg.norm(
        structure,
        axis=2,
    )
    detail_lengths = np.linalg.norm(
        detail,
        axis=2,
    )

    assert np.allclose(
        structure_lengths,
        1.0,
        atol=1e-8,
    )
    assert np.allclose(
        detail_lengths,
        1.0,
        atol=1e-8,
    )


def test_flat_normals_remain_flat_in_both_layers() -> None:
    normals = np.zeros(
        (32, 44, 3),
        dtype=np.float64,
    )
    normals[..., 2] = 1.0

    structure, detail = (
        AtlasReliefNormalStructureDetailDecomposer.decompose(
            normals,
            structure_radius=4,
        )
    )

    expected = np.zeros_like(normals)
    expected[..., 2] = 1.0

    assert np.allclose(
        structure,
        expected,
        atol=1e-10,
    )
    assert np.allclose(
        detail,
        expected,
        atol=1e-10,
    )


def test_structure_layer_retains_broad_convex_form() -> None:
    rows = 61
    columns = 61

    y, x = np.mgrid[
        -1.0:1.0:complex(rows),
        -1.0:1.0:complex(columns),
    ]

    broad_height = np.exp(
        -3.0 * (x * x + y * y)
    )

    normals = _normals_from_height(
        broad_height
    )

    structure, _ = (
        AtlasReliefNormalStructureDetailDecomposer.decompose(
            normals,
            structure_radius=5,
        )
    )

    structure_gx, structure_gy = (
        _gradient_from_normals(
            structure
        )
    )

    center_left = float(
        structure_gx[
            rows // 2,
            columns // 2 - 10,
        ]
    )
    center_right = float(
        structure_gx[
            rows // 2,
            columns // 2 + 10,
        ]
    )

    assert center_left > 0.0
    assert center_right < 0.0
    assert np.max(
        np.abs(structure_gy)
    ) > 0.0


def test_detail_layer_is_small_for_broad_smooth_form() -> None:
    rows = 64
    columns = 64

    y, x = np.mgrid[
        -1.0:1.0:complex(rows),
        -1.0:1.0:complex(columns),
    ]

    broad_height = np.exp(
        -2.5 * (x * x + y * y)
    )

    normals = _normals_from_height(
        broad_height
    )

    _, detail = (
        AtlasReliefNormalStructureDetailDecomposer.decompose(
            normals,
            structure_radius=5,
        )
    )

    detail_gx, detail_gy = (
        _gradient_from_normals(
            detail
        )
    )

    detail_energy = float(
        np.mean(
            detail_gx * detail_gx
            + detail_gy * detail_gy
        )
    )

    assert detail_energy < 0.002


def test_detail_layer_retains_high_frequency_ridges() -> None:
    rows = 64
    columns = 80

    y, x = np.mgrid[
        -1.0:1.0:complex(rows),
        -1.0:1.0:complex(columns),
    ]

    broad = 0.35 * np.exp(
        -2.0 * (x * x + y * y)
    )
    ridges = 0.025 * np.sin(
        22.0 * x
    )

    broad_normals = _normals_from_height(
        broad
    )
    combined_normals = _normals_from_height(
        broad + ridges
    )

    _, detail = (
        AtlasReliefNormalStructureDetailDecomposer.decompose(
            combined_normals,
            structure_radius=5,
        )
    )

    combined_gx, combined_gy = (
        _gradient_from_normals(
            combined_normals
        )
    )
    broad_gx, broad_gy = (
        _gradient_from_normals(
            broad_normals
        )
    )
    detail_gx, detail_gy = (
        _gradient_from_normals(
            detail
        )
    )

    true_ridge_energy = float(
        np.mean(
            (
                combined_gx
                - broad_gx
            ) ** 2
            + (
                combined_gy
                - broad_gy
            ) ** 2
        )
    )

    horizontal_energy = float(
        np.mean(
            detail_gx * detail_gx
        )
    )
    vertical_energy = float(
        np.mean(
            detail_gy * detail_gy
        )
    )
    detail_energy = float(
        np.mean(
            detail_gx * detail_gx
            + detail_gy * detail_gy
        )
    )

    retained_ratio = (
        detail_energy
        / max(
            true_ridge_energy,
            1e-12,
        )
    )

    assert horizontal_energy > vertical_energy * 4.0
    assert retained_ratio > 0.80


def test_structure_plus_detail_gradients_reconstruct_input_gradients() -> None:
    rows = 54
    columns = 66

    y, x = np.mgrid[
        -1.0:1.0:complex(rows),
        -1.0:1.0:complex(columns),
    ]

    height = (
        0.40 * np.exp(
            -2.5 * (x * x + y * y)
        )
        + 0.015 * np.sin(
            17.0 * x
        )
        + 0.012 * np.cos(
            15.0 * y
        )
    )

    normals = _normals_from_height(
        height
    )

    structure, detail = (
        AtlasReliefNormalStructureDetailDecomposer.decompose(
            normals,
            structure_radius=4,
        )
    )

    input_gx, input_gy = (
        _gradient_from_normals(
            normals
        )
    )
    structure_gx, structure_gy = (
        _gradient_from_normals(
            structure
        )
    )
    detail_gx, detail_gy = (
        _gradient_from_normals(
            detail
        )
    )

    assert np.allclose(
        structure_gx + detail_gx,
        input_gx,
        atol=1e-8,
    )
    assert np.allclose(
        structure_gy + detail_gy,
        input_gy,
        atol=1e-8,
    )


def test_mask_makes_layers_flat_outside_subject() -> None:
    rows = 50
    columns = 60

    y, x = np.mgrid[
        -1.0:1.0:complex(rows),
        -1.0:1.0:complex(columns),
    ]

    normals = _normals_from_height(
        np.exp(
            -3.0 * (x * x + y * y)
        )
    )

    mask = np.zeros(
        (rows, columns),
        dtype=np.float64,
    )
    mask[8:42, 10:50] = 1.0

    structure, detail = (
        AtlasReliefNormalStructureDetailDecomposer.decompose(
            normals,
            mask=mask,
            structure_radius=4,
        )
    )

    outside = mask <= 0.0

    assert np.allclose(
        structure[..., 0][outside],
        0.0,
        atol=1e-12,
    )
    assert np.allclose(
        structure[..., 1][outside],
        0.0,
        atol=1e-12,
    )
    assert np.allclose(
        structure[..., 2][outside],
        1.0,
        atol=1e-12,
    )

    assert np.allclose(
        detail[..., 0][outside],
        0.0,
        atol=1e-12,
    )
    assert np.allclose(
        detail[..., 1][outside],
        0.0,
        atol=1e-12,
    )
    assert np.allclose(
        detail[..., 2][outside],
        1.0,
        atol=1e-12,
    )


def test_invalid_normal_shape_is_rejected() -> None:
    normals = np.zeros(
        (40, 50, 2),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="normals",
    ):
        AtlasReliefNormalStructureDetailDecomposer.decompose(
            normals,
        )


def test_nonfinite_normals_are_rejected() -> None:
    normals = np.zeros(
        (30, 40, 3),
        dtype=np.float64,
    )
    normals[..., 2] = 1.0
    normals[10, 12, 0] = np.nan

    with pytest.raises(
        ValueError,
        match="normals",
    ):
        AtlasReliefNormalStructureDetailDecomposer.decompose(
            normals,
        )


def test_mask_shape_must_match_normal_field() -> None:
    normals = np.zeros(
        (30, 40, 3),
        dtype=np.float64,
    )
    normals[..., 2] = 1.0

    wrong_mask = np.ones(
        (31, 40),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="mask",
    ):
        AtlasReliefNormalStructureDetailDecomposer.decompose(
            normals,
            mask=wrong_mask,
        )


@pytest.mark.parametrize(
    "structure_radius",
    [
        0,
        -1,
        1.5,
        np.nan,
        np.inf,
    ],
)
def test_invalid_structure_radius_is_rejected(
    structure_radius: float,
) -> None:
    normals = np.zeros(
        (30, 40, 3),
        dtype=np.float64,
    )
    normals[..., 2] = 1.0

    with pytest.raises(
        ValueError,
        match="structure_radius",
    ):
        AtlasReliefNormalStructureDetailDecomposer.decompose(
            normals,
            structure_radius=structure_radius,
        )


@pytest.mark.parametrize(
    "minimum_nz",
    [
        0.0,
        -0.1,
        np.nan,
        np.inf,
    ],
)
def test_invalid_minimum_nz_is_rejected(
    minimum_nz: float,
) -> None:
    normals = np.zeros(
        (30, 40, 3),
        dtype=np.float64,
    )
    normals[..., 2] = 1.0

    with pytest.raises(
        ValueError,
        match="minimum_nz",
    ):
        AtlasReliefNormalStructureDetailDecomposer.decompose(
            normals,
            minimum_nz=minimum_nz,
        )


def test_recombine_restores_structure_plus_detail_gradients() -> None:
    rows = 36
    columns = 44

    y, x = np.mgrid[
        -1.0:1.0:complex(rows),
        -1.0:1.0:complex(columns),
    ]

    height = (
        0.35 * np.exp(-2.0 * (x * x + y * y))
        + 0.018 * np.sin(15.0 * x)
        + 0.013 * np.cos(13.0 * y)
    )

    normals = _normals_from_height(height)

    structure, detail = (
        AtlasReliefNormalStructureDetailDecomposer.decompose(
            normals,
            structure_radius=4,
        )
    )

    combined = (
        AtlasReliefNormalStructureDetailDecomposer.recombine(
            structure,
            detail,
        )
    )

    input_gx, input_gy = _gradient_from_normals(normals)
    combined_gx, combined_gy = _gradient_from_normals(combined)

    assert combined.shape == normals.shape
    assert combined.dtype == np.float64
    assert np.allclose(
        np.linalg.norm(combined, axis=2),
        1.0,
        atol=1e-10,
    )
    assert np.allclose(combined_gx, input_gx, atol=1e-8)
    assert np.allclose(combined_gy, input_gy, atol=1e-8)


def test_recombine_restores_structure_plus_detail_gradients() -> None:
    rows = 36
    columns = 44

    y, x = np.mgrid[
        -1.0:1.0:complex(rows),
        -1.0:1.0:complex(columns),
    ]

    height = (
        0.35 * np.exp(-2.0 * (x * x + y * y))
        + 0.018 * np.sin(15.0 * x)
        + 0.013 * np.cos(13.0 * y)
    )

    normals = _normals_from_height(height)

    structure, detail = (
        AtlasReliefNormalStructureDetailDecomposer.decompose(
            normals,
            structure_radius=4,
        )
    )

    combined = (
        AtlasReliefNormalStructureDetailDecomposer.recombine(
            structure,
            detail,
        )
    )

    input_gx, input_gy = _gradient_from_normals(normals)
    combined_gx, combined_gy = _gradient_from_normals(combined)

    assert combined.shape == normals.shape
    assert combined.dtype == np.float64
    assert np.allclose(
        np.linalg.norm(combined, axis=2),
        1.0,
        atol=1e-10,
    )
    assert np.allclose(combined_gx, input_gx, atol=1e-8)
    assert np.allclose(combined_gy, input_gy, atol=1e-8)
