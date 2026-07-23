from CORE.atlas_building_analyzer import AtlasBuildingAnalyzer
from CORE.atlas_building_roof_profiler import (
    AtlasBuildingRoofProfiler,
)


class AtlasBuildingRoofMetadataProfiler:
    """
    Normal bina çatı kararını mesh metadata'sına dönüştürür.

    Bu sınıf çatı geometrisi üretmez ve mesh üçgenlerini değiştirmez.
    """

    @staticmethod
    def profile(
        atlas_building,
        is_building_part=False,
    ):
        if getattr(
            atlas_building,
            "is_castle_building",
            False,
        ):
            return None

        oriented_aspect_ratio = (
            AtlasBuildingAnalyzer.oriented_aspect_ratio(
                atlas_building
            )
        )
        rectangularity = (
            AtlasBuildingAnalyzer.rectangularity(
                atlas_building
            )
        )

        if oriented_aspect_ratio <= 0.0:
            return {
                "building_roof_profile": "flat",
                "building_roof_decision_source": "fallback",
                "building_oriented_aspect_ratio": (
                    oriented_aspect_ratio
                ),
                "building_rectangularity": rectangularity,
            }

        decision = AtlasBuildingRoofProfiler.classify(
            roof_shape=getattr(
                atlas_building,
                "roof_type",
                None,
            ),
            aspect_ratio=oriented_aspect_ratio,
            rectangularity=rectangularity,
            is_building_part=is_building_part,
        )

        return {
            "building_roof_profile": decision[
                "roof_profile"
            ],
            "building_roof_decision_source": decision[
                "decision_source"
            ],
            "building_oriented_aspect_ratio": (
                oriented_aspect_ratio
            ),
            "building_rectangularity": rectangularity,
        }

    @staticmethod
    def attach(
        mesh,
        atlas_building,
        is_building_part=False,
        profile_counts=None,
        decision_source_counts=None,
    ):
        metadata = AtlasBuildingRoofMetadataProfiler.profile(
            atlas_building=atlas_building,
            is_building_part=is_building_part,
        )

        if metadata is None:
            return mesh

        mesh.update(metadata)

        if profile_counts is not None:
            profile = metadata["building_roof_profile"]
            profile_counts[profile] = (
                profile_counts.get(profile, 0)
                + 1
            )

        if decision_source_counts is not None:
            source = metadata[
                "building_roof_decision_source"
            ]
            decision_source_counts[source] = (
                decision_source_counts.get(source, 0)
                + 1
            )

        return mesh
