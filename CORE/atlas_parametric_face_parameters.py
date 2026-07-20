from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AtlasParametricFaceParameters:
    """
    Immutable frontal parametric face parameters.

    The contract stores deterministic global pose,
    scale, and normalized facial proportion values.
    It does not perform landmark fitting, mesh
    deformation, depth rendering, or projection.
    """

    scale: float
    translation_x: float
    translation_y: float
    rotation_degrees: float
    face_width: float
    face_height: float
    eye_spacing: float
    eye_height: float
    nose_width: float
    nose_length: float
    mouth_width: float
    chin_width: float
    chin_length: float
    jaw_width: float
    forehead_height: float

    def __post_init__(self) -> None:
        positive_values = {
            "scale": self.scale,
            "face_width": self.face_width,
            "face_height": self.face_height,
            "eye_spacing": self.eye_spacing,
            "eye_height": self.eye_height,
            "nose_width": self.nose_width,
            "nose_length": self.nose_length,
            "mouth_width": self.mouth_width,
            "chin_width": self.chin_width,
            "chin_length": self.chin_length,
            "jaw_width": self.jaw_width,
            "forehead_height": self.forehead_height,
        }

        signed_values = {
            "translation_x": self.translation_x,
            "translation_y": self.translation_y,
            "rotation_degrees": self.rotation_degrees,
        }

        converted: dict[str, float] = {}

        for name, value in {
            **positive_values,
            **signed_values,
        }.items():
            converted[name] = self._normalize_numeric(
                value,
                name=name,
            )

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
            numeric_value = float(value)
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
