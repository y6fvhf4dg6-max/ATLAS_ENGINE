from __future__ import annotations

from CORE.atlas_lod_level_catalog import (
    AtlasLoDLevelCatalog,
)
from CORE.atlas_lod_resolution_contract import (
    AtlasLoDResolutionInput,
    AtlasLoDResolutionResult,
)


class AtlasLoDResolver:
    @classmethod
    def resolve(
        cls,
        source: AtlasLoDResolutionInput,
    ) -> AtlasLoDResolutionResult:
        if not isinstance(
            source,
            AtlasLoDResolutionInput,
        ):
            raise TypeError(
                "source must be an "
                "AtlasLoDResolutionInput"
            )

        print_cap = cls._resolve_print_cap(
            source
        )
        visibility_cap = (
            cls._resolve_visibility_cap(
                source
            )
        )

        resolved_level = min(
            print_cap,
            visibility_cap,
        )

        limiting_factors = []

        if print_cap < 3:
            limiting_factors.append(
                "print_resolution"
            )

        if visibility_cap < 3:
            limiting_factors.append(
                "product_visibility"
            )

        supporting_factors = []

        if print_cap == 3:
            supporting_factors.append(
                "standard_print_resolution"
            )
        elif print_cap == 4:
            supporting_factors.append(
                "fine_print_resolution"
            )

        if visibility_cap == 4:
            supporting_factors.append(
                "high_product_visibility"
            )

        if source.landmark_importance >= 0.75:
            supporting_factors.append(
                "landmark_importance"
            )

        if source.available_color_count >= 4:
            supporting_factors.append(
                "multicolor_capacity"
            )

        return AtlasLoDResolutionResult(
            level=(
                AtlasLoDLevelCatalog.resolve(
                    resolved_level
                )
            ),
            source=source,
            limiting_factors=tuple(
                limiting_factors
            ),
            supporting_factors=tuple(
                supporting_factors
            ),
        )

    @staticmethod
    def _resolve_print_cap(
        source: AtlasLoDResolutionInput,
    ) -> int:
        nozzle = source.nozzle_diameter_mm
        layer = source.layer_height_mm
        wall = (
            source.minimum_wall_thickness_mm
        )

        if (
            nozzle >= 0.8
            or layer >= 0.4
            or wall >= 1.6
        ):
            return 0

        if (
            nozzle >= 0.6
            or layer >= 0.3
            or wall >= 1.2
        ):
            return 2

        if (
            nozzle <= 0.25
            and layer <= 0.10
            and wall <= 0.50
        ):
            return 4

        return 3

    @staticmethod
    def _resolve_visibility_cap(
        source: AtlasLoDResolutionInput,
    ) -> int:
        product_size = source.product_size_mm
        scale = source.scale_ratio
        viewing_distance = (
            source.viewing_distance_mm
        )

        if (
            product_size <= 60.0
            or scale >= 10000.0
            or viewing_distance >= 2200.0
        ):
            return 0

        if (
            product_size <= 90.0
            or scale >= 6500.0
            or viewing_distance >= 1300.0
        ):
            return 1

        if (
            product_size <= 120.0
            or scale >= 5000.0
            or viewing_distance >= 1000.0
        ):
            return 2

        if (
            product_size >= 190.0
            and scale <= 2500.0
            and viewing_distance <= 400.0
        ):
            return 4

        return 3
