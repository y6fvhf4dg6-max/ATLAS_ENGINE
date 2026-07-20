from __future__ import annotations

from CORE.atlas_frontal_face_measurements import (
    AtlasFrontalFaceMeasurements,
)
from CORE.atlas_frontal_face_parameter_comparison_result import (
    AtlasFrontalFaceParameterComparisonResult,
)
from CORE.atlas_frontal_face_parameter_initializer import (
    AtlasFrontalFaceParameterInitializer,
)
from CORE.atlas_frontal_face_reference_profile import (
    AtlasFrontalFaceReferenceProfile,
)


class AtlasFrontalFaceParameterComparator:
    """
    Builds deterministic frontal face parameter
    comparison results.

    The comparator initializes parametric face values
    from source measurements and reports each measured
    proportion's deviation from the neutral value 1.0.
    It performs no optimization, deformation, rendering,
    projection, or mesh generation.
    """

    RATIO_PARAMETER_NAMES = (
        "face_width",
        "eye_spacing",
        "nose_width",
        "nose_length",
        "mouth_width",
        "jaw_width",
        "forehead_height",
    )

    @classmethod
    def compare(
        cls,
        measurements: AtlasFrontalFaceMeasurements,
        *,
        reference_profile: AtlasFrontalFaceReferenceProfile,
    ) -> AtlasFrontalFaceParameterComparisonResult:
        if not isinstance(
            measurements,
            AtlasFrontalFaceMeasurements,
        ):
            raise TypeError(
                "measurements must be an " "AtlasFrontalFaceMeasurements instance."
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

        ratio_deviations = {
            name: cls._normalize_deviation(
                getattr(
                    parameters,
                    name,
                )
                - 1.0
            )
            for name in cls.RATIO_PARAMETER_NAMES
        }

        return AtlasFrontalFaceParameterComparisonResult(
            reference_profile_name=reference_profile.name,
            measurements=measurements,
            parameters=parameters,
            ratio_deviations=ratio_deviations,
        )

    @staticmethod
    def _normalize_deviation(
        value: float,
    ) -> float:
        if abs(value) < 1e-12:
            return 0.0

        return value
