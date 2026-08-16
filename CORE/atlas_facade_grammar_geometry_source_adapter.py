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


class AtlasFacadeGrammarGeometrySourceAdapter(
    AtlasGeometrySourceAdapter,
):
    SUPPORTED_GRAMMARS = (
        "uniform_openings",
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
            "grammar_type",
            "facade_width_mm",
            "facade_height_mm",
            "level_count",
            "bay_count",
            "opening_kind",
            "horizontal_margin_ratio",
            "vertical_margin_ratio",
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

        grammar_type = self._normalized_identifier(
            source["grammar_type"],
            field_name="grammar_type",
        )

        if grammar_type not in self.SUPPORTED_GRAMMARS:
            raise ValueError(
                "unsupported grammar_type: "
                f"{grammar_type}"
            )

        facade_width_mm = self._positive_finite_float(
            source["facade_width_mm"],
            field_name="facade_width_mm",
        )
        facade_height_mm = self._positive_finite_float(
            source["facade_height_mm"],
            field_name="facade_height_mm",
        )

        level_count = self._positive_integer(
            source["level_count"],
            field_name="level_count",
        )
        bay_count = self._positive_integer(
            source["bay_count"],
            field_name="bay_count",
        )

        opening_kind = self._normalized_identifier(
            source["opening_kind"],
            field_name="opening_kind",
        )

        horizontal_margin_ratio = self._margin_ratio(
            source["horizontal_margin_ratio"],
            field_name="horizontal_margin_ratio",
        )
        vertical_margin_ratio = self._margin_ratio(
            source["vertical_margin_ratio"],
            field_name="vertical_margin_ratio",
        )

        opening_count = (
            level_count * bay_count
        )

        result = AtlasGeometrySourceResult(
            normalized_geometry={
                "geometry_kind": "facade_grammar",
                "grammar_type": grammar_type,
                "facade_width_mm": facade_width_mm,
                "facade_height_mm": facade_height_mm,
                "level_count": level_count,
                "bay_count": bay_count,
                "opening_kind": opening_kind,
                "horizontal_margin_ratio": (
                    horizontal_margin_ratio
                ),
                "vertical_margin_ratio": (
                    vertical_margin_ratio
                ),
                "opening_count": opening_count,
            },
            local_bounds=(
                (0.0, 0.0, 0.0),
                (
                    facade_width_mm,
                    0.0,
                    facade_height_mm,
                ),
            ),
            anchors={
                "bottom_left": (
                    0.0,
                    0.0,
                    0.0,
                ),
                "bottom_center": (
                    facade_width_mm / 2.0,
                    0.0,
                    0.0,
                ),
                "top_center": (
                    facade_width_mm / 2.0,
                    0.0,
                    facade_height_mm,
                ),
            },
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
    def _positive_integer(
        value: Any,
        *,
        field_name: str,
    ) -> int:
        if isinstance(value, bool):
            raise ValueError(
                f"{field_name} must be a positive integer"
            )

        try:
            integer = int(value)
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{field_name} must be a positive integer"
            ) from exc

        if (
            not math.isfinite(numeric)
            or numeric != float(integer)
            or integer < 1
        ):
            raise ValueError(
                f"{field_name} must be a positive integer"
            )

        return integer

    @staticmethod
    def _margin_ratio(
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

        if not 0.0 <= numeric < 0.5:
            raise ValueError(
                f"{field_name} must satisfy "
                "0.0 <= value < 0.5"
            )

        return numeric
