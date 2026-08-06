from __future__ import annotations

import math
from dataclasses import dataclass

from CORE.atlas_lod_level_catalog import (
    AtlasLoDLevel,
)


def _positive_finite(
    value,
    *,
    field_name: str,
) -> float:
    try:
        numeric = float(
            value
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            f"{field_name} must be numeric"
        ) from exc

    if not math.isfinite(
        numeric
    ):
        raise ValueError(
            f"{field_name} must be finite"
        )

    if numeric <= 0.0:
        raise ValueError(
            f"{field_name} must be greater than zero"
        )

    return numeric


def _normalize_identifier(
    value,
    *,
    field_name: str,
) -> str:
    normalized = "_".join(
        str(value).strip().lower().split()
    )

    if not normalized:
        raise ValueError(
            f"{field_name} must not be blank"
        )

    return normalized


def _normalize_factors(
    values,
    *,
    field_name: str,
) -> tuple[str, ...]:
    normalized = tuple(
        _normalize_identifier(
            value,
            field_name=field_name,
        )
        for value in values
    )

    if (
        len(normalized)
        != len(set(normalized))
    ):
        raise ValueError(
            f"{field_name} must contain unique values"
        )

    return normalized


@dataclass(frozen=True, slots=True)
class AtlasLoDResolutionInput:
    product_size_mm: float
    scale_ratio: float
    nozzle_diameter_mm: float
    layer_height_mm: float
    minimum_wall_thickness_mm: float
    landmark_importance: float
    viewing_distance_mm: float
    available_color_count: int

    def __post_init__(self) -> None:
        product_size_mm = _positive_finite(
            self.product_size_mm,
            field_name="product_size_mm",
        )
        scale_ratio = _positive_finite(
            self.scale_ratio,
            field_name="scale_ratio",
        )
        nozzle_diameter_mm = _positive_finite(
            self.nozzle_diameter_mm,
            field_name="nozzle_diameter_mm",
        )
        layer_height_mm = _positive_finite(
            self.layer_height_mm,
            field_name="layer_height_mm",
        )
        minimum_wall_thickness_mm = (
            _positive_finite(
                self.minimum_wall_thickness_mm,
                field_name=(
                    "minimum_wall_thickness_mm"
                ),
            )
        )
        viewing_distance_mm = _positive_finite(
            self.viewing_distance_mm,
            field_name="viewing_distance_mm",
        )

        try:
            landmark_importance = float(
                self.landmark_importance
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "landmark_importance must be numeric"
            ) from exc

        if not math.isfinite(
            landmark_importance
        ):
            raise ValueError(
                "landmark_importance must be finite"
            )

        if not (
            0.0
            <= landmark_importance
            <= 1.0
        ):
            raise ValueError(
                "landmark_importance must be in the "
                "0.0..1.0 range"
            )

        available_color_count = (
            self.available_color_count
        )

        if (
            isinstance(
                available_color_count,
                bool,
            )
            or not isinstance(
                available_color_count,
                int,
            )
            or available_color_count < 1
        ):
            raise ValueError(
                "available_color_count must be a "
                "positive integer"
            )

        object.__setattr__(
            self,
            "product_size_mm",
            product_size_mm,
        )
        object.__setattr__(
            self,
            "scale_ratio",
            scale_ratio,
        )
        object.__setattr__(
            self,
            "nozzle_diameter_mm",
            nozzle_diameter_mm,
        )
        object.__setattr__(
            self,
            "layer_height_mm",
            layer_height_mm,
        )
        object.__setattr__(
            self,
            "minimum_wall_thickness_mm",
            minimum_wall_thickness_mm,
        )
        object.__setattr__(
            self,
            "landmark_importance",
            landmark_importance,
        )
        object.__setattr__(
            self,
            "viewing_distance_mm",
            viewing_distance_mm,
        )
        object.__setattr__(
            self,
            "available_color_count",
            available_color_count,
        )


@dataclass(frozen=True, slots=True)
class AtlasLoDResolutionResult:
    level: AtlasLoDLevel
    source: AtlasLoDResolutionInput
    limiting_factors: tuple[str, ...] = ()
    supporting_factors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(
            self.level,
            AtlasLoDLevel,
        ):
            raise TypeError(
                "level must be an AtlasLoDLevel"
            )

        if not isinstance(
            self.source,
            AtlasLoDResolutionInput,
        ):
            raise TypeError(
                "source must be an "
                "AtlasLoDResolutionInput"
            )

        limiting_factors = (
            _normalize_factors(
                self.limiting_factors,
                field_name="limiting_factors",
            )
        )
        supporting_factors = (
            _normalize_factors(
                self.supporting_factors,
                field_name="supporting_factors",
            )
        )

        object.__setattr__(
            self,
            "limiting_factors",
            limiting_factors,
        )
        object.__setattr__(
            self,
            "supporting_factors",
            supporting_factors,
        )
