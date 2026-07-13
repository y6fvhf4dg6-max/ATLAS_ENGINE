"""
ATLAS Input Quality Report v0.1

Ham OSM ve terrain girdileri için ölçülebilir kalite
metriklerini tek raporda toplar.
"""

from CORE.atlas_polygon_validator import (
    AtlasPolygonValidator,
)


class AtlasInputQualityReport:
    VERSION = "0.1"

    @staticmethod
    def build(
        buildings=None,
        castles=None,
        castle_geometry=None,
        terrain_grid=None,
    ):
        buildings = buildings or []
        castles = castles or []
        castle_geometry = castle_geometry or {}
        terrain_grid = terrain_grid or {}

        geometry_records = list(buildings) + list(castles)

        valid_geometry_count = 0

        for record in geometry_records:
            geometry = record.get(
                "geometry",
                [],
            )

            if AtlasPolygonValidator.validate(geometry):
                valid_geometry_count += 1

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

        building_count = len(buildings)

        height_count = sum(
            1
            for building in buildings
            if AtlasInputQualityReport._has_height(
                building
            )
        )

        roof_count = sum(
            1
            for building in buildings
            if AtlasInputQualityReport._has_roof(
                building
            )
        )

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

        return {
            "version": AtlasInputQualityReport.VERSION,
            "geometry": {
                "total_count": total_geometry_count,
                "valid_count": valid_geometry_count,
                "invalid_count": invalid_geometry_count,
                "valid_percent": valid_percent,
            },
            "semantics": {
                "building_count": building_count,
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
            },
            "terrain": {
                "sample_count": sample_count,
                "missing_sample_count": (
                    missing_sample_count
                ),
                "coverage_percent": coverage_percent,
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

        reasons = []

        if valid_percent < 70.0:
            reasons.append(
                "geometry_valid_percent_below_70"
            )

        if terrain_coverage_percent < 80.0:
            reasons.append(
                "terrain_coverage_percent_below_80"
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
    def _has_height(building):
        if building.get("height") is not None:
            return True

        tags = building.get(
            "tags",
            {},
        )

        return (
            tags.get("height") is not None
            or tags.get("building:levels") is not None
        )

    @staticmethod
    def _has_roof(building):
        if building.get("roof_type") is not None:
            return True

        tags = building.get(
            "tags",
            {},
        )

        return (
            tags.get("roof:shape") is not None
            or tags.get("roof:type") is not None
        )
