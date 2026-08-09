from __future__ import annotations

import math

from CORE.atlas_lod_level_catalog import (
    AtlasLoDLevel,
)


class AtlasCityCompositionLoDResolver:
    ALWAYS_RETAIN = frozenset(
        {
            "landmark",
            "major_road",
            "railway",
            "light_rail",
            "tram",
            "park",
            "water",
        }
    )

    SIMPLIFIABLE = frozenset(
        {
            "generic_building",
            "urban_block",
            "tree_row",
            "vegetation",
            "isolated_building",
        }
    )

    MINOR = frozenset(
        {
            "minor_path",
            "pedestrian_path",
            "service_road",
        }
    )

    @classmethod
    def resolve_semantic_narrative_priority(
        cls,
        semantic_class,
    ) -> float:
        semantic_class = cls._normalize_identifier(
            semantic_class,
            field_name="semantic_class",
        )

        priorities = {
            "landmark": 1.00,
            "major_road": 0.90,
            "railway": 0.88,
            "light_rail": 0.85,
            "tram": 0.82,
            "water": 0.80,
            "park": 0.75,
            "plaza": 0.72,
            "infrastructure_corridor": 0.68,
            "urban_block": 0.55,
            "generic_building": 0.40,
            "isolated_building": 0.38,
            "tree_row": 0.35,
            "vegetation": 0.30,
            "service_road": 0.25,
            "pedestrian_path": 0.20,
            "minor_path": 0.15,
        }

        return priorities.get(
            semantic_class,
            0.30,
        )

    @staticmethod
    def _normalize_identifier(value, *, field_name):
        normalized = "_".join(
            str(value).strip().lower().split()
        )

        if not normalized:
            raise ValueError(
                f"{field_name} must not be blank"
            )

        return normalized

    @staticmethod
    def _priority(value):
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                "product_priority must be numeric"
            ) from exc

        if (
            not math.isfinite(value)
            or not 0.0 <= value <= 1.0
        ):
            raise ValueError(
                "product_priority must be finite "
                "and within 0..1"
            )

        return value

    @staticmethod
    def _positive(value, *, field_name):
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

    @classmethod
    def resolve(
        cls,
        *,
        semantic_class,
        product_priority,
        product_size_mm,
        scene_morphology,
        landmark_proximity_m,
        printable,
        lod_level,
    ):
        semantic_class = cls._normalize_identifier(
            semantic_class,
            field_name="semantic_class",
        )
        scene_morphology = cls._normalize_identifier(
            scene_morphology,
            field_name="scene_morphology",
        )
        product_priority = cls._priority(
            product_priority
        )
        product_size_mm = cls._positive(
            product_size_mm,
            field_name="product_size_mm",
        )
        landmark_proximity_m = cls._positive(
            landmark_proximity_m,
            field_name="landmark_proximity_m",
        )

        if not isinstance(printable, bool):
            raise TypeError(
                "printable must be bool"
            )

        if not isinstance(
            lod_level,
            AtlasLoDLevel,
        ):
            raise TypeError(
                "lod_level must be an AtlasLoDLevel"
            )

        retain = True
        simplify = False
        reason = "retained"

        if (
            semantic_class in cls.MINOR
            and not printable
        ):
            retain = False
            reason = "suppressed_minor_unprintable"

        elif (
            semantic_class == "minor_path"
            and lod_level.level <= 1
        ):
            retain = False
            reason = "suppressed_minor_lod"

        elif (
            semantic_class == "pedestrian_path"
            and product_size_mm < 120.0
            and lod_level.level <= 1
        ):
            retain = False
            reason = "suppressed_minor_product_scale"

        elif semantic_class in cls.SIMPLIFIABLE:
            if semantic_class == "vegetation":
                simplify = (
                    scene_morphology == "dense_urban"
                    and lod_level.level <= 2
                )
            else:
                simplify = lod_level.level <= 2

            reason = (
                "retained_simplified"
                if simplify
                else "retained"
            )

        if semantic_class in cls.ALWAYS_RETAIN:
            retain = True
            simplify = False
            reason = "retained_primary_structure"

        narrative_priority = max(
            product_priority,
            cls.resolve_semantic_narrative_priority(
                semantic_class
            ),
        )

        if semantic_class == "landmark":
            narrative_priority = 1.0

        elif (
            landmark_proximity_m <= 25.0
            and retain
        ):
            narrative_priority = min(
                1.0,
                narrative_priority + 0.10,
            )

        representation_mode = "source_detail"

        if not retain:
            representation_mode = "suppressed"

        elif (
            semantic_class == "tree_row"
            and simplify
        ):
            representation_mode = "generalized_row"

        elif (
            semantic_class == "vegetation"
            and simplify
        ):
            representation_mode = "canopy_or_cluster"

        elif (
            semantic_class in {
                "generic_building",
                "urban_block",
                "isolated_building",
            }
            and simplify
        ):
            representation_mode = "simplified_mass"

        return {
            "semantic_class": semantic_class,
            "scene_morphology": scene_morphology,
            "product_size_mm": product_size_mm,
            "landmark_proximity_m": (
                landmark_proximity_m
            ),
            "printable": printable,
            "lod_level": lod_level,
            "retain": retain,
            "simplify": simplify,
            "narrative_priority": (
                narrative_priority
            ),
            "reason": reason,
            "representation_mode": (
                representation_mode
            ),
        }

    @classmethod
    def resolve_from_lod_result(
        cls,
        *,
        semantic_class,
        product_priority,
        scene_morphology,
        landmark_proximity_m,
        printable,
        lod_result,
    ):
        from CORE.atlas_lod_resolution_contract import (
            AtlasLoDResolutionResult,
        )

        if not isinstance(
            lod_result,
            AtlasLoDResolutionResult,
        ):
            raise TypeError(
                "lod_result must be an "
                "AtlasLoDResolutionResult"
            )

        return cls.resolve(
            semantic_class=semantic_class,
            product_priority=product_priority,
            product_size_mm=(
                lod_result.source.product_size_mm
            ),
            scene_morphology=scene_morphology,
            landmark_proximity_m=(
                landmark_proximity_m
            ),
            printable=printable,
            lod_level=lod_result.level,
        )

    @classmethod
    def resolve_urban_block_profile(
        cls,
        *,
        profile,
        product_size_mm,
        scene_morphology,
        printable,
    ):
        from CORE.atlas_urban_block_resolver import (
            AtlasUrbanBlockProfile,
        )

        if not isinstance(
            profile,
            AtlasUrbanBlockProfile,
        ):
            raise TypeError(
                "profile must be an AtlasUrbanBlockProfile"
            )

        lod_level = profile.composition_lod_level

        if lod_level is None:
            raise ValueError(
                "profile.composition_lod_level is required"
            )

        nearest_landmark_distance = (
            profile.nearest_landmark_distance
        )

        if nearest_landmark_distance is None:
            nearest_landmark_distance = 1_000_000.0

        density_priority = min(
            0.70,
            max(
                0.30,
                0.30 + (
                    profile.density_ratio * 0.40
                ),
            ),
        )

        return cls.resolve(
            semantic_class="urban_block",
            product_priority=density_priority,
            product_size_mm=product_size_mm,
            scene_morphology=scene_morphology,
            landmark_proximity_m=(
                nearest_landmark_distance
            ),
            printable=printable,
            lod_level=lod_level,
        )

    @classmethod
    def resolve_urban_fabric_scene(
        cls,
        *,
        scene,
        product_size_mm,
        scene_morphology,
        lod_level,
        printability_by_element_id=None,
        landmark_proximity_by_element_id=None,
    ):
        from CORE.atlas_urban_fabric_scene_contract import (
            AtlasUrbanFabricScene,
        )

        if not isinstance(
            scene,
            AtlasUrbanFabricScene,
        ):
            raise TypeError(
                "scene must be an AtlasUrbanFabricScene"
            )

        result = cls.resolve_scene(
            elements=scene.elements,
            product_size_mm=product_size_mm,
            scene_morphology=scene_morphology,
            lod_level=lod_level,
            printability_by_element_id=(
                printability_by_element_id
            ),
            landmark_proximity_by_element_id=(
                landmark_proximity_by_element_id
            ),
        )

        return {
            **result,
            "scene": scene,
        }

    @classmethod
    def resolve_scene(
        cls,
        *,
        elements,
        product_size_mm,
        scene_morphology,
        lod_level,
        printability_by_element_id=None,
        landmark_proximity_by_element_id=None,
    ):
        from CORE.atlas_urban_fabric_scene_contract import (
            AtlasUrbanFabricElement,
        )

        elements = tuple(elements or ())
        printability_by_element_id = dict(
            printability_by_element_id or {}
        )
        landmark_proximity_by_element_id = dict(
            landmark_proximity_by_element_id or {}
        )

        decisions = {}
        retained_element_ids = []
        suppressed_element_ids = []
        simplified_element_ids = []

        for element in elements:
            if not isinstance(
                element,
                AtlasUrbanFabricElement,
            ):
                raise TypeError(
                    "elements must contain "
                    "AtlasUrbanFabricElement values"
                )

            element_id = element.element_id

            if not element.lod_eligible:
                decision = {
                    "semantic_class": (
                        element.semantic_class
                    ),
                    "scene_morphology": (
                        cls._normalize_identifier(
                            scene_morphology,
                            field_name=(
                                "scene_morphology"
                            ),
                        )
                    ),
                    "product_size_mm": cls._positive(
                        product_size_mm,
                        field_name="product_size_mm",
                    ),
                    "landmark_proximity_m": (
                        cls._positive(
                            landmark_proximity_by_element_id
                            .get(
                                element_id,
                                0.0,
                            ),
                            field_name=(
                                "landmark_proximity_m"
                            ),
                        )
                    ),
                    "printable": bool(
                        printability_by_element_id.get(
                            element_id,
                            True,
                        )
                    ),
                    "lod_level": lod_level,
                    "retain": True,
                    "simplify": False,
                    "narrative_priority": (
                        element.product_priority
                    ),
                    "reason": (
                        "lod_ineligible_preserved"
                    ),
                }
            else:
                decision = cls.resolve(
                    semantic_class=(
                        element.semantic_class
                    ),
                    product_priority=(
                        element.product_priority
                    ),
                    product_size_mm=(
                        product_size_mm
                    ),
                    scene_morphology=(
                        scene_morphology
                    ),
                    landmark_proximity_m=(
                        landmark_proximity_by_element_id
                        .get(
                            element_id,
                            0.0,
                        )
                    ),
                    printable=(
                        printability_by_element_id
                        .get(
                            element_id,
                            True,
                        )
                    ),
                    lod_level=lod_level,
                )

            decisions[element_id] = decision

            if decision["retain"]:
                retained_element_ids.append(
                    element_id
                )
            else:
                suppressed_element_ids.append(
                    element_id
                )

            if decision["simplify"]:
                simplified_element_ids.append(
                    element_id
                )

        return {
            "lod_level": lod_level,
            "scene_morphology": (
                cls._normalize_identifier(
                    scene_morphology,
                    field_name="scene_morphology",
                )
            ),
            "product_size_mm": cls._positive(
                product_size_mm,
                field_name="product_size_mm",
            ),
            "decisions": decisions,
            "retained_element_ids": tuple(
                retained_element_ids
            ),
            "suppressed_element_ids": tuple(
                suppressed_element_ids
            ),
            "simplified_element_ids": tuple(
                simplified_element_ids
            ),
        }
