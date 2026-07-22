from __future__ import annotations

from typing import Any

import numpy as np


class AtlasPortraitFlameImageCoordinateNormalizer:
    """
    Converts FLAME canonical coordinates to the
    normalized portrait image coordinate convention.

    FLAME uses a Y-up coordinate system. Portrait image
    coordinates use Y-down. The conversion therefore
    preserves X and Z while reversing Y:

        (x, y, z) -> (x, -y, z)

    It performs no camera estimation, rotation, pose
    fitting, FLAME deformation, projection, rendering,
    relief compression, or STL generation.
    """

    @staticmethod
    def normalize(
        source_points_3d: Any,
    ) -> np.ndarray:
        try:
            points = np.asarray(
                source_points_3d,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "source_points_3d must be numeric."
            ) from exc

        if (
            points.ndim != 2
            or points.shape[1] != 3
            or points.shape[0] < 1
        ):
            raise ValueError(
                "source_points_3d must have shape "
                "(N, 3) and contain at least one point."
            )

        if not np.isfinite(
            points,
        ).all():
            raise ValueError(
                "source_points_3d contains non-finite "
                "values."
            )

        normalized = points.astype(
            np.float64,
            copy=True,
        )

        normalized[
            :,
            1,
        ] *= -1.0

        normalized.setflags(
            write=False,
        )

        return normalized
