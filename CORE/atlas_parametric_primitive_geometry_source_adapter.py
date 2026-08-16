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


class AtlasParametricPrimitiveGeometrySourceAdapter(
    AtlasGeometrySourceAdapter,
):
    SUPPORTED_PRIMITIVES = (
        "closed_cylinder",
    )

    def adapt(
        self,
        source: Any,
    ) -> AtlasGeometrySourceResult:
        if not isinstance(source, Mapping):
            raise TypeError(
                "source must be a mapping"
            )

        required_fields = (
            "primitive_type",
            "parameters",
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

        primitive_type = self._normalized_identifier(
            source["primitive_type"],
            field_name="primitive_type",
        )

        if primitive_type not in self.SUPPORTED_PRIMITIVES:
            raise ValueError(
                "unsupported primitive_type: "
                f"{primitive_type}"
            )

        if primitive_type == "closed_cylinder":
            (
                parameters,
                local_bounds,
                anchors,
            ) = self._closed_cylinder_contract(
                source["parameters"]
            )
        else:
            raise ValueError(
                "unsupported primitive_type: "
                f"{primitive_type}"
            )

        result = AtlasGeometrySourceResult(
            normalized_geometry={
                "geometry_kind": "parametric_primitive",
                "primitive_type": primitive_type,
                "parameters": parameters,
            },
            local_bounds=local_bounds,
            anchors=anchors,
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

    @classmethod
    def _closed_cylinder_contract(
        cls,
        parameters: Any,
    ) -> tuple:
        if not isinstance(parameters, Mapping):
            raise TypeError(
                "parameters must be a mapping"
            )

        required = (
            "center_x",
            "center_y",
            "base_z",
            "radius",
            "height",
            "segments",
        )

        missing = tuple(
            name
            for name in required
            if name not in parameters
        )

        if missing:
            raise ValueError(
                "parameters missing required fields: "
                + ", ".join(missing)
            )

        center_x = cls._finite_float(
            parameters["center_x"],
            field_name="center_x",
        )
        center_y = cls._finite_float(
            parameters["center_y"],
            field_name="center_y",
        )
        base_z = cls._finite_float(
            parameters["base_z"],
            field_name="base_z",
        )
        radius = cls._positive_finite_float(
            parameters["radius"],
            field_name="radius",
        )
        height = cls._positive_finite_float(
            parameters["height"],
            field_name="height",
        )
        segments = cls._segments(
            parameters["segments"]
        )

        top_z = base_z + height

        normalized_parameters = {
            "center_x": center_x,
            "center_y": center_y,
            "base_z": base_z,
            "radius": radius,
            "height": height,
            "segments": segments,
        }

        local_bounds = (
            (
                center_x - radius,
                center_y - radius,
                base_z,
            ),
            (
                center_x + radius,
                center_y + radius,
                top_z,
            ),
        )

        anchors = {
            "base_center": (
                center_x,
                center_y,
                base_z,
            ),
            "top_center": (
                center_x,
                center_y,
                top_z,
            ),
        }

        return (
            normalized_parameters,
            local_bounds,
            anchors,
        )

    @staticmethod
    def _normalized_identifier(
        value: Any,
        *,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise ValueError(
                f"{field_name} must be a string"
            )

        normalized = "_".join(
            value.strip().lower().split()
        )

        if not normalized:
            raise ValueError(
                f"{field_name} must not be blank"
            )

        return normalized

    @staticmethod
    def _finite_float(
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

        return numeric

    @classmethod
    def _positive_finite_float(
        cls,
        value: Any,
        *,
        field_name: str,
    ) -> float:
        numeric = cls._finite_float(
            value,
            field_name=field_name,
        )

        if numeric <= 0.0:
            raise ValueError(
                f"{field_name} must be greater than zero"
            )

        return numeric

    @staticmethod
    def _segments(
        value: Any,
    ) -> int:
        if isinstance(value, bool):
            raise ValueError(
                "segments must be an integer"
            )

        try:
            numeric = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "segments must be an integer"
            ) from exc

        if float(value) != float(numeric):
            raise ValueError(
                "segments must be an integer"
            )

        if numeric < 6:
            raise ValueError(
                "segments must be at least 6"
            )

        return numeric
