from __future__ import annotations

import math

from CORE.atlas_frontal_face_measurements import (
    AtlasFrontalFaceMeasurements,
)
from CORE.atlas_portrait_landmark_result import (
    AtlasPortraitLandmarkResult,
)


class AtlasFrontalFaceMeasurer:
    """
    Deterministic frontal portrait landmark measurer.

    The measurer converts required normalized frontal
    landmarks into immutable two-dimensional face
    measurements. It does not detect landmarks, fit
    parametric models, deform meshes, or render depth.
    """

    REQUIRED_LANDMARKS = (
        "left_face_edge",
        "right_face_edge",
        "hairline_center",
        "left_eye_center",
        "right_eye_center",
        "nose_root",
        "nose_left",
        "nose_tip",
        "nose_right",
        "mouth_left",
        "mouth_right",
        "left_jaw",
        "chin_tip",
        "right_jaw",
    )

    @classmethod
    def measure(
        cls,
        result: AtlasPortraitLandmarkResult,
    ) -> AtlasFrontalFaceMeasurements:
        if not isinstance(
            result,
            AtlasPortraitLandmarkResult,
        ):
            raise TypeError("result must be an " "AtlasPortraitLandmarkResult.")

        cls._validate_required_landmarks(
            result,
        )

        left_face_edge = result.landmarks["left_face_edge"]
        right_face_edge = result.landmarks["right_face_edge"]
        hairline_center = result.landmarks["hairline_center"]
        left_eye_center = result.landmarks["left_eye_center"]
        right_eye_center = result.landmarks["right_eye_center"]
        nose_root = result.landmarks["nose_root"]
        nose_left = result.landmarks["nose_left"]
        nose_tip = result.landmarks["nose_tip"]
        nose_right = result.landmarks["nose_right"]
        mouth_left = result.landmarks["mouth_left"]
        mouth_right = result.landmarks["mouth_right"]
        left_jaw = result.landmarks["left_jaw"]
        chin_tip = result.landmarks["chin_tip"]
        right_jaw = result.landmarks["right_jaw"]

        face_width = cls._distance(
            left_face_edge,
            right_face_edge,
        )

        face_height = cls._distance(
            hairline_center,
            chin_tip,
        )

        eye_spacing = cls._distance(
            left_eye_center,
            right_eye_center,
        )

        eye_line_angle_degrees = math.degrees(
            math.atan2(
                (left_eye_center[1] - right_eye_center[1]),
                (left_eye_center[0] - right_eye_center[0]),
            )
        )

        nose_width = cls._distance(
            nose_left,
            nose_right,
        )

        nose_length = cls._distance(
            nose_root,
            nose_tip,
        )

        mouth_width = cls._distance(
            mouth_left,
            mouth_right,
        )

        jaw_width = cls._distance(
            left_jaw,
            right_jaw,
        )

        forehead_height = cls._distance(
            hairline_center,
            nose_root,
        )

        center_x = (left_face_edge[0] + right_face_edge[0]) / 2.0

        center_y = (hairline_center[1] + chin_tip[1]) / 2.0

        return AtlasFrontalFaceMeasurements(
            center_x=center_x,
            center_y=center_y,
            reference_scale=face_height,
            face_width=face_width,
            face_height=face_height,
            eye_spacing=eye_spacing,
            eye_line_angle_degrees=(eye_line_angle_degrees),
            nose_width=nose_width,
            nose_length=nose_length,
            mouth_width=mouth_width,
            jaw_width=jaw_width,
            forehead_height=forehead_height,
        )

    @classmethod
    def _validate_required_landmarks(
        cls,
        result: AtlasPortraitLandmarkResult,
    ) -> None:
        for name in cls.REQUIRED_LANDMARKS:
            if name not in result.landmarks:
                raise ValueError(f"required landmark is missing: {name}")

    @staticmethod
    def _distance(
        point_a: tuple[float, float],
        point_b: tuple[float, float],
    ) -> float:
        return math.hypot(
            point_b[0] - point_a[0],
            point_b[1] - point_a[1],
        )
