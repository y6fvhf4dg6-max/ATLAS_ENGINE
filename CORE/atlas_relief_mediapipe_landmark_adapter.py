from __future__ import annotations

from typing import Dict, Mapping, Sequence, Tuple

import numpy as np


_GROUP_INDICES: Mapping[str, Tuple[int, ...]] = {
    "face_oval": (
        10,
        338,
        297,
        332,
        284,
        251,
        389,
        356,
        454,
        323,
        361,
        288,
        397,
        365,
        379,
        378,
        400,
        377,
        152,
        148,
        176,
        149,
        150,
        136,
        172,
        58,
        132,
        93,
        234,
        127,
        162,
        21,
        54,
        103,
        67,
        109,
    ),
    "right_eye": (
        33,
        160,
        158,
        133,
        153,
        144,
    ),
    "left_eye": (
        362,
        385,
        387,
        263,
        373,
        380,
    ),
    "nose_bridge": (
        168,
        6,
        197,
        195,
    ),
    "nose_body": (
        129,
        49,
        98,
        2,
        327,
        279,
        358,
    ),
    "nose_base": (
        94,
        141,
        2,
        370,
        326,
    ),
    "upper_lip": (
        61,
        40,
        0,
        270,
        291,
        269,
        17,
        39,
    ),
    "lower_lip": (
        78,
        95,
        17,
        324,
        308,
        318,
        200,
        88,
    ),
    "chin": (
        149,
        176,
        152,
        400,
        378,
    ),
}


class AtlasReliefMediaPipeLandmarkAdapter:
    """
    Convert MediaPipe Face Landmarker output into ATLAS semantic groups.

    Input coordinates use absolute image pixels in ``[x, y]`` order.
    The adapter performs no face reconstruction and no 3D inference.
    """

    @classmethod
    def convert(
        cls,
        *,
        points_xy: np.ndarray,
        image_shape: Sequence[int],
    ) -> Dict[str, np.ndarray]:
        height, width = _validate_image_shape(image_shape)
        points = _validate_points(
            points_xy=points_xy,
            height=height,
            width=width,
        )

        return {
            group_name: np.ascontiguousarray(
                points[np.asarray(indices, dtype=np.int64)],
                dtype=np.float64,
            )
            for group_name, indices in _GROUP_INDICES.items()
        }


def _validate_image_shape(
    image_shape: Sequence[int],
) -> Tuple[int, int]:
    if isinstance(image_shape, (str, bytes)):
        raise TypeError(
            "image_shape must contain exactly two integers"
        )

    try:
        values = tuple(image_shape)
    except TypeError as exc:
        raise TypeError(
            "image_shape must contain exactly two integers"
        ) from exc

    if len(values) != 2:
        raise ValueError(
            "image_shape must contain exactly two values"
        )

    height, width = values

    if (
        isinstance(height, bool)
        or isinstance(width, bool)
        or not isinstance(height, (int, np.integer))
        or not isinstance(width, (int, np.integer))
    ):
        raise TypeError(
            "image_shape values must be integers"
        )

    height = int(height)
    width = int(width)

    if height <= 0 or width <= 0:
        raise ValueError(
            "image_shape values must be positive"
        )

    return height, width


def _validate_points(
    *,
    points_xy: np.ndarray,
    height: int,
    width: int,
) -> np.ndarray:
    points = np.asarray(
        points_xy,
        dtype=np.float64,
    )

    if points.shape != (478, 2):
        raise ValueError(
            "points_xy must have shape (478, 2)"
        )

    if not np.all(np.isfinite(points)):
        raise ValueError(
            "points_xy contains non-finite coordinates"
        )

    x = points[:, 0]
    y = points[:, 1]

    if (
        np.any(x < 0.0)
        or np.any(x > float(width - 1))
        or np.any(y < 0.0)
        or np.any(y > float(height - 1))
    ):
        raise ValueError(
            "points_xy contains coordinates outside the image"
        )

    return np.ascontiguousarray(
        points,
        dtype=np.float64,
    )
