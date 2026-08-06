from __future__ import annotations

import math
from typing import Any

from CORE.atlas_relief_quality_report import (
    AtlasReliefQualityReport,
)
from CORE.atlas_relief_risk_profile import (
    AtlasReliefRiskProfile,
)


class AtlasArchitecturalReliefQualityReport:
    @classmethod
    def build(
        cls,
        mesh_production: dict[str, Any],
        *,
        risk_profile: AtlasReliefRiskProfile | None = None,
    ) -> dict[str, Any]:
        production = cls._validated_production(
            mesh_production
        )

        if risk_profile is None:
            risk_profile = AtlasReliefRiskProfile()

        if not isinstance(
            risk_profile,
            AtlasReliefRiskProfile,
        ):
            raise TypeError(
                "risk_profile must be an "
                "AtlasReliefRiskProfile"
            )

        general_quality_report = (
            AtlasReliefQualityReport.build(
                production["mesh"],
                **risk_profile.to_pipeline_kwargs(),
            )
        )

        physical_plan = production[
            "physical_plan"
        ]

        expected_width_mm = cls._finite(
            physical_plan.get("width_mm"),
            name="physical_plan width_mm",
        )
        expected_depth_mm = cls._finite(
            physical_plan.get("depth_mm"),
            name="physical_plan depth_mm",
        )
        minimum_total_height_mm = cls._finite(
            physical_plan.get(
                "base_thickness_mm"
            ),
            name="physical_plan base_thickness_mm",
        )
        maximum_total_height_mm = cls._finite(
            physical_plan.get(
                "total_height_mm"
            ),
            name="physical_plan total_height_mm",
        )

        actual_width_mm = float(
            general_quality_report["width_mm"]
        )
        actual_depth_mm = float(
            general_quality_report["depth_mm"]
        )
        actual_total_height_mm = float(
            general_quality_report[
                "total_height_mm"
            ]
        )

        physical_dimensions_match = bool(
            math.isclose(
                actual_width_mm,
                expected_width_mm,
                rel_tol=1e-9,
                abs_tol=1e-9,
            )
            and math.isclose(
                actual_depth_mm,
                expected_depth_mm,
                rel_tol=1e-9,
                abs_tol=1e-9,
            )
        )

        height_tolerance = 1e-9

        total_height_matches = bool(
            actual_total_height_mm
            >= minimum_total_height_mm
            - height_tolerance
            and actual_total_height_mm
            <= maximum_total_height_mm
            + height_tolerance
        )

        expected_triangle_count = int(
            production[
                "expected_triangle_count"
            ]
        )
        actual_triangle_count = int(
            production[
                "triangle_count"
            ]
        )
        mesh_triangle_count = len(
            production["mesh"]["triangles"]
        )

        triangle_count_matches = bool(
            expected_triangle_count
            == actual_triangle_count
            == mesh_triangle_count
        )

        issues: list[dict[str, Any]] = []

        if not physical_dimensions_match:
            issues.append(
                {
                    "severity": "FAIL",
                    "code": (
                        "architectural_physical_dimension_mismatch"
                    ),
                    "expected_width_mm": expected_width_mm,
                    "actual_width_mm": actual_width_mm,
                    "expected_depth_mm": expected_depth_mm,
                    "actual_depth_mm": actual_depth_mm,
                }
            )

        if not total_height_matches:
            issues.append(
                {
                    "severity": "FAIL",
                    "code": (
                        "architectural_total_height_mismatch"
                    ),
                    "minimum_total_height_mm": (
                        minimum_total_height_mm
                    ),
                    "maximum_total_height_mm": (
                        maximum_total_height_mm
                    ),
                    "actual_total_height_mm": (
                        actual_total_height_mm
                    ),
                }
            )

        if not triangle_count_matches:
            issues.append(
                {
                    "severity": "FAIL",
                    "code": (
                        "architectural_triangle_count_mismatch"
                    ),
                    "expected_triangle_count": (
                        expected_triangle_count
                    ),
                    "actual_triangle_count": (
                        actual_triangle_count
                    ),
                    "mesh_triangle_count": (
                        mesh_triangle_count
                    ),
                }
            )

        for issue in general_quality_report[
            "print_risk_issues"
        ]:
            issues.append(dict(issue))

        status = cls._resolve_status(
            issues
        )

        return {
            "type": (
                "architectural_relief_quality_report"
            ),
            "status": status,
            "is_print_ready": status == "PASS",
            "issue_count": len(issues),
            "issues": tuple(issues),
            "risk_profile_name": (
                risk_profile.name
            ),
            "physical_dimensions_match": (
                physical_dimensions_match
            ),
            "total_height_matches": (
                total_height_matches
            ),
            "triangle_count_matches": (
                triangle_count_matches
            ),
            "expected_width_mm": (
                expected_width_mm
            ),
            "actual_width_mm": (
                actual_width_mm
            ),
            "expected_depth_mm": (
                expected_depth_mm
            ),
            "actual_depth_mm": (
                actual_depth_mm
            ),
            "minimum_total_height_mm": (
                minimum_total_height_mm
            ),
            "maximum_total_height_mm": (
                maximum_total_height_mm
            ),
            "actual_total_height_mm": (
                actual_total_height_mm
            ),
            "expected_triangle_count": (
                expected_triangle_count
            ),
            "actual_triangle_count": (
                actual_triangle_count
            ),
            "general_quality_report": (
                general_quality_report
            ),
        }

    @staticmethod
    def _validated_production(
        value: Any,
    ) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError(
                "mesh_production must be a dictionary"
            )

        if value.get("type") != (
            "architectural_relief_mesh_production"
        ):
            raise ValueError(
                "mesh_production has an invalid type"
            )

        required = (
            "mesh",
            "physical_plan",
            "triangle_count",
            "expected_triangle_count",
        )

        if any(
            name not in value
            for name in required
        ):
            raise ValueError(
                "mesh_production is missing required fields"
            )

        if not isinstance(
            value["mesh"],
            dict,
        ):
            raise ValueError(
                "mesh_production must contain a mesh"
            )

        if not isinstance(
            value["physical_plan"],
            dict,
        ):
            raise ValueError(
                "mesh_production must contain a physical_plan"
            )

        triangles = value[
            "mesh"
        ].get("triangles")

        if not isinstance(
            triangles,
            list,
        ) or not triangles:
            raise ValueError(
                "mesh_production must contain "
                "a non-empty relief mesh"
            )

        for field_name in (
            "triangle_count",
            "expected_triangle_count",
        ):
            value_to_check = value[
                field_name
            ]

            if (
                isinstance(value_to_check, bool)
                or not isinstance(
                    value_to_check,
                    int,
                )
                or value_to_check <= 0
            ):
                raise ValueError(
                    "mesh_production triangle counts "
                    "must be positive integers"
                )

        return value

    @staticmethod
    def _finite(
        value: Any,
        *,
        name: str,
    ) -> float:
        try:
            numeric = float(value)
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric"
            ) from exc

        if not math.isfinite(numeric):
            raise ValueError(
                f"{name} must be finite"
            )

        return numeric

    @staticmethod
    def _resolve_status(
        issues: list[dict[str, Any]],
    ) -> str:
        severities = {
            str(
                issue.get(
                    "severity",
                    "WARN",
                )
            ).upper()
            for issue in issues
        }

        if "FAIL" in severities:
            return "FAIL"

        if "WARN" in severities:
            return "WARN"

        return "PASS"
