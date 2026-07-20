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

    This initial contract preserves all coordinates.
    Anatomical Z components are added incrementally
    in later packages.

    The deformer never mutates the source surface.
    """

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

        return AtlasParametricFaceSurface(
            x_coordinates=np.asarray(
                surface.x_coordinates,
                dtype=np.float64,
            ).copy(),
            y_coordinates=np.asarray(
                surface.y_coordinates,
                dtype=np.float64,
            ).copy(),
            z_coordinates=np.asarray(
                surface.z_coordinates,
                dtype=np.float64,
            ).copy(),
        )
