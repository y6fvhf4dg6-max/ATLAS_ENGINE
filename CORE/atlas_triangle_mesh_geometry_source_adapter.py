from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from CORE.atlas_geometry_source_adapter import (
    AtlasGeometrySourceAdapter,
)
from CORE.atlas_geometry_source_result import (
    AtlasGeometrySourceResult,
)


class AtlasTriangleMeshGeometrySourceAdapter(
    AtlasGeometrySourceAdapter,
):
    def adapt(
        self,
        source: Any,
    ) -> AtlasGeometrySourceResult:
        if not isinstance(source, Mapping):
            raise TypeError(
                "source must be a mapping"
            )

        required_fields = (
            "triangles",
            "anchors",
            "confidence",
            "provenance",
            "supported_projection_modes",
        )

        missing_fields = tuple(
            field_name
            for field_name in required_fields
            if field_name not in source
        )

        if missing_fields:
            raise ValueError(
                "source missing required fields: "
                + ", ".join(missing_fields)
            )

        triangles = self._normalized_triangles(
            source["triangles"]
        )

        points = tuple(
            point
            for triangle in triangles
            for point in triangle
        )

        local_bounds = (
            (
                min(point[0] for point in points),
                min(point[1] for point in points),
                min(point[2] for point in points),
            ),
            (
                max(point[0] for point in points),
                max(point[1] for point in points),
                max(point[2] for point in points),
            ),
        )

        result = AtlasGeometrySourceResult(
            normalized_geometry={
                "geometry_kind": "triangle_mesh",
                "triangles": triangles,
                "triangle_count": len(triangles),
            },
            local_bounds=local_bounds,
            anchors=source["anchors"],
            confidence=source["confidence"],
            provenance=source["provenance"],
            supported_projection_modes=(
                source[
                    "supported_projection_modes"
                ]
            ),
        )

        return self.validate_result(
            result
        )

    @staticmethod
    def _normalized_triangles(
        triangles: Any,
    ) -> tuple:
        if isinstance(
            triangles,
            (str, bytes),
        ):
            raise ValueError(
                "triangles must be a non-empty "
                "triangle collection"
            )

        try:
            triangle_items = tuple(triangles)
        except TypeError as exc:
            raise ValueError(
                "triangles must be a non-empty "
                "triangle collection"
            ) from exc

        if not triangle_items:
            raise ValueError(
                "triangles must be non-empty"
            )

        normalized = []

        for triangle in triangle_items:
            try:
                points = tuple(triangle)
            except TypeError as exc:
                raise ValueError(
                    "each triangle must contain "
                    "exactly three points"
                ) from exc

            if len(points) != 3:
                raise ValueError(
                    "each triangle must contain "
                    "exactly three points"
                )

            normalized_triangle = []

            for point in points:
                try:
                    coordinates = tuple(point)
                except TypeError as exc:
                    raise ValueError(
                        "each triangle point must "
                        "contain exactly three coordinates"
                    ) from exc

                if len(coordinates) != 3:
                    raise ValueError(
                        "each triangle point must "
                        "contain exactly three coordinates"
                    )

                normalized_point = []

                for coordinate in coordinates:
                    if isinstance(
                        coordinate,
                        bool,
                    ):
                        raise ValueError(
                            "triangle coordinates "
                            "must be numeric"
                        )

                    try:
                        value = float(
                            coordinate
                        )
                    except (
                        TypeError,
                        ValueError,
                    ) as exc:
                        raise ValueError(
                            "triangle coordinates "
                            "must be numeric"
                        ) from exc

                    if not math.isfinite(
                        value
                    ):
                        raise ValueError(
                            "triangle coordinates "
                            "must be finite"
                        )

                    normalized_point.append(
                        value
                    )

                normalized_triangle.append(
                    tuple(
                        normalized_point
                    )
                )

            normalized.append(
                tuple(
                    normalized_triangle
                )
            )

        return tuple(
            normalized
        )
