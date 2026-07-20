from __future__ import annotations

import math

import numpy as np

from CORE.atlas_parametric_face_parameters import (
    AtlasParametricFaceParameters,
)
from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)


class AtlasParametricFaceSurfaceDeformer:
    """
    Applies global frontal face transformations.

    Processing order:
    - local face-width and face-height scaling
    - global XYZ scaling
    - counterclockwise XY rotation
    - XY translation

    Local anatomical deformation is intentionally
    excluded from this stage.
    """

    @staticmethod
    def deform(
        surface: AtlasParametricFaceSurface,
        *,
        parameters: AtlasParametricFaceParameters,
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
            parameters,
            AtlasParametricFaceParameters,
        ):
            raise TypeError(
                "parameters must be an "
                "AtlasParametricFaceParameters instance."
            )

        local_x = (
            surface.x_coordinates
            * parameters.face_width
        )
        local_y = (
            surface.y_coordinates
            * parameters.face_height
        )
        local_z = surface.z_coordinates.copy()

        scaled_x = local_x * parameters.scale
        scaled_y = local_y * parameters.scale
        scaled_z = local_z * parameters.scale

        angle_radians = math.radians(
            parameters.rotation_degrees,
        )
        cosine = math.cos(
            angle_radians,
        )
        sine = math.sin(
            angle_radians,
        )

        rotated_x = (
            scaled_x * cosine
            - scaled_y * sine
        )
        rotated_y = (
            scaled_x * sine
            + scaled_y * cosine
        )

        translated_x = (
            rotated_x
            + parameters.translation_x
        )
        translated_y = (
            rotated_y
            + parameters.translation_y
        )

        return AtlasParametricFaceSurface(
            x_coordinates=np.asarray(
                translated_x,
                dtype=np.float64,
            ),
            y_coordinates=np.asarray(
                translated_y,
                dtype=np.float64,
            ),
            z_coordinates=np.asarray(
                scaled_z,
                dtype=np.float64,
            ),
        )
