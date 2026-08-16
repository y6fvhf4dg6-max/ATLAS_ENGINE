from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from CORE.atlas_geometry_source_adapter import (
    AtlasGeometrySourceAdapter,
)
from CORE.atlas_geometry_source_result import (
    AtlasGeometrySourceResult,
)
from CORE.atlas_master_landmark_catalog import (
    AtlasMasterLandmarkCatalog,
)


class AtlasCatalogComponentGeometrySourceAdapter(
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
            "component_role",
            "component_geometry_kind",
            "instance_index",
            "local_bounds",
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

        entry = AtlasMasterLandmarkCatalog.resolve(
            wikidata_id=source.get(
                "wikidata_id"
            ),
            osm_id=source.get(
                "osm_id"
            ),
        )

        if entry is None:
            raise ValueError(
                "catalog entry could not be resolved"
            )

        component_role = self._normalized_identifier(
            source["component_role"],
            field_name="component_role",
        )

        component_geometry_kind = (
            self._normalized_identifier(
                source[
                    "component_geometry_kind"
                ],
                field_name=(
                    "component_geometry_kind"
                ),
            )
        )

        instance_index = source[
            "instance_index"
        ]

        if (
            isinstance(instance_index, bool)
            or not isinstance(
                instance_index,
                int,
            )
            or instance_index < 0
        ):
            raise ValueError(
                "instance_index must be a "
                "non-negative integer"
            )

        if (
            entry.component_flags
            and component_role
            not in entry.component_flags
        ):
            raise ValueError(
                "component_role is not declared "
                "by catalog entry"
            )

        result = AtlasGeometrySourceResult(
            normalized_geometry={
                "geometry_kind": (
                    "catalog_component"
                ),
                "catalog_key": entry.key,
                "landmark_family": (
                    entry.landmark_family
                ),
                "wikidata_id": (
                    entry.wikidata_id
                ),
                "osm_ids": entry.osm_ids,
                "grammar_name": (
                    entry.grammar_name
                ),
                "profile_name": (
                    entry.profile_name
                ),
                "component_flags": (
                    entry.component_flags
                ),
                "geometry_overrides": (
                    entry.geometry_overrides
                ),
                "component_role": (
                    component_role
                ),
                "component_geometry_kind": (
                    component_geometry_kind
                ),
                "instance_index": (
                    instance_index
                ),
            },
            local_bounds=source[
                "local_bounds"
            ],
            anchors=source["anchors"],
            confidence=source[
                "confidence"
            ],
            provenance=source[
                "provenance"
            ],
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
