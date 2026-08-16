from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from CORE.atlas_geometry_source_adapter import (
    AtlasGeometrySourceAdapter,
)
from CORE.atlas_geometry_source_result import (
    AtlasGeometrySourceResult,
)
from CORE.atlas_semantic_relief_component import (
    AtlasSemanticReliefComponent,
)


class AtlasBodyPosePropGeometrySourceAdapter(
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
            "component",
            "local_bounds",
            "anchors",
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

        component = source["component"]

        if not isinstance(
            component,
            AtlasSemanticReliefComponent,
        ):
            raise TypeError(
                "component must be an "
                "AtlasSemanticReliefComponent"
            )

        if component.semantic_class not in (
            "figurative_sculpture",
            "figurative_ornament",
        ):
            raise ValueError(
                "component semantic_class must be figurative"
            )

        result = AtlasGeometrySourceResult(
            normalized_geometry={
                "geometry_kind": (
                    "body_pose_prop_semantic_reference"
                ),
                "descriptor_status": (
                    "semantic_reference_only"
                ),
                "component_id": (
                    component.component_id
                ),
                "semantic_class": (
                    component.semantic_class
                ),
                "declared_geometry_source_kind": (
                    component.geometry_source_kind
                ),
                "source_reference": (
                    component.source_reference
                ),
                "output_modes": (
                    component.output_modes
                ),
                "material_role": (
                    component.material_role
                ),
                "physical_feature_policy": (
                    component.physical_feature_policy
                ),
            },
            local_bounds=source[
                "local_bounds"
            ],
            anchors=source[
                "anchors"
            ],
            confidence=component.confidence,
            provenance=component.provenance,
            supported_projection_modes=source[
                "supported_projection_modes"
            ],
        )

        return self.validate_result(
            result
        )
