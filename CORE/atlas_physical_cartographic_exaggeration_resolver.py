from __future__ import annotations

import math
from dataclasses import dataclass

from CORE.atlas_lod_level_catalog import (
    AtlasLoDLevel,
)


@dataclass(frozen=True, slots=True)
class AtlasPhysicalCartographicExaggeration:
    semantic_class: str
    source_width_m: float
    strict_scale_width_mm: float
    physical_width_mm: float
    effective_minimum_width_mm: float
    semantic_priority: float
    product_size_mm: float
    scale_ratio: float
    nozzle_diameter_mm: float
    lod_level: AtlasLoDLevel
    exaggerated: bool
    reason: str


class AtlasPhysicalCartographicExaggerationResolver:
    SUPPORTED_SEMANTIC_CLASSES = frozenset(
        {
            "major_road",
            "local_road",
            "service_road",
            "pedestrian_path",
            "cycleway",
            "railway",
            "light_rail",
            "tram",
            "narrow_waterway",
            "shoreline_edge",
            "vegetation_element",
        }
    )

    @staticmethod
    def _positive_finite(
        value,
        *,
        field_name,
    ) -> float:
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                f"{field_name} must be numeric"
            ) from exc

        if (
            not math.isfinite(value)
            or value <= 0.0
        ):
            raise ValueError(
                f"{field_name} must be finite "
                "and greater than zero"
            )

        return value

    @staticmethod
    def _priority(value) -> float:
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                "semantic_priority must be numeric"
            ) from exc

        if (
            not math.isfinite(value)
            or not 0.0 <= value <= 1.0
        ):
            raise ValueError(
                "semantic_priority must be finite "
                "and within 0..1"
            )

        return value

    @staticmethod
    def _semantic_class(value) -> str:
        semantic_class = "_".join(
            str(value).strip().lower().split()
        )

        if not semantic_class:
            raise ValueError(
                "semantic_class must not be blank"
            )

        if (
            semantic_class
            not in AtlasPhysicalCartographicExaggerationResolver
            .SUPPORTED_SEMANTIC_CLASSES
        ):
            raise ValueError(
                "unsupported semantic_class: "
                f"{semantic_class}"
            )

        return semantic_class

    @classmethod
    def resolve(
        cls,
        *,
        semantic_class,
        source_width_m,
        scale_ratio,
        product_size_mm,
        nozzle_diameter_mm,
        minimum_printable_width_mm,
        semantic_priority,
        lod_level,
    ) -> AtlasPhysicalCartographicExaggeration:
        semantic_class = cls._semantic_class(
            semantic_class
        )

        source_width_m = cls._positive_finite(
            source_width_m,
            field_name="source_width_m",
        )
        scale_ratio = cls._positive_finite(
            scale_ratio,
            field_name="scale_ratio",
        )
        product_size_mm = cls._positive_finite(
            product_size_mm,
            field_name="product_size_mm",
        )
        nozzle_diameter_mm = cls._positive_finite(
            nozzle_diameter_mm,
            field_name="nozzle_diameter_mm",
        )
        minimum_printable_width_mm = (
            cls._positive_finite(
                minimum_printable_width_mm,
                field_name=(
                    "minimum_printable_width_mm"
                ),
            )
        )
        semantic_priority = cls._priority(
            semantic_priority
        )

        if not isinstance(
            lod_level,
            AtlasLoDLevel,
        ):
            raise TypeError(
                "lod_level must be an AtlasLoDLevel"
            )

        strict_scale_width_mm = (
            source_width_m
            * 1000.0
            / scale_ratio
        )

        effective_minimum_width_mm = max(
            minimum_printable_width_mm,
            nozzle_diameter_mm,
        )

        physical_width_mm = max(
            strict_scale_width_mm,
            effective_minimum_width_mm,
        )

        exaggerated = (
            physical_width_mm
            > strict_scale_width_mm
            + 1e-12
        )

        reason = (
            "physical_minimum"
            if exaggerated
            else "strict_scale_readable"
        )

        return AtlasPhysicalCartographicExaggeration(
            semantic_class=semantic_class,
            source_width_m=source_width_m,
            strict_scale_width_mm=(
                strict_scale_width_mm
            ),
            physical_width_mm=physical_width_mm,
            effective_minimum_width_mm=(
                effective_minimum_width_mm
            ),
            semantic_priority=semantic_priority,
            product_size_mm=product_size_mm,
            scale_ratio=scale_ratio,
            nozzle_diameter_mm=nozzle_diameter_mm,
            lod_level=lod_level,
            exaggerated=exaggerated,
            reason=reason,
        )

    @classmethod
    def validate_relative_hierarchy(
        cls,
        results,
    ) -> None:
        results = tuple(results)

        for result in results:
            if not isinstance(
                result,
                AtlasPhysicalCartographicExaggeration,
            ):
                raise TypeError(
                    "results must contain "
                    "AtlasPhysicalCartographicExaggeration "
                    "values"
                )

        hierarchy = {
            "major_road": 4,
            "local_road": 3,
            "service_road": 2,
            "pedestrian_path": 1,
        }

        ranked = [
            result
            for result in results
            if result.semantic_class in hierarchy
        ]

        ranked.sort(
            key=lambda result: hierarchy[
                result.semantic_class
            ],
            reverse=True,
        )

        for more_important, less_important in zip(
            ranked,
            ranked[1:],
        ):
            if (
                more_important.semantic_priority
                <= less_important.semantic_priority
            ):
                raise ValueError(
                    "semantic_priority must preserve "
                    "relative hierarchy"
                )

            if (
                more_important.physical_width_mm
                < less_important.physical_width_mm
            ):
                raise ValueError(
                    "physical_width_mm must preserve "
                    "relative hierarchy"
                )
