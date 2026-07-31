from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_relief_face_anchor_enhancer import (
    AtlasReliefFaceAnchorEnhancer,
)


def test_shape_is_preserved() -> None:
    anchor = np.full(
        (120, 100),
        0.50,
        dtype=np.float64,
    )
    mask = np.ones_like(anchor)

    result = AtlasReliefFaceAnchorEnhancer.enhance(
        anchor,
        mask,
    )

    assert result.shape == anchor.shape


def test_output_is_float64() -> None:
    anchor = np.full(
        (80, 60),
        0.50,
        dtype=np.float32,
    )
    mask = np.ones(
        (80, 60),
        dtype=np.float64,
    )

    result = AtlasReliefFaceAnchorEnhancer.enhance(
        anchor,
        mask,
    )

    assert result.dtype == np.float64


def test_zero_strength_preserves_anchor_exactly() -> None:
    anchor = np.linspace(
        0.10,
        0.90,
        100 * 80,
        dtype=np.float64,
    ).reshape(100, 80)

    mask = np.ones_like(anchor)

    result = AtlasReliefFaceAnchorEnhancer.enhance(
        anchor,
        mask,
        face_strength=0.0,
    )

    assert np.allclose(
        result,
        anchor,
        atol=1e-12,
    )


def test_face_bounds_prevent_changes_outside_face() -> None:
    rows = 160
    columns = 120

    y, x = np.mgrid[
        -1.0:1.0:complex(rows),
        -1.0:1.0:complex(columns),
    ]

    anchor = (
        0.40
        + 0.10 * np.exp(
            -6.0 * (x * x + y * y)
        )
    )

    mask = np.ones_like(anchor)

    face_bounds = (
        20,
        120,
        25,
        95,
    )

    result = AtlasReliefFaceAnchorEnhancer.enhance(
        anchor,
        mask,
        face_bounds=face_bounds,
        face_strength=0.25,
    )

    top, bottom, left, right = face_bounds

    outside = np.ones_like(
        anchor,
        dtype=bool,
    )
    outside[
        top:bottom + 1,
        left:right + 1,
    ] = False

    assert np.allclose(
        result[outside],
        anchor[outside],
        atol=1e-12,
    )


def test_midface_contrast_is_increased() -> None:
    rows = 120
    columns = 100

    y, x = np.mgrid[
        -1.0:1.0:complex(rows),
        -1.0:1.0:complex(columns),
    ]

    anchor = (
        0.45
        + 0.04 * np.exp(
            -12.0 * (
                x * x
                + (y + 0.15) ** 2
            )
        )
    )

    mask = np.ones_like(anchor)

    result = AtlasReliefFaceAnchorEnhancer.enhance(
        anchor,
        mask,
        face_bounds=(10, 105, 15, 85),
        face_strength=0.30,
    )

    original_range = float(
        np.ptp(
            anchor[30:85, 25:75]
        )
    )
    enhanced_range = float(
        np.ptp(
            result[30:85, 25:75]
        )
    )

    assert enhanced_range > original_range


def test_mouth_region_changes_less_than_midface() -> None:
    rows = 160
    columns = 120

    y, x = np.mgrid[
        -1.0:1.0:complex(rows),
        -1.0:1.0:complex(columns),
    ]

    anchor = (
        0.45
        + 0.05 * np.exp(
            -5.0 * (x * x + y * y)
        )
        + 0.02 * np.sin(
            8.0 * x
        )
    )

    mask = np.ones_like(anchor)

    result = AtlasReliefFaceAnchorEnhancer.enhance(
        anchor,
        mask,
        face_bounds=(20, 120, 25, 95),
        face_strength=0.30,
        mouth_suppression_strength=0.80,
    )

    midface_delta = float(
        np.mean(
            np.abs(
                result[45:70, 45:75]
                - anchor[45:70, 45:75]
            )
        )
    )

    mouth_delta = float(
        np.mean(
            np.abs(
                result[80:98, 45:75]
                - anchor[80:98, 45:75]
            )
        )
    )

    assert mouth_delta < midface_delta


def test_subject_mask_prevents_changes_outside_subject() -> None:
    anchor = np.linspace(
        0.20,
        0.80,
        90 * 70,
        dtype=np.float64,
    ).reshape(90, 70)

    mask = np.zeros_like(anchor)
    mask[10:80, 12:58] = 1.0

    result = AtlasReliefFaceAnchorEnhancer.enhance(
        anchor,
        mask,
        face_bounds=(12, 75, 15, 55),
        face_strength=0.25,
    )

    assert np.allclose(
        result[mask <= 0.0],
        anchor[mask <= 0.0],
        atol=1e-12,
    )


def test_output_is_clamped_to_unit_interval() -> None:
    anchor = np.linspace(
        0.0,
        1.0,
        80 * 60,
        dtype=np.float64,
    ).reshape(80, 60)

    mask = np.ones_like(anchor)

    result = AtlasReliefFaceAnchorEnhancer.enhance(
        anchor,
        mask,
        face_bounds=(5, 74, 5, 54),
        face_strength=1.0,
    )

    assert float(result.min()) >= 0.0
    assert float(result.max()) <= 1.0


def test_invalid_anchor_dimension_is_rejected() -> None:
    anchor = np.zeros(
        (80, 60, 3),
        dtype=np.float64,
    )
    mask = np.ones(
        (80, 60),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="anchor_height",
    ):
        AtlasReliefFaceAnchorEnhancer.enhance(
            anchor,
            mask,
        )


def test_subject_mask_shape_must_match_anchor() -> None:
    anchor = np.zeros(
        (80, 60),
        dtype=np.float64,
    )
    mask = np.ones(
        (81, 60),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="subject_mask",
    ):
        AtlasReliefFaceAnchorEnhancer.enhance(
            anchor,
            mask,
        )


@pytest.mark.parametrize(
    "face_bounds",
    [
        (20, 20, 10, 80),
        (60, 20, 10, 80),
        (20, 100, 50, 50),
        (-1, 100, 10, 80),
        (20, 161, 10, 80),
        (20, 100, -1, 80),
        (20, 100, 10, 121),
        (20, 100, 10),
    ],
)
def test_invalid_face_bounds_are_rejected(
    face_bounds: tuple[int, ...],
) -> None:
    anchor = np.full(
        (160, 120),
        0.50,
        dtype=np.float64,
    )
    mask = np.ones_like(anchor)

    with pytest.raises(
        ValueError,
        match="face_bounds",
    ):
        AtlasReliefFaceAnchorEnhancer.enhance(
            anchor,
            mask,
            face_bounds=face_bounds,
        )
