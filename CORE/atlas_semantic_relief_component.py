from __future__ import annotations

import math
from dataclasses import dataclass

from CORE.atlas_semantic_relief_repetition import (
    AtlasSemanticReliefRepetition,
)
from CORE.atlas_semantic_relief_transform import (
    AtlasSemanticReliefTransform,
)


def _normalize_identifier(value, *, field_name: str) -> str:
    normalized = "_".join(
        str(value).strip().lower().split()
    )

    if not normalized:
        raise ValueError(
            f"{field_name} must not be blank"
        )

    return normalized


@dataclass(frozen=True, slots=True)
class AtlasSemanticReliefComponent:
    component_id: str
    semantic_class: str
    geometry_source_kind: str
    parent_component_id: str | None = None
    transform: AtlasSemanticReliefTransform | None = None
    repetition: AtlasSemanticReliefRepetition | None = None
    source_reference: str | None = None
    target_surface_id: str | None = None
    projection_mode: str = "none"
    depth_band: str = "primary"
    layer_order: int = 0
    material_role: str = "unassigned"
    physical_feature_policy: str = "preserve"
    output_modes: tuple[str, ...] = ("relief",)
    provenance: str = "unspecified"
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if self.repetition is not None and not isinstance(
            self.repetition,
            AtlasSemanticReliefRepetition,
        ):
            raise TypeError(
                "repetition must be an "
                "AtlasSemanticReliefRepetition or None"
            )

        if self.transform is not None and not isinstance(
            self.transform,
            AtlasSemanticReliefTransform,
        ):
            raise TypeError(
                "transform must be an "
                "AtlasSemanticReliefTransform or None"
            )

        if isinstance(self.confidence, bool):
            raise ValueError(
                "confidence must be numeric"
            )
        try:
            confidence = float(self.confidence)
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
        object.__setattr__(
            self,
            "confidence",
            confidence,
        )

        if not isinstance(self.provenance, str):
            raise TypeError(
                "provenance must be a string"
            )
        provenance = self.provenance.strip()
        if not provenance:
            raise ValueError(
                "provenance must not be blank"
            )
        object.__setattr__(
            self,
            "provenance",
            provenance,
        )

        if isinstance(self.output_modes, (str, bytes)):
            raise ValueError(
                "output_modes must be a non-empty sequence"
            )

        try:
            output_modes = tuple(
                _normalize_identifier(
                    mode,
                    field_name="output_mode",
                )
                for mode in self.output_modes
            )
        except TypeError as exc:
            raise ValueError(
                "output_modes must be a non-empty sequence"
            ) from exc

        if (
            not output_modes
            or len(output_modes) != len(set(output_modes))
        ):
            raise ValueError(
                "output_modes must be non-empty and unique"
            )

        object.__setattr__(
            self,
            "output_modes",
            output_modes,
        )

        if (
            isinstance(self.layer_order, bool)
            or not isinstance(self.layer_order, int)
            or self.layer_order < 0
        ):
            raise ValueError(
                "layer_order must be a non-negative integer"
            )

        if self.target_surface_id is not None:
            object.__setattr__(
                self,
                "target_surface_id",
                _normalize_identifier(
                    self.target_surface_id,
                    field_name="target_surface_id",
                ),
            )

        if self.source_reference is not None:
            if not isinstance(self.source_reference, str):
                raise TypeError(
                    "source_reference must be a string or None"
                )
            source_reference = self.source_reference.strip()
            if not source_reference:
                raise ValueError(
                    "source_reference must not be blank"
                )
            object.__setattr__(
                self,
                "source_reference",
                source_reference,
            )

        if self.parent_component_id is not None:
            object.__setattr__(
                self,
                "parent_component_id",
                _normalize_identifier(
                    self.parent_component_id,
                    field_name="parent_component_id",
                ),
            )

        for field_name in (
            "component_id",
            "semantic_class",
            "geometry_source_kind",
            "projection_mode",
            "depth_band",
            "material_role",
            "physical_feature_policy",
        ):
            object.__setattr__(
                self,
                field_name,
                _normalize_identifier(
                    getattr(self, field_name),
                    field_name=field_name,
                ),
            )

        has_target_surface = self.target_surface_id is not None
        has_projection = self.projection_mode != "none"

        if has_target_surface != has_projection:
            raise ValueError(
                "target_surface_id and projection_mode "
                "must be provided together"
            )
