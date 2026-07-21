from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any


@dataclass(frozen=True)
class AtlasPortraitReconstructionEvaluation:
    """
    Immutable provider-independent reconstruction evaluation.

    The contract records model identity, license constraints,
    input capabilities, mesh topology, semantic outputs,
    parameter support, platform requirements, performance,
    determinism, ATLAS adapter feasibility, maintenance risk,
    and deterministic metadata.

    It performs no model installation, inference, fitting,
    canonical mesh conversion, projection, compression,
    rendering, triangulation, or STL generation.
    """

    approach_name: str
    model_name: str
    model_version: str

    license_type: str
    commercial_use_allowed: bool
    redistribution_conditions: str

    supports_single_image: bool
    supports_multi_view: bool

    topology_type: str
    vertex_count: int
    triangle_count: int

    supports_surface_normals: bool
    supports_uv_coordinates: bool
    semantic_regions: tuple[str, ...]
    supports_landmark_vertex_map: bool

    supports_identity_parameters: bool
    supports_expression_parameters: bool
    supports_pose_parameters: bool

    supports_confidence: bool
    supports_visibility: bool

    supports_apple_silicon: bool
    supported_python_versions: tuple[str, ...]
    requires_cpu: bool
    requires_gpu: bool

    runtime_seconds: float
    peak_memory_mb: float

    deterministic_output: bool
    fixture_generation_supported: bool

    atlas_adapter_feasibility: str
    maintenance_risk: str

    metadata: Mapping[str, Any]

    TOPOLOGY_TYPES = (
        "fixed",
        "variable",
    )

    RISK_LEVELS = (
        "low",
        "medium",
        "high",
    )

    def __post_init__(self) -> None:
        text_fields = (
            "approach_name",
            "model_name",
            "model_version",
            "license_type",
            "redistribution_conditions",
        )

        for field_name in text_fields:
            object.__setattr__(
                self,
                field_name,
                self._normalize_required_text(
                    getattr(
                        self,
                        field_name,
                    ),
                    name=field_name,
                ),
            )

        boolean_fields = (
            "commercial_use_allowed",
            "supports_single_image",
            "supports_multi_view",
            "supports_surface_normals",
            "supports_uv_coordinates",
            "supports_landmark_vertex_map",
            "supports_identity_parameters",
            "supports_expression_parameters",
            "supports_pose_parameters",
            "supports_confidence",
            "supports_visibility",
            "supports_apple_silicon",
            "requires_cpu",
            "requires_gpu",
            "deterministic_output",
            "fixture_generation_supported",
        )

        for field_name in boolean_fields:
            object.__setattr__(
                self,
                field_name,
                self._normalize_boolean(
                    getattr(
                        self,
                        field_name,
                    ),
                    name=field_name,
                ),
            )

        object.__setattr__(
            self,
            "topology_type",
            self._normalize_choice(
                self.topology_type,
                name="topology_type",
                allowed=self.TOPOLOGY_TYPES,
            ),
        )

        object.__setattr__(
            self,
            "vertex_count",
            self._normalize_positive_integer(
                self.vertex_count,
                name="vertex_count",
            ),
        )

        object.__setattr__(
            self,
            "triangle_count",
            self._normalize_positive_integer(
                self.triangle_count,
                name="triangle_count",
            ),
        )

        object.__setattr__(
            self,
            "semantic_regions",
            self._normalize_string_sequence(
                self.semantic_regions,
                name="semantic_regions",
            ),
        )

        object.__setattr__(
            self,
            "supported_python_versions",
            self._normalize_string_sequence(
                self.supported_python_versions,
                name="supported_python_versions",
            ),
        )

        object.__setattr__(
            self,
            "runtime_seconds",
            self._normalize_nonnegative_float(
                self.runtime_seconds,
                name="runtime_seconds",
            ),
        )

        object.__setattr__(
            self,
            "peak_memory_mb",
            self._normalize_nonnegative_float(
                self.peak_memory_mb,
                name="peak_memory_mb",
            ),
        )

        object.__setattr__(
            self,
            "atlas_adapter_feasibility",
            self._normalize_choice(
                self.atlas_adapter_feasibility,
                name="atlas_adapter_feasibility",
                allowed=self.RISK_LEVELS,
            ),
        )

        object.__setattr__(
            self,
            "maintenance_risk",
            self._normalize_choice(
                self.maintenance_risk,
                name="maintenance_risk",
                allowed=self.RISK_LEVELS,
            ),
        )

        object.__setattr__(
            self,
            "metadata",
            self._normalize_metadata(
                self.metadata,
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "approach_name": self.approach_name,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "license_type": self.license_type,
            "commercial_use_allowed": (
                self.commercial_use_allowed
            ),
            "redistribution_conditions": (
                self.redistribution_conditions
            ),
            "supports_single_image": (
                self.supports_single_image
            ),
            "supports_multi_view": (
                self.supports_multi_view
            ),
            "topology_type": self.topology_type,
            "vertex_count": self.vertex_count,
            "triangle_count": self.triangle_count,
            "supports_surface_normals": (
                self.supports_surface_normals
            ),
            "supports_uv_coordinates": (
                self.supports_uv_coordinates
            ),
            "semantic_regions": list(
                self.semantic_regions,
            ),
            "supports_landmark_vertex_map": (
                self.supports_landmark_vertex_map
            ),
            "supports_identity_parameters": (
                self.supports_identity_parameters
            ),
            "supports_expression_parameters": (
                self.supports_expression_parameters
            ),
            "supports_pose_parameters": (
                self.supports_pose_parameters
            ),
            "supports_confidence": (
                self.supports_confidence
            ),
            "supports_visibility": (
                self.supports_visibility
            ),
            "supports_apple_silicon": (
                self.supports_apple_silicon
            ),
            "supported_python_versions": list(
                self.supported_python_versions,
            ),
            "requires_cpu": self.requires_cpu,
            "requires_gpu": self.requires_gpu,
            "runtime_seconds": self.runtime_seconds,
            "peak_memory_mb": self.peak_memory_mb,
            "deterministic_output": (
                self.deterministic_output
            ),
            "fixture_generation_supported": (
                self.fixture_generation_supported
            ),
            "atlas_adapter_feasibility": (
                self.atlas_adapter_feasibility
            ),
            "maintenance_risk": self.maintenance_risk,
            "metadata": {
                key: self.metadata[key]
                for key in sorted(
                    self.metadata,
                )
            },
        }

    @staticmethod
    def _normalize_required_text(
        value: Any,
        *,
        name: str,
    ) -> str:
        if value is None:
            raise ValueError(
                f"{name} must not be empty."
            )

        text = str(
            value,
        ).strip()

        if not text:
            raise ValueError(
                f"{name} must not be empty."
            )

        return text

    @staticmethod
    def _normalize_boolean(
        value: Any,
        *,
        name: str,
    ) -> bool:
        if not isinstance(
            value,
            bool,
        ):
            raise TypeError(
                f"{name} must be a boolean."
            )

        return value

    @staticmethod
    def _normalize_positive_integer(
        value: Any,
        *,
        name: str,
    ) -> int:
        if (
            isinstance(
                value,
                bool,
            )
            or not isinstance(
                value,
                int,
            )
        ):
            raise TypeError(
                f"{name} must be an integer."
            )

        if value <= 0:
            raise ValueError(
                f"{name} must be greater than zero."
            )

        return value

    @staticmethod
    def _normalize_nonnegative_float(
        value: Any,
        *,
        name: str,
    ) -> float:
        try:
            numeric_value = float(
                value,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if not math.isfinite(
            numeric_value,
        ):
            raise ValueError(
                f"{name} must be finite."
            )

        if numeric_value < 0.0:
            raise ValueError(
                f"{name} must not be negative."
            )

        return numeric_value

    @staticmethod
    def _normalize_choice(
        value: Any,
        *,
        name: str,
        allowed: tuple[str, ...],
    ) -> str:
        if value is None:
            raise ValueError(
                f"{name} is invalid."
            )

        normalized = str(
            value,
        ).strip().lower()

        if normalized not in allowed:
            raise ValueError(
                f"{name} must be one of: "
                + ", ".join(
                    allowed,
                )
                + "."
            )

        return normalized

    @staticmethod
    def _normalize_string_sequence(
        value: Any,
        *,
        name: str,
    ) -> tuple[str, ...]:
        if (
            value is None
            or isinstance(
                value,
                (
                    str,
                    bytes,
                ),
            )
        ):
            raise TypeError(
                f"{name} must be a sequence of strings."
            )

        try:
            raw_values = tuple(
                value,
            )
        except TypeError as exc:
            raise TypeError(
                f"{name} must be a sequence of strings."
            ) from exc

        if not raw_values:
            raise ValueError(
                f"{name} must not be empty."
            )

        normalized_values: list[str] = []

        for item in raw_values:
            if not isinstance(
                item,
                str,
            ):
                raise TypeError(
                    f"{name} must contain only strings."
                )

            normalized_item = item.strip()

            if not normalized_item:
                raise ValueError(
                    f"{name} must not contain empty values."
                )

            normalized_values.append(
                normalized_item,
            )

        return tuple(
            sorted(
                set(
                    normalized_values,
                )
            )
        )

    @staticmethod
    def _normalize_metadata(
        value: Any,
    ) -> Mapping[str, Any]:
        if not isinstance(
            value,
            Mapping,
        ):
            raise TypeError(
                "metadata must be a mapping."
            )

        copied = {
            str(
                key,
            ): item
            for key, item in value.items()
        }

        return MappingProxyType(
            {
                key: copied[key]
                for key in sorted(
                    copied,
                )
            }
        )
