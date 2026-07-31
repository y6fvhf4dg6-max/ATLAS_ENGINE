from __future__ import annotations

from typing import Dict, Tuple

import numpy as np
import pytest

from CORE.atlas_relief_mediapipe_landmark_adapter import (
    AtlasReliefMediaPipeLandmarkAdapter,
)


IMAGE_SHAPE: Tuple[int, int] = (400, 320)


def _synthetic_mediapipe_points() -> np.ndarray:
    """
    Build a synthetic 478-point MediaPipe-like landmark array.

    Only the indices used by the adapter are populated with meaningful
    face coordinates. All other indices stay at a neutral in-bounds value.
    """

    points = np.full((478, 2), [160.0, 200.0], dtype=np.float64)

    def set_points(index_to_xy: Dict[int, Tuple[float, float]]) -> None:
        for index, xy in index_to_xy.items():
            points[index] = np.asarray(xy, dtype=np.float64)

    set_points(
        {
            10: (160.0, 56.0),
            338: (204.0, 64.0),
            297: (238.0, 84.0),
            332: (258.0, 120.0),
            284: (266.0, 180.0),
            251: (262.0, 244.0),
            389: (242.0, 304.0),
            356: (204.0, 346.0),
            454: (160.0, 362.0),
            323: (116.0, 346.0),
            361: (78.0, 304.0),
            288: (58.0, 244.0),
            397: (54.0, 180.0),
            365: (62.0, 120.0),
            379: (82.0, 84.0),
            152: (116.0, 64.0),

            33: (92.0, 154.0),
            160: (108.0, 144.0),
            158: (126.0, 146.0),
            133: (138.0, 156.0),
            153: (124.0, 164.0),
            144: (106.0, 164.0),

            362: (182.0, 156.0),
            385: (194.0, 146.0),
            387: (212.0, 144.0),
            263: (228.0, 154.0),
            373: (214.0, 164.0),
            380: (196.0, 164.0),

            168: (160.0, 142.0),
            6: (159.0, 166.0),
            197: (159.0, 190.0),
            195: (160.0, 214.0),

            129: (142.0, 182.0),
            49: (136.0, 208.0),
            98: (144.0, 230.0),
            2: (160.0, 238.0),
            327: (176.0, 230.0),
            279: (184.0, 208.0),
            358: (178.0, 182.0),

            94: (140.0, 226.0),
            141: (150.0, 236.0),
            2: (160.0, 240.0),
            370: (170.0, 236.0),
            326: (180.0, 226.0),

            61: (126.0, 268.0),
            40: (144.0, 260.0),
            0: (160.0, 264.0),
            270: (176.0, 260.0),
            291: (194.0, 268.0),
            269: (176.0, 274.0),
            17: (160.0, 276.0),
            39: (144.0, 274.0),

            78: (128.0, 272.0),
            95: (144.0, 278.0),
            17: (160.0, 282.0),
            324: (176.0, 278.0),
            308: (192.0, 272.0),
            318: (176.0, 290.0),
            200: (160.0, 296.0),
            88: (144.0, 290.0),

            149: (126.0, 308.0),
            176: (142.0, 326.0),
            152: (160.0, 334.0),
            400: (178.0, 326.0),
            378: (194.0, 308.0),
        }
    )

    return points


def test_convert_returns_required_region_groups() -> None:
    grouped = AtlasReliefMediaPipeLandmarkAdapter.convert(
        points_xy=_synthetic_mediapipe_points(),
        image_shape=IMAGE_SHAPE,
    )

    assert set(grouped) == {
        "face_oval",
        "left_eye",
        "right_eye",
        "nose_bridge",
        "nose_body",
        "nose_base",
        "upper_lip",
        "lower_lip",
        "chin",
    }


