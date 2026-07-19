from __future__ import annotations

import math
from typing import Any

from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)


class AtlasReliefQualityReport:
    """
    ATLAS Relief Quality Report v0.1

    Produces deterministic structural and dimensional
    diagnostics for a generated relief mesh.
    """

    @staticmethod
    def build(
        relief_mesh: dict[str, Any],
        *,
        warning_slope_degrees: float = 55.0,
        critical_slope_degrees: float = 75.0,
    ) -> dict[str, Any]:
        if not isinstance(relief_mesh, dict):
            raise ValueError(
                "relief_mesh must be a dictionary."
            )

        triangles = relief_mesh.get("triangles")

        if not isinstance(triangles, list):
            raise ValueError(
                "relief_mesh must contain a "
                "triangle list."
            )

        if not triangles:
            raise ValueError(
                "relief_mesh must contain triangles."
            )

        points = [
            point
            for triangle in triangles
            for point in triangle
        ]

        if any(
            len(point) != 3
            or not all(
                math.isfinite(float(value))
                for value in point
            )
            for point in points
        ):
            raise ValueError(
                "Relief geometry contains invalid "
                "vertex coordinates."
            )

        topology = (
            AtlasMeshValidator._topology_report(
                relief_mesh
            )
        )

        x_values = [
            float(point[0])
            for point in points
        ]
        y_values = [
            float(point[1])
            for point in points
        ]
        z_values = [
            float(point[2])
            for point in points
        ]

        minimum_z = min(z_values)
        maximum_z = max(z_values)

        open_edge_count = topology[
            "open_edge_count"
        ]
        non_manifold_edge_count = topology[
            "non_manifold_edge_count"
        ]

        is_closed = open_edge_count == 0
        is_manifold = (
            non_manifold_edge_count == 0
        )

        surface_analysis = (
            AtlasReliefQualityReport
            ._analyze_top_surface(
                relief_mesh
            )
        )

        print_risk = (
            AtlasReliefQualityReport
            ._classify_print_risk(
                is_closed=is_closed,
                is_manifold=is_manifold,
                surface_analysis=(
                    surface_analysis
                ),
                warning_slope_degrees=(
                    warning_slope_degrees
                ),
                critical_slope_degrees=(
                    critical_slope_degrees
                ),
            )
        )

        return {
            "geometry_type": (
                relief_mesh.get(
                    "geometry_type",
                    relief_mesh.get(
                        "type",
                        "unknown",
                    ),
                )
            ),
            "triangle_count": len(triangles),
            "vertex_reference_count": len(points),
            "minimum_x": min(x_values),
            "maximum_x": max(x_values),
            "minimum_y": min(y_values),
            "maximum_y": max(y_values),
            "minimum_z": minimum_z,
            "maximum_z": maximum_z,
            "width_mm": (
                max(x_values) - min(x_values)
            ),
            "depth_mm": (
                max(y_values) - min(y_values)
            ),
            "total_height_mm": (
                maximum_z - minimum_z
            ),
            "open_edge_count": open_edge_count,
            "non_manifold_edge_count": (
                non_manifold_edge_count
            ),
            "is_closed": is_closed,
            "is_manifold": is_manifold,
            "is_printable_topology": (
                is_closed and is_manifold
            ),
            **surface_analysis,
            **print_risk,
        }

    @staticmethod
    def _classify_print_risk(
        *,
        is_closed: bool,
        is_manifold: bool,
        surface_analysis: dict[str, Any],
        warning_slope_degrees: float,
        critical_slope_degrees: float,
    ) -> dict[str, Any]:
        thresholds = {
            "warning_slope_degrees": (
                warning_slope_degrees
            ),
            "critical_slope_degrees": (
                critical_slope_degrees
            ),
        }

        for name, value in thresholds.items():
            if not math.isfinite(float(value)):
                raise ValueError(
                    f"{name} must be finite."
                )

        warning_slope_degrees = float(
            warning_slope_degrees
        )
        critical_slope_degrees = float(
            critical_slope_degrees
        )

        if not (
            0.0
            <= warning_slope_degrees
            < 90.0
        ):
            raise ValueError(
                "warning_slope_degrees must be "
                "in the 0.0..<90.0 range."
            )

        if not (
            0.0
            < critical_slope_degrees
            < 90.0
        ):
            raise ValueError(
                "critical_slope_degrees must be "
                "in the 0.0..<90.0 range."
            )

        if (
            warning_slope_degrees
            >= critical_slope_degrees
        ):
            raise ValueError(
                "warning_slope_degrees must be "
                "lower than "
                "critical_slope_degrees."
            )

        issues = []

        if not is_closed:
            issues.append(
                {
                    "severity": "FAIL",
                    "code": "open_relief_mesh",
                }
            )

        if not is_manifold:
            issues.append(
                {
                    "severity": "FAIL",
                    "code": (
                        "non_manifold_relief_mesh"
                    ),
                }
            )

        if not surface_analysis[
            "surface_analysis_available"
        ]:
            issues.append(
                {
                    "severity": "WARN",
                    "code": (
                        "surface_analysis_unavailable"
                    ),
                }
            )
        else:
            maximum_slope = float(
                surface_analysis[
                    "maximum_slope_degrees"
                ]
            )

            if (
                maximum_slope
                >= critical_slope_degrees
            ):
                issues.append(
                    {
                        "severity": "FAIL",
                        "code": (
                            "critical_surface_slope"
                        ),
                        "value": maximum_slope,
                        "limit": (
                            critical_slope_degrees
                        ),
                    }
                )
            elif (
                maximum_slope
                >= warning_slope_degrees
            ):
                issues.append(
                    {
                        "severity": "WARN",
                        "code": (
                            "steep_surface_slope"
                        ),
                        "value": maximum_slope,
                        "limit": (
                            warning_slope_degrees
                        ),
                    }
                )

        severities = {
            issue["severity"]
            for issue in issues
        }

        if "FAIL" in severities:
            status = "FAIL"
        elif "WARN" in severities:
            status = "WARN"
        else:
            status = "PASS"

        return {
            "print_risk_status": status,
            "print_risk_issue_count": len(
                issues
            ),
            "print_risk_issues": issues,
            "warning_slope_degrees": (
                warning_slope_degrees
            ),
            "critical_slope_degrees": (
                critical_slope_degrees
            ),
        }

    @staticmethod
    def _analyze_top_surface(
        relief_mesh: dict[str, Any],
    ) -> dict[str, Any]:
        top_grid = relief_mesh.get("top_grid")

        if not top_grid:
            return {
                "surface_analysis_available": False,
                "sample_spacing_x_mm": None,
                "sample_spacing_y_mm": None,
                "surface_edge_count": 0,
                "maximum_adjacent_rise_mm": None,
                "maximum_slope_degrees": None,
                "average_slope_degrees": None,
            }

        row_count = len(top_grid)

        if row_count < 2:
            raise ValueError(
                "Relief top_grid must contain "
                "at least two rows."
            )

        column_count = len(top_grid[0])

        if column_count < 2:
            raise ValueError(
                "Relief top_grid must contain "
                "at least two columns."
            )

        if any(
            len(row) != column_count
            for row in top_grid
        ):
            raise ValueError(
                "Relief top_grid rows must have "
                "equal lengths."
            )

        spacing_x_values = []
        spacing_y_values = []
        diagonal_spacing_values = []
        slope_values = []
        rise_values = []

        for row in range(row_count):
            for column in range(
                column_count - 1
            ):
                point_a = top_grid[row][column]
                point_b = top_grid[row][
                    column + 1
                ]

                AtlasReliefQualityReport._add_slope(
                    point_a,
                    point_b,
                    slope_values=slope_values,
                    rise_values=rise_values,
                    planar_values=(
                        spacing_x_values
                    ),
                )

        for row in range(row_count - 1):
            for column in range(column_count):
                point_a = top_grid[row][column]
                point_b = top_grid[row + 1][
                    column
                ]

                AtlasReliefQualityReport._add_slope(
                    point_a,
                    point_b,
                    slope_values=slope_values,
                    rise_values=rise_values,
                    planar_values=(
                        spacing_y_values
                    ),
                )

        for row in range(row_count - 1):
            for column in range(
                column_count - 1
            ):
                lower_left = top_grid[row][column]
                upper_right = top_grid[
                    row + 1
                ][column + 1]

                AtlasReliefQualityReport._add_slope(
                    lower_left,
                    upper_right,
                    slope_values=slope_values,
                    rise_values=rise_values,
                    planar_values=(
                        diagonal_spacing_values
                    ),
                )

        return {
            "surface_analysis_available": True,
            "sample_spacing_x_mm": (
                sum(spacing_x_values)
                / len(spacing_x_values)
            ),
            "sample_spacing_y_mm": (
                sum(spacing_y_values)
                / len(spacing_y_values)
            ),
            "surface_edge_count": len(
                slope_values
            ),
            "maximum_adjacent_rise_mm": max(
                rise_values
            ),
            "maximum_slope_degrees": max(
                slope_values
            ),
            "average_slope_degrees": (
                sum(slope_values)
                / len(slope_values)
            ),
        }

    @staticmethod
    def _add_slope(
        point_a: Any,
        point_b: Any,
        *,
        slope_values: list[float],
        rise_values: list[float],
        planar_values: list[float],
    ) -> None:
        for point in (point_a, point_b):
            try:
                point_size = len(point)
            except TypeError:
                raise ValueError(
                    "Relief top_grid contains an "
                    "invalid point."
                ) from None

            if point_size != 3:
                raise ValueError(
                    "Relief top_grid contains an "
                    "invalid point."
                )

        try:
            coordinates = [
                float(value)
                for point in (point_a, point_b)
                for value in point
            ]
        except (TypeError, ValueError):
            raise ValueError(
                "Relief top_grid contains "
                "invalid coordinates."
            ) from None

        if not all(
            math.isfinite(value)
            for value in coordinates
        ):
            raise ValueError(
                "Relief top_grid contains "
                "non-finite coordinates."
            )

        delta_x = (
            float(point_b[0])
            - float(point_a[0])
        )
        delta_y = (
            float(point_b[1])
            - float(point_a[1])
        )
        delta_z = abs(
            float(point_b[2])
            - float(point_a[2])
        )

        planar_distance = math.hypot(
            delta_x,
            delta_y,
        )

        if planar_distance <= 0.0:
            raise ValueError(
                "Relief top_grid contains "
                "duplicate planar samples."
            )

        slope_degrees = math.degrees(
            math.atan2(
                delta_z,
                planar_distance,
            )
        )

        planar_values.append(planar_distance)
        rise_values.append(delta_z)
        slope_values.append(slope_degrees)
