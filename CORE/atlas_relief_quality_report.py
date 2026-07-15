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
        }
