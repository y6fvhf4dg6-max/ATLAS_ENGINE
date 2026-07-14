"""
ATLAS Input Quality Report v0.1

Ham OSM ve terrain girdileri için ölçülebilir kalite
metriklerini tek raporda toplar.
"""

from CORE.atlas_polygon_validator import (
    AtlasPolygonValidator,
)
from CORE.atlas_geometry_simplifier import (
    AtlasGeometrySimplifier,
)


class AtlasInputQualityReport:
    VERSION = "0.1"

    @staticmethod
    def build(
        buildings=None,
        castles=None,
        castle_geometry=None,
        terrain_grid=None,
        castle_focus_result=None,
    ):
        buildings = buildings or []
        castles = castles or []
        castle_geometry = castle_geometry or {}
        terrain_grid = terrain_grid or {}
        castle_focus_result = castle_focus_result or {}

        main_buildings = []
        building_parts = []

        for building in buildings:
            tags = building.get(
                "tags",
                {},
            )

            if tags.get("building") is not None:
                main_buildings.append(building)

            if tags.get("building:part") is not None:
                building_parts.append(building)

        geometry_records = list(buildings) + list(castles)

        issue_counts = {
            "valid": 0,
            "not_enough_points": 0,
            "duplicate_points": 0,
            "zero_area": 0,
            "self_intersection": 0,
        }

        for record in geometry_records:
            geometry = record.get(
                "geometry",
                [],
            )

            issue_name = (
                AtlasInputQualityReport._classify_geometry_issue(
                    geometry
                )
            )

            issue_counts[issue_name] += 1

        valid_geometry_count = issue_counts["valid"]

        total_geometry_count = len(geometry_records)
        invalid_geometry_count = (
            total_geometry_count
            - valid_geometry_count
        )

        valid_percent = (
            valid_geometry_count
            / total_geometry_count
            * 100.0
            if total_geometry_count
            else 100.0
        )

        building_count = len(main_buildings)
        building_part_count = len(building_parts)

        height_count = sum(
            1
            for building in main_buildings
            if AtlasInputQualityReport._has_height(
                building
            )
        )

        roof_count = sum(
            1
            for building in main_buildings
            if AtlasInputQualityReport._has_roof(
                building
            )
        )

        semantic_issue_counts = {
            "invalid_height": 0,
            "non_positive_height": 0,
            "invalid_levels": 0,
            "non_positive_levels": 0,
            "unknown_roof_shape": 0,
            "complex_roof_shape": 0,
            "conflicting_height_values": 0,
            "conflicting_roof_shapes": 0,
            "relation_missing_outer_geometry": 0,
            "way_has_inner_geometry": 0,
            "unsupported_castle_geometry_type": 0,
            "missing_castle_tag": 0,
        }

        semantic_issue_records = {
            issue_name: []
            for issue_name in semantic_issue_counts
        }

        for building in main_buildings:
            building_issues = (
                AtlasInputQualityReport
                ._classify_building_semantic_issues(
                    building
                )
            )

            for issue_name in building_issues:
                semantic_issue_counts[issue_name] += 1

                semantic_issue_records[
                    issue_name
                ].append(
                    AtlasInputQualityReport
                    ._build_semantic_issue_record(
                        record_type="building",
                        record=building,
                        issue_name=issue_name,
                    )
                )

        for castle in castles:
            castle_issues = (
                AtlasInputQualityReport
                ._classify_castle_semantic_issues(
                    castle
                )
            )

            for issue_name in castle_issues:
                semantic_issue_counts[issue_name] += 1

                semantic_issue_records[
                    issue_name
                ].append(
                    AtlasInputQualityReport
                    ._build_semantic_issue_record(
                        record_type="castle",
                        record=castle,
                        issue_name=issue_name,
                    )
                )

        semantic_issue_severity = {
            "complex_roof_shape": "INFO",
            "invalid_height": "WARN",
            "non_positive_height": "WARN",
            "invalid_levels": "WARN",
            "non_positive_levels": "WARN",
            "unknown_roof_shape": "WARN",
            "conflicting_height_values": "WARN",
            "conflicting_roof_shapes": "WARN",
            "missing_castle_tag": "WARN",
            "relation_missing_outer_geometry": "FAIL",
            "way_has_inner_geometry": "FAIL",
            "unsupported_castle_geometry_type": "FAIL",
        }

        semantic_severity_issues = {
            "INFO": {},
            "WARN": {},
            "FAIL": {},
        }

        for issue_name, issue_count in (
            semantic_issue_counts.items()
        ):
            issue_count = int(issue_count or 0)

            if issue_count <= 0:
                continue

            severity = semantic_issue_severity[
                issue_name
            ]

            semantic_severity_issues[
                severity
            ][issue_name] = issue_count

        semantic_severity_counts = {
            severity: sum(
                issue_counts_by_name.values()
            )
            for severity, issue_counts_by_name
            in semantic_severity_issues.items()
        }

        height_coverage_percent = (
            height_count
            / building_count
            * 100.0
            if building_count
            else 100.0
        )

        roof_coverage_percent = (
            roof_count
            / building_count
            * 100.0
            if building_count
            else 100.0
        )

        unknown_castles = castle_geometry.get(
            "unknown_castles",
            [],
        )

        inferred_perimeter_walls = castle_geometry.get(
            "inferred_perimeter_walls",
            [],
        )

        sample_count = int(
            terrain_grid.get(
                "sample_count",
                0,
            )
            or 0
        )

        missing_sample_count = int(
            terrain_grid.get(
                "missing_sample_count",
                0,
            )
            or 0
        )

        coverage_percent = (
            max(
                0.0,
                min(
                    100.0,
                    (
                        sample_count
                        - missing_sample_count
                    )
                    / sample_count
                    * 100.0,
                ),
            )
            if sample_count
            else 0.0
        )

        inferred_perimeter_wall_count = len(
            inferred_perimeter_walls
        )

        castle_focus_fallback_used = bool(
            castle_focus_result.get(
                "used_fallback",
                False,
            )
        )

        automatic_correction_count = (
            missing_sample_count
            + inferred_perimeter_wall_count
            + int(castle_focus_fallback_used)
        )

        return {
            "version": AtlasInputQualityReport.VERSION,
            "geometry": {
                "total_count": total_geometry_count,
                "valid_count": valid_geometry_count,
                "invalid_count": invalid_geometry_count,
                "valid_percent": valid_percent,
                "issue_counts": issue_counts,
            },
            "semantics": {
                "building_count": building_count,
                "building_part_count": building_part_count,
                "height_count": height_count,
                "roof_count": roof_count,
                "height_coverage_percent": (
                    height_coverage_percent
                ),
                "roof_coverage_percent": (
                    roof_coverage_percent
                ),
                "castle_count": len(castles),
                "unknown_castle_count": len(
                    unknown_castles
                ),
                "issue_counts": semantic_issue_counts,
                "issue_records": semantic_issue_records,
                "severity_counts": (
                    semantic_severity_counts
                ),
                "severity_issues": (
                    semantic_severity_issues
                ),
            },
            "terrain": {
                "sample_count": sample_count,
                "missing_sample_count": (
                    missing_sample_count
                ),
                "coverage_percent": coverage_percent,
            },
            "automatic_corrections": {
                "terrain_missing_samples_filled": (
                    missing_sample_count
                ),
                "inferred_perimeter_walls": (
                    inferred_perimeter_wall_count
                ),
                "castle_focus_fallback_used": (
                    castle_focus_fallback_used
                ),
                "total_count": automatic_correction_count,
            },
        }

    @staticmethod
    def evaluate_policy(report):
        geometry = report.get(
            "geometry",
            {},
        )

        semantics = report.get(
            "semantics",
            {},
        )

        terrain = report.get(
            "terrain",
            {},
        )

        valid_percent = float(
            geometry.get(
                "valid_percent",
                0.0,
            )
            or 0.0
        )

        terrain_coverage_percent = float(
            terrain.get(
                "coverage_percent",
                0.0,
            )
            or 0.0
        )

        unknown_castle_count = int(
            semantics.get(
                "unknown_castle_count",
                0,
            )
            or 0
        )

        building_count = int(
            semantics.get(
                "building_count",
                0,
            )
            or 0
        )

        height_coverage_percent = float(
            semantics.get(
                "height_coverage_percent",
                100.0,
            )
            or 0.0
        )

        roof_coverage_percent = float(
            semantics.get(
                "roof_coverage_percent",
                100.0,
            )
            or 0.0
        )

        semantic_issues = semantics.get(
            "issue_counts",
            {},
        ) or {}

        relation_missing_outer_count = int(
            semantic_issues.get(
                "relation_missing_outer_geometry",
                0,
            )
            or 0
        )

        way_has_inner_count = int(
            semantic_issues.get(
                "way_has_inner_geometry",
                0,
            )
            or 0
        )

        unsupported_castle_geometry_count = int(
            semantic_issues.get(
                "unsupported_castle_geometry_type",
                0,
            )
            or 0
        )

        missing_castle_tag_count = int(
            semantic_issues.get(
                "missing_castle_tag",
                0,
            )
            or 0
        )

        invalid_height_count = int(
            semantic_issues.get(
                "invalid_height",
                0,
            )
            or 0
        )

        non_positive_height_count = int(
            semantic_issues.get(
                "non_positive_height",
                0,
            )
            or 0
        )

        invalid_levels_count = int(
            semantic_issues.get(
                "invalid_levels",
                0,
            )
            or 0
        )

        non_positive_levels_count = int(
            semantic_issues.get(
                "non_positive_levels",
                0,
            )
            or 0
        )

        unknown_roof_shape_count = int(
            semantic_issues.get(
                "unknown_roof_shape",
                0,
            )
            or 0
        )

        conflicting_height_values_count = int(
            semantic_issues.get(
                "conflicting_height_values",
                0,
            )
            or 0
        )

        conflicting_roof_shapes_count = int(
            semantic_issues.get(
                "conflicting_roof_shapes",
                0,
            )
            or 0
        )

        reasons = []

        if valid_percent < 70.0:
            reasons.append(
                "geometry_valid_percent_below_70"
            )

        if terrain_coverage_percent < 80.0:
            reasons.append(
                "terrain_coverage_percent_below_80"
            )

        if relation_missing_outer_count > 0:
            reasons.append(
                "castle_relation_missing_outer_geometry"
            )

        if way_has_inner_count > 0:
            reasons.append(
                "castle_way_has_inner_geometry"
            )

        if unsupported_castle_geometry_count > 0:
            reasons.append(
                "unsupported_castle_geometry_type_present"
            )

        if reasons:
            return {
                "risk_level": "HIGH",
                "action": "FAIL",
                "reasons": reasons,
            }

        if valid_percent < 90.0:
            reasons.append(
                "geometry_valid_percent_below_90"
            )

        if terrain_coverage_percent < 95.0:
            reasons.append(
                "terrain_coverage_percent_below_95"
            )

        if unknown_castle_count > 0:
            reasons.append(
                "unknown_castle_records_present"
            )

        if (
            building_count > 0
            and height_coverage_percent < 25.0
        ):
            reasons.append(
                "building_height_coverage_below_25"
            )

        if (
            building_count > 0
            and roof_coverage_percent < 10.0
        ):
            reasons.append(
                "building_roof_coverage_below_10"
            )

        if invalid_height_count > 0:
            reasons.append(
                "invalid_building_height_present"
            )

        if non_positive_height_count > 0:
            reasons.append(
                "non_positive_building_height_present"
            )

        if invalid_levels_count > 0:
            reasons.append(
                "invalid_building_levels_present"
            )

        if non_positive_levels_count > 0:
            reasons.append(
                "non_positive_building_levels_present"
            )

        if unknown_roof_shape_count > 0:
            reasons.append(
                "unknown_building_roof_shape_present"
            )

        if conflicting_height_values_count > 0:
            reasons.append(
                "conflicting_building_height_values_present"
            )

        if conflicting_roof_shapes_count > 0:
            reasons.append(
                "conflicting_building_roof_shapes_present"
            )

        if missing_castle_tag_count > 0:
            reasons.append(
                "castle_record_missing_tag"
            )

        if reasons:
            return {
                "risk_level": "MEDIUM",
                "action": "WARN",
                "reasons": reasons,
            }

        return {
            "risk_level": "LOW",
            "action": "CONTINUE",
            "reasons": [],
        }

    @staticmethod
    def _classify_geometry_issue(geometry):
        if not AtlasPolygonValidator.has_enough_points(
            geometry
        ):
            return "not_enough_points"

        if AtlasPolygonValidator.has_duplicate_points(
            geometry
        ):
            return "duplicate_points"

        if AtlasGeometrySimplifier.has_self_intersection(
            geometry
        ):
            return "self_intersection"

        if not AtlasPolygonValidator.has_valid_area(
            geometry
        ):
            return "zero_area"

        return "valid"

    @staticmethod
    def add_shell_corrections(
        report,
        shell_meshes,
    ):
        corrections = report.setdefault(
            "automatic_corrections",
            {},
        )

        corrected_role_count = sum(
            1
            for mesh in (shell_meshes or [])
            if mesh.get("roles_corrected") is True
        )

        previous_count = int(
            corrections.get(
                "castle_relation_roles_corrected",
                0,
            )
            or 0
        )

        total_count = int(
            corrections.get(
                "total_count",
                0,
            )
            or 0
        )

        corrections[
            "castle_relation_roles_corrected"
        ] = corrected_role_count

        corrections["total_count"] = (
            total_count
            - previous_count
            + corrected_role_count
        )

    @staticmethod
    def enforce_policy(
        policy,
        strict=False,
    ):
        if not strict:
            return None

        action = str(
            policy.get(
                "action",
                "",
            )
        ).upper()

        if action != "FAIL":
            return None

        reasons = policy.get(
            "reasons",
            [],
        )

        reason_text = (
            ", ".join(str(reason) for reason in reasons)
            if reasons
            else "unspecified"
        )

        raise RuntimeError(
            "Input quality policy failed: "
            f"{reason_text}"
        )

    @staticmethod
    def _build_semantic_issue_record(
        record_type,
        record,
        issue_name,
    ):
        tags = record.get(
            "tags",
            {},
        )

        field_name = None
        value = None

        if issue_name in (
            "invalid_height",
            "non_positive_height",
        ):
            field_name = "height"
            value = (
                record.get("height")
                if record.get("height") is not None
                else tags.get("height")
            )

        elif issue_name in (
            "invalid_levels",
            "non_positive_levels",
        ):
            field_name = "building:levels"
            value = tags.get("building:levels")

        elif issue_name in (
            "unknown_roof_shape",
            "complex_roof_shape",
        ):
            if record.get("roof_type") is not None:
                field_name = "roof_type"
                value = record.get("roof_type")
            elif tags.get("roof:shape") is not None:
                field_name = "roof:shape"
                value = tags.get("roof:shape")
            else:
                field_name = "roof:type"
                value = tags.get("roof:type")

        elif issue_name == "conflicting_height_values":
            field_name = "height"
            value = {
                "direct": record.get("height"),
                "tag": tags.get("height"),
            }

        elif issue_name == "conflicting_roof_shapes":
            field_name = "roof"
            value = {
                "direct": record.get("roof_type"),
                "tag": (
                    tags.get("roof:shape")
                    or tags.get("roof:type")
                ),
            }

        elif issue_name == "relation_missing_outer_geometry":
            field_name = "outer_geometries"
            value = record.get("outer_geometries")

        elif issue_name == "way_has_inner_geometry":
            field_name = "inner_geometries"
            value = record.get("inner_geometries")

        elif issue_name == "unsupported_castle_geometry_type":
            field_name = "geometry_type"
            value = record.get("geometry_type")

        elif issue_name == "missing_castle_tag":
            field_name = "historic/building"
            value = None

        return {
            "record_type": record_type,
            "id": record.get("id"),
            "field": field_name,
            "value": value,
        }

    @staticmethod
    def _classify_castle_semantic_issues(
        castle,
    ):
        issues = []

        tags = castle.get(
            "tags",
            {},
        )

        geometry_type = castle.get(
            "geometry_type"
        )

        outer_geometries = castle.get(
            "outer_geometries",
            [],
        ) or []

        inner_geometries = castle.get(
            "inner_geometries",
            [],
        ) or []

        is_castle_tagged = (
            tags.get("historic") == "castle"
            or tags.get("building") == "castle"
        )

        if not is_castle_tagged:
            issues.append("missing_castle_tag")

        if geometry_type not in (
            "way",
            "relation",
        ):
            issues.append(
                "unsupported_castle_geometry_type"
            )

        if (
            geometry_type == "relation"
            and not outer_geometries
        ):
            issues.append(
                "relation_missing_outer_geometry"
            )

        if (
            geometry_type == "way"
            and inner_geometries
        ):
            issues.append(
                "way_has_inner_geometry"
            )

        return issues

    @staticmethod
    def _classify_building_semantic_issues(
        building,
    ):
        tags = building.get(
            "tags",
            {},
        )

        issues = []

        direct_height = building.get("height")
        tagged_height = tags.get("height")

        if (
            direct_height is not None
            and tagged_height is not None
        ):
            parsed_direct_height = (
                AtlasInputQualityReport._parse_numeric_value(
                    direct_height,
                    remove_meter_suffix=True,
                )
            )

            parsed_tagged_height = (
                AtlasInputQualityReport._parse_numeric_value(
                    tagged_height,
                    remove_meter_suffix=True,
                )
            )

            if (
                parsed_direct_height is not None
                and parsed_tagged_height is not None
                and abs(
                    parsed_direct_height
                    - parsed_tagged_height
                ) > 1e-9
            ):
                issues.append(
                    "conflicting_height_values"
                )

        height_value = (
            direct_height
            if direct_height is not None
            else tagged_height
        )

        if height_value is not None:
            parsed_height = (
                AtlasInputQualityReport._parse_numeric_value(
                    height_value,
                    remove_meter_suffix=True,
                )
            )

            if parsed_height is None:
                issues.append("invalid_height")
            elif parsed_height <= 0.0:
                issues.append("non_positive_height")

        levels_value = tags.get("building:levels")

        if levels_value is not None:
            parsed_levels = (
                AtlasInputQualityReport._parse_numeric_value(
                    levels_value,
                )
            )

            if parsed_levels is None:
                issues.append("invalid_levels")
            elif parsed_levels <= 0.0:
                issues.append("non_positive_levels")

        direct_roof_type = building.get("roof_type")

        tagged_roof_shape = (
            tags.get("roof:shape")
            or tags.get("roof:type")
        )

        if (
            direct_roof_type is not None
            and tagged_roof_shape is not None
        ):
            normalized_direct_roof = str(
                direct_roof_type
            ).strip().lower()

            normalized_tagged_roof = str(
                tagged_roof_shape
            ).strip().lower()

            if (
                normalized_direct_roof
                != normalized_tagged_roof
            ):
                issues.append(
                    "conflicting_roof_shapes"
                )

        roof_shape = (
            direct_roof_type
            if direct_roof_type is not None
            else tagged_roof_shape
        )

        if roof_shape is not None:
            normalized_roof_shape = str(
                roof_shape
            ).strip().lower()

            if normalized_roof_shape == "many":
                issues.append(
                    "complex_roof_shape"
                )
            elif not AtlasInputQualityReport._is_known_roof_shape(
                normalized_roof_shape
            ):
                issues.append("unknown_roof_shape")

        return issues

    @staticmethod
    def _parse_numeric_value(
        value,
        remove_meter_suffix=False,
    ):
        value_text = str(value).strip().lower()

        if remove_meter_suffix:
            value_text = value_text.removesuffix(
                "m"
            ).strip()

        try:
            return float(value_text)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _is_positive_numeric_value(
        value,
        remove_meter_suffix=False,
    ):
        if value is None:
            return False

        parsed_value = (
            AtlasInputQualityReport._parse_numeric_value(
                value,
                remove_meter_suffix=remove_meter_suffix,
            )
        )

        return (
            parsed_value is not None
            and parsed_value > 0.0
        )

    @staticmethod
    def _is_known_roof_shape(value):
        if value is None:
            return False

        normalized_value = str(
            value
        ).strip().lower()

        known_roof_shapes = {
            "flat",
            "pitched",
            "gable",
            "gabled",
            "hipped",
            "half-hipped",
            "pyramidal",
            "skillion",
            "gambrel",
            "mansard",
            "dome",
            "onion",
            "round",
            "cone",
            "many",
            "saltbox",
        }

        return normalized_value in known_roof_shapes

    @staticmethod
    def _has_height(building):
        if AtlasInputQualityReport._is_positive_numeric_value(
            building.get("height"),
            remove_meter_suffix=True,
        ):
            return True

        tags = building.get(
            "tags",
            {},
        )

        if AtlasInputQualityReport._is_positive_numeric_value(
            tags.get("height"),
            remove_meter_suffix=True,
        ):
            return True

        return AtlasInputQualityReport._is_positive_numeric_value(
            tags.get("building:levels")
        )

    @staticmethod
    def _has_roof(building):
        if AtlasInputQualityReport._is_known_roof_shape(
            building.get("roof_type")
        ):
            return True

        tags = building.get(
            "tags",
            {},
        )

        roof_shape = (
            tags.get("roof:shape")
            or tags.get("roof:type")
        )

        return AtlasInputQualityReport._is_known_roof_shape(
            roof_shape
        )
