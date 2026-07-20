from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AtlasFrontalFaceMeasurements:
    """
    Immutable normalized frontal face measurements.

    The contract stores deterministic two-dimensional
    measurements derived from frontal portrait
    landmarks. It does not perform landmark detection,
    parameter fitting, mesh deformation, or rendering.
    """

    center_x: float
    center_y: float
    reference_scale: float
    face_width: float
    face_height: float
    eye_spacing: float
    eye_line_angle_degrees: float
    nose_width: float
    nose_length: float
    mouth_width: float
    jaw_width: float
    forehead_height: float

    def __post_init__(self) -> None:
        normalized_center_values = {
            "center_x": self.center_x,
            "center_y": self.center_y,
        }

        positive_values = {
            "reference_scale": self.reference_scale,
            "face_width": self.face_width,
            "face_height": self.face_height,
            "eye_spacing": self.eye_spacing,
            "nose_width": self.nose_width,
            "nose_length": self.nose_length,
            "mouth_width": self.mouth_width,
            "jaw_width": self.jaw_width,
            "forehead_height": self.forehead_height,
        }

        signed_values = {
            "eye_line_angle_degrees": (self.eye_line_angle_degrees),
        }

        converted: dict[str, float] = {}

        for name, value in {
            **normalized_center_values,
            **positive_values,
            **signed_values,
        }.items():
            converted[name] = self._normalize_numeric(
                value,
                name=name,
            )

        for name in normalized_center_values:
            if not (0.0 <= converted[name] <= 1.0):
                raise ValueError(f"{name} must be in the " "0.0..1.0 range.")

        for name in positive_values:
            if converted[name] <= 0.0:
                raise ValueError(f"{name} must be greater than zero.")

        for name, value in converted.items():
            object.__setattr__(
                self,
                name,
                value,
            )

    @staticmethod
    def _normalize_numeric(
        value: Any,
        *,
        name: str,
    ) -> float:
        try:
            numeric_value = float(
                value,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(f"{name} must be numeric.") from exc

        if not math.isfinite(
            numeric_value,
        ):
            raise ValueError(f"{name} must be finite.")

        return numeric_value
