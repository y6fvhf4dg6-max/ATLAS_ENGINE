from __future__ import annotations


class AtlasUrbanFabricQualityReport:
    VERSION = "0.1"

    @staticmethod
    def _safe_ratio(value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            return 0.0

        if value < 0.0:
            return 0.0

        if value > 1.0:
            return 1.0

        return value

    @classmethod
    def build(
        cls,
        *,
        scene_result,
    ):
        if not isinstance(
            scene_result,
            dict,
        ):
            raise TypeError(
                "scene_result must be a dict"
            )

        evidence = dict(
            scene_result.get(
                "scene_morphology_evidence",
                {},
            )
        )

        metrics = {
            "building_density": cls._safe_ratio(
                evidence.get(
                    "building_density",
                    0.0,
                )
            ),
            "road_density": cls._safe_ratio(
                evidence.get(
                    "road_density",
                    0.0,
                )
            ),
            "block_compactness": cls._safe_ratio(
                evidence.get(
                    "block_compactness",
                    0.0,
                )
            ),
            "vegetation_coverage": cls._safe_ratio(
                evidence.get(
                    "vegetation_coverage",
                    0.0,
                )
            ),
            "forest_coverage": cls._safe_ratio(
                evidence.get(
                    "forest_coverage",
                    0.0,
                )
            ),
            "water_coverage": cls._safe_ratio(
                evidence.get(
                    "water_coverage",
                    0.0,
                )
            ),
            "railway_presence": bool(
                evidence.get(
                    "railway_presence",
                    False,
                )
            ),
            "terrain_relief": cls._safe_ratio(
                evidence.get(
                    "terrain_relief",
                    0.0,
                )
            ),
            "landmark_density": cls._safe_ratio(
                evidence.get(
                    "landmark_density",
                    0.0,
                )
            ),
        }

        lod = scene_result.get(
            "city_composition_lod",
            {},
        )

        if not isinstance(
            lod,
            dict,
        ):
            lod = {}

        decisions = lod.get(
            "decisions",
            {},
        )

        if not isinstance(
            decisions,
            dict,
        ):
            decisions = {}

        decision_values = tuple(
            decisions.values()
        )

        decision_count = len(
            decision_values
        )

        retained_count = sum(
            1
            for decision in decision_values
            if isinstance(decision, dict)
            and decision.get("retain") is True
        )

        suppressed_count = sum(
            1
            for decision in decision_values
            if isinstance(decision, dict)
            and decision.get("retain") is False
        )

        simplified_count = sum(
            1
            for decision in decision_values
            if isinstance(decision, dict)
            and decision.get("simplify") is True
        )

        def ratio(count):
            if not decision_count:
                return 0.0

            return (
                count
                / decision_count
            )

        composition_lod_statistics = {
            "decision_count": decision_count,
            "retained_count": retained_count,
            "suppressed_count": suppressed_count,
            "simplified_count": simplified_count,
            "retained_ratio": ratio(
                retained_count
            ),
            "suppressed_ratio": ratio(
                suppressed_count
            ),
            "simplified_ratio": ratio(
                simplified_count
            ),
        }

        mesh_groups = scene_result.get(
            "mesh_groups",
            {},
        )

        if not isinstance(
            mesh_groups,
            dict,
        ):
            mesh_groups = {}

        vegetation_composition = scene_result.get(
            "vegetation_composition",
            {},
        )

        if not isinstance(
            vegetation_composition,
            dict,
        ):
            vegetation_composition = {}

        isolated_trees = tuple(
            vegetation_composition.get(
                "isolated_trees",
                (),
            )
            or ()
        )
        tree_rows = tuple(
            vegetation_composition.get(
                "tree_rows",
                (),
            )
            or ()
        )
        forest_canopies = tuple(
            vegetation_composition.get(
                "forest_canopies",
                (),
            )
            or ()
        )

        tree_row_member_count = int(
            vegetation_composition.get(
                "tree_row_member_count",
                0,
            )
            or 0
        )

        isolated_tree_count = len(
            isolated_trees
        )
        tree_row_count = len(
            tree_rows
        )
        forest_canopy_count = len(
            forest_canopies
        )

        vegetation_mode_total = (
            isolated_tree_count
            + tree_row_count
            + forest_canopy_count
        )

        def vegetation_ratio(count):
            if not vegetation_mode_total:
                return 0.0

            return (
                count
                / vegetation_mode_total
            )

        vegetation_composition_metrics = {
            "isolated_tree_count": (
                isolated_tree_count
            ),
            "tree_row_count": tree_row_count,
            "forest_canopy_count": (
                forest_canopy_count
            ),
            "tree_row_member_count": (
                tree_row_member_count
            ),
            "vegetation_mode_distribution": {
                "isolated_tree": vegetation_ratio(
                    isolated_tree_count
                ),
                "tree_row": vegetation_ratio(
                    tree_row_count
                ),
                "forest_canopy": vegetation_ratio(
                    forest_canopy_count
                ),
            },
            "isolated_tree_clutter_ratio": (
                vegetation_ratio(
                    isolated_tree_count
                )
            ),
        }

        building_height_resolutions = tuple(
            scene_result.get(
                "building_height_resolutions",
                (),
            )
            or ()
        )

        building_height_outlier_count = sum(
            1
            for resolution
            in building_height_resolutions
            if isinstance(
                resolution,
                dict,
            )
            and resolution.get(
                "is_statistical_outlier"
            ) is True
        )

        building_height_metrics = {
            "building_height_outlier_count": (
                building_height_outlier_count
            ),
        }

        composition_policy = scene_result.get(
            "morphology_composition_policy",
            {},
        )

        if not isinstance(
            composition_policy,
            dict,
        ):
            composition_policy = {}

        terrain_metrics = {
            "terrain_prominence_ratio": (
                cls._safe_ratio(
                    composition_policy.get(
                        "terrain_emphasis",
                        0.0,
                    )
                )
            ),
        }

        landmark_priorities = []
        background_priorities = []

        for decision in decision_values:
            if not isinstance(
                decision,
                dict,
            ):
                continue

            try:
                priority = float(
                    decision.get(
                        "narrative_priority"
                    )
                )
            except (
                TypeError,
                ValueError,
            ):
                continue

            semantic_class = str(
                decision.get(
                    "semantic_class",
                    "",
                )
            ).strip().lower()

            if semantic_class == "landmark":
                landmark_priorities.append(
                    priority
                )
            else:
                background_priorities.append(
                    priority
                )

        landmark_narrative_priority = (
            sum(landmark_priorities)
            / len(landmark_priorities)
            if landmark_priorities
            else 0.0
        )

        background_narrative_priority = (
            sum(background_priorities)
            / len(background_priorities)
            if background_priorities
            else 0.0
        )

        if background_narrative_priority > 0.0:
            landmark_to_background_ratio = (
                landmark_narrative_priority
                / background_narrative_priority
            )
        else:
            landmark_to_background_ratio = 0.0

        landmark_prominence_metrics = {
            "landmark_narrative_priority": (
                landmark_narrative_priority
            ),
            "background_narrative_priority": (
                background_narrative_priority
            ),
            "landmark_to_background_prominence_ratio": (
                landmark_to_background_ratio
            ),
        }

        bridge_records = tuple(
            scene_result.get(
                "bridge_urban_integration",
                (),
            )
            or ()
        )

        valid_bridge_records = tuple(
            record
            for record in bridge_records
            if isinstance(record, dict)
        )

        bridge_record_count = len(
            valid_bridge_records
        )

        continuous_bridge_count = sum(
            1
            for record in valid_bridge_records
            if record.get(
                "approach_road_continuity"
            ) is True
        )

        road_continuity_metrics = {
            "bridge_record_count": (
                bridge_record_count
            ),
            "continuous_bridge_count": (
                continuous_bridge_count
            ),
            "major_road_continuity_ratio": (
                continuous_bridge_count
                / bridge_record_count
                if bridge_record_count
                else 0.0
            ),
        }

        water_records = tuple(
            scene_result.get(
                "water_shoreline_composition",
                (),
            )
            or ()
        )

        valid_water_records = tuple(
            record
            for record in water_records
            if isinstance(record, dict)
        )

        composition_record_count = len(
            valid_water_records
        )

        continuous_surface_record_count = sum(
            1
            for record in valid_water_records
            if record.get(
                "supports_water_surface_continuity"
            ) is True
        )

        water_quality_metrics = {
            "composition_record_count": (
                composition_record_count
            ),
            "continuous_surface_record_count": (
                continuous_surface_record_count
            ),
            "water_completeness_ratio": (
                continuous_surface_record_count
                / composition_record_count
                if composition_record_count
                else 0.0
            ),
        }

        city_composition_scene = (
            scene_result.get(
                "city_composition_scene"
            )
        )

        road_semantic_classes = (
            "major_road",
            "local_road",
            "service_road",
            "pedestrian_path",
        )

        road_class_counts = {
            semantic_class: 0
            for semantic_class
            in road_semantic_classes
        }

        scene_elements = tuple(
            getattr(
                city_composition_scene,
                "elements",
                (),
            )
            or ()
        )

        for element in scene_elements:
            semantic_class = str(
                getattr(
                    element,
                    "semantic_class",
                    "",
                )
            ).strip().lower()

            if (
                semantic_class
                in road_class_counts
            ):
                road_class_counts[
                    semantic_class
                ] += 1

        road_element_count = sum(
            road_class_counts.values()
        )

        represented_road_classes = sum(
            1
            for count
            in road_class_counts.values()
            if count > 0
        )

        road_hierarchy_metrics = {
            "road_element_count": (
                road_element_count
            ),
            "major_road_count": (
                road_class_counts[
                    "major_road"
                ]
            ),
            "local_road_count": (
                road_class_counts[
                    "local_road"
                ]
            ),
            "service_road_count": (
                road_class_counts[
                    "service_road"
                ]
            ),
            "pedestrian_path_count": (
                road_class_counts[
                    "pedestrian_path"
                ]
            ),
            "road_hierarchy_class_count": (
                represented_road_classes
            ),
            "road_hierarchy_coverage_ratio": (
                represented_road_classes
                / len(
                    road_semantic_classes
                )
            ),
        }

        park_meshes = tuple(
            mesh_groups.get(
                "parks",
                (),
            )
            or ()
        )

        eligible_surface_count = len(
            park_meshes
        )

        textured_surface_count = sum(
            1
            for mesh in park_meshes
            if isinstance(mesh, dict)
            and isinstance(
                mesh.get(
                    "semantic_surface_texture"
                ),
                dict,
            )
        )

        semantic_surface_metrics = {
            "eligible_surface_count": (
                eligible_surface_count
            ),
            "textured_surface_count": (
                textured_surface_count
            ),
            "semantic_surface_coverage_ratio": (
                textured_surface_count
                / eligible_surface_count
                if eligible_surface_count
                else 0.0
            ),
        }

        forest_canopy_meshes = tuple(
            mesh_groups.get(
                "forest_canopies",
                (),
            )
            or ()
        )

        forest_continuity_metrics = {
            "forest_canopy_mesh_count": (
                len(
                    forest_canopy_meshes
                )
            ),
            "forest_canopy_present": bool(
                forest_canopy_meshes
            ),
        }

        issues = []

        def add_issue(
            *,
            code,
            severity,
            category,
            message,
        ):
            issues.append(
                {
                    "code": code,
                    "severity": severity,
                    "category": category,
                    "message": message,
                }
            )

        if not mesh_groups.get("parks"):
            add_issue(
                code="missing_park_content",
                severity="warning",
                category="missing_semantic_content",
                message=(
                    "No park semantic content is "
                    "present in the scene."
                ),
            )

        if not mesh_groups.get("waters"):
            add_issue(
                code="missing_water_content",
                severity="warning",
                category="missing_semantic_content",
                message=(
                    "No water semantic content is "
                    "present in the scene."
                ),
            )

        if not mesh_groups.get("railways"):
            add_issue(
                code="missing_railway_content",
                severity="warning",
                category="missing_semantic_content",
                message=(
                    "No railway semantic content is "
                    "present in the scene."
                ),
            )

        if (
            mesh_groups.get("roads")
            and metrics["road_density"] < 0.05
        ):
            add_issue(
                code="weak_road_presence",
                severity="warning",
                category="visually_weak_content",
                message=(
                    "Road content is present but "
                    "measured road density is weak."
                ),
            )

        vegetation_present = bool(
            mesh_groups.get("parks")
            or mesh_groups.get("trees")
            or mesh_groups.get(
                "forest_canopies"
            )
        )

        if (
            vegetation_present
            and metrics[
                "vegetation_coverage"
            ] < 0.05
        ):
            add_issue(
                code="weak_vegetation_presence",
                severity="warning",
                category="visually_weak_content",
                message=(
                    "Vegetation content is present "
                    "but measured coverage is weak."
                ),
            )

        if (
            bridge_record_count
            and road_continuity_metrics[
                "major_road_continuity_ratio"
            ] < 0.50
        ):
            add_issue(
                code="weak_major_road_continuity",
                severity="warning",
                category="visually_weak_content",
                message=(
                    "Bridge integration is present "
                    "but approach-road continuity is weak."
                ),
            )

        if (
            composition_record_count
            and water_quality_metrics[
                "water_completeness_ratio"
            ] < 0.50
        ):
            add_issue(
                code="weak_water_surface_continuity",
                severity="warning",
                category="visually_weak_content",
                message=(
                    "Water composition is present "
                    "but surface continuity is weak."
                ),
            )

        return {
            "type": (
                "urban_fabric_quality_report"
            ),
            "version": cls.VERSION,
            "metrics": metrics,
            "composition_lod_statistics": (
                composition_lod_statistics
            ),
            "vegetation_composition_metrics": (
                vegetation_composition_metrics
            ),
            "building_height_metrics": (
                building_height_metrics
            ),
            "terrain_metrics": terrain_metrics,
            "landmark_prominence_metrics": (
                landmark_prominence_metrics
            ),
            "road_continuity_metrics": (
                road_continuity_metrics
            ),
            "water_quality_metrics": (
                water_quality_metrics
            ),
            "road_hierarchy_metrics": (
                road_hierarchy_metrics
            ),
            "semantic_surface_metrics": (
                semantic_surface_metrics
            ),
            "forest_continuity_metrics": (
                forest_continuity_metrics
            ),
            "issues": tuple(issues),
        }
