from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from CORE.atlas_frontal_face_measurements import (
    AtlasFrontalFaceMeasurements,
)
from CORE.atlas_parametric_face_parameters import (
    AtlasParametricFaceParameters,
)


@dataclass(frozen=True)
class AtlasFrontalFaceParameterComparisonResult:
    """
    Immutable frontal face parameter comparison result.

    The result stores source measurements, initialized
    parametric face values, the reference-profile name,
    and normalized ratio deviations. It performs no
    measurement, fitting, optimization, deformation,
    rendering, or projection.
    """

    reference_profile_name: str
    measurements: AtlasFrontalFaceMeasurements
    parameters: AtlasParametricFaceParameters
    ratio_deviations: Mapping[str, float]

    def __post_init__(self) -> None:
        reference_profile_name = self._normalize_reference_profile_name(
            self.reference_profile_name,
        )

        if not isinstance(
            self.measurements,
            AtlasFrontalFaceMeasurements,
        ):
            raise TypeError(
                "measurements must be an " "AtlasFrontalFaceMeasurements instance."
            )

        if not isinstance(
            self.parameters,
            AtlasParametricFaceParameters,
        ):
            raise TypeError(
                "parameters must be an " "AtlasParametricFaceParameters instance."
            )

        ratio_deviations = self._normalize_ratio_deviations(
            self.ratio_deviations,
        )

        object.__setattr__(
            self,
            "reference_profile_name",
            reference_profile_name,
        )
        object.__setattr__(
            self,
            "ratio_deviations",
            ratio_deviations,
        )

    @staticmethod
    def _normalize_reference_profile_name(
        value: Any,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise ValueError("reference_profile_name must be a string.")

        normalized_name = value.strip()

        if not normalized_name:
            raise ValueError("reference_profile_name must not be blank.")

        return normalized_name

    @classmethod
    def _normalize_ratio_deviations(
        cls,
        value: Any,
    ) -> Mapping[str, float]:
        if not isinstance(
            value,
            Mapping,
        ):
            raise ValueError("ratio_deviations must be a mapping.")

        if not value:
            raise ValueError("ratio_deviations must not be empty.")

        normalized: dict[str, float] = {}

        for raw_name, raw_value in value.items():
            if not isinstance(
                raw_name,
                str,
            ):
                raise ValueError("ratio deviation names must be strings.")

            name = raw_name.strip()

            if not name:
                raise ValueError("ratio deviation names must not be blank.")

            if name in normalized:
                raise ValueError(
                    "ratio deviation names must be unique " "after normalization."
                )

            normalized[name] = cls._normalize_deviation(
                raw_value,
                name=name,
            )

        return MappingProxyType(
            normalized,
        )

    @staticmethod
    def _normalize_deviation(
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
            raise ValueError(f"{name} deviation must be numeric.") from exc

        if not math.isfinite(
            numeric_value,
        ):
            raise ValueError(f"{name} deviation must be finite.")

        return numeric_value
