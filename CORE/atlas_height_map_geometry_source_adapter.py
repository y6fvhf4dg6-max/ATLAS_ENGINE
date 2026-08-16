from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np

from CORE.atlas_geometry_source_adapter import (
    AtlasGeometrySourceAdapter,
)
from CORE.atlas_geometry_source_result import (
    AtlasGeometrySourceResult,
)
from CORE.atlas_architectural_relief_mesh_producer import (
    AtlasArchitecturalReliefMeshProducer,
)


class AtlasHeightMapGeometrySourceAdapter(
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
            "height_map",
            "width_mm",
            "depth_mm",
            "relief_height_mm",
            "confidence",
            "provenance",
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

        height_map = (
            AtlasArchitecturalReliefMeshProducer
            ._validated_height_map(
                source["height_map"]
            )
        )

        width_mm = self._positive_finite_float(
            source["width_mm"],
            field_name="width_mm",
        )
        depth_mm = self._positive_finite_float(
            source["depth_mm"],
            field_name="depth_mm",
        )
        relief_height_mm = (
            self._non_negative_finite_float(
                source["relief_height_mm"],
                field_name="relief_height_mm",
            )
        )

        geometry = {
            "geometry_kind": "height_map_relief",
            "height_map": tuple(
                tuple(float(value) for value in row)
                for row in height_map
            ),
            "row_count": int(height_map.shape[0]),
            "column_count": int(height_map.shape[1]),
            "width_mm": width_mm,
            "depth_mm": depth_mm,
            "relief_height_mm": relief_height_mm,
        }

        result = AtlasGeometrySourceResult(
            normalized_geometry=geometry,
            local_bounds=(
                (0.0, 0.0, 0.0),
                (
                    width_mm,
                    depth_mm,
                    relief_height_mm,
                ),
            ),
            anchors={
                "origin": (0.0, 0.0, 0.0),
            },
            confidence=source["confidence"],
            provenance=source["provenance"],
            supported_projection_modes=(
                "flat_plane",
            ),
        )

        return self.validate_result(
            result
        )

    @staticmethod
    def _positive_finite_float(
        value: Any,
        *,
        field_name: str,
    ) -> float:
        if isinstance(value, bool):
            raise ValueError(
                f"{field_name} must be numeric"
            )

        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{field_name} must be numeric"
            ) from exc

        if not math.isfinite(numeric):
            raise ValueError(
                f"{field_name} must be finite"
            )

        if numeric <= 0.0:
            raise ValueError(
                f"{field_name} must be greater than zero"
            )

        return numeric

    @staticmethod
    def _non_negative_finite_float(
        value: Any,
        *,
        field_name: str,
    ) -> float:
        if isinstance(value, bool):
            raise ValueError(
                f"{field_name} must be numeric"
            )

        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{field_name} must be numeric"
            ) from exc

        if not math.isfinite(numeric):
            raise ValueError(
                f"{field_name} must be finite"
            )

        if numeric < 0.0:
            raise ValueError(
                f"{field_name} must not be negative"
            )

        return numeric
