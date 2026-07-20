from __future__ import annotations

import numpy as np

from CORE.atlas_parametric_face_depth_profile import (
    AtlasParametricFaceDepthProfile,
)
from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)


class AtlasParametricFaceDepthDeformer:
    """
    Applies anatomical depth deformation to a
    parametric face surface.

    Anatomical components modify Z only. X and Y
    coordinates are preserved exactly.

    The deformer never mutates the source surface.
    """

    NOSE_TIP_CENTER_X = 0.00
    NOSE_TIP_CENTER_Y = -0.12
    NOSE_TIP_RADIUS_X = 0.30
    NOSE_TIP_RADIUS_Y = 0.32

    @classmethod
    def deform(
        cls,
        surface: AtlasParametricFaceSurface,
        *,
        depth_profile: AtlasParametricFaceDepthProfile,
    ) -> AtlasParametricFaceSurface:
        if not isinstance(
            surface,
            AtlasParametricFaceSurface,
        ):
            raise TypeError(
                "surface must be an "
                "AtlasParametricFaceSurface instance."
            )

        if not isinstance(
            depth_profile,
            AtlasParametricFaceDepthProfile,
        ):
            raise TypeError(
                "depth_profile must be an "
                "AtlasParametricFaceDepthProfile instance."
            )

        source_x = np.asarray(
            surface.x_coordinates,
            dtype=np.float64,
        )
        source_y = np.asarray(
            surface.y_coordinates,
            dtype=np.float64,
        )
        source_z = np.asarray(
            surface.z_coordinates,
            dtype=np.float64,
        )

        nose_tip_delta = cls._build_nose_tip_delta(
            x_coordinates=source_x,
            y_coordinates=source_y,
            projection=depth_profile.nose_tip_projection,
        )

        deformed_z = (
            source_z
            + nose_tip_delta
        )

        return AtlasParametricFaceSurface(
            x_coordinates=source_x.copy(),
            y_coordinates=source_y.copy(),
            z_coordinates=deformed_z,
        )

    @classmethod
    def _build_nose_tip_delta(
        cls,
        *,
        x_coordinates: np.ndarray,
        y_coordinates: np.ndarray,
        projection: float,
    ) -> np.ndarray:
        if projection == 0.0:
            return np.zeros_like(
                x_coordinates,
                dtype=np.float64,
            )

        normalized_radius_squared = (
            (
                (
                    x_coordinates
                    - cls.NOSE_TIP_CENTER_X
                )
                / cls.NOSE_TIP_RADIUS_X
            )
            ** 2
            + (
                (
                    y_coordinates
                    - cls.NOSE_TIP_CENTER_Y
                )
                / cls.NOSE_TIP_RADIUS_Y
            )
            ** 2
        )

        compact_support = np.clip(
            1.0
            - normalized_radius_squared,
            0.0,
            1.0,
        )

        smooth_weight = (
            compact_support
            * compact_support
            * (
                3.0
                - 2.0
                * compact_support
            )
        )

        return (
            float(
                projection,
            )
            * smooth_weight
        ).astype(
            np.float64,
            copy=False,
        )
