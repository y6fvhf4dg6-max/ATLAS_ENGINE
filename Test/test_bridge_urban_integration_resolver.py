from CORE.atlas_bridge_urban_integration_resolver import (
    AtlasBridgeUrbanIntegrationResolver,
)
from CORE.atlas_urban_fabric_scene_contract import (
    AtlasUrbanFabricElement,
    AtlasUrbanFabricScene,
)


def _bridge_source():
    return {
        "id": 81523,
        "geometry_type": "way",
        "geometry": (
            (41.0190, 28.9720),
            (41.0200, 28.9730),
            (41.0210, 28.9740),
        ),
        "tags": {
            "man_made": "bridge",
            "name": "Generic Bridge",
        },
    }


def test_resolves_bridge_as_urban_fabric_element_without_rewriting_geometry():
    source = _bridge_source()

    element = (
        AtlasBridgeUrbanIntegrationResolver
        .resolve_bridge_element(source)
    )

    assert isinstance(
        element,
        AtlasUrbanFabricElement,
    )
    assert element.element_id == "bridge_81523"
    assert element.semantic_class == "bridge"
    assert element.source_id == 81523
    assert element.source_type == "way"
    assert element.geometry_ref == "bridge_source_81523"
    assert element.product_priority == 1.0
    assert element.lod_eligible is True

    assert source["geometry"] == (
        (41.0190, 28.9720),
        (41.0200, 28.9730),
        (41.0210, 28.9740),
    )


def test_bridge_relationship_types_cover_required_8_11_context():
    relationship_types = (
        AtlasBridgeUrbanIntegrationResolver
        .RELATIONSHIP_TYPES
    )

    assert relationship_types == {
        "road": "connects_road",
        "railway": "connects_railway",
        "water": "crosses_water",
        "shoreline": "meets_shoreline",
        "embankment": "meets_embankment",
        "urban_block": "adjacent_to_block",
        "terrain": "placed_on_terrain",
    }


def test_integrates_bridge_with_existing_urban_fabric_scene():
    scene = AtlasUrbanFabricScene(
        elements=(
            AtlasUrbanFabricElement(
                element_id="road_1",
                semantic_class="road",
                source_id=1,
            ),
            AtlasUrbanFabricElement(
                element_id="water_2",
                semantic_class="water",
                source_id=2,
            ),
            AtlasUrbanFabricElement(
                element_id="terrain_main",
                semantic_class="terrain",
            ),
        ),
    )

    resolved = (
        AtlasBridgeUrbanIntegrationResolver
        .integrate(
            scene=scene,
            bridge_source=_bridge_source(),
            target_element_ids={
                "road": ("road_1",),
                "water": ("water_2",),
                "terrain": ("terrain_main",),
            },
        )
    )

    assert isinstance(
        resolved,
        AtlasUrbanFabricScene,
    )

    assert resolved.get_element(
        "bridge_81523"
    ) is not None

    assert {
        relationship.relation_type
        for relationship in resolved.relationships
    } == {
        "connects_road",
        "crosses_water",
        "placed_on_terrain",
    }


def test_bridge_integration_preserves_existing_scene_elements():
    road = AtlasUrbanFabricElement(
        element_id="road_1",
        semantic_class="road",
        source_id=1,
    )

    scene = AtlasUrbanFabricScene(
        elements=(road,),
    )

    resolved = (
        AtlasBridgeUrbanIntegrationResolver
        .integrate(
            scene=scene,
            bridge_source=_bridge_source(),
            target_element_ids={
                "road": ("road_1",),
            },
        )
    )

    assert resolved.get_element("road_1") is road
    assert len(resolved.elements) == 2


