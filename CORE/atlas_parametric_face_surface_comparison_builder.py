from __future__ import annotations

from CORE.atlas_parametric_face_deformation_pipeline import (
    AtlasParametricFaceDeformationPipeline,
)
from CORE.atlas_parametric_face_parameters import (
    AtlasParametricFaceParameters,
)
from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)
from CORE.atlas_parametric_face_surface_comparison_result import (
    AtlasParametricFaceSurfaceComparisonResult,
)


class AtlasParametricFaceSurfaceComparisonBuilder:
    """
    Builds deterministic neutral/adapted face-surface
    comparison results.

    Processing:
    - preserve the supplied neutral surface
    - adapt it through the complete deformation pipeline
    - return an immutable surface comparison result

    The builder performs no measurement, parameter
    initialization, optimization, rendering, projection,
    triangulation, or mesh generation.
    """

    @staticmethod
    def build(
        neutral_surface: AtlasParametricFaceSurface,
        *,
        parameters: AtlasParametricFaceParameters,
    ) -> AtlasParametricFaceSurfaceComparisonResult:
        if not isinstance(
            neutral_surface,
            AtlasParametricFaceSurface,
        ):
            raise TypeError(
                "neutral_surface must be an "
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

        adapted_surface = (
            AtlasParametricFaceDeformationPipeline.deform(
                neutral_surface,
                parameters=parameters,
            )
        )

        return AtlasParametricFaceSurfaceComparisonResult(
            neutral_surface=neutral_surface,
            adapted_surface=adapted_surface,
            parameters=parameters,
        )
