import math


class AtlasMorphologyAwareTerrainProductResolver:
    _MORPHOLOGY_PROFILES = {
        "dense_urban": {
            "terrain_emphasis": "secondary",
            "vertical_compression": "strong",
        },
        "historic_core": {
            "terrain_emphasis": "restrained",
            "vertical_compression": None,
        },
        "suburban": {
            "terrain_emphasis": "moderate",
            "vertical_compression": None,
        },
        "rural": {
            "terrain_emphasis": "important",
            "vertical_compression": None,
        },
        "mountain": {
            "terrain_emphasis": "dominant",
            "vertical_compression": None,
        },
        "landscape_nature": {
            "terrain_emphasis": "primary",
            "vertical_compression": None,
        },
    }

    @staticmethod
    def _finite_non_negative(value, name):
        try:
            parsed = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{name} must be finite and non-negative"
            ) from exc

        if not math.isfinite(parsed) or parsed < 0.0:
            raise ValueError(
                f"{name} must be finite and non-negative"
            )

        return parsed

    @staticmethod
    def _positive(value, name):
        try:
            parsed = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{name} must be positive"
            ) from exc

        if not math.isfinite(parsed) or parsed <= 0.0:
            raise ValueError(
                f"{name} must be positive"
            )

        return parsed

    @classmethod
    def resolve(
        cls,
        *,
        scene_morphology,
        source_elevation_range_m,
        product_size_mm,
        urban_density,
        landmark_present,
        physical_relief_range_mm,
        minimum_printable_relief_mm,
        maximum_printable_relief_mm,
    ):
        profile = cls._MORPHOLOGY_PROFILES.get(
            scene_morphology
        )

        if profile is None:
            raise ValueError(
                "Unsupported scene_morphology"
            )

        source_elevation_range_m = (
            cls._finite_non_negative(
                source_elevation_range_m,
                "source_elevation_range_m",
            )
        )

        product_size_mm = cls._positive(
            product_size_mm,
            "product_size_mm",
        )

        urban_density = cls._finite_non_negative(
            urban_density,
            "urban_density",
        )

        if urban_density > 1.0:
            raise ValueError(
                "urban_density must be between 0 and 1"
            )

        physical_relief_range_mm = (
            cls._finite_non_negative(
                physical_relief_range_mm,
                "physical_relief_range_mm",
            )
        )

        minimum_printable_relief_mm = cls._positive(
            minimum_printable_relief_mm,
            "minimum_printable_relief_mm",
        )

        maximum_printable_relief_mm = cls._positive(
            maximum_printable_relief_mm,
            "maximum_printable_relief_mm",
        )

        if (
            maximum_printable_relief_mm
            < minimum_printable_relief_mm
        ):
            raise ValueError(
                "maximum_printable_relief_mm must be "
                "greater than or equal to "
                "minimum_printable_relief_mm"
            )

        if (
            physical_relief_range_mm
            < minimum_printable_relief_mm
        ):
            resolved_physical_relief_mm = (
                minimum_printable_relief_mm
            )
            printability_adjustment = (
                "raised_to_minimum"
            )
        elif (
            physical_relief_range_mm
            > maximum_printable_relief_mm
        ):
            resolved_physical_relief_mm = (
                maximum_printable_relief_mm
            )
            printability_adjustment = (
                "limited_to_maximum"
            )
        else:
            resolved_physical_relief_mm = (
                physical_relief_range_mm
            )
            printability_adjustment = "none"

        landmark_present = bool(landmark_present)

        return {
            "type": "morphology_aware_terrain_product_profile",
            "scene_morphology": scene_morphology,
            "terrain_emphasis": profile["terrain_emphasis"],
            "vertical_compression": profile[
                "vertical_compression"
            ],
            "source_elevation_range_m": (
                source_elevation_range_m
            ),
            "source_elevation_modified": False,
            "product_size_mm": product_size_mm,
            "urban_density": urban_density,
            "urban_density_pressure": urban_density,
            "landmark_present": landmark_present,
            "semantic_content_priority": (
                "protect"
                if landmark_present
                else "normal"
            ),
            "physical_relief_range_mm": (
                physical_relief_range_mm
            ),
            "minimum_printable_relief_mm": (
                minimum_printable_relief_mm
            ),
            "maximum_printable_relief_mm": (
                maximum_printable_relief_mm
            ),
            "resolved_physical_relief_mm": (
                resolved_physical_relief_mm
            ),
            "relative_physical_relief": (
                resolved_physical_relief_mm
                / product_size_mm
            ),
            "printability_adjustment": (
                printability_adjustment
            ),
        }