def test_resolves_bridge_context_targets_by_source_identity():
    scene = AtlasUrbanFabricScene(
        elements=(
            AtlasUrbanFabricElement(
                element_id="road_primary_20",
                semantic_class="major_road",
                source_id=20,
            ),
            AtlasUrbanFabricElement(
                element_id="rail_30",
                semantic_class="railway",
                source_id=30,
            ),
            AtlasUrbanFabricElement(
                element_id="water_40",
                semantic_class="water",
                source_id=40,
            ),
            AtlasUrbanFabricElement(
                element_id="shoreline_50",
                semantic_class="shoreline",
                source_id=50,
            ),
            AtlasUrbanFabricElement(
                element_id="embankment_60",
                semantic_class="embankment",
                source_id=60,
            ),
            AtlasUrbanFabricElement(
                element_id="block_70",
                semantic_class="urban_block",
                source_id=70,
            ),
            AtlasUrbanFabricElement(
                element_id="terrain_main",
                semantic_class="terrain",
                source_id="terrain-main",
            ),
        ),
    )

    targets = (
        AtlasBridgeUrbanIntegrationResolver
        .resolve_context_targets(
            scene=scene,
            context_source_ids={
                "road": (20,),
                "railway": (30,),
                "water": (40,),
                "shoreline": (50,),
                "embankment": (60,),
                "urban_block": (70,),
                "terrain": ("terrain-main",),
            },
        )
    )

    assert targets == {
        "road": ("road_primary_20",),
        "railway": ("rail_30",),
        "water": ("water_40",),
        "shoreline": ("shoreline_50",),
        "embankment": ("embankment_60",),
        "urban_block": ("block_70",),
        "terrain": ("terrain_main",),
    }


def test_context_target_resolver_understands_road_hierarchy_classes():
    scene = AtlasUrbanFabricScene(
        elements=(
            AtlasUrbanFabricElement(
                element_id="major_road_1",
                semantic_class="major_road",
                source_id=1,
            ),
            AtlasUrbanFabricElement(
                element_id="local_road_2",
                semantic_class="local_road",
                source_id=2,
            ),
            AtlasUrbanFabricElement(
                element_id="service_road_3",
                semantic_class="service_road",
                source_id=3,
            ),
        ),
    )

    targets = (
        AtlasBridgeUrbanIntegrationResolver
        .resolve_context_targets(
            scene=scene,
            context_source_ids={
                "road": (1, 2, 3),
            },
        )
    )

    assert targets["road"] == (
        "major_road_1",
        "local_road_2",
        "service_road_3",
    )


def test_context_target_resolver_understands_rail_family():
    scene = AtlasUrbanFabricScene(
        elements=(
            AtlasUrbanFabricElement(
                element_id="rail_1",
                semantic_class="railway",
                source_id=1,
            ),
            AtlasUrbanFabricElement(
                element_id="light_rail_2",
                semantic_class="light_rail",
                source_id=2,
            ),
            AtlasUrbanFabricElement(
                element_id="tram_3",
                semantic_class="tram",
                source_id=3,
            ),
        ),
    )

    targets = (
        AtlasBridgeUrbanIntegrationResolver
        .resolve_context_targets(
            scene=scene,
            context_source_ids={
                "railway": (1, 2, 3),
            },
        )
    )

    assert targets["railway"] == (
        "rail_1",
        "light_rail_2",
        "tram_3",
    )


def test_context_target_resolver_does_not_link_wrong_semantic_family():
    scene = AtlasUrbanFabricScene(
        elements=(
            AtlasUrbanFabricElement(
                element_id="building_20",
                semantic_class="generic_building",
                source_id=20,
            ),
        ),
    )

    targets = (
        AtlasBridgeUrbanIntegrationResolver
        .resolve_context_targets(
            scene=scene,
            context_source_ids={
                "road": (20,),
            },
        )
    )

    assert targets == {
        "road": (),
    }


