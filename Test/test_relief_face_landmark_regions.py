from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pytest

from CORE.atlas_relief_face_landmark_regions import (
    AtlasReliefFaceLandmarkRegions,
)
from CORE.atlas_relief_mediapipe_landmark_adapter import (
    AtlasReliefMediaPipeLandmarkAdapter,
)


IMAGE_SHAPE: Tuple[int, int] = (400, 320)


def _valid_landmarks() -> Dict[str, np.ndarray]:
    """
    Return a synthetic frontal-face landmark set in pixel coordinates.

    Every point uses the coordinate order:
        [x, y]
    """

    return {
        "face_oval": np.asarray(
            [
                [82.0, 84.0],
                [62.0, 120.0],
                [54.0, 180.0],
                [58.0, 244.0],
                [78.0, 304.0],
                [116.0, 346.0],
                [160.0, 362.0],
                [204.0, 346.0],
                [242.0, 304.0],
                [262.0, 244.0],
                [266.0, 180.0],
                [258.0, 120.0],
                [238.0, 84.0],
                [204.0, 64.0],
                [160.0, 56.0],
                [116.0, 64.0],
            ],
            dtype=np.float64,
        ),
        "left_eye": np.asarray(
            [
                [92.0, 154.0],
                [108.0, 144.0],
                [126.0, 146.0],
                [138.0, 156.0],
                [124.0, 164.0],
                [106.0, 164.0],
            ],
            dtype=np.float64,
        ),
        "right_eye": np.asarray(
            [
                [182.0, 156.0],
                [194.0, 146.0],
                [212.0, 144.0],
                [228.0, 154.0],
                [214.0, 164.0],
                [196.0, 164.0],
            ],
            dtype=np.float64,
        ),
        "nose_bridge": np.asarray(
            [
                [160.0, 142.0],
                [159.0, 166.0],
                [159.0, 190.0],
                [160.0, 214.0],
            ],
            dtype=np.float64,
        ),
        "nose_body": np.asarray(
            [
                [142.0, 182.0],
                [136.0, 208.0],
                [144.0, 230.0],
                [160.0, 238.0],
                [176.0, 230.0],
                [184.0, 208.0],
                [178.0, 182.0],
            ],
            dtype=np.float64,
        ),
        "nose_base": np.asarray(
            [
                [140.0, 226.0],
                [150.0, 236.0],
                [160.0, 240.0],
                [170.0, 236.0],
                [180.0, 226.0],
            ],
            dtype=np.float64,
        ),
        "upper_lip": np.asarray(
            [
                [126.0, 268.0],
                [144.0, 260.0],
                [160.0, 264.0],
                [176.0, 260.0],
                [194.0, 268.0],
                [176.0, 274.0],
                [160.0, 276.0],
                [144.0, 274.0],
            ],
            dtype=np.float64,
        ),
        "lower_lip": np.asarray(
            [
                [128.0, 272.0],
                [144.0, 278.0],
                [160.0, 282.0],
                [176.0, 278.0],
                [192.0, 272.0],
                [176.0, 290.0],
                [160.0, 296.0],
                [144.0, 290.0],
            ],
            dtype=np.float64,
        ),
        "chin": np.asarray(
            [
                [126.0, 308.0],
                [142.0, 326.0],
                [160.0, 334.0],
                [178.0, 326.0],
                [194.0, 308.0],
            ],
            dtype=np.float64,
        ),
    }


def _build_regions() -> AtlasReliefFaceLandmarkRegions:
    return AtlasReliefFaceLandmarkRegions.build(
        image_shape=IMAGE_SHAPE,
        landmarks=_valid_landmarks(),
    )


def _mask_centroid(mask: np.ndarray) -> Tuple[float, float]:
    yy, xx = np.nonzero(mask > 0.25)

    assert xx.size > 0
    assert yy.size > 0

    weights = mask[yy, xx]
    total = float(np.sum(weights))

    return (
        float(np.sum(xx * weights) / total),
        float(np.sum(yy * weights) / total),
    )


def test_build_returns_expected_region_names() -> None:
    regions = _build_regions()

    assert set(regions.masks) == {
        "eye_glasses",
        "nose_bridge",
        "nose_body",
        "nose_base",
        "philtrum",
        "upper_lip",
        "lower_lip",
        "left_cheek",
        "right_cheek",
        "chin",
        "face_interior",
        "face_boundary_falloff",
    }


