import pytest

from CORE.atlas_print_optimization_report_builder import (
    AtlasPrintOptimizationReportBuilder,
)
from CORE.atlas_print_optimization_report import (
    PRINTABLE,
    WARNING,
    MUST_SIMPLIFY,
    MUST_THICKEN,
    SUPPORT_REQUIRED,
    THICKNESS_BELOW_MINIMUM,
    SUPPORT_REQUIRED_ISSUE,
    DETAIL_BELOW_NOZZLE,
    FRAGILE_COMPONENT,
    EXCESSIVE_COLOR_CHANGE,
    EXCESSIVE_TRIANGLE_COUNT,
    EXCESSIVE_FILE_COUNT,
)
from CORE.atlas_minimum_thickness_analyzer import (
    AtlasMinimumThicknessAnalyzer,
    AtlasThicknessMeasurement,
)
from CORE.atlas_overhang_support_analyzer import (
    AtlasOverhangMeasurement,
    AtlasOverhangSupportAnalyzer,
)
from CORE.atlas_fragile_connection_analyzer import (
    AtlasConnectionMeasurement,
    AtlasFragileConnectionAnalyzer,
)
from CORE.atlas_nozzle_detail_analyzer import (
    AtlasNozzleDetailAnalyzer,
    AtlasNozzleDetailMeasurement,
)
from CORE.atlas_color_change_analyzer import (
    AtlasColorChangeAnalyzer,
)
from CORE.atlas_triangle_file_count_analyzer import (
    AtlasTriangleFileCountAnalyzer,
)


def _analyses(
    *,
    thin=False,
    support=False,
    fragile=False,
    below_nozzle=False,
    excessive_color=False,
    excessive_triangles=False,
    excessive_files=False,
):
    thickness = AtlasMinimumThicknessAnalyzer.analyze(
        measurements=(
            AtlasThicknessMeasurement(
                component="wall",
                thickness_mm=0.6 if thin else 1.2,
            ),
        ),
        minimum_thickness_mm=0.8,
    )

    overhang = AtlasOverhangSupportAnalyzer.analyze(
        measurements=(
            AtlasOverhangMeasurement(
                component="roof",
                overhang_degrees=60.0 if support else 30.0,
            ),
        ),
        support_threshold_degrees=45.0,
    )

    connection = AtlasFragileConnectionAnalyzer.analyze(
        measurements=(
            AtlasConnectionMeasurement(
                component="tower",
                connection_width_mm=1.0 if fragile else 3.0,
                component_span_mm=10.0,
            ),
        ),
        minimum_connection_ratio=0.2,
    )

    nozzle = AtlasNozzleDetailAnalyzer.analyze(
        measurements=(
            AtlasNozzleDetailMeasurement(
                component="window",
                detail_size_mm=0.3 if below_nozzle else 0.5,
                nozzle_diameter_mm=0.4,
            ),
        ),
        nozzle_diameter_mm=0.4,
    )

    color = AtlasColorChangeAnalyzer.analyze(
        color_change_count=60 if excessive_color else 20,
        maximum_color_changes=40,
    )

    counts = AtlasTriangleFileCountAnalyzer.analyze(
        triangle_count=250_000 if excessive_triangles else 150_000,
        maximum_triangle_count=200_000,
        file_count=7 if excessive_files else 4,
        maximum_file_count=5,
    )

    return {
        "minimum_thickness_analysis": thickness,
        "overhang_support_analysis": overhang,
        "fragile_connection_analysis": connection,
        "nozzle_detail_analysis": nozzle,
        "color_change_analysis": color,
        "triangle_file_count_analysis": counts,
    }


def _build(**flags):
    return AtlasPrintOptimizationReportBuilder.build(
        **_analyses(**flags)
    )


def test_all_safe_analyses_produce_printable_report():
    report = _build()

    assert report.status == PRINTABLE
    assert report.issues == ()
    assert report.is_printable is True