@pytest.mark.parametrize(
    "group_name",
    [
        "face_oval",
        "left_eye",
        "right_eye",
        "nose_bridge",
        "nose_body",
        "nose_base",
        "upper_lip",
        "lower_lip",
        "chin",
    ],
)
def test_each_group_is_float64_n_by_2(group_name: str) -> None:
    grouped = AtlasReliefMediaPipeLandmarkAdapter.convert(
        points_xy=_synthetic_mediapipe_points(),
        image_shape=IMAGE_SHAPE,
    )

    points = grouped[group_name]

    assert points.ndim == 2
    assert points.shape[1] == 2
    assert points.dtype == np.float64
    assert np.all(np.isfinite(points))


def test_convert_preserves_expected_eye_coordinates() -> None:
    grouped = AtlasReliefMediaPipeLandmarkAdapter.convert(
        points_xy=_synthetic_mediapipe_points(),
        image_shape=IMAGE_SHAPE,
    )

    anatomical_right_eye = grouped["right_eye"]
    anatomical_left_eye = grouped["left_eye"]

    assert np.any(
        np.all(
            np.isclose(
                anatomical_right_eye,
                [92.0, 154.0],
            ),
            axis=1,
        )
    )
    assert np.any(
        np.all(
            np.isclose(
                anatomical_left_eye,
                [228.0, 154.0],
            ),
            axis=1,
        )
    )


def test_convert_preserves_expected_nose_and_mouth_coordinates() -> None:
    grouped = AtlasReliefMediaPipeLandmarkAdapter.convert(
        points_xy=_synthetic_mediapipe_points(),
        image_shape=IMAGE_SHAPE,
    )

    nose_base = grouped["nose_base"]
    upper_lip = grouped["upper_lip"]
    lower_lip = grouped["lower_lip"]

    assert np.any(np.all(np.isclose(nose_base, [160.0, 240.0]), axis=1))
    assert np.any(np.all(np.isclose(upper_lip, [160.0, 264.0]), axis=1))
    assert np.any(np.all(np.isclose(lower_lip, [160.0, 296.0]), axis=1))


def test_convert_rejects_wrong_shape() -> None:
    with pytest.raises(ValueError):
        AtlasReliefMediaPipeLandmarkAdapter.convert(
            points_xy=np.zeros((477, 2), dtype=np.float64),
            image_shape=IMAGE_SHAPE,
        )


def test_convert_rejects_non_finite_points() -> None:
    points = _synthetic_mediapipe_points()
    points[10, 0] = np.nan

    with pytest.raises(ValueError):
        AtlasReliefMediaPipeLandmarkAdapter.convert(
            points_xy=points,
            image_shape=IMAGE_SHAPE,
        )


def test_convert_rejects_points_outside_image() -> None:
    points = _synthetic_mediapipe_points()
    points[33] = np.asarray([-1.0, 154.0], dtype=np.float64)

    with pytest.raises(ValueError):
        AtlasReliefMediaPipeLandmarkAdapter.convert(
            points_xy=points,
            image_shape=IMAGE_SHAPE,
        )


def test_convert_rejects_invalid_image_shape() -> None:
    with pytest.raises((TypeError, ValueError)):
        AtlasReliefMediaPipeLandmarkAdapter.convert(
            points_xy=_synthetic_mediapipe_points(),
            image_shape=(400,),
        )


def test_convert_uses_anatomical_left_right_eye_names() -> None:
    grouped = AtlasReliefMediaPipeLandmarkAdapter.convert(
        points_xy=_synthetic_mediapipe_points(),
        image_shape=IMAGE_SHAPE,
    )

    anatomical_right_eye = grouped["right_eye"]
    anatomical_left_eye = grouped["left_eye"]

    assert np.any(
        np.all(
            np.isclose(
                anatomical_right_eye,
                [92.0, 154.0],
            ),
            axis=1,
        )
    )
    assert np.any(
        np.all(
            np.isclose(
                anatomical_left_eye,
                [228.0, 154.0],
            ),
            axis=1,
        )
    )
