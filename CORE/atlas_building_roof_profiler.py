class AtlasBuildingRoofProfiler:
    """
    Normal şehir binaları için çatı profil karar katmanı.

    Bu modül yalnızca çatı tipini sınıflandırır.
    Mesh veya çatı geometrisi üretmez.
    """

    SUPPORTED_OSM_PROFILES = {
        "flat": "flat",
        "gable": "gable",
        "gabled": "gable",
        "hipped": "hipped",
        "pyramidal": "pyramidal",
        "skillion": "skillion",
        "apse_gabled": "apse_gabled",
    }

    MIN_RECTANGULARITY = 0.75
    GABLE_ASPECT_RATIO = 1.35

    @staticmethod
    def classify(
        roof_shape,
        aspect_ratio,
        rectangularity,
        is_building_part,
        is_special_architectural_building=False,
    ):
        aspect_ratio = float(aspect_ratio)
        rectangularity = float(rectangularity)

        if aspect_ratio <= 0.0:
            raise ValueError(
                "aspect_ratio sıfırdan büyük olmalıdır."
            )

        if not 0.0 <= rectangularity <= 1.0:
            raise ValueError(
                "rectangularity 0 ile 1 arasında olmalıdır."
            )

        normalized_roof_shape = (
            str(roof_shape).strip().lower()
            if roof_shape is not None
            else None
        )

        explicit_profile = (
            AtlasBuildingRoofProfiler.SUPPORTED_OSM_PROFILES.get(
                normalized_roof_shape
            )
        )

        if explicit_profile is not None:
            return {
                "roof_profile": explicit_profile,
                "decision_source": "osm",
                "aspect_ratio": aspect_ratio,
                "rectangularity": rectangularity,
            }

        if is_building_part:
            return {
                "roof_profile": "flat",
                "decision_source": "building_part",
                "aspect_ratio": aspect_ratio,
                "rectangularity": rectangularity,
            }

        if is_special_architectural_building:
            return {
                "roof_profile": "flat",
                "decision_source": "special_architecture",
                "aspect_ratio": aspect_ratio,
                "rectangularity": rectangularity,
            }

        if (
            rectangularity
            < AtlasBuildingRoofProfiler.MIN_RECTANGULARITY
        ):
            return {
                "roof_profile": "flat",
                "decision_source": "fallback",
                "aspect_ratio": aspect_ratio,
                "rectangularity": rectangularity,
            }

        if (
            aspect_ratio
            >= AtlasBuildingRoofProfiler.GABLE_ASPECT_RATIO
        ):
            return {
                "roof_profile": "gable",
                "decision_source": "inferred",
                "aspect_ratio": aspect_ratio,
                "rectangularity": rectangularity,
            }

        return {
            "roof_profile": "hipped",
            "decision_source": "inferred",
            "aspect_ratio": aspect_ratio,
            "rectangularity": rectangularity,
        }