@pytest.mark.parametrize(
    "region_name",
    [
        "eye_glasses",
        "nose_bridge",
        "nose_body",
        "nose_base",
        "philtrum",
        "upper_lip",
        "lower_lip",
        "left_cheek",
        "right_cheek",
        "chin",
        "face_interior",
        "face_boundary_falloff",
    ],
)
def test_each_region_is_float64_and_matches_image_shape(
    region_name: str,
) -> None:
    regions = _build_regions()
    mask = regions.masks[region_name]

    assert mask.shape == IMAGE_SHAPE
    assert mask.dtype == np.float64
    assert np.all(np.isfinite(mask))
    assert float(np.min(mask)) >= 0.0
    assert float(np.max(mask)) <= 1.0


def test_landmark_regions_are_zero_outside_face_support() -> None:
    regions = _build_regions()

    outside_samples = [
        (0, 0),
        (10, 160),
        (399, 0),
        (399, 319),
    ]

    for mask in regions.masks.values():
        for y, x in outside_samples:
            assert mask[y, x] == pytest.approx(0.0)


def test_eye_glasses_region_tracks_real_eye_coordinates() -> None:
    regions = _build_regions()
    mask = regions.masks["eye_glasses"]

    assert mask[154, 114] > 0.5
    assert mask[154, 206] > 0.5
    assert mask[278, 160] < 0.1


def test_nose_base_region_tracks_real_nose_base() -> None:
    regions = _build_regions()
    mask = regions.masks["nose_base"]

    assert mask[234, 160] > 0.5
    assert mask[110, 160] < 0.1
    assert mask[326, 160] < 0.1


def test_philtrum_lies_between_nose_base_and_upper_lip() -> None:
    regions = _build_regions()

    philtrum_x, philtrum_y = _mask_centroid(
        regions.masks["philtrum"]
    )
    _, nose_base_y = _mask_centroid(
        regions.masks["nose_base"]
    )
    _, upper_lip_y = _mask_centroid(
        regions.masks["upper_lip"]
    )

    assert abs(philtrum_x - 160.0) < 12.0
    assert nose_base_y < philtrum_y < upper_lip_y


def test_cheek_regions_stay_separate_from_eyes_and_mouth() -> None:
    regions = _build_regions()

    left_cheek = regions.masks["left_cheek"]
    right_cheek = regions.masks["right_cheek"]

    assert left_cheek[214, 112] > 0.25
    assert right_cheek[214, 208] > 0.25

    assert left_cheek[154, 112] < 0.25
    assert right_cheek[154, 208] < 0.25

    assert left_cheek[278, 160] < 0.1
    assert right_cheek[278, 160] < 0.1


def test_chin_region_is_below_lower_lip() -> None:
    regions = _build_regions()

    _, lower_lip_y = _mask_centroid(
        regions.masks["lower_lip"]
    )
    _, chin_y = _mask_centroid(
        regions.masks["chin"]
    )

    assert chin_y > lower_lip_y
    assert regions.masks["chin"][326, 160] > 0.25


def test_face_boundary_falloff_is_inside_face_support() -> None:
    regions = _build_regions()

    face_interior = regions.masks["face_interior"]
    boundary = regions.masks["face_boundary_falloff"]

    assert np.all(boundary <= face_interior + 1.0e-12)
    assert float(np.max(boundary)) > 0.0

    center_value = boundary[220, 160]
    edge_value = boundary[180, 58]

    assert edge_value > center_value


def test_build_rejects_non_mapping_landmarks() -> None:
    with pytest.raises(TypeError):
        AtlasReliefFaceLandmarkRegions.build(
            image_shape=IMAGE_SHAPE,
            landmarks=np.zeros((10, 2), dtype=np.float64),
        )


def test_build_rejects_missing_required_landmark_group() -> None:
    landmarks = _valid_landmarks()
    del landmarks["nose_base"]

    with pytest.raises(ValueError, match="nose_base"):
        AtlasReliefFaceLandmarkRegions.build(
            image_shape=IMAGE_SHAPE,
            landmarks=landmarks,
        )


def test_build_rejects_non_finite_landmark_coordinate() -> None:
    landmarks = _valid_landmarks()
    landmarks["nose_bridge"][1, 0] = np.nan

    with pytest.raises(ValueError):
        AtlasReliefFaceLandmarkRegions.build(
            image_shape=IMAGE_SHAPE,
            landmarks=landmarks,
        )


def test_build_rejects_landmarks_outside_image_bounds() -> None:
    landmarks = _valid_landmarks()
    landmarks["left_eye"][0] = np.asarray(
        [-1.0, 154.0],
        dtype=np.float64,
    )

    with pytest.raises(ValueError):
        AtlasReliefFaceLandmarkRegions.build(
            image_shape=IMAGE_SHAPE,
            landmarks=landmarks,
        )


@pytest.mark.parametrize(
    "invalid_shape",
    [
        (0, 320),
        (400, 0),
        (-1, 320),
        (400,),
        (400, 320, 3),
    ],
)
def test_build_rejects_invalid_image_shape(
    invalid_shape: Tuple[int, ...],
) -> None:
    with pytest.raises((TypeError, ValueError)):
        AtlasReliefFaceLandmarkRegions.build(
            image_shape=invalid_shape,
            landmarks=_valid_landmarks(),
        )


