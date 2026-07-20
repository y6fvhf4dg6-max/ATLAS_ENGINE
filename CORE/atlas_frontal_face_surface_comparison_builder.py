from __future__ import annotations

from CORE.atlas_frontal_face_measurements import (
    AtlasFrontalFaceMeasurements,
)
from CORE.atlas_frontal_face_parameter_initializer import (
    AtlasFrontalFaceParameterInitializer,
)
from CORE.atlas_frontal_face_reference_profile import (
    AtlasFrontalFaceReferenceProfile,
)
from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)
from CORE.atlas_parametric_face_surface_comparison_builder import (
    AtlasParametricFaceSurfaceComparisonBuilder,
)
from CORE.atlas_parametric_face_surface_comparison_result import (
    AtlasParametricFaceSurfaceComparisonResult,
)


class AtlasFrontalFaceSurfaceComparisonBuilder:
    """
    Builds a frontal face surface comparison from
    normalized measurements.

    Processing:
    - validate the supplied neutral surface
    - validate frontal measurements
    - validate the reference profile
    - initialize parametric face parameters
    - build the neutral/adapted surface comparison

    The builder performs no landmark detection,
    measurement extraction, optimization, rendering,
    projection, triangulation, or mesh generation.
    """

    @staticmethod
    def build(
        neutral_surface: AtlasParametricFaceSurface,
        *,
        measurements: AtlasFrontalFaceMeasurements,
        reference_profile: AtlasFrontalFaceReferenceProfile,
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
            measurements,
            AtlasFrontalFaceMeasurements,
        ):
            raise TypeError(
                "measurements must be an "
                "AtlasFrontalFaceMeasurements instance."
            )

        if not isinstance(
            reference_profile,
            AtlasFrontalFaceReferenceProfile,
        ):
            raise TypeError(
                "reference_profile must be an "
                "AtlasFrontalFaceReferenceProfile instance."
            )

        parameters = AtlasFrontalFaceParameterInitializer.initialize(
            measurements,
            reference_profile=reference_profile,
        )

        return AtlasParametricFaceSurfaceComparisonBuilder.build(
            neutral_surface,
            parameters=parameters,
        )
