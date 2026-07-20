from __future__ import annotations

from CORE.atlas_frontal_face_measurements import (
    AtlasFrontalFaceMeasurements,
)
from CORE.atlas_frontal_face_reference_profile import (
    AtlasFrontalFaceReferenceProfile,
)
from CORE.atlas_parametric_face_parameters import (
    AtlasParametricFaceParameters,
)


class AtlasFrontalFaceParameterInitializer:
    """
    Converts deterministic frontal measurements into
    initial normalized parametric face values.

    Facial proportions are interpreted relative to an
    immutable frontal reference profile. The initializer
    performs no optimization, landmark fitting, mesh
    deformation, depth rendering, or projection.
    """

    DEFAULT_REFERENCE_PROFILE = AtlasFrontalFaceReferenceProfile(
        name="synthetic-neutral",
        face_width_ratio=0.7500,
        eye_spacing_ratio=0.3250,
        nose_width_ratio=0.1250,
        nose_length_ratio=0.1875,
        mouth_width_ratio=0.2250,
        jaw_width_ratio=0.5500,
        forehead_height_ratio=0.3750,
    )

    @classmethod
    def initialize(
        cls,
        measurements: AtlasFrontalFaceMeasurements,
        *,
        reference_profile: AtlasFrontalFaceReferenceProfile | None = None,
    ) -> AtlasParametricFaceParameters:
        if not isinstance(
            measurements,
            AtlasFrontalFaceMeasurements,
        ):
            raise TypeError(
                "measurements must be an " "AtlasFrontalFaceMeasurements instance."
            )

        if reference_profile is None:
            reference_profile = cls.DEFAULT_REFERENCE_PROFILE
        elif not isinstance(
            reference_profile,
            AtlasFrontalFaceReferenceProfile,
        ):
            raise TypeError(
                "reference_profile must be an "
                "AtlasFrontalFaceReferenceProfile "
                "instance or None."
            )

        face_height = measurements.face_height

        return AtlasParametricFaceParameters(
            scale=measurements.reference_scale,
            translation_x=(measurements.center_x - 0.50),
            translation_y=(measurements.center_y - 0.50),
            rotation_degrees=(measurements.eye_line_angle_degrees),
            face_width=cls._relative_parameter(
                measurements.face_width,
                face_height=face_height,
                neutral_ratio=(reference_profile.face_width_ratio),
            ),
            face_height=(measurements.face_height / measurements.reference_scale),
            eye_spacing=cls._relative_parameter(
                measurements.eye_spacing,
                face_height=face_height,
                neutral_ratio=(reference_profile.eye_spacing_ratio),
            ),
            eye_height=1.0,
            nose_width=cls._relative_parameter(
                measurements.nose_width,
                face_height=face_height,
                neutral_ratio=(reference_profile.nose_width_ratio),
            ),
            nose_length=cls._relative_parameter(
                measurements.nose_length,
                face_height=face_height,
                neutral_ratio=(reference_profile.nose_length_ratio),
            ),
            mouth_width=cls._relative_parameter(
                measurements.mouth_width,
                face_height=face_height,
                neutral_ratio=(reference_profile.mouth_width_ratio),
            ),
            chin_width=1.0,
            chin_length=1.0,
            jaw_width=cls._relative_parameter(
                measurements.jaw_width,
                face_height=face_height,
                neutral_ratio=(reference_profile.jaw_width_ratio),
            ),
            forehead_height=cls._relative_parameter(
                measurements.forehead_height,
                face_height=face_height,
                neutral_ratio=(reference_profile.forehead_height_ratio),
            ),
        )

    @staticmethod
    def _relative_parameter(
        measurement: float,
        *,
        face_height: float,
        neutral_ratio: float,
    ) -> float:
        measured_ratio = measurement / face_height

        return measured_ratio / neutral_ratio
