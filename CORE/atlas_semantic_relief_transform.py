from __future__ import annotations

import math
from dataclasses import dataclass


def _finite_triplet(value, *, field_name: str) -> tuple[float, float, float]:
    if isinstance(value, (str, bytes)):
        raise ValueError(
            f"{field_name} must contain exactly three numeric values"
        )

    try:
        items = tuple(value)
    except TypeError as exc:
        raise ValueError(
            f"{field_name} must contain exactly three numeric values"
        ) from exc

    if len(items) != 3:
        raise ValueError(
            f"{field_name} must contain exactly three numeric values"
        )

    try:
        result = tuple(float(item) for item in items)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{field_name} must contain numeric values"
        ) from exc

    if not all(math.isfinite(item) for item in result):
        raise ValueError(
            f"{field_name} must contain only finite values"
        )

    return result


@dataclass(frozen=True, slots=True)
class AtlasSemanticReliefTransform:
    translation_mm: tuple[float, float, float]
    rotation_degrees_xyz: tuple[float, float, float]
    dimensions_mm: tuple[float, float, float]
    coordinate_space: str = "component_local"

    def __post_init__(self) -> None:
        coordinate_space = "_".join(
            str(self.coordinate_space).strip().lower().split()
        )
        if not coordinate_space:
            raise ValueError(
                "coordinate_space must not be blank"
            )
        object.__setattr__(
            self,
            "coordinate_space",
            coordinate_space,
        )

        for field_name in (
            "translation_mm",
            "rotation_degrees_xyz",
            "dimensions_mm",
        ):
            object.__setattr__(
                self,
                field_name,
                _finite_triplet(
                    getattr(self, field_name),
                    field_name=field_name,
                ),
            )

        if any(value <= 0.0 for value in self.dimensions_mm):
            raise ValueError(
                "dimensions_mm values must be greater than zero"
            )