def test_integrate_from_context_resolves_and_connects_required_scene_families():
    scene = AtlasUrbanFabricScene(
        elements=(
            AtlasUrbanFabricElement(
                element_id="major_road_20",
                semantic_class="major_road",
                source_id=20,
            ),
            AtlasUrbanFabricElement(
                element_id="tram_30",
                semantic_class="tram",
                source_id=30,
            ),
            AtlasUrbanFabricElement(
                element_id="water_40",
                semantic_class="water",
                source_id=40,
            ),
            AtlasUrbanFabricElement(
                element_id="quay_50",
                semantic_class="quay",
                source_id=50,
            ),
            AtlasUrbanFabricElement(
                element_id="embankment_60",
                semantic_class="embankment",
                source_id=60,
            ),
            AtlasUrbanFabricElement(
                element_id="block_70",
                semantic_class="urban_block",
                source_id=70,
            ),
            AtlasUrbanFabricElement(
                element_id="terrain_main",
                semantic_class="terrain",
                source_id="terrain-main",
            ),
        ),
    )

    resolved = (
        AtlasBridgeUrbanIntegrationResolver
        .integrate_from_context(
            scene=scene,
            bridge_source=_bridge_source(),
            context_source_ids={
                "road": (20,),
                "railway": (30,),
                "water": (40,),
                "shoreline": (50,),
                "embankment": (60,),
                "urban_block": (70,),
                "terrain": ("terrain-main",),
            },
        )
    )

    bridge = resolved.get_element(
        "bridge_81523"
    )

    assert bridge is not None

    assert {
        relationship.relation_type
        for relationship in resolved.relationships
    } == {
        "connects_road",
        "connects_railway",
        "crosses_water",
        "meets_shoreline",
        "meets_embankment",
        "adjacent_to_block",
        "placed_on_terrain",
    }


def test_integrate_from_context_does_not_invent_missing_relationships():
    scene = AtlasUrbanFabricScene(
        elements=(
            AtlasUrbanFabricElement(
                element_id="water_40",
                semantic_class="water",
                source_id=40,
            ),
        ),
    )

    resolved = (
        AtlasBridgeUrbanIntegrationResolver
        .integrate_from_context(
            scene=scene,
            bridge_source=_bridge_source(),
            context_source_ids={
                "water": (40,),
                "road": (999,),
                "railway": (998,),
            },
        )
    )

    assert {
        relationship.relation_type
        for relationship in resolved.relationships
    } == {
        "crosses_water",
    }


def test_resolves_geometry_context_from_real_source_intersections():
    bridge_source = {
        "id": 100,
        "geometry_type": "way",
        "geometry": (
            (50.0000, 8.0000),
            (50.0000, 8.2000),
        ),
        "tags": {
            "bridge": "yes",
        },
    }

    context_sources = {
        "road": (
            {
                "id": 200,
                "geometry": (
                    (49.9500, 8.1000),
                    (50.0500, 8.1000),
                ),
                "tags": {
                    "highway": "primary",
                },
            },
        ),
        "railway": (
            {
                "id": 300,
                "geometry": (
                    (49.9500, 8.1500),
                    (50.0500, 8.1500),
                ),
                "tags": {
                    "railway": "tram",
                },
            },
        ),
        "water": (
            {
                "id": 400,
                "geometry": (
                    (49.9900, 8.0500),
                    (49.9900, 8.1800),
                    (50.0100, 8.1800),
                    (50.0100, 8.0500),
                    (49.9900, 8.0500),
                ),
                "tags": {
                    "waterway": "river",
                },
            },
        ),
        "shoreline": (
            {
                "id": 500,
                "geometry": (
                    (50.0000, 8.0000),
                    (50.0500, 8.0000),
                ),
                "tags": {
                    "man_made": "quay",
                },
            },
        ),
        "embankment": (
            {
                "id": 600,
                "geometry": (
                    (50.0000, 8.2000),
                    (50.0500, 8.2000),
                ),
                "tags": {
                    "man_made": "embankment",
                },
            },
        ),
    }

    resolved = (
        AtlasBridgeUrbanIntegrationResolver
        .resolve_geometry_context_source_ids(
            bridge_source=bridge_source,
            context_sources=context_sources,
        )
    )

    assert resolved == {
        "road": (200,),
        "railway": (300,),
        "water": (400,),
        "shoreline": (500,),
        "embankment": (600,),
    }


