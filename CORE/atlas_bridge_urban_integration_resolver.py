from __future__ import annotations

from collections.abc import Mapping

from shapely.geometry import LineString, Polygon

from CORE.atlas_urban_fabric_scene_contract import (
    AtlasUrbanFabricElement,
    AtlasUrbanFabricRelationship,
    AtlasUrbanFabricScene,
)


class AtlasBridgeUrbanIntegrationResolver:
    RELATIONSHIP_TYPES = {
        "road": "connects_road",
        "railway": "connects_railway",
        "water": "crosses_water",
        "shoreline": "meets_shoreline",
        "embankment": "meets_embankment",
        "urban_block": "adjacent_to_block",
        "terrain": "placed_on_terrain",
    }

    @staticmethod
    def resolve_bridge_element(
        source,
    ) -> AtlasUrbanFabricElement:
        if not isinstance(source, Mapping):
            raise TypeError(
                "bridge source must be a mapping"
            )

        source_id = source.get("id")

        if source_id is None:
            raise ValueError(
                "bridge source must include id"
            )

        source_type = source.get(
            "geometry_type",
            "way",
        )

        return AtlasUrbanFabricElement(
            element_id=f"bridge_{source_id}",
            semantic_class="bridge",
            source_id=source_id,
            source_type=source_type,
            product_priority=1.0,
            lod_eligible=True,
            geometry_ref=(
                f"bridge_source_{source_id}"
            ),
        )

    SEMANTIC_FAMILIES = {
        "road": {
            "road",
            "major_road",
            "local_road",
            "service_road",
            "pedestrian_path",
            "cycleway",
            "bridleway",
        },
        "railway": {
            "railway",
            "light_rail",
            "tram",
        },
        "water": {
            "water",
            "river",
            "canal",
            "lake",
            "coastline",
        },
        "shoreline": {
            "shoreline",
            "quay",
            "waterfront_pier",
            "marina",
        },
        "embankment": {
            "embankment",
        },
        "urban_block": {
            "urban_block",
        },
        "terrain": {
            "terrain",
        },
    }

    @classmethod
    def resolve_context_targets(
        cls,
        *,
        scene,
        context_source_ids,
    ):
        if not isinstance(
            scene,
            AtlasUrbanFabricScene,
        ):
            raise TypeError(
                "scene must be an "
                "AtlasUrbanFabricScene"
            )

        if not isinstance(
            context_source_ids,
            Mapping,
        ):
            raise TypeError(
                "context_source_ids must be a mapping"
            )

        result = {}

        for semantic_key, source_ids in (
            context_source_ids.items()
        ):
            normalized_key = (
                str(semantic_key)
                .strip()
                .lower()
            )

            allowed_classes = (
                cls.SEMANTIC_FAMILIES.get(
                    normalized_key,
                    set(),
                )
            )

            requested_ids = set(
                source_ids or ()
            )

            matches = tuple(
                element.element_id
                for element in scene.elements
                if (
                    element.semantic_class
                    in allowed_classes
                    and element.source_id
                    in requested_ids
                )
            )

            result[normalized_key] = matches

        return result

    @staticmethod
    def _source_shape(source):
        if not isinstance(source, Mapping):
            return None

        geometry = source.get(
            "geometry",
            (),
        )

        if not geometry or len(geometry) < 2:
            return None

        points = tuple(
            (
                float(point[0]),
                float(point[1]),
            )
            for point in geometry
        )

        if len(points) >= 3:
            polygon = Polygon(points)

            if (
                polygon.is_valid
                and not polygon.is_empty
                and polygon.area > 0.0
            ):
                return polygon

        line = LineString(points)

        if (
            line.is_empty
            or line.length <= 0.0
        ):
            return None

        return line

    @classmethod
    def resolve_geometry_context_source_ids(
        cls,
        *,
        bridge_source,
        context_sources,
    ):
        if not isinstance(
            bridge_source,
            Mapping,
        ):
            raise TypeError(
                "bridge_source must be a mapping"
            )

        if not isinstance(
            context_sources,
            Mapping,
        ):
            raise TypeError(
                "context_sources must be a mapping"
            )

        bridge_shape = cls._source_shape(
            bridge_source
        )

        result = {}

        for semantic_key, sources in (
            context_sources.items()
        ):
            normalized_key = (
                str(semantic_key)
                .strip()
                .lower()
            )

            matched_source_ids = []

            if bridge_shape is not None:
                for source in sources or ():
                    source_shape = cls._source_shape(
                        source
                    )

                    if source_shape is None:
                        continue

                    if not bridge_shape.intersects(
                        source_shape
                    ):
                        continue

                    source_id = source.get(
                        "id"
                    )

                    if source_id is None:
                        continue

                    matched_source_ids.append(
                        source_id
                    )

            result[normalized_key] = tuple(
                matched_source_ids
            )

        return result

    @staticmethod
    def resolve_approach_continuity(
        *,
        bridge_mesh,
    ):
        if not isinstance(
            bridge_mesh,
            Mapping,
        ):
            raise TypeError(
                "bridge_mesh must be a mapping"
            )

        approaches = tuple(
            bridge_mesh.get(
                "road_approaches",
                (),
            )
            or ()
        )

        if not approaches:
            return {
                "available": False,
                "approach_count": 0,
                "road_mesh_indices": (),
                "maximum_source_distance_mm": None,
                "total_approach_length_mm": 0.0,
            }

        road_mesh_indices = tuple(
            int(
                approach[
                    "road_mesh_index"
                ]
            )
            for approach in approaches
        )

        source_distances = tuple(
            float(
                approach[
                    "source_distance_mm"
                ]
            )
            for approach in approaches
        )

        lengths = tuple(
            float(
                approach[
                    "length_mm"
                ]
            )
            for approach in approaches
        )

        return {
            "available": True,
            "approach_count": len(
                approaches
            ),
            "road_mesh_indices": (
                road_mesh_indices
            ),
            "maximum_source_distance_mm": max(
                source_distances
            ),
            "total_approach_length_mm": sum(
                lengths
            ),
        }

    @classmethod
    def resolve_visual_lod_coordination(
        cls,
        *,
        scene,
        bridge_element_id,
    ):
        if not isinstance(
            scene,
            AtlasUrbanFabricScene,
        ):
            raise TypeError(
                "scene must be an "
                "AtlasUrbanFabricScene"
            )

        bridge = scene.get_element(
            bridge_element_id
        )

        if bridge is None:
            raise ValueError(
                "bridge element must exist in scene"
            )

        if bridge.semantic_class != "bridge":
            raise ValueError(
                "bridge_element_id must reference "
                "a bridge element"
            )

        related_ids = []

        for relationship in scene.relationships:
            if (
                relationship.source_element_id
                == bridge.element_id
            ):
                related_ids.append(
                    relationship.target_element_id
                )
            elif (
                relationship.target_element_id
                == bridge.element_id
            ):
                related_ids.append(
                    relationship.source_element_id
                )

        ordered_related_ids = tuple(
            dict.fromkeys(
                related_ids
            )
        )

        related_elements = tuple(
            scene.get_element(
                element_id
            )
            for element_id in ordered_related_ids
        )

        related_lod_eligible_ids = tuple(
            element.element_id
            for element in related_elements
            if (
                element is not None
                and element.lod_eligible
            )
        )

        related_priorities = tuple(
            element.product_priority
            for element in related_elements
            if element is not None
        )

        bridge_has_visual_priority = (
            all(
                bridge.product_priority
                >= priority
                for priority in related_priorities
            )
        )

        coordinate_lod_with_context = (
            bridge.lod_eligible
            and bool(
                related_lod_eligible_ids
            )
        )

        return {
            "bridge_product_priority": (
                bridge.product_priority
            ),
            "bridge_lod_eligible": (
                bridge.lod_eligible
            ),
            "related_element_ids": (
                ordered_related_ids
            ),
            "related_lod_eligible_ids": (
                related_lod_eligible_ids
            ),
            "bridge_has_visual_priority": (
                bridge_has_visual_priority
            ),
            "coordinate_lod_with_context": (
                coordinate_lod_with_context
            ),
        }

    @classmethod
    def resolve_integration_record(
        cls,
        *,
        bridge_source,
        bridge_mesh,
    ):
        bridge_element = cls.resolve_bridge_element(
            bridge_source
        )

        continuity = cls.resolve_approach_continuity(
            bridge_mesh=bridge_mesh,
        )

        return {
            "bridge_element_id": (
                bridge_element.element_id
            ),
            "approach_road_continuity": (
                continuity["available"]
            ),
            "approach_count": (
                continuity["approach_count"]
            ),
            "approach_road_mesh_indices": (
                continuity["road_mesh_indices"]
            ),
            "maximum_approach_source_distance_mm": (
                continuity[
                    "maximum_source_distance_mm"
                ]
            ),
            "total_approach_length_mm": (
                continuity[
                    "total_approach_length_mm"
                ]
            ),
            "existing_bridge_topology_preserved": True,
            "bridge_geometry_rewritten": False,
        }

    @classmethod
    def integrate_from_geometry_context(
        cls,
        *,
        scene,
        bridge_source,
        context_sources,
    ) -> AtlasUrbanFabricScene:
        context_source_ids = (
            cls.resolve_geometry_context_source_ids(
                bridge_source=bridge_source,
                context_sources=context_sources,
            )
        )

        return cls.integrate_from_context(
            scene=scene,
            bridge_source=bridge_source,
            context_source_ids=(
                context_source_ids
            ),
        )

    @classmethod
    def integrate_from_context(
        cls,
        *,
        scene,
        bridge_source,
        context_source_ids,
    ) -> AtlasUrbanFabricScene:
        target_element_ids = (
            cls.resolve_context_targets(
                scene=scene,
                context_source_ids=(
                    context_source_ids
                ),
            )
        )

        return cls.integrate(
            scene=scene,
            bridge_source=bridge_source,
            target_element_ids=(
                target_element_ids
            ),
        )

    @classmethod
    def integrate(
        cls,
        *,
        scene,
        bridge_source,
        target_element_ids,
    ) -> AtlasUrbanFabricScene:
        if not isinstance(
            scene,
            AtlasUrbanFabricScene,
        ):
            raise TypeError(
                "scene must be an "
                "AtlasUrbanFabricScene"
            )

        if not isinstance(
            target_element_ids,
            Mapping,
        ):
            raise TypeError(
                "target_element_ids must be a mapping"
            )

        bridge = cls.resolve_bridge_element(
            bridge_source
        )

        existing_ids = {
            element.element_id
            for element in scene.elements
        }

        if bridge.element_id in existing_ids:
            raise ValueError(
                "bridge element already exists in scene"
            )

        relationships = list(
            scene.relationships
        )

        for semantic_key, targets in (
            target_element_ids.items()
        ):
            relation_type = (
                cls.RELATIONSHIP_TYPES.get(
                    str(semantic_key)
                    .strip()
                    .lower()
                )
            )

            if relation_type is None:
                continue

            for target_id in targets or ():
                normalized_target = (
                    str(target_id)
                    .strip()
                    .lower()
                )

                if normalized_target not in existing_ids:
                    raise ValueError(
                        "bridge relationship target "
                        "must exist in scene"
                    )

                relationships.append(
                    AtlasUrbanFabricRelationship(
                        relationship_id=(
                            f"{bridge.element_id}_"
                            f"{relation_type}_"
                            f"{normalized_target}"
                        ),
                        relation_type=relation_type,
                        source_element_id=(
                            bridge.element_id
                        ),
                        target_element_id=(
                            normalized_target
                        ),
                    )
                )

        return AtlasUrbanFabricScene(
            elements=(
                *scene.elements,
                bridge,
            ),
            relationships=tuple(
                relationships
            ),
        )
