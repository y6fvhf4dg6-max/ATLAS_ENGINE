from __future__ import annotations

import math

from CORE.atlas_urban_block_resolver import (
    AtlasUrbanBlockProfile,
)


class AtlasSceneMorphologyEvidenceResolver:
    @staticmethod
    def _non_negative(
        value,
        *,
        field_name,
    ):
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                f"{field_name} must be numeric"
            ) from exc

        if (
            not math.isfinite(value)
            or value < 0.0
        ):
            raise ValueError(
                f"{field_name} must be finite "
                "and non-negative"
            )

        return value

    @staticmethod
    def _count(
        value,
        *,
        field_name,
    ):
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or value < 0
        ):
            raise ValueError(
                f"{field_name} must be a "
                "non-negative integer"
            )

        return value

    @staticmethod
    def _ratio(
        numerator,
        denominator,
    ):
        if denominator <= 0.0:
            return 0.0

        return min(
            1.0,
            max(
                0.0,
                numerator / denominator,
            ),
        )

    @classmethod
    def resolve(
        cls,
        *,
        product_area_mm2,
        building_footprint_area_mm2,
        road_surface_area_mm2,
        vegetation_area_mm2,
        forest_area_mm2,
        water_area_mm2,
        railway_count,
        terrain_relief_mm,
        terrain_reference_height_mm,
        landmark_count,
        building_count,
        block_profiles=(),
    ):
        product_area_mm2 = cls._non_negative(
            product_area_mm2,
            field_name="product_area_mm2",
        )

        if product_area_mm2 <= 0.0:
            raise ValueError(
                "product_area_mm2 must be positive"
            )

        building_footprint_area_mm2 = (
            cls._non_negative(
                building_footprint_area_mm2,
                field_name=(
                    "building_footprint_area_mm2"
                ),
            )
        )

        road_surface_area_mm2 = cls._non_negative(
            road_surface_area_mm2,
            field_name="road_surface_area_mm2",
        )

        vegetation_area_mm2 = cls._non_negative(
            vegetation_area_mm2,
            field_name="vegetation_area_mm2",
        )

        forest_area_mm2 = cls._non_negative(
            forest_area_mm2,
            field_name="forest_area_mm2",
        )

        water_area_mm2 = cls._non_negative(
            water_area_mm2,
            field_name="water_area_mm2",
        )

        terrain_relief_mm = cls._non_negative(
            terrain_relief_mm,
            field_name="terrain_relief_mm",
        )

        terrain_reference_height_mm = (
            cls._non_negative(
                terrain_reference_height_mm,
                field_name=(
                    "terrain_reference_height_mm"
                ),
            )
        )

        railway_count = cls._count(
            railway_count,
            field_name="railway_count",
        )
        landmark_count = cls._count(
            landmark_count,
            field_name="landmark_count",
        )
        building_count = cls._count(
            building_count,
            field_name="building_count",
        )

        block_profiles = tuple(
            block_profiles or ()
        )

        density_values = []

        for profile in block_profiles:
            if not isinstance(
                profile,
                AtlasUrbanBlockProfile,
            ):
                raise TypeError(
                    "block_profiles must contain "
                    "AtlasUrbanBlockProfile values"
                )

            density_values.append(
                profile.density_ratio
            )

        block_compactness = (
            sum(density_values)
            / len(density_values)
            if density_values
            else 0.0
        )

        terrain_relief = cls._ratio(
            terrain_relief_mm,
            terrain_reference_height_mm,
        )

        landmark_density = (
            cls._ratio(
                landmark_count,
                building_count,
            )
            if building_count > 0
            else 0.0
        )

        return {
            "building_density": cls._ratio(
                building_footprint_area_mm2,
                product_area_mm2,
            ),
            "road_density": cls._ratio(
                road_surface_area_mm2,
                product_area_mm2,
            ),
            "block_compactness": (
                block_compactness
            ),
            "vegetation_coverage": cls._ratio(
                vegetation_area_mm2,
                product_area_mm2,
            ),
            "forest_coverage": cls._ratio(
                forest_area_mm2,
                product_area_mm2,
            ),
            "water_coverage": cls._ratio(
                water_area_mm2,
                product_area_mm2,
            ),
            "railway_presence": (
                railway_count > 0
            ),
            "terrain_relief": terrain_relief,
            "landmark_density": (
                landmark_density
            ),
        }