def test_geometry_context_does_not_invent_distant_relationships():
    bridge_source = {
        "id": 101,
        "geometry_type": "way",
        "geometry": (
            (50.0000, 8.0000),
            (50.0000, 8.1000),
        ),
        "tags": {
            "bridge": "yes",
        },
    }

    resolved = (
        AtlasBridgeUrbanIntegrationResolver
        .resolve_geometry_context_source_ids(
            bridge_source=bridge_source,
            context_sources={
                "road": (
                    {
                        "id": 201,
                        "geometry": (
                            (51.0000, 9.0000),
                            (51.1000, 9.1000),
                        ),
                        "tags": {
                            "highway": "secondary",
                        },
                    },
                ),
            },
        )
    )

    assert resolved == {
        "road": (),
    }


def test_geometry_context_preserves_bridge_source_geometry():
    geometry = (
        (50.0000, 8.0000),
        (50.0000, 8.1000),
    )

    bridge_source = {
        "id": 102,
        "geometry_type": "way",
        "geometry": geometry,
        "tags": {
            "bridge": "yes",
        },
    }

    AtlasBridgeUrbanIntegrationResolver.resolve_geometry_context_source_ids(
        bridge_source=bridge_source,
        context_sources={},
    )

    assert bridge_source["geometry"] == geometry


def test_integrate_from_geometry_context_builds_typed_bridge_relationships():
    scene = AtlasUrbanFabricScene(
        elements=(
            AtlasUrbanFabricElement(
                element_id="major_road_200",
                semantic_class="major_road",
                source_id=200,
            ),
            AtlasUrbanFabricElement(
                element_id="tram_300",
                semantic_class="tram",
                source_id=300,
            ),
            AtlasUrbanFabricElement(
                element_id="water_400",
                semantic_class="water",
                source_id=400,
            ),
            AtlasUrbanFabricElement(
                element_id="quay_500",
                semantic_class="quay",
                source_id=500,
            ),
            AtlasUrbanFabricElement(
                element_id="embankment_600",
                semantic_class="embankment",
                source_id=600,
            ),
        ),
    )

    bridge_source = {
        "id": 100,
        "geometry_type": "way",
        "geometry": (
            (50.0000, 8.0000),
            (50.0000, 8.2000),
        ),
        "tags": {
            "bridge": "yes",
        },
    }

    context_sources = {
        "road": (
            {
                "id": 200,
                "geometry": (
                    (49.9500, 8.1000),
                    (50.0500, 8.1000),
                ),
                "tags": {
                    "highway": "primary",
                },
            },
        ),
        "railway": (
            {
                "id": 300,
                "geometry": (
                    (49.9500, 8.1500),
                    (50.0500, 8.1500),
                ),
                "tags": {
                    "railway": "tram",
                },
            },
        ),
        "water": (
            {
                "id": 400,
                "geometry": (
                    (49.9900, 8.0500),
                    (49.9900, 8.1800),
                    (50.0100, 8.1800),
                    (50.0100, 8.0500),
                    (49.9900, 8.0500),
                ),
                "tags": {
                    "waterway": "river",
                },
            },
        ),
        "shoreline": (
            {
                "id": 500,
                "geometry": (
                    (50.0000, 8.0000),
                    (50.0500, 8.0000),
                ),
                "tags": {
                    "man_made": "quay",
                },
            },
        ),
        "embankment": (
            {
                "id": 600,
                "geometry": (
                    (50.0000, 8.2000),
                    (50.0500, 8.2000),
                ),
                "tags": {
                    "man_made": "embankment",
                },
            },
        ),
    }

    resolved = (
        AtlasBridgeUrbanIntegrationResolver
        .integrate_from_geometry_context(
            scene=scene,
            bridge_source=bridge_source,
            context_sources=context_sources,
        )
    )

    assert resolved.get_element(
        "bridge_100"
    ) is not None

    assert {
        relationship.relation_type
        for relationship in resolved.relationships
    } == {
        "connects_road",
        "connects_railway",
        "crosses_water",
        "meets_shoreline",
        "meets_embankment",
    }


