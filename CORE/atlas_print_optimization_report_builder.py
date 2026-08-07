from __future__ import annotations

from CORE.atlas_color_change_analyzer import (
    AtlasColorChangeAnalysis,
)
from CORE.atlas_fragile_connection_analyzer import (
    AtlasFragileConnectionAnalysis,
)
from CORE.atlas_minimum_thickness_analyzer import (
    AtlasMinimumThicknessAnalysis,
)
from CORE.atlas_nozzle_detail_analyzer import (
    AtlasNozzleDetailAnalysis,
)
from CORE.atlas_overhang_support_analyzer import (
    AtlasOverhangSupportAnalysis,
)
from CORE.atlas_print_optimization_report import (
    DETAIL_BELOW_NOZZLE,
    EXCESSIVE_COLOR_CHANGE,
    EXCESSIVE_FILE_COUNT,
    EXCESSIVE_TRIANGLE_COUNT,
    FRAGILE_COMPONENT,
    MUST_SIMPLIFY,
    MUST_THICKEN,
    PRINTABLE,
    SUPPORT_REQUIRED,
    SUPPORT_REQUIRED_ISSUE,
    THICKNESS_BELOW_MINIMUM,
    WARNING,
    AtlasPrintOptimizationIssue,
    AtlasPrintOptimizationReport,
)
from CORE.atlas_triangle_file_count_analyzer import (
    AtlasTriangleFileCountAnalysis,
)


class AtlasPrintOptimizationReportBuilder:
    @staticmethod
    def _require_type(value, expected_type, *, name: str):
        if not isinstance(value, expected_type):
            raise TypeError(
                f"{name} must be {expected_type.__name__}"
            )
        return value

    @classmethod
    def build(
        cls,
        *,
        minimum_thickness_analysis: AtlasMinimumThicknessAnalysis,
        overhang_support_analysis: AtlasOverhangSupportAnalysis,
        fragile_connection_analysis: AtlasFragileConnectionAnalysis,
        nozzle_detail_analysis: AtlasNozzleDetailAnalysis,
        color_change_analysis: AtlasColorChangeAnalysis,
        triangle_file_count_analysis: AtlasTriangleFileCountAnalysis,
    ) -> AtlasPrintOptimizationReport:
        thickness = cls._require_type(
            minimum_thickness_analysis,
            AtlasMinimumThicknessAnalysis,
            name="minimum_thickness_analysis",
        )
        overhang = cls._require_type(
            overhang_support_analysis,
            AtlasOverhangSupportAnalysis,
            name="overhang_support_analysis",
        )
        fragile = cls._require_type(
            fragile_connection_analysis,
            AtlasFragileConnectionAnalysis,
            name="fragile_connection_analysis",
        )
        nozzle = cls._require_type(
            nozzle_detail_analysis,
            AtlasNozzleDetailAnalysis,
            name="nozzle_detail_analysis",
        )
        color = cls._require_type(
            color_change_analysis,
            AtlasColorChangeAnalysis,
            name="color_change_analysis",
        )
        counts = cls._require_type(
            triangle_file_count_analysis,
            AtlasTriangleFileCountAnalysis,
            name="triangle_file_count_analysis",
        )

        issues = []

        for component in thickness.violating_components:
            issues.append(
                AtlasPrintOptimizationIssue(
                    code=THICKNESS_BELOW_MINIMUM,
                    severity=MUST_THICKEN,
                    message=(
                        "Component thickness is below "
                        "the configured minimum."
                    ),
                    component=component,
                )
            )

        for component in overhang.support_required_components:
            issues.append(
                AtlasPrintOptimizationIssue(
                    code=SUPPORT_REQUIRED_ISSUE,
                    severity=SUPPORT_REQUIRED,
                    message=(
                        "Component overhang requires print support."
                    ),
                    component=component,
                )
            )

        for component in fragile.fragile_components:
            issues.append(
                AtlasPrintOptimizationIssue(
                    code=FRAGILE_COMPONENT,
                    severity=MUST_THICKEN,
                    message=(
                        "Component connection is below "
                        "the minimum safe ratio."
                    ),
                    component=component,
                )
            )

        for component in nozzle.below_nozzle_components:
            issues.append(
                AtlasPrintOptimizationIssue(
                    code=DETAIL_BELOW_NOZZLE,
                    severity=WARNING,
                    message=(
                        "Component detail is below "
                        "the selected nozzle diameter."
                    ),
                    component=component,
                )
            )

        if color.is_excessive:
            issues.append(
                AtlasPrintOptimizationIssue(
                    code=EXCESSIVE_COLOR_CHANGE,
                    severity=WARNING,
                    message=(
                        "Print job exceeds the configured "
                        "color-change limit."
                    ),
                    component="print_job",
                )
            )

        if counts.is_triangle_count_excessive:
            issues.append(
                AtlasPrintOptimizationIssue(
                    code=EXCESSIVE_TRIANGLE_COUNT,
                    severity=MUST_SIMPLIFY,
                    message=(
                        "Print job exceeds the configured "
                        "triangle-count limit."
                    ),
                    component="print_job",
                )
            )

        if counts.is_file_count_excessive:
            issues.append(
                AtlasPrintOptimizationIssue(
                    code=EXCESSIVE_FILE_COUNT,
                    severity=WARNING,
                    message=(
                        "Print job exceeds the configured "
                        "file-count limit."
                    ),
                    component="print_job",
                )
            )

        severities = {
            issue.severity
            for issue in issues
        }

        if MUST_THICKEN in severities:
            status = MUST_THICKEN
        elif SUPPORT_REQUIRED in severities:
            status = SUPPORT_REQUIRED
        elif MUST_SIMPLIFY in severities:
            status = MUST_SIMPLIFY
        elif WARNING in severities:
            status = WARNING
        else:
            status = PRINTABLE

        return AtlasPrintOptimizationReport(
            status=status,
            issues=issues,
        )
