from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AtlasParametricFaceDepthProfile:
    """
    Immutable anatomical face-depth profile.

    All values are nonnegative normalized depth
    amplitudes. Projection values are added to the
    neutral Z field; depth values are subtracted by
    the anatomical depth-deformation stage.

    The profile performs no measurement, landmark
    fitting, coordinate deformation, rendering,
    triangulation, or mesh generation.
    """

    name: str
    brow_projection: float
    eye_socket_depth: float
    cheek_projection: float
    nose_bridge_projection: float
    nose_tip_projection: float
    nose_wing_projection: float
    upper_lip_projection: float
    lower_lip_projection: float
    philtrum_depth: float
    labiomental_fold_depth: float
    chin_projection: float

    def __post_init__(self) -> None:
        if not isinstance(
            self.name,
            str,
        ):
            raise ValueError(
                "name must be a string."
            )

        normalized_name = self.name.strip()

        if not normalized_name:
            raise ValueError(
                "name must not be blank."
            )

        object.__setattr__(
            self,
            "name",
            normalized_name,
        )

        values = {
            "brow_projection": self.brow_projection,
            "eye_socket_depth": self.eye_socket_depth,
            "cheek_projection": self.cheek_projection,
            "nose_bridge_projection": (
                self.nose_bridge_projection
            ),
            "nose_tip_projection": (
                self.nose_tip_projection
            ),
            "nose_wing_projection": (
                self.nose_wing_projection
            ),
            "upper_lip_projection": (
                self.upper_lip_projection
            ),
            "lower_lip_projection": (
                self.lower_lip_projection
            ),
            "philtrum_depth": self.philtrum_depth,
            "labiomental_fold_depth": (
                self.labiomental_fold_depth
            ),
            "chin_projection": self.chin_projection,
        }

        for name, value in values.items():
            normalized_value = self._normalize_depth(
                value,
                name=name,
            )

            object.__setattr__(
                self,
                name,
                normalized_value,
            )

    @staticmethod
    def _normalize_depth(
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
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if not math.isfinite(
            numeric_value,
        ):
            raise ValueError(
                f"{name} must be finite."
            )

        if numeric_value < 0.0:
            raise ValueError(
                f"{name} must be nonnegative."
            )

        return numeric_value
