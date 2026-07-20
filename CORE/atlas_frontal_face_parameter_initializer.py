from __future__ import annotations

from CORE.atlas_frontal_face_measurements import (
    AtlasFrontalFaceMeasurements,
)
from CORE.atlas_parametric_face_parameters import (
    AtlasParametricFaceParameters,
)


class AtlasFrontalFaceParameterInitializer:
    """
    Converts deterministic frontal measurements into
    initial normalized parametric face values.

    The initializer performs no optimization, landmark
    fitting, mesh deformation, depth rendering, or
    projection.
    """

    NEUTRAL_FACE_WIDTH_RATIO = 0.7500
    NEUTRAL_EYE_SPACING_RATIO = 0.3250
    NEUTRAL_NOSE_WIDTH_RATIO = 0.1250
    NEUTRAL_NOSE_LENGTH_RATIO = 0.1875
    NEUTRAL_MOUTH_WIDTH_RATIO = 0.2250
    NEUTRAL_JAW_WIDTH_RATIO = 0.5500
    NEUTRAL_FOREHEAD_HEIGHT_RATIO = 0.3750

    @classmethod
    def initialize(
        cls,
        measurements: AtlasFrontalFaceMeasurements,
    ) -> AtlasParametricFaceParameters:
        if not isinstance(
            measurements,
            AtlasFrontalFaceMeasurements,
        ):
            raise TypeError(
                "measurements must be an " "AtlasFrontalFaceMeasurements instance."
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
                neutral_ratio=(cls.NEUTRAL_FACE_WIDTH_RATIO),
            ),
            face_height=(measurements.face_height / measurements.reference_scale),
            eye_spacing=cls._relative_parameter(
                measurements.eye_spacing,
                face_height=face_height,
                neutral_ratio=(cls.NEUTRAL_EYE_SPACING_RATIO),
            ),
            eye_height=1.0,
            nose_width=cls._relative_parameter(
                measurements.nose_width,
                face_height=face_height,
                neutral_ratio=(cls.NEUTRAL_NOSE_WIDTH_RATIO),
            ),
            nose_length=cls._relative_parameter(
                measurements.nose_length,
                face_height=face_height,
                neutral_ratio=(cls.NEUTRAL_NOSE_LENGTH_RATIO),
            ),
            mouth_width=cls._relative_parameter(
                measurements.mouth_width,
                face_height=face_height,
                neutral_ratio=(cls.NEUTRAL_MOUTH_WIDTH_RATIO),
            ),
            chin_width=1.0,
            chin_length=1.0,
            jaw_width=cls._relative_parameter(
                measurements.jaw_width,
                face_height=face_height,
                neutral_ratio=(cls.NEUTRAL_JAW_WIDTH_RATIO),
            ),
            forehead_height=cls._relative_parameter(
                measurements.forehead_height,
                face_height=face_height,
                neutral_ratio=(cls.NEUTRAL_FOREHEAD_HEIGHT_RATIO),
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