def test_cheek_masks_have_no_hard_midline_discontinuity() -> None:
    regions = _build_regions()

    left_cheek = regions.masks["left_cheek"]
    right_cheek = regions.masks["right_cheek"]

    row = 214
    center_x = 160

    left_jump = abs(
        float(left_cheek[row, center_x])
        - float(left_cheek[row, center_x - 1])
    )
    right_jump = abs(
        float(right_cheek[row, center_x])
        - float(right_cheek[row, center_x + 1])
    )

    assert left_jump < 0.10
    assert right_jump < 0.10


def test_cheek_centroids_stay_above_mouth_center() -> None:
    regions = _build_regions()

    _, left_cheek_y = _mask_centroid(
        regions.masks["left_cheek"]
    )
    _, right_cheek_y = _mask_centroid(
        regions.masks["right_cheek"]
    )
    _, upper_lip_y = _mask_centroid(
        regions.masks["upper_lip"]
    )

    assert left_cheek_y < upper_lip_y
    assert right_cheek_y < upper_lip_y


def test_eye_glasses_region_covers_outer_eye_corners() -> None:
    regions = _build_regions()
    mask = regions.masks["eye_glasses"]

    assert mask[154, 92] > 0.25
    assert mask[154, 228] > 0.25


def test_eye_glasses_region_does_not_spread_to_mouth_or_high_forehead() -> None:
    regions = _build_regions()
    mask = regions.masks["eye_glasses"]

    assert mask[278, 160] < 0.10
    assert mask[104, 160] < 0.10


def test_eye_glasses_region_extends_beyond_eye_landmark_centers() -> None:
    regions = _build_regions()
    mask = regions.masks["eye_glasses"]

    # Controlled frame margin beyond the synthetic outer eye corners.
    assert mask[154, 84] > 0.10
    assert mask[154, 236] > 0.10

    # Upper frame must be represented without reaching the high forehead.
    assert mask[138, 114] > 0.10
    assert mask[138, 206] > 0.10
    assert mask[104, 160] < 0.10


def test_cheek_regions_keep_meaningful_peak_strength() -> None:
    regions = _build_regions()

    left_cheek = regions.masks["left_cheek"]
    right_cheek = regions.masks["right_cheek"]

    assert float(np.max(left_cheek)) > 0.35
    assert float(np.max(right_cheek)) > 0.35

    assert np.count_nonzero(left_cheek > 0.20) > 150
    assert np.count_nonzero(right_cheek > 0.20) > 150


def test_cheek_regions_cover_under_eye_nose_side_area() -> None:
    regions = _build_regions()

    left_cheek = regions.masks["left_cheek"]
    right_cheek = regions.masks["right_cheek"]

    assert left_cheek[205, 116] > 0.20
    assert right_cheek[205, 204] > 0.20

    # Mouth and chin remain excluded.
    assert left_cheek[278, 160] < 0.10
    assert right_cheek[278, 160] < 0.10
    assert left_cheek[326, 160] < 0.05
    assert right_cheek[326, 160] < 0.05


def _compact_landmarks() -> Dict[str, np.ndarray]:
    """
    Compress the synthetic face around its center.

    This approximates the real 320x400 portrait, where the detected face
    occupies a substantially smaller portion of the full image.
    """

    landmarks = _valid_landmarks()
    center = np.asarray([160.0, 205.0], dtype=np.float64)

    transformed: Dict[str, np.ndarray] = {}

    for name, points in landmarks.items():
        relative = points - center
        relative[:, 0] *= 0.62
        relative[:, 1] *= 0.58

        transformed[name] = np.ascontiguousarray(
            relative + center,
            dtype=np.float64,
        )

    return transformed


def test_compact_face_keeps_meaningful_cheek_strength() -> None:
    regions = AtlasReliefFaceLandmarkRegions.build(
        image_shape=IMAGE_SHAPE,
        landmarks=_compact_landmarks(),
    )

    left_cheek = regions.masks["left_cheek"]
    right_cheek = regions.masks["right_cheek"]

    assert float(np.max(left_cheek)) > 0.35
    assert float(np.max(right_cheek)) > 0.35

    assert np.count_nonzero(left_cheek > 0.20) > 100
    assert np.count_nonzero(right_cheek > 0.20) > 100


