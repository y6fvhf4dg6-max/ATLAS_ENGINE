from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_relief_screened_normal_integrator import (
    AtlasReliefScreenedNormalIntegrator,
)


def _normalize_normals(normals: np.ndarray) -> np.ndarray:
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

    return _normalize_normals(normals)


def test_flat_normals_preserve_flat_anchor() -> None:
    anchor = np.full(
        (24, 32),
        0.42,
        dtype=np.float64,
    )

    normals = np.zeros(
        (24, 32, 3),
        dtype=np.float64,
    )
    normals[..., 2] = 1.0

    result = AtlasReliefScreenedNormalIntegrator.integrate(
        normals,
        anchor,
        screening_strength=2.0,
        normalize_output=False,
    )

    assert result.shape == anchor.shape
    assert result.dtype == np.float64
    assert np.all(np.isfinite(result))
    assert np.allclose(
        result,
        anchor,
        atol=1e-8,
    )


def test_zero_confidence_returns_anchor() -> None:
    rows = 28
    columns = 36

    y, x = np.mgrid[
        -1.0:1.0:complex(rows),
        -1.0:1.0:complex(columns),
    ]

    source_height = np.exp(
        -4.0 * (x * x + y * y)
    )
    normals = _normals_from_height(
        source_height
    )

    anchor = np.linspace(
        0.15,
        0.75,
        rows * columns,
        dtype=np.float64,
    ).reshape(rows, columns)

    confidence = np.zeros(
        (rows, columns),
        dtype=np.float64,
    )

    result = AtlasReliefScreenedNormalIntegrator.integrate(
        normals,
        anchor,
        confidence_map=confidence,
        screening_strength=1.5,
        normalize_output=False,
    )

    assert np.allclose(
        result,
        anchor,
        atol=1e-8,
    )


def test_full_confidence_reconstructs_convex_center() -> None:
    rows = 51
    columns = 51

    y, x = np.mgrid[
        -1.0:1.0:complex(rows),
        -1.0:1.0:complex(columns),
    ]

    source_height = np.exp(
        -5.0 * (x * x + y * y)
    )

    normals = _normals_from_height(
        source_height
    )

    anchor = np.zeros(
        (rows, columns),
        dtype=np.float64,
    )

    result = AtlasReliefScreenedNormalIntegrator.integrate(
        normals,
        anchor,
        confidence_map=np.ones(
            (rows, columns),
            dtype=np.float64,
        ),
        screening_strength=0.05,
        normalize_output=True,
    )

    center = result[
        rows // 2,
        columns // 2,
    ]

    corners = np.array(
        [
            result[0, 0],
            result[0, -1],
            result[-1, 0],
            result[-1, -1],
        ]
    )

    assert result.min() == pytest.approx(
        0.0,
        abs=1e-8,
    )
    assert result.max() == pytest.approx(
        1.0,
        abs=1e-8,
    )
    assert center > 0.85
    assert np.all(corners < 0.20)


def test_stronger_screening_stays_closer_to_anchor() -> None:
    rows = 42
    columns = 46

    y, x = np.mgrid[
        -1.0:1.0:complex(rows),
        -1.0:1.0:complex(columns),
    ]

    source_height = np.exp(
        -4.0 * (x * x + y * y)
    )
    normals = _normals_from_height(
        source_height
    )

    anchor = np.full(
        (rows, columns),
        0.30,
        dtype=np.float64,
    )

    weak = AtlasReliefScreenedNormalIntegrator.integrate(
        normals,
        anchor,
        screening_strength=0.05,
        normalize_output=False,
    )

    strong = AtlasReliefScreenedNormalIntegrator.integrate(
        normals,
        anchor,
        screening_strength=20.0,
        normalize_output=False,
    )

    weak_distance = float(
        np.mean(
            np.abs(
                weak - anchor
            )
        )
    )
    strong_distance = float(
        np.mean(
            np.abs(
                strong - anchor
            )
        )
    )

    assert strong_distance < weak_distance


