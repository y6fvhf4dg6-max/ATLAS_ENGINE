import dataclasses

import pytest

from CORE.atlas_print_optimization_report import (
    DETAIL_BELOW_NOZZLE,
    EXCESSIVE_COLOR_CHANGE,
    EXCESSIVE_TRIANGLE_COUNT,
    FRAGILE_COMPONENT,
    MUST_SIMPLIFY,
    MUST_THICKEN,
    PRINTABLE,
    SUPPORT_REQUIRED,
    WARNING,
    AtlasPrintOptimizationIssue,
    AtlasPrintOptimizationReport,
)


def test_public_status_constants_use_normalized_values():
    assert PRINTABLE == "printable"
    assert WARNING == "warning"
    assert MUST_SIMPLIFY == "must_simplify"
    assert MUST_THICKEN == "must_thicken"
    assert SUPPORT_REQUIRED == "support_required"


def test_public_issue_code_constants_use_normalized_values():
    assert DETAIL_BELOW_NOZZLE == "detail_below_nozzle"
    assert FRAGILE_COMPONENT == "fragile_component"
    assert EXCESSIVE_COLOR_CHANGE == "excessive_color_change"
    assert EXCESSIVE_TRIANGLE_COUNT == "excessive_triangle_count"


def test_issue_normalizes_string_fields_and_is_immutable():
    issue = AtlasPrintOptimizationIssue(
        code="  FRAGILE_COMPONENT ",
        severity=" WARNING ",
        message="  Thin minaret connection  ",
        component="  MINARET ",
    )

    assert issue.code == FRAGILE_COMPONENT
    assert issue.severity == WARNING
    assert issue.message == "Thin minaret connection"
    assert issue.component == "minaret"

    with pytest.raises(dataclasses.FrozenInstanceError):
        issue.code = DETAIL_BELOW_NOZZLE


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("code", ""),
        ("code", "   "),
        ("severity", ""),
        ("message", ""),
        ("component", ""),
    ],
)
def test_issue_rejects_empty_required_strings(field, value):
    kwargs = {
        "code": FRAGILE_COMPONENT,
        "severity": WARNING,
        "message": "Thin connection",
        "component": "minaret",
    }
    kwargs[field] = value

    with pytest.raises(ValueError):
        AtlasPrintOptimizationIssue(**kwargs)


def test_report_normalizes_status_freezes_issues_and_is_immutable():
    issue = AtlasPrintOptimizationIssue(
        code=DETAIL_BELOW_NOZZLE,
        severity=WARNING,
        message="Window detail is below nozzle resolution",
        component="window",
    )

    report = AtlasPrintOptimizationReport(
        status=" PRINTABLE ",
        issues=[issue],
    )

    assert report.status == PRINTABLE
    assert report.issues == (issue,)
    assert isinstance(report.issues, tuple)

    with pytest.raises(dataclasses.FrozenInstanceError):
        report.status = WARNING


def test_report_issue_helpers():
    window_issue = AtlasPrintOptimizationIssue(
        code=DETAIL_BELOW_NOZZLE,
        severity=WARNING,
        message="Window detail is below nozzle resolution",
        component="window",
    )
    minaret_issue = AtlasPrintOptimizationIssue(
        code=FRAGILE_COMPONENT,
        severity=WARNING,
        message="Minaret connection is fragile",
        component="minaret",
    )

    report = AtlasPrintOptimizationReport(
        status=WARNING,
        issues=(window_issue, minaret_issue),
    )

    assert report.has_issue(DETAIL_BELOW_NOZZLE)
    assert report.has_issue(" DETAIL_BELOW_NOZZLE ")
    assert not report.has_issue(EXCESSIVE_COLOR_CHANGE)

    assert report.issues_for_component("WINDOW") == (window_issue,)
    assert report.issues_for_component(" minaret ") == (minaret_issue,)
    assert report.issues_for_component("roof") == ()

    assert not report.is_printable
    assert report.has_warnings


def test_printable_report_helpers():
    report = AtlasPrintOptimizationReport(
        status=PRINTABLE,
        issues=(),
    )

    assert report.is_printable
    assert not report.has_warnings


@pytest.mark.parametrize("status", ["", "unknown", None])
def test_report_rejects_invalid_status(status):
    with pytest.raises((TypeError, ValueError)):
        AtlasPrintOptimizationReport(status=status, issues=())


def test_report_rejects_invalid_issue_collection():
    with pytest.raises((TypeError, ValueError)):
        AtlasPrintOptimizationReport(
            status=WARNING,
            issues=("not-an-issue",),
        )
