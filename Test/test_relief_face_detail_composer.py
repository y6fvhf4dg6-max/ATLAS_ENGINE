from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_relief_face_detail_composer import (
    AtlasReliefFaceDetailComposer,
)


def test_output_preserves_shape_and_dtype() -> None:
    base = np.full(
        (24, 32),
        0.40,
        dtype=np.float64,
    )
    detail = np.zeros_like(base)
    weight = np.ones_like(base)

    result = AtlasReliefFaceDetailComposer.compose(
        base,
        detail,
        weight,
    )

    assert result.shape == base.shape
    assert result.dtype == np.float64


def test_zero_weight_preserves_base_height_exactly() -> None:
    base = np.linspace(
        0.10,
        0.90,
        20 * 30,
        dtype=np.float64,
    ).reshape(20, 30)

    detail = np.ones_like(base)
    weight = np.zeros_like(base)

    result = AtlasReliefFaceDetailComposer.compose(
        base,
        detail,
        weight,
    )

    assert np.allclose(
        result,
        base,
        atol=1e-12,
    )


def test_detail_is_applied_only_where_weight_is_active() -> None:
    base = np.full(
        (20, 30),
        0.50,
        dtype=np.float64,
    )

    detail = np.zeros_like(base)
    detail[5:10, 8:22] = -1.0
    detail[10:15, 8:22] = 1.0

    weight = np.zeros_like(base)
    weight[5:15, 8:22] = 1.0

    result = AtlasReliefFaceDetailComposer.compose(
        base,
        detail,
        weight,
        max_detail_amplitude=0.10,
    )

    assert np.allclose(
        result[:5],
        0.50,
    )
    assert np.allclose(
        result[15:],
        0.50,
    )
    assert np.allclose(
        result[:, :8],
        0.50,
    )
    assert np.allclose(
        result[:, 22:],
        0.50,
    )

    assert np.all(
        result[6:9, 9:21] < 0.50
    )
    assert np.all(
        result[11:14, 9:21] > 0.50
    )


def test_detail_amplitude_is_limited() -> None:
    base = np.full(
        (16, 18),
        0.50,
        dtype=np.float64,
    )

    detail = np.full_like(
        base,
        100.0,
    )
    weight = np.ones_like(base)

    result = AtlasReliefFaceDetailComposer.compose(
        base,
        detail,
        weight,
        max_detail_amplitude=0.08,
        clamp_output=False,
    )

    delta = result - base

    assert float(delta.max()) <= 0.08 + 1e-12


def test_negative_detail_is_limited_symmetrically() -> None:
    base = np.full(
        (16, 18),
        0.50,
        dtype=np.float64,
    )

    detail = np.full_like(
        base,
        -100.0,
    )
    weight = np.ones_like(base)

    result = AtlasReliefFaceDetailComposer.compose(
        base,
        detail,
        weight,
        max_detail_amplitude=0.06,
        clamp_output=False,
    )

    delta = result - base

    assert float(delta.min()) >= -0.06 - 1e-12


def test_detail_is_centered_before_application() -> None:
    base = np.full(
        (20, 20),
        0.50,
        dtype=np.float64,
    )

    detail = np.full_like(
        base,
        0.75,
    )
    weight = np.ones_like(base)

    result = AtlasReliefFaceDetailComposer.compose(
        base,
        detail,
        weight,
        max_detail_amplitude=0.10,
    )

    assert np.allclose(
        result,
        base,
        atol=1e-12,
    )


def test_face_bounds_prevent_detail_leakage() -> None:
    base = np.full(
        (30, 40),
        0.50,
        dtype=np.float64,
    )

    detail = np.ones_like(base)
    weight = np.ones_like(base)

    result = AtlasReliefFaceDetailComposer.compose(
        base,
        detail,
        weight,
        face_bounds=(6, 23, 9, 30),
        max_detail_amplitude=0.10,
    )

    assert np.allclose(
        result[:6],
        base[:6],
    )
    assert np.allclose(
        result[24:],
        base[24:],
    )
    assert np.allclose(
        result[:, :9],
        base[:, :9],
    )
    assert np.allclose(
        result[:, 31:],
        base[:, 31:],
    )


def test_output_is_clamped_to_unit_interval() -> None:
    base = np.full(
        (12, 14),
        0.98,
        dtype=np.float64,
    )

    detail = np.ones_like(base)
    weight = np.ones_like(base)

    result = AtlasReliefFaceDetailComposer.compose(
        base,
        detail,
        weight,
        max_detail_amplitude=0.20,
        clamp_output=True,
    )

    assert float(result.min()) >= 0.0
    assert float(result.max()) <= 1.0


@pytest.mark.parametrize(
    "bad_shape",
    [
        (10, 12, 1),
        (10, 12, 3),
        (10,),
    ],
)
def test_base_height_must_be_two_dimensional(
    bad_shape: tuple[int, ...],
) -> None:
    base = np.zeros(
        bad_shape,
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="base_height",
    ):
        AtlasReliefFaceDetailComposer.compose(
            base,
            np.zeros((10, 12), dtype=np.float64),
            np.zeros((10, 12), dtype=np.float64),
        )


def test_detail_shape_must_match_base() -> None:
    base = np.zeros(
        (10, 12),
        dtype=np.float64,
    )

    detail = np.zeros(
        (9, 12),
        dtype=np.float64,
    )

    weight = np.zeros_like(base)

    with pytest.raises(
        ValueError,
        match="detail_height",
    ):
        AtlasReliefFaceDetailComposer.compose(
            base,
            detail,
            weight,
        )


def test_weight_shape_must_match_base() -> None:
    base = np.zeros(
        (10, 12),
        dtype=np.float64,
    )

    detail = np.zeros_like(base)

    weight = np.zeros(
        (10, 11),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="detail_weight",
    ):
        AtlasReliefFaceDetailComposer.compose(
            base,
            detail,
            weight,
        )


def test_nonfinite_input_is_rejected() -> None:
    base = np.zeros(
        (10, 12),
        dtype=np.float64,
    )

    detail = np.zeros_like(base)
    detail[3, 4] = np.nan

    weight = np.ones_like(base)

    with pytest.raises(
        ValueError,
        match="finite",
    ):
        AtlasReliefFaceDetailComposer.compose(
            base,
            detail,
            weight,
        )


@pytest.mark.parametrize(
    "face_bounds",
    [
        (5, 5, 2, 8),
        (8, 3, 2, 8),
        (2, 8, 6, 6),
        (-1, 8, 2, 8),
        (2, 11, 2, 8),
        (2, 8, -1, 8),
        (2, 8, 2, 13),
        (2, 8, 2),
    ],
)
def test_invalid_face_bounds_are_rejected(
    face_bounds: tuple[int, ...],
) -> None:
    base = np.zeros(
        (10, 12),
        dtype=np.float64,
    )

    detail = np.zeros_like(base)
    weight = np.ones_like(base)

    with pytest.raises(
        ValueError,
        match="face_bounds",
    ):
        AtlasReliefFaceDetailComposer.compose(
            base,
            detail,
            weight,
            face_bounds=face_bounds,
        )