def test_integrate_from_geometry_context_does_not_link_distant_scene_sources():
    scene = AtlasUrbanFabricScene(
        elements=(
            AtlasUrbanFabricElement(
                element_id="road_201",
                semantic_class="road",
                source_id=201,
            ),
        ),
    )

    resolved = (
        AtlasBridgeUrbanIntegrationResolver
        .integrate_from_geometry_context(
            scene=scene,
            bridge_source={
                "id": 101,
                "geometry_type": "way",
                "geometry": (
                    (50.0000, 8.0000),
                    (50.0000, 8.1000),
                ),
                "tags": {
                    "bridge": "yes",
                },
            },
            context_sources={
                "road": (
                    {
                        "id": 201,
                        "geometry": (
                            (51.0000, 9.0000),
                            (51.1000, 9.1000),
                        ),
                        "tags": {
                            "highway": "secondary",
                        },
                    },
                ),
            },
        )
    )

    assert resolved.get_element(
        "bridge_101"
    ) is not None

    assert resolved.relationships == ()


def test_resolves_existing_bridge_approach_continuity_metadata():
    bridge_mesh = {
        "road_approaches": (
            {
                "road_mesh_index": 3,
                "source_distance_mm": 0.75,
                "length_mm": 1.25,
                "start_edge": (
                    (0.0, -3.0),
                    (0.0, 3.0),
                ),
                "target_edge": (
                    (-1.25, -3.0),
                    (-1.25, 3.0),
                ),
            },
            {
                "road_mesh_index": 7,
                "source_distance_mm": 0.50,
                "length_mm": 1.00,
                "start_edge": (
                    (20.0, -3.0),
                    (20.0, 3.0),
                ),
                "target_edge": (
                    (21.0, -3.0),
                    (21.0, 3.0),
                ),
            },
        ),
    }

    continuity = (
        AtlasBridgeUrbanIntegrationResolver
        .resolve_approach_continuity(
            bridge_mesh=bridge_mesh,
        )
    )

    assert continuity == {
        "available": True,
        "approach_count": 2,
        "road_mesh_indices": (3, 7),
        "maximum_source_distance_mm": 0.75,
        "total_approach_length_mm": 2.25,
    }


def test_approach_continuity_reports_absent_without_existing_geometry():
    continuity = (
        AtlasBridgeUrbanIntegrationResolver
        .resolve_approach_continuity(
            bridge_mesh={
                "road_approaches": (),
            },
        )
    )

    assert continuity == {
        "available": False,
        "approach_count": 0,
        "road_mesh_indices": (),
        "maximum_source_distance_mm": None,
        "total_approach_length_mm": 0.0,
    }


def test_bridge_integration_record_exposes_existing_approach_continuity():
    bridge_source = _bridge_source()

    bridge_mesh = {
        "road_approaches": (
            {
                "road_mesh_index": 2,
                "source_distance_mm": 0.60,
                "length_mm": 1.20,
            },
            {
                "road_mesh_index": 5,
                "source_distance_mm": 0.80,
                "length_mm": 1.40,
            },
        ),
    }

    record = (
        AtlasBridgeUrbanIntegrationResolver
        .resolve_integration_record(
            bridge_source=bridge_source,
            bridge_mesh=bridge_mesh,
        )
    )

    assert record["bridge_element_id"] == "bridge_81523"
    assert record["approach_road_continuity"] is True
    assert record["approach_count"] == 2
    assert record["approach_road_mesh_indices"] == (
        2,
        5,
    )
    assert record["maximum_approach_source_distance_mm"] == 0.80
    assert record["existing_bridge_topology_preserved"] is True
    assert record["bridge_geometry_rewritten"] is False


def test_bridge_integration_record_handles_bridge_without_approaches():
    record = (
        AtlasBridgeUrbanIntegrationResolver
        .resolve_integration_record(
            bridge_source=_bridge_source(),
            bridge_mesh={
                "road_approaches": (),
            },
        )
    )

    assert record["approach_road_continuity"] is False
    assert record["approach_count"] == 0
    assert record["approach_road_mesh_indices"] == ()
    assert record["maximum_approach_source_distance_mm"] is None
    assert record["existing_bridge_topology_preserved"] is True
    assert record["bridge_geometry_rewritten"] is False