def test_thickness_violation_requires_thickening():
    report = _build(thin=True)

    assert report.status == MUST_THICKEN
    assert report.has_issue(THICKNESS_BELOW_MINIMUM)

    issues = report.issues_for_component("wall")
    assert len(issues) == 1
    assert issues[0].severity == MUST_THICKEN


def test_fragile_connection_requires_thickening():
    report = _build(fragile=True)

    assert report.status == MUST_THICKEN
    assert report.has_issue(FRAGILE_COMPONENT)

    issues = report.issues_for_component("tower")
    assert len(issues) == 1
    assert issues[0].severity == MUST_THICKEN


def test_overhang_requires_support():
    report = _build(support=True)

    assert report.status == SUPPORT_REQUIRED
    assert report.has_issue(SUPPORT_REQUIRED_ISSUE)

    issues = report.issues_for_component("roof")
    assert len(issues) == 1
    assert issues[0].severity == SUPPORT_REQUIRED


def test_triangle_excess_requires_simplification():
    report = _build(excessive_triangles=True)

    assert report.status == MUST_SIMPLIFY
    assert report.has_issue(EXCESSIVE_TRIANGLE_COUNT)

    issues = report.issues_for_component("print_job")
    assert len(issues) == 1
    assert issues[0].severity == MUST_SIMPLIFY


@pytest.mark.parametrize(
    ("flag", "issue_code"),
    (
        ("below_nozzle", DETAIL_BELOW_NOZZLE),
        ("excessive_color", EXCESSIVE_COLOR_CHANGE),
        ("excessive_files", EXCESSIVE_FILE_COUNT),
    ),
)
def test_non_blocking_optimization_findings_produce_warning(
    flag,
    issue_code,
):
    report = _build(**{flag: True})

    assert report.status == WARNING
    assert report.has_issue(issue_code)
    assert report.has_warnings is True


def test_file_count_excess_is_separate_from_triangle_excess():
    report = _build(excessive_files=True)

    assert report.has_issue(EXCESSIVE_FILE_COUNT)
    assert not report.has_issue(EXCESSIVE_TRIANGLE_COUNT)


def test_builder_emits_deterministic_issue_order():
    report = _build(
        thin=True,
        support=True,
        fragile=True,
        below_nozzle=True,
        excessive_color=True,
        excessive_triangles=True,
        excessive_files=True,
    )

    assert tuple(issue.code for issue in report.issues) == (
        THICKNESS_BELOW_MINIMUM,
        SUPPORT_REQUIRED_ISSUE,
        FRAGILE_COMPONENT,
        DETAIL_BELOW_NOZZLE,
        EXCESSIVE_COLOR_CHANGE,
        EXCESSIVE_TRIANGLE_COUNT,
        EXCESSIVE_FILE_COUNT,
    )


def test_status_precedence_prefers_must_thicken_over_all_other_findings():
    report = _build(
        thin=True,
        support=True,
        excessive_triangles=True,
        excessive_color=True,
    )

    assert report.status == MUST_THICKEN


def test_status_precedence_prefers_support_over_simplify_and_warning():
    report = _build(
        support=True,
        excessive_triangles=True,
        excessive_color=True,
    )

    assert report.status == SUPPORT_REQUIRED


def test_status_precedence_prefers_simplify_over_warning():
    report = _build(
        excessive_triangles=True,
        excessive_color=True,
    )

    assert report.status == MUST_SIMPLIFY


@pytest.mark.parametrize(
    "field_name",
    (
        "minimum_thickness_analysis",
        "overhang_support_analysis",
        "fragile_connection_analysis",
        "nozzle_detail_analysis",
        "color_change_analysis",
        "triangle_file_count_analysis",
    ),
)
def test_builder_rejects_wrong_analysis_types(field_name):
    kwargs = _analyses()
    kwargs[field_name] = object()

    with pytest.raises(TypeError):
        AtlasPrintOptimizationReportBuilder.build(**kwargs)
