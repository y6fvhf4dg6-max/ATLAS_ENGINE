import pytest

from CORE.atlas_urban_fabric_scene_contract import (
    AtlasUrbanFabricElement,
)


def test_urban_fabric_element_preserves_semantic_identity():
    element = AtlasUrbanFabricElement(
        element_id="road_123",
        semantic_class="road",
        source_id=123,
        source_type="osm_way",
        product_priority=0.75,
        lod_eligible=True,
        geometry_ref="road_geometry_123",
        related_element_ids=("block_9", "park_4"),
    )

    assert element.element_id == "road_123"
    assert element.semantic_class == "road"
    assert element.source_id == 123
    assert element.source_type == "osm_way"
    assert element.product_priority == pytest.approx(0.75)
    assert element.lod_eligible is True
    assert element.geometry_ref == "road_geometry_123"
    assert element.related_element_ids == (
        "block_9",
        "park_4",
    )


def test_urban_fabric_element_normalizes_identifiers():
    element = AtlasUrbanFabricElement(
        element_id="  ROAD Main  ",
        semantic_class="  Pedestrian Path ",
        related_element_ids=(
            " Block 9 ",
            "PARK 4",
        ),
    )

    assert element.element_id == "road_main"
    assert element.semantic_class == "pedestrian_path"
    assert element.related_element_ids == (
        "block_9",
        "park_4",
    )


@pytest.mark.parametrize(
    "field_name,value",
    [
        ("element_id", ""),
        ("semantic_class", "   "),
    ],
)
def test_urban_fabric_element_rejects_blank_identifiers(
    field_name,
    value,
):
    values = {
        "element_id": "road_1",
        "semantic_class": "road",
    }
    values[field_name] = value

    with pytest.raises(ValueError):
        AtlasUrbanFabricElement(**values)


@pytest.mark.parametrize(
    "value",
    [-0.01, 1.01, float("inf"), float("nan")],
)
def test_urban_fabric_element_rejects_invalid_product_priority(
    value,
):
    with pytest.raises(ValueError):
        AtlasUrbanFabricElement(
            element_id="road_1",
            semantic_class="road",
            product_priority=value,
        )


def test_urban_fabric_element_requires_boolean_lod_eligibility():
    with pytest.raises(TypeError):
        AtlasUrbanFabricElement(
            element_id="road_1",
            semantic_class="road",
            lod_eligible=1,
        )


def test_urban_fabric_element_rejects_duplicate_relationships():
    with pytest.raises(ValueError):
        AtlasUrbanFabricElement(
            element_id="road_1",
            semantic_class="road",
            related_element_ids=(
                "block_9",
                " Block 9 ",
            ),
        )


def test_urban_fabric_element_normalizes_optional_references():
    element = AtlasUrbanFabricElement(
        element_id="road_1",
        semantic_class="road",
        source_type="  OSM Way ",
        geometry_ref=" Road Geometry 1 ",
    )

    assert element.source_type == "osm_way"
    assert element.geometry_ref == "road_geometry_1"


@pytest.mark.parametrize(
    "field_name",
    [
        "source_type",
        "geometry_ref",
    ],
)
def test_urban_fabric_element_rejects_blank_optional_references(
    field_name,
):
    values = {
        "element_id": "road_1",
        "semantic_class": "road",
        field_name: "   ",
    }

    with pytest.raises(ValueError):
        AtlasUrbanFabricElement(**values)


def test_urban_fabric_element_preserves_numeric_source_id():
    element = AtlasUrbanFabricElement(
        element_id="road_1",
        semantic_class="road",
        source_id=123456,
    )

    assert element.source_id == 123456


def test_urban_fabric_element_normalizes_string_source_id():
    element = AtlasUrbanFabricElement(
        element_id="terrain_1",
        semantic_class="terrain",
        source_id=" COP30 Tile 7 ",
    )

    assert element.source_id == "cop30_tile_7"


def test_urban_fabric_element_rejects_blank_string_source_id():
    with pytest.raises(ValueError):
        AtlasUrbanFabricElement(
            element_id="road_1",
            semantic_class="road",
            source_id="   ",
        )


def test_urban_fabric_element_rejects_boolean_source_id():
    with pytest.raises(TypeError):
        AtlasUrbanFabricElement(
            element_id="road_1",
            semantic_class="road",
            source_id=True,
        )


from CORE.atlas_urban_fabric_scene_contract import (
    AtlasUrbanFabricScene,
)


def _element(
    element_id,
    semantic_class,
):
    return AtlasUrbanFabricElement(
        element_id=element_id,
        semantic_class=semantic_class,
    )


def test_urban_fabric_scene_preserves_elements():
    road = _element(
        "road_1",
        "road",
    )
    park = _element(
        "park_1",
        "park",
    )

    scene = AtlasUrbanFabricScene(
        elements=(
            road,
            park,
        )
    )

    assert scene.elements == (
        road,
        park,
    )