def test_resolves_bridge_visual_priority_and_lod_coordination():
    bridge = AtlasUrbanFabricElement(
        element_id="bridge_100",
        semantic_class="bridge",
        source_id=100,
        product_priority=1.0,
        lod_eligible=True,
    )

    road = AtlasUrbanFabricElement(
        element_id="road_200",
        semantic_class="major_road",
        source_id=200,
        product_priority=0.90,
        lod_eligible=True,
    )

    railway = AtlasUrbanFabricElement(
        element_id="rail_300",
        semantic_class="railway",
        source_id=300,
        product_priority=0.85,
        lod_eligible=True,
    )

    water = AtlasUrbanFabricElement(
        element_id="water_400",
        semantic_class="water",
        source_id=400,
        product_priority=0.70,
        lod_eligible=True,
    )

    scene = AtlasUrbanFabricScene(
        elements=(
            bridge,
            road,
            railway,
            water,
        ),
        relationships=(
            __import__(
                "CORE.atlas_urban_fabric_scene_contract",
                fromlist=["AtlasUrbanFabricRelationship"],
            ).AtlasUrbanFabricRelationship(
                relationship_id="bridge_road",
                relation_type="connects_road",
                source_element_id="bridge_100",
                target_element_id="road_200",
            ),
            __import__(
                "CORE.atlas_urban_fabric_scene_contract",
                fromlist=["AtlasUrbanFabricRelationship"],
            ).AtlasUrbanFabricRelationship(
                relationship_id="bridge_rail",
                relation_type="connects_railway",
                source_element_id="bridge_100",
                target_element_id="rail_300",
            ),
            __import__(
                "CORE.atlas_urban_fabric_scene_contract",
                fromlist=["AtlasUrbanFabricRelationship"],
            ).AtlasUrbanFabricRelationship(
                relationship_id="bridge_water",
                relation_type="crosses_water",
                source_element_id="bridge_100",
                target_element_id="water_400",
            ),
        ),
    )

    policy = (
        AtlasBridgeUrbanIntegrationResolver
        .resolve_visual_lod_coordination(
            scene=scene,
            bridge_element_id="bridge_100",
        )
    )

    assert policy == {
        "bridge_product_priority": 1.0,
        "bridge_lod_eligible": True,
        "related_element_ids": (
            "road_200",
            "rail_300",
            "water_400",
        ),
        "related_lod_eligible_ids": (
            "road_200",
            "rail_300",
            "water_400",
        ),
        "bridge_has_visual_priority": True,
        "coordinate_lod_with_context": True,
    }


def test_visual_lod_coordination_does_not_force_ineligible_context_into_lod():
    bridge = AtlasUrbanFabricElement(
        element_id="bridge_100",
        semantic_class="bridge",
        source_id=100,
        product_priority=1.0,
        lod_eligible=True,
    )

    context = AtlasUrbanFabricElement(
        element_id="context_200",
        semantic_class="infrastructure_corridor",
        source_id=200,
        product_priority=0.5,
        lod_eligible=False,
    )

    relationship = __import__(
        "CORE.atlas_urban_fabric_scene_contract",
        fromlist=["AtlasUrbanFabricRelationship"],
    ).AtlasUrbanFabricRelationship(
        relationship_id="bridge_context",
        relation_type="connects_road",
        source_element_id="bridge_100",
        target_element_id="context_200",
    )

    scene = AtlasUrbanFabricScene(
        elements=(bridge, context),
        relationships=(relationship,),
    )

    policy = (
        AtlasBridgeUrbanIntegrationResolver
        .resolve_visual_lod_coordination(
            scene=scene,
            bridge_element_id="bridge_100",
        )
    )

    assert policy["related_element_ids"] == (
        "context_200",
    )
    assert policy["related_lod_eligible_ids"] == ()
    assert policy["coordinate_lod_with_context"] is False
