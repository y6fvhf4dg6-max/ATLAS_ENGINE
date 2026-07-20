from __future__ import annotations

from CORE.atlas_parametric_face_local_deformer import (
    AtlasParametricFaceLocalDeformer,
)
from CORE.atlas_parametric_face_parameters import (
    AtlasParametricFaceParameters,
)
from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)
from CORE.atlas_parametric_face_surface_deformer import (
    AtlasParametricFaceSurfaceDeformer,
)


class AtlasParametricFaceDeformationPipeline:
    """
    Applies the complete deterministic face deformation chain.

    Processing order:
    - local anatomical deformation
    - global face-width and face-height scaling
    - global XYZ scaling
    - counterclockwise XY rotation
    - XY translation

    The pipeline performs no measurement, parameter
    initialization, optimization, rendering, projection,
    triangulation, or mesh generation.
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

        locally_deformed = (
            AtlasParametricFaceLocalDeformer.deform(
                surface,
                parameters=parameters,
            )
        )

        return AtlasParametricFaceSurfaceDeformer.deform(
            locally_deformed,
            parameters=parameters,
        )
