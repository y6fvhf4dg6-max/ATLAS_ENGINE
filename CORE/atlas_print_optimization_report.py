from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


PRINTABLE = "printable"
WARNING = "warning"
MUST_SIMPLIFY = "must_simplify"
MUST_THICKEN = "must_thicken"
SUPPORT_REQUIRED = "support_required"

THICKNESS_BELOW_MINIMUM = "thickness_below_minimum"
SUPPORT_REQUIRED_ISSUE = "support_required"
DETAIL_BELOW_NOZZLE = "detail_below_nozzle"
FRAGILE_COMPONENT = "fragile_component"
EXCESSIVE_COLOR_CHANGE = "excessive_color_change"
EXCESSIVE_TRIANGLE_COUNT = "excessive_triangle_count"
EXCESSIVE_FILE_COUNT = "excessive_file_count"


_VALID_STATUSES = frozenset(
    {
        PRINTABLE,
        WARNING,
        MUST_SIMPLIFY,
        MUST_THICKEN,
        SUPPORT_REQUIRED,
    }
)


def _normalize_required_string(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")

    normalized = value.strip()

    if not normalized:
        raise ValueError(f"{field_name} must not be empty")

    return normalized


def _normalize_identifier(value: str, *, field_name: str) -> str:
    return _normalize_required_string(
        value,
        field_name=field_name,
    ).lower()


@dataclass(frozen=True)
class AtlasPrintOptimizationIssue:
    code: str
    severity: str
    message: str
    component: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "code",
            _normalize_identifier(self.code, field_name="code"),
        )
        object.__setattr__(
            self,
            "severity",
            _normalize_identifier(self.severity, field_name="severity"),
        )
        object.__setattr__(
            self,
            "message",
            _normalize_required_string(self.message, field_name="message"),
        )
        object.__setattr__(
            self,
            "component",
            _normalize_identifier(self.component, field_name="component"),
        )


@dataclass(frozen=True)
class AtlasPrintOptimizationReport:
    status: str
    issues: tuple[AtlasPrintOptimizationIssue, ...]

    def __init__(
        self,
        status: str,
        issues: Iterable[AtlasPrintOptimizationIssue] = (),
    ) -> None:
        normalized_status = _normalize_identifier(
            status,
            field_name="status",
        )

        if normalized_status not in _VALID_STATUSES:
            raise ValueError(
                f"unsupported print optimization status: {normalized_status!r}"
            )

        try:
            normalized_issues = tuple(issues)
        except TypeError as exc:
            raise TypeError("issues must be an iterable") from exc

        if not all(
            isinstance(issue, AtlasPrintOptimizationIssue)
            for issue in normalized_issues
        ):
            raise TypeError(
                "issues must contain only AtlasPrintOptimizationIssue values"
            )

        object.__setattr__(self, "status", normalized_status)
        object.__setattr__(self, "issues", normalized_issues)

    def has_issue(self, code: str) -> bool:
        normalized_code = _normalize_identifier(
            code,
            field_name="code",
        )
        return any(issue.code == normalized_code for issue in self.issues)

    def issues_for_component(
        self,
        component: str,
    ) -> tuple[AtlasPrintOptimizationIssue, ...]:
        normalized_component = _normalize_identifier(
            component,
            field_name="component",
        )
        return tuple(
            issue
            for issue in self.issues
            if issue.component == normalized_component
        )

    @property
    def is_printable(self) -> bool:
        return self.status == PRINTABLE

    @property
    def has_warnings(self) -> bool:
        return self.status == WARNING
