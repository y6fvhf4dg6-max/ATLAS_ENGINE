from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AtlasFrontalFaceReferenceProfile:
    """
    Immutable frontal face proportion reference.

    Ratios are normalized against frontal face height.
    The profile carries calibration values only; it
    performs no measurement, fitting, optimization,
    deformation, rendering, or projection.
    """

    name: str
    face_width_ratio: float
    eye_spacing_ratio: float
    nose_width_ratio: float
    nose_length_ratio: float
    mouth_width_ratio: float
    jaw_width_ratio: float
    forehead_height_ratio: float

    def __post_init__(self) -> None:
        if not isinstance(
            self.name,
            str,
        ):
            raise ValueError("name must be a string.")

        normalized_name = self.name.strip()

        if not normalized_name:
            raise ValueError("name must not be blank.")

        object.__setattr__(
            self,
            "name",
            normalized_name,
        )

        values = {
            "face_width_ratio": self.face_width_ratio,
            "eye_spacing_ratio": self.eye_spacing_ratio,
            "nose_width_ratio": self.nose_width_ratio,
            "nose_length_ratio": self.nose_length_ratio,
            "mouth_width_ratio": self.mouth_width_ratio,
            "jaw_width_ratio": self.jaw_width_ratio,
            "forehead_height_ratio": (self.forehead_height_ratio),
        }

        converted: dict[str, float] = {}

        for name, value in values.items():
            converted[name] = self._normalize_numeric(
                value,
                name=name,
            )

        for name, value in converted.items():
            if value <= 0.0:
                raise ValueError(f"{name} must be greater than zero.")

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
