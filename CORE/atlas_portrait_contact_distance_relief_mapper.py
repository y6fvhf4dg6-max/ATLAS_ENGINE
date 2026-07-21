from __future__ import annotations

import numpy as np

from CORE.atlas_portrait_contact_plane_projection_result import (
    AtlasPortraitContactPlaneProjectionResult,
)


class AtlasPortraitContactDistanceReliefMapper:
    """
    Maps contact-plane distance into a frontal relief
    height candidate.

    Contact-plane distance uses the following direction:

    - zero distance: foremost contact point
    - larger distance: surface point farther behind plane

    Relief height uses the inverse direction:

    - maximum height: foremost contact point
    - zero height: farthest surface point

    The linear mapping is:

        maximum_distance - distance_to_plane

    It performs no percentile clipping, gamma shaping,
    feature-sensitive compression, rendering,
    triangulation, or mesh generation.
    """

    MAPPING_MODE = "maximum_distance_minus_distance"

    @classmethod
    def map(
        cls,
        projection: AtlasPortraitContactPlaneProjectionResult,
    ) -> dict[str, object]:
        if not isinstance(
            projection,
            AtlasPortraitContactPlaneProjectionResult,
        ):
            raise TypeError(
                "projection must be an "
                "AtlasPortraitContactPlaneProjectionResult "
                "instance."
            )

        relief_height = (
            projection.maximum_distance
            - projection.distance_to_plane
        ).astype(
            np.float64,
            copy=True,
        )

        relief_height = np.maximum(
            relief_height,
            0.0,
        ).astype(
            np.float64,
            copy=False,
        )

        minimum_relief_height = float(
            np.min(
                relief_height,
            )
        )

        maximum_relief_height = float(
            np.max(
                relief_height,
            )
        )

        return {
            "type": (
                "portrait_contact_distance_relief_mapping"
            ),
            "mapping_mode": cls.MAPPING_MODE,
            "source_shape": projection.source_shape,
            "minimum_relief_height": (
                minimum_relief_height
            ),
            "maximum_relief_height": (
                maximum_relief_height
            ),
            "relief_height": relief_height,
        }
