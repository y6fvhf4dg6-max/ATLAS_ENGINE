from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_relief_detail_weight_map import (
    AtlasReliefDetailWeightMap,
)


def _build_subject_mask(
    rows: int = 120,
    columns: int = 100,
) -> np.ndarray:
    yy, xx = np.mgrid[0:rows, 0:columns]

    center_x = 0.50 * (columns - 1)
    center_y = 0.54 * (rows - 1)

    radius_x = 0.28 * columns
    radius_y = 0.36 * rows

    ellipse = (
        ((xx - center_x) / radius_x) ** 2
        + ((yy - center_y) / radius_y) ** 2
    ) <= 1.0

    mask = np.zeros(
        (rows, columns),
        dtype=np.float64,
    )
    mask[ellipse] = 1.0

    return mask


def test_returns_expected_shape() -> None:
    subject_mask = _build_subject_mask()

    result = AtlasReliefDetailWeightMap.build_portrait_weight_map(
        subject_mask
    )

    assert result.shape == subject_mask.shape
    assert result.dtype == np.float64


def test_output_is_clamped_to_unit_interval() -> None:
    subject_mask = _build_subject_mask()

    result = AtlasReliefDetailWeightMap.build_portrait_weight_map(
        subject_mask,
        mouth_suppression_strength=0.90,
        lip_restore_strength=0.50,
    )

    assert float(result.min()) >= 0.0
    assert float(result.max()) <= 1.0


def test_output_is_zero_outside_subject() -> None:
    subject_mask = _build_subject_mask()

    result = AtlasReliefDetailWeightMap.build_portrait_weight_map(
        subject_mask
    )

    assert result[0, 0] == pytest.approx(0.0)
    assert result[-1, -1] == pytest.approx(0.0)


def test_face_region_receives_more_weight_than_background() -> None:
    subject_mask = _build_subject_mask()

    result = AtlasReliefDetailWeightMap.build_portrait_weight_map(
        subject_mask
    )

    assert result[40, 50] > result[10, 10]


def test_upper_mouth_region_is_suppressed_relative_to_cheek() -> None:
    subject_mask = _build_subject_mask()

    result = AtlasReliefDetailWeightMap.build_portrait_weight_map(
        subject_mask,
        mouth_suppression_strength=0.75,
        lip_restore_strength=0.20,
    )

    cheek_weight = result[55, 38]
    upper_mouth_weight = result[67, 50]

    assert upper_mouth_weight < cheek_weight


def test_lip_restore_raises_lip_band_above_upper_mouth_band() -> None:
    subject_mask = _build_subject_mask()

    result = AtlasReliefDetailWeightMap.build_portrait_weight_map(
        subject_mask,
        mouth_suppression_strength=0.80,
        lip_restore_strength=0.35,
    )

    upper_mouth_weight = result[66, 50]
    lip_weight = result[73, 50]

    assert lip_weight > upper_mouth_weight


def test_stronger_mouth_suppression_reduces_mouth_weight() -> None:
    subject_mask = _build_subject_mask()

    softer = AtlasReliefDetailWeightMap.build_portrait_weight_map(
        subject_mask,
        mouth_suppression_strength=0.30,
        lip_restore_strength=0.0,
    )

    stronger = AtlasReliefDetailWeightMap.build_portrait_weight_map(
        subject_mask,
        mouth_suppression_strength=0.85,
        lip_restore_strength=0.0,
    )

    assert stronger[68, 50] < softer[68, 50]


def test_stronger_lip_restore_increases_lip_weight() -> None:
    subject_mask = _build_subject_mask()

    weaker = AtlasReliefDetailWeightMap.build_portrait_weight_map(
        subject_mask,
        mouth_suppression_strength=0.80,
        lip_restore_strength=0.10,
    )

    stronger = AtlasReliefDetailWeightMap.build_portrait_weight_map(
        subject_mask,
        mouth_suppression_strength=0.80,
        lip_restore_strength=0.45,
    )

    assert stronger[73, 50] > weaker[73, 50]


def test_invalid_subject_mask_dimension_is_rejected() -> None:
    with pytest.raises(ValueError, match="subject_mask"):
        AtlasReliefDetailWeightMap.build_portrait_weight_map(
            np.zeros(
                (10, 10, 3),
                dtype=np.float64,
            )
        )


def test_empty_subject_mask_is_rejected() -> None:
    with pytest.raises(ValueError, match="subject_mask"):
        AtlasReliefDetailWeightMap.build_portrait_weight_map(
            np.zeros(
                (40, 50),
                dtype=np.float64,
            )
        )


def test_explicit_face_bounds_position_mouth_regions_within_face() -> None:
    subject_mask = np.ones(
        (160, 120),
        dtype=np.float64,
    )

    face_bounds = (
        20,
        120,
        25,
        95,
    )

    result = AtlasReliefDetailWeightMap.build_portrait_weight_map(
        subject_mask,
        face_bounds=face_bounds,
        mouth_suppression_strength=0.80,
        lip_restore_strength=0.35,
    )

    cheek_weight = result[65, 45]
    upper_mouth_weight = result[82, 60]
    lip_weight = result[92, 60]
    lower_torso_weight = result[145, 60]

    assert upper_mouth_weight < cheek_weight
    assert lip_weight > upper_mouth_weight
    assert lower_torso_weight < cheek_weight


def test_face_bounds_change_weight_map_position() -> None:
    subject_mask = np.ones(
        (180, 120),
        dtype=np.float64,
    )

    upper_face = AtlasReliefDetailWeightMap.build_portrait_weight_map(
        subject_mask,
        face_bounds=(10, 100, 25, 95),
    )

    lower_face = AtlasReliefDetailWeightMap.build_portrait_weight_map(
        subject_mask,
        face_bounds=(60, 150, 25, 95),
    )

    assert not np.allclose(
        upper_face,
        lower_face,
    )

    assert upper_face[45, 60] > lower_face[45, 60]
    assert lower_face[105, 60] > upper_face[105, 60]


@pytest.mark.parametrize(
    "face_bounds",
    [
        (20, 20, 10, 80),
        (60, 20, 10, 80),
        (20, 100, 50, 50),
        (20, 100, 90, 30),
        (-1, 100, 10, 80),
        (20, 181, 10, 80),
        (20, 100, -1, 80),
        (20, 100, 10, 121),
        (20, 100, 10),
    ],
)
def test_invalid_face_bounds_are_rejected(
    face_bounds: tuple[int, ...],
) -> None:
    subject_mask = np.ones(
        (180, 120),
        dtype=np.float64,
    )

    with pytest.raises(ValueError, match="face_bounds"):
        AtlasReliefDetailWeightMap.build_portrait_weight_map(
            subject_mask,
            face_bounds=face_bounds,
        )