def test_compact_face_cheeks_survive_glasses_tail_suppression() -> None:
    landmarks = _compact_landmarks()

    regions = AtlasReliefFaceLandmarkRegions.build(
        image_shape=IMAGE_SHAPE,
        landmarks=landmarks,
    )

    left_eye_center = np.mean(
        landmarks["left_eye"],
        axis=0,
    )
    right_eye_center = np.mean(
        landmarks["right_eye"],
        axis=0,
    )
    nose_base_center = np.mean(
        landmarks["nose_base"],
        axis=0,
    )
    upper_lip_center = np.mean(
        landmarks["upper_lip"],
        axis=0,
    )

    cheek_y = int(
        round(
            0.68 * float(nose_base_center[1])
            + 0.32 * float(upper_lip_center[1])
        )
    )

    left_x = int(round(float(left_eye_center[0])))
    right_x = int(round(float(right_eye_center[0])))

    assert regions.masks["left_cheek"][cheek_y, left_x] > 0.15
    assert regions.masks["right_cheek"][cheek_y, right_x] > 0.15


def test_compact_face_cheeks_still_exclude_mouth_and_chin() -> None:
    regions = AtlasReliefFaceLandmarkRegions.build(
        image_shape=IMAGE_SHAPE,
        landmarks=_compact_landmarks(),
    )

    for name in ("left_cheek", "right_cheek"):
        mask = regions.masks[name]

        assert mask[250, 160] < 0.10
        assert mask[285, 160] < 0.05


_REAL_PORTRAIT_LANDMARK_PATH = Path(
    "Data/RELIEF/real_portrait_01/landmarks/"
    "mediapipe_face_landmarks_2d.npz"
)


def _real_portrait_regions() -> tuple[
    AtlasReliefFaceLandmarkRegions,
    Dict[str, np.ndarray],
]:
    if not _REAL_PORTRAIT_LANDMARK_PATH.exists():
        pytest.skip(
            "real portrait MediaPipe landmark fixture is unavailable"
        )

    with np.load(_REAL_PORTRAIT_LANDMARK_PATH) as data:
        points_xy = np.asarray(
            data["points_xy"],
            dtype=np.float64,
        )
        image_shape = tuple(
            int(value)
            for value in data["image_shape"]
        )

    grouped = AtlasReliefMediaPipeLandmarkAdapter.convert(
        points_xy=points_xy,
        image_shape=image_shape,
    )

    regions = AtlasReliefFaceLandmarkRegions.build(
        image_shape=image_shape,
        landmarks=grouped,
    )

    return regions, grouped


def test_real_portrait_keeps_meaningful_cheek_peak_strength() -> None:
    regions, _ = _real_portrait_regions()

    left_cheek = regions.masks["left_cheek"]
    right_cheek = regions.masks["right_cheek"]

    assert float(np.max(left_cheek)) > 0.35
    assert float(np.max(right_cheek)) > 0.35

    assert np.count_nonzero(left_cheek > 0.20) > 100
    assert np.count_nonzero(right_cheek > 0.20) > 100


def test_real_portrait_cheeks_survive_glasses_tail_suppression() -> None:
    regions, grouped = _real_portrait_regions()

    image_left_eye = min(
        grouped["left_eye"],
        grouped["right_eye"],
        key=lambda points: float(np.mean(points[:, 0])),
    )
    image_right_eye = max(
        grouped["left_eye"],
        grouped["right_eye"],
        key=lambda points: float(np.mean(points[:, 0])),
    )

    nose_base_center = np.mean(
        grouped["nose_base"],
        axis=0,
    )
    upper_lip_center = np.mean(
        grouped["upper_lip"],
        axis=0,
    )

    cheek_y = int(
        round(
            0.70 * float(nose_base_center[1])
            + 0.30 * float(upper_lip_center[1])
        )
    )

    image_left_x = int(
        round(float(np.mean(image_left_eye[:, 0])))
    )
    image_right_x = int(
        round(float(np.mean(image_right_eye[:, 0])))
    )

    # Region names currently follow image-side placement.
    assert (
        regions.masks["right_cheek"][
            cheek_y,
            image_left_x,
        ]
        > 0.15
    )
    assert (
        regions.masks["left_cheek"][
            cheek_y,
            image_right_x,
        ]
        > 0.15
    )


def test_real_portrait_cheeks_remain_outside_mouth_core() -> None:
    regions, grouped = _real_portrait_regions()

    upper_lip_center = np.mean(
        grouped["upper_lip"],
        axis=0,
    )
    lower_lip_center = np.mean(
        grouped["lower_lip"],
        axis=0,
    )

    mouth_x = int(
        round(
            0.5
            * (
                float(upper_lip_center[0])
                + float(lower_lip_center[0])
            )
        )
    )
    mouth_y = int(
        round(
            0.5
            * (
                float(upper_lip_center[1])
                + float(lower_lip_center[1])
            )
        )
    )

    for name in ("left_cheek", "right_cheek"):
        assert regions.masks[name][mouth_y, mouth_x] < 0.10
