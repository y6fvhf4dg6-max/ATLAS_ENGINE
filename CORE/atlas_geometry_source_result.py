from __future__ import annotations

import copy
import math
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any


def _normalize_identifier(
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


def _normalize_point3(
    value: Any,
    *,
    field_name: str,
) -> tuple[float, float, float]:
    if isinstance(value, (str, bytes)):
        raise ValueError(
            f"{field_name} must contain exactly three numeric values"
        )

    try:
        coordinates = tuple(value)
    except TypeError as exc:
        raise ValueError(
            f"{field_name} must contain exactly three numeric values"
        ) from exc

    if len(coordinates) != 3:
        raise ValueError(
            f"{field_name} must contain exactly three numeric values"
        )

    normalized = []

    for coordinate in coordinates:
        if isinstance(coordinate, bool):
            raise ValueError(
                f"{field_name} coordinates must be numeric"
            )

        try:
            numeric = float(coordinate)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{field_name} coordinates must be numeric"
            ) from exc

        if not math.isfinite(numeric):
            raise ValueError(
                f"{field_name} coordinates must be finite"
            )

        normalized.append(numeric)

    return (
        normalized[0],
        normalized[1],
        normalized[2],
    )


@dataclass(frozen=True, slots=True)
class AtlasGeometrySourceResult:
    normalized_geometry: Any
    local_bounds: tuple[
        tuple[float, float, float],
        tuple[float, float, float],
    ]
    anchors: Mapping[
        str,
        tuple[float, float, float],
    ]
    confidence: float
    provenance: str
    supported_projection_modes: tuple[str, ...]

    def __post_init__(self) -> None:
        geometry = copy.deepcopy(
            self.normalized_geometry
        )

        if isinstance(
            self.local_bounds,
            (str, bytes),
        ):
            raise ValueError(
                "local_bounds must contain exactly two 3D points"
            )

        try:
            bounds = tuple(self.local_bounds)
        except TypeError as exc:
            raise ValueError(
                "local_bounds must contain exactly two 3D points"
            ) from exc

        if len(bounds) != 2:
            raise ValueError(
                "local_bounds must contain exactly two 3D points"
            )

        local_bounds = (
            _normalize_point3(
                bounds[0],
                field_name="local_bounds minimum",
            ),
            _normalize_point3(
                bounds[1],
                field_name="local_bounds maximum",
            ),
        )

        if any(
            minimum > maximum
            for minimum, maximum in zip(
                local_bounds[0],
                local_bounds[1],
                strict=True,
            )
        ):
            raise ValueError(
                "local_bounds minimum must not exceed maximum"
            )

        if not isinstance(self.anchors, Mapping):
            raise ValueError(
                "anchors must be a mapping"
            )

        anchors = {}

        for raw_name, raw_point in self.anchors.items():
            name = _normalize_identifier(
                raw_name,
                field_name="anchor name",
            )

            if name in anchors:
                raise ValueError(
                    "anchor names must be unique after normalization"
                )

            anchors[name] = _normalize_point3(
                raw_point,
                field_name=f"anchor {name}",
            )

        if isinstance(self.confidence, bool):
            raise ValueError(
                "confidence must be numeric"
            )

        try:
            confidence = float(
                self.confidence
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "confidence must be numeric"
            ) from exc

        if (
            not math.isfinite(confidence)
            or confidence < 0.0
            or confidence > 1.0
        ):
            raise ValueError(
                "confidence must be in the 0.0..1.0 range"
            )

        if not isinstance(self.provenance, str):
            raise ValueError(
                "provenance must be a string"
            )

        provenance = self.provenance.strip()

        if not provenance:
            raise ValueError(
                "provenance must not be blank"
            )

        if isinstance(
            self.supported_projection_modes,
            (str, bytes),
        ):
            raise ValueError(
                "supported_projection_modes must be a non-empty sequence"
            )

        try:
            projection_modes = tuple(
                _normalize_identifier(
                    mode,
                    field_name="projection mode",
                )
                for mode in self.supported_projection_modes
            )
        except TypeError as exc:
            raise ValueError(
                "supported_projection_modes must be a non-empty sequence"
            ) from exc

        if (
            not projection_modes
            or len(projection_modes)
            != len(set(projection_modes))
        ):
            raise ValueError(
                "supported_projection_modes must be non-empty and unique"
            )

        object.__setattr__(
            self,
            "normalized_geometry",
            geometry,
        )
        object.__setattr__(
            self,
            "local_bounds",
            local_bounds,
        )
        object.__setattr__(
            self,
            "anchors",
            MappingProxyType(anchors),
        )
        object.__setattr__(
            self,
            "confidence",
            confidence,
        )
        object.__setattr__(
            self,
            "provenance",
            provenance,
        )
        object.__setattr__(
            self,
            "supported_projection_modes",
            projection_modes,
        )

    def require_projection_mode(
        self,
        projection_mode: Any,
    ) -> str:
        normalized_mode = _normalize_identifier(
            projection_mode,
            field_name="projection mode",
        )

        if normalized_mode not in self.supported_projection_modes:
            raise ValueError(
                f"unsupported projection mode: {normalized_mode}"
            )

        return normalized_mode