def test_confidence_limits_normal_influence_to_active_region() -> None:
    rows = 40
    columns = 48

    y, x = np.mgrid[
        -1.0:1.0:complex(rows),
        -1.0:1.0:complex(columns),
    ]

    source_height = np.exp(
        -5.0 * (x * x + y * y)
    )
    normals = _normals_from_height(
        source_height
    )

    anchor = np.full(
        (rows, columns),
        0.40,
        dtype=np.float64,
    )

    confidence = np.zeros(
        (rows, columns),
        dtype=np.float64,
    )
    confidence[8:32, 12:36] = 1.0

    result = AtlasReliefScreenedNormalIntegrator.integrate(
        normals,
        anchor,
        confidence_map=confidence,
        screening_strength=2.0,
        normalize_output=False,
    )

    outside = confidence == 0.0
    inside = confidence > 0.5

    outside_error = float(
        np.mean(
            np.abs(
                result[outside]
                - anchor[outside]
            )
        )
    )

    inside_change = float(
        np.mean(
            np.abs(
                result[inside]
                - anchor[inside]
            )
        )
    )

    assert outside_error < inside_change


def test_mask_zeroes_output_outside_subject() -> None:
    rows = 30
    columns = 40

    anchor = np.full(
        (rows, columns),
        0.50,
        dtype=np.float64,
    )

    normals = np.zeros(
        (rows, columns, 3),
        dtype=np.float64,
    )
    normals[..., 0] = -0.20
    normals[..., 2] = 1.0
    normals = _normalize_normals(
        normals
    )

    mask = np.zeros(
        (rows, columns),
        dtype=np.float64,
    )
    mask[5:25, 8:32] = 1.0

    result = AtlasReliefScreenedNormalIntegrator.integrate(
        normals,
        anchor,
        mask=mask,
        screening_strength=1.0,
        normalize_output=True,
    )

    assert np.allclose(
        result[mask <= 0.0],
        0.0,
    )
    assert np.all(
        np.isfinite(
            result[mask > 0.0]
        )
    )


@pytest.mark.parametrize(
    "invalid_normals",
    [
        np.zeros(
            (16, 16),
            dtype=np.float64,
        ),
        np.zeros(
            (16, 16, 2),
            dtype=np.float64,
        ),
        np.zeros(
            (16, 16, 4),
            dtype=np.float64,
        ),
    ],
)
def test_invalid_normal_shape_is_rejected(
    invalid_normals: np.ndarray,
) -> None:
    anchor = np.zeros(
        (16, 16),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="normals",
    ):
        AtlasReliefScreenedNormalIntegrator.integrate(
            invalid_normals,
            anchor,
        )


def test_anchor_shape_must_match_normal_field() -> None:
    normals = np.zeros(
        (16, 20, 3),
        dtype=np.float64,
    )
    normals[..., 2] = 1.0

    wrong_anchor = np.zeros(
        (15, 20),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="anchor_height",
    ):
        AtlasReliefScreenedNormalIntegrator.integrate(
            normals,
            wrong_anchor,
        )


def test_confidence_shape_must_match_normal_field() -> None:
    normals = np.zeros(
        (16, 20, 3),
        dtype=np.float64,
    )
    normals[..., 2] = 1.0

    anchor = np.zeros(
        (16, 20),
        dtype=np.float64,
    )

    wrong_confidence = np.ones(
        (15, 20),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="confidence_map",
    ):
        AtlasReliefScreenedNormalIntegrator.integrate(
            normals,
            anchor,
            confidence_map=wrong_confidence,
        )


@pytest.mark.parametrize(
    "screening_strength",
    [
        0.0,
        -1.0,
        np.nan,
        np.inf,
    ],
)
def test_invalid_screening_strength_is_rejected(
    screening_strength: float,
) -> None:
    normals = np.zeros(
        (12, 14, 3),
        dtype=np.float64,
    )
    normals[..., 2] = 1.0

    anchor = np.zeros(
        (12, 14),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="screening_strength",
    ):
        AtlasReliefScreenedNormalIntegrator.integrate(
            normals,
            anchor,
            screening_strength=screening_strength,
        )