def test_urban_fabric_scene_rejects_duplicate_element_ids():
    with pytest.raises(ValueError):
        AtlasUrbanFabricScene(
            elements=(
                _element(
                    "road_1",
                    "road",
                ),
                _element(
                    " ROAD 1 ",
                    "park",
                ),
            )
        )


def test_urban_fabric_scene_finds_element_by_id():
    road = _element(
        "road_1",
        "road",
    )

    scene = AtlasUrbanFabricScene(
        elements=(road,)
    )

    assert scene.get_element(
        " ROAD 1 "
    ) is road
    assert scene.get_element(
        "missing"
    ) is None


def test_urban_fabric_scene_filters_semantic_class():
    road_1 = _element(
        "road_1",
        "road",
    )
    road_2 = _element(
        "road_2",
        "road",
    )
    park = _element(
        "park_1",
        "park",
    )

    scene = AtlasUrbanFabricScene(
        elements=(
            road_1,
            park,
            road_2,
        )
    )

    assert scene.elements_for_class(
        " ROAD "
    ) == (
        road_1,
        road_2,
    )


def test_urban_fabric_scene_accepts_valid_relationships():
    block = AtlasUrbanFabricElement(
        element_id="block_1",
        semantic_class="urban_block",
    )
    road = AtlasUrbanFabricElement(
        element_id="road_1",
        semantic_class="road",
        related_element_ids=("block_1",),
    )

    scene = AtlasUrbanFabricScene(
        elements=(
            block,
            road,
        )
    )

    assert scene.get_element("road_1") is road


def test_urban_fabric_scene_rejects_missing_relationship_targets():
    road = AtlasUrbanFabricElement(
        element_id="road_1",
        semantic_class="road",
        related_element_ids=("block_404",),
    )

    with pytest.raises(ValueError):
        AtlasUrbanFabricScene(
            elements=(road,)
        )


@pytest.mark.parametrize(
    "semantic_class",
    [
        "road",
        "railway",
        "pedestrian_path",
        "urban_block",
        "generic_building",
        "park",
        "plaza",
        "vegetation",
        "water",
        "infrastructure_corridor",
        "terrain",
    ],
)
def test_urban_fabric_element_accepts_required_semantic_classes(
    semantic_class,
):
    element = AtlasUrbanFabricElement(
        element_id=f"{semantic_class}_1",
        semantic_class=semantic_class,
    )

    assert element.semantic_class == semantic_class


def test_urban_fabric_element_allows_extensible_semantic_class():
    element = AtlasUrbanFabricElement(
        element_id="future_1",
        semantic_class="future_urban_class",
    )

    assert element.semantic_class == "future_urban_class"


from CORE.atlas_urban_fabric_scene_contract import (
    AtlasUrbanFabricRelationship,
)


def test_urban_fabric_relationship_preserves_semantics():
    relationship = AtlasUrbanFabricRelationship(
        relationship_id=" park path 1 ",
        relation_type=" Inside ",
        source_element_id=" path 1 ",
        target_element_id=" park 1 ",
    )

    assert relationship.relationship_id == "park_path_1"
    assert relationship.relation_type == "inside"
    assert relationship.source_element_id == "path_1"
    assert relationship.target_element_id == "park_1"


def test_urban_fabric_scene_preserves_typed_relationships():
    path = AtlasUrbanFabricElement(
        element_id="path_1",
        semantic_class="pedestrian_path",
    )
    park = AtlasUrbanFabricElement(
        element_id="park_1",
        semantic_class="park",
    )
    relationship = AtlasUrbanFabricRelationship(
        relationship_id="park_path_1",
        relation_type="inside",
        source_element_id="path_1",
        target_element_id="park_1",
    )

    scene = AtlasUrbanFabricScene(
        elements=(path, park),
        relationships=(relationship,),
    )

    assert scene.relationships == (relationship,)


def test_urban_fabric_scene_rejects_relationship_to_missing_element():
    road = AtlasUrbanFabricElement(
        element_id="road_1",
        semantic_class="road",
    )
    relationship = AtlasUrbanFabricRelationship(
        relationship_id="road_block_1",
        relation_type="borders",
        source_element_id="road_1",
        target_element_id="block_404",
    )

    with pytest.raises(ValueError):
        AtlasUrbanFabricScene(
            elements=(road,),
            relationships=(relationship,),
        )


def test_urban_fabric_scene_reports_present_semantic_classes():
    scene = AtlasUrbanFabricScene(
        elements=(
            AtlasUrbanFabricElement(
                element_id="road_1",
                semantic_class="road",
            ),
            AtlasUrbanFabricElement(
                element_id="park_1",
                semantic_class="park",
            ),
        )
    )

    assert scene.semantic_classes() == (
        "park",
        "road",
    )


def test_urban_fabric_scene_reports_missing_required_classes():
    scene = AtlasUrbanFabricScene(
        elements=(
            AtlasUrbanFabricElement(
                element_id="road_1",
                semantic_class="road",
            ),
        )
    )

    missing = scene.missing_required_semantic_classes()

    assert "road" not in missing
    assert "railway" in missing
    assert "terrain" in missing
    assert tuple(sorted(missing)) == missing
