import pytest

from CORE.atlas_lod_level_catalog import (
    AtlasLoDLevelCatalog,
)
from CORE.atlas_city_composition_lod_resolver import (
    AtlasCityCompositionLoDResolver,
)


def test_city_composition_lod_preserves_landmarks_and_major_structure():
    lod = AtlasLoDLevelCatalog.resolve(2)

    result = AtlasCityCompositionLoDResolver.resolve(
        semantic_class="landmark",
        product_priority=1.0,
        product_size_mm=150.0,
        scene_morphology="historic_core",
        landmark_proximity_m=0.0,
        printable=True,
        lod_level=lod,
    )

    assert result["retain"] is True
    assert result["simplify"] is False
    assert result["narrative_priority"] > 0.90


@pytest.mark.parametrize(
    "semantic_class,expected_retain",
    [
        ("major_road", True),
        ("railway", True),
        ("park", True),
        ("water", True),
        ("minor_path", False),
    ],
)
def test_city_composition_lod_uses_urban_semantics(
    semantic_class,
    expected_retain,
):
    result = AtlasCityCompositionLoDResolver.resolve(
        semantic_class=semantic_class,
        product_priority=0.50,
        product_size_mm=140.0,
        scene_morphology="dense_urban",
        landmark_proximity_m=100.0,
        printable=True,
        lod_level=AtlasLoDLevelCatalog.resolve(1),
    )

    assert result["retain"] is expected_retain


def test_city_composition_lod_can_simplify_generic_urban_fabric():
    result = AtlasCityCompositionLoDResolver.resolve(
        semantic_class="generic_building",
        product_priority=0.35,
        product_size_mm=140.0,
        scene_morphology="dense_urban",
        landmark_proximity_m=120.0,
        printable=True,
        lod_level=AtlasLoDLevelCatalog.resolve(1),
    )

    assert result["retain"] is True
    assert result["simplify"] is True


def test_city_composition_lod_rejects_unprintable_minor_detail():
    result = AtlasCityCompositionLoDResolver.resolve(
        semantic_class="minor_path",
        product_priority=0.20,
        product_size_mm=100.0,
        scene_morphology="dense_urban",
        landmark_proximity_m=200.0,
        printable=False,
        lod_level=AtlasLoDLevelCatalog.resolve(0),
    )

    assert result["retain"] is False
    assert result["reason"] == "suppressed_minor_unprintable"


def test_city_composition_lod_keeps_existing_lod_contract():
    lod = AtlasLoDLevelCatalog.resolve(3)

    result = AtlasCityCompositionLoDResolver.resolve(
        semantic_class="tree_row",
        product_priority=0.45,
        product_size_mm=150.0,
        scene_morphology="suburban",
        landmark_proximity_m=80.0,
        printable=True,
        lod_level=lod,
    )

    assert result["lod_level"] is lod


from CORE.atlas_urban_fabric_scene_contract import (
    AtlasUrbanFabricElement,
)


def test_city_composition_lod_resolves_scene_element_collection():
    elements = (
        AtlasUrbanFabricElement(
            element_id="landmark_1",
            semantic_class="landmark",
            product_priority=1.0,
            lod_eligible=True,
        ),
        AtlasUrbanFabricElement(
            element_id="road_1",
            semantic_class="major_road",
            product_priority=0.90,
            lod_eligible=True,
        ),
        AtlasUrbanFabricElement(
            element_id="building_1",
            semantic_class="generic_building",
            product_priority=0.35,
            lod_eligible=True,
        ),
        AtlasUrbanFabricElement(
            element_id="path_1",
            semantic_class="minor_path",
            product_priority=0.20,
            lod_eligible=True,
        ),
    )

    result = AtlasCityCompositionLoDResolver.resolve_scene(
        elements=elements,
        product_size_mm=140.0,
        scene_morphology="dense_urban",
        lod_level=AtlasLoDLevelCatalog.resolve(1),
        printability_by_element_id={
            "landmark_1": True,
            "road_1": True,
            "building_1": True,
            "path_1": False,
        },
        landmark_proximity_by_element_id={
            "landmark_1": 0.0,
            "road_1": 25.0,
            "building_1": 80.0,
            "path_1": 150.0,
        },
    )

    assert result["retained_element_ids"] == (
        "landmark_1",
        "road_1",
        "building_1",
    )

    assert result["suppressed_element_ids"] == (
        "path_1",
    )

    assert result["simplified_element_ids"] == (
        "building_1",
    )

    assert (
        result["decisions"]["landmark_1"][
            "narrative_priority"
        ]
        == pytest.approx(1.0)
    )


def test_city_composition_lod_respects_lod_ineligible_elements():
    element = AtlasUrbanFabricElement(
        element_id="vegetation_1",
        semantic_class="vegetation",
        product_priority=0.40,
        lod_eligible=False,
    )

    result = AtlasCityCompositionLoDResolver.resolve_scene(
        elements=(element,),
        product_size_mm=140.0,
        scene_morphology="dense_urban",
        lod_level=AtlasLoDLevelCatalog.resolve(1),
    )

    assert result["retained_element_ids"] == (
        "vegetation_1",
    )

    assert result["suppressed_element_ids"] == ()
    assert result["simplified_element_ids"] == ()
    assert (
        result["decisions"]["vegetation_1"]["reason"]
        == "lod_ineligible_preserved"
    )


from CORE.atlas_urban_fabric_scene_contract import (
    AtlasUrbanFabricScene,
)


def test_city_composition_lod_resolves_urban_fabric_scene_object():
    scene = AtlasUrbanFabricScene(
        elements=(
            AtlasUrbanFabricElement(
                element_id="landmark_1",
                semantic_class="landmark",
                product_priority=1.0,
                lod_eligible=True,
            ),
            AtlasUrbanFabricElement(
                element_id="building_1",
                semantic_class="generic_building",
                product_priority=0.35,
                lod_eligible=True,
            ),
            AtlasUrbanFabricElement(
                element_id="path_1",
                semantic_class="minor_path",
                product_priority=0.20,
                lod_eligible=True,
            ),
        ),
    )

    result = (
        AtlasCityCompositionLoDResolver
        .resolve_urban_fabric_scene(
            scene=scene,
            product_size_mm=140.0,
            scene_morphology="historic_core",
            lod_level=(
                AtlasLoDLevelCatalog.resolve(1)
            ),
            printability_by_element_id={
                "landmark_1": True,
                "building_1": True,
                "path_1": False,
            },
            landmark_proximity_by_element_id={
                "landmark_1": 0.0,
                "building_1": 50.0,
                "path_1": 120.0,
            },
        )
    )

    assert result["scene"] is scene

    assert result["retained_element_ids"] == (
        "landmark_1",
        "building_1",
    )

    assert result["suppressed_element_ids"] == (
        "path_1",
    )

    assert result["simplified_element_ids"] == (
        "building_1",
    )


def test_city_composition_lod_requires_urban_fabric_scene():
    with pytest.raises(
        TypeError,
        match="AtlasUrbanFabricScene",
    ):
        (
            AtlasCityCompositionLoDResolver
            .resolve_urban_fabric_scene(
                scene=object(),
                product_size_mm=140.0,
                scene_morphology="dense_urban",
                lod_level=(
                    AtlasLoDLevelCatalog.resolve(1)
                ),
            )
        )


from CORE.atlas_urban_block_resolver import (
    AtlasUrbanBlockProfile,
)


def test_city_composition_lod_can_resolve_urban_block_profile():
    profile = AtlasUrbanBlockProfile(
        block_id="block_1",
        member_element_ids=(
            "building_1",
            "building_2",
        ),
        density_ratio=0.72,
        median_height_m=14.0,
        nearest_landmark_distance=80.0,
        composition_lod_level=(
            AtlasLoDLevelCatalog.resolve(1)
        ),
    )

    decision = (
        AtlasCityCompositionLoDResolver
        .resolve_urban_block_profile(
            profile=profile,
            product_size_mm=140.0,
            scene_morphology="dense_urban",
            printable=True,
        )
    )

    assert decision["semantic_class"] == "urban_block"
    assert decision["retain"] is True
    assert decision["simplify"] is True
    assert (
        decision["lod_level"]
        is profile.composition_lod_level
    )


def test_city_composition_lod_preserves_block_near_landmark_priority():
    profile = AtlasUrbanBlockProfile(
        block_id="block_near_landmark",
        member_element_ids=("building_1",),
        density_ratio=0.55,
        nearest_landmark_distance=15.0,
        composition_lod_level=(
            AtlasLoDLevelCatalog.resolve(1)
        ),
    )

    decision = (
        AtlasCityCompositionLoDResolver
        .resolve_urban_block_profile(
            profile=profile,
            product_size_mm=140.0,
            scene_morphology="historic_core",
            printable=True,
        )
    )

    assert decision["retain"] is True
    assert decision["narrative_priority"] >= 0.50


@pytest.mark.parametrize(
    "semantic_class,expected_minimum",
    [
        ("landmark", 0.95),
        ("major_road", 0.80),
        ("railway", 0.80),
        ("water", 0.75),
        ("park", 0.70),
        ("urban_block", 0.45),
        ("generic_building", 0.35),
        ("tree_row", 0.30),
        ("vegetation", 0.25),
        ("minor_path", 0.10),
    ],
)
def test_city_composition_lod_resolves_semantic_narrative_priority(
    semantic_class,
    expected_minimum,
):
    priority = (
        AtlasCityCompositionLoDResolver
        .resolve_semantic_narrative_priority(
            semantic_class
        )
    )

    assert priority >= expected_minimum
    assert 0.0 <= priority <= 1.0


def test_city_composition_lod_semantic_priority_preserves_city_hierarchy():
    resolve = (
        AtlasCityCompositionLoDResolver
        .resolve_semantic_narrative_priority
    )

    assert resolve("landmark") > resolve("major_road")
    assert resolve("major_road") > resolve("urban_block")
    assert resolve("urban_block") > resolve("vegetation")
    assert resolve("vegetation") > resolve("minor_path")


def test_city_composition_lod_small_product_suppresses_minor_detail_more_aggressively():
    small = AtlasCityCompositionLoDResolver.resolve(
        semantic_class="pedestrian_path",
        product_priority=0.20,
        product_size_mm=100.0,
        scene_morphology="dense_urban",
        landmark_proximity_m=150.0,
        printable=True,
        lod_level=AtlasLoDLevelCatalog.resolve(1),
    )

    large = AtlasCityCompositionLoDResolver.resolve(
        semantic_class="pedestrian_path",
        product_priority=0.20,
        product_size_mm=200.0,
        scene_morphology="dense_urban",
        landmark_proximity_m=150.0,
        printable=True,
        lod_level=AtlasLoDLevelCatalog.resolve(1),
    )

    assert small["retain"] is False
    assert large["retain"] is True


def test_city_composition_lod_dense_urban_simplifies_vegetation_more_than_suburban():
    dense = AtlasCityCompositionLoDResolver.resolve(
        semantic_class="vegetation",
        product_priority=0.30,
        product_size_mm=140.0,
        scene_morphology="dense_urban",
        landmark_proximity_m=100.0,
        printable=True,
        lod_level=AtlasLoDLevelCatalog.resolve(2),
    )

    suburban = AtlasCityCompositionLoDResolver.resolve(
        semantic_class="vegetation",
        product_priority=0.30,
        product_size_mm=140.0,
        scene_morphology="suburban",
        landmark_proximity_m=100.0,
        printable=True,
        lod_level=AtlasLoDLevelCatalog.resolve(2),
    )

    assert dense["simplify"] is True
    assert suburban["simplify"] is False


def test_city_composition_lod_landmark_proximity_protects_generic_building_context():
    near = AtlasCityCompositionLoDResolver.resolve(
        semantic_class="generic_building",
        product_priority=0.35,
        product_size_mm=120.0,
        scene_morphology="historic_core",
        landmark_proximity_m=15.0,
        printable=True,
        lod_level=AtlasLoDLevelCatalog.resolve(1),
    )

    far = AtlasCityCompositionLoDResolver.resolve(
        semantic_class="generic_building",
        product_priority=0.35,
        product_size_mm=120.0,
        scene_morphology="historic_core",
        landmark_proximity_m=150.0,
        printable=True,
        lod_level=AtlasLoDLevelCatalog.resolve(1),
    )

    assert near["retain"] is True
    assert near["narrative_priority"] > far["narrative_priority"]


from CORE.atlas_lod_resolution_contract import (
    AtlasLoDResolutionInput,
)
from CORE.atlas_lod_resolver import (
    AtlasLoDResolver,
)


def test_city_composition_lod_uses_existing_lod_resolution_result():
    lod_result = AtlasLoDResolver.resolve(
        AtlasLoDResolutionInput(
            product_size_mm=150.0,
            scale_ratio=5500.0,
            nozzle_diameter_mm=0.4,
            layer_height_mm=0.2,
            minimum_wall_thickness_mm=0.8,
            landmark_importance=0.90,
            viewing_distance_mm=600.0,
            available_color_count=4,
        )
    )

    decision = (
        AtlasCityCompositionLoDResolver
        .resolve_from_lod_result(
            semantic_class="landmark",
            product_priority=1.0,
            scene_morphology="historic_core",
            landmark_proximity_m=0.0,
            printable=True,
            lod_result=lod_result,
        )
    )

    assert decision["lod_level"] is lod_result.level
    assert decision["retain"] is True
    assert decision["simplify"] is False


def test_city_composition_lod_requires_existing_lod_resolution_result():
    with pytest.raises(
        TypeError,
        match="AtlasLoDResolutionResult",
    ):
        (
            AtlasCityCompositionLoDResolver
            .resolve_from_lod_result(
                semantic_class="generic_building",
                product_priority=0.35,
                scene_morphology="dense_urban",
                landmark_proximity_m=100.0,
                printable=True,
                lod_result=object(),
            )
        )


def test_city_composition_lod_generalizes_tree_rows_without_suppressing_them():
    decision = AtlasCityCompositionLoDResolver.resolve(
        semantic_class="tree_row",
        product_priority=0.35,
        product_size_mm=120.0,
        scene_morphology="dense_urban",
        landmark_proximity_m=80.0,
        printable=True,
        lod_level=AtlasLoDLevelCatalog.resolve(1),
    )

    assert decision["retain"] is True
    assert decision["simplify"] is True
    assert (
        decision["representation_mode"]
        == "generalized_row"
    )


def test_city_composition_lod_collapses_dense_vegetation_detail():
    decision = AtlasCityCompositionLoDResolver.resolve(
        semantic_class="vegetation",
        product_priority=0.30,
        product_size_mm=120.0,
        scene_morphology="dense_urban",
        landmark_proximity_m=120.0,
        printable=True,
        lod_level=AtlasLoDLevelCatalog.resolve(1),
    )

    assert decision["retain"] is True
    assert decision["simplify"] is True
    assert (
        decision["representation_mode"]
        == "canopy_or_cluster"
    )


def test_city_composition_lod_keeps_suburban_vegetation_detail():
    decision = AtlasCityCompositionLoDResolver.resolve(
        semantic_class="vegetation",
        product_priority=0.30,
        product_size_mm=180.0,
        scene_morphology="suburban",
        landmark_proximity_m=120.0,
        printable=True,
        lod_level=AtlasLoDLevelCatalog.resolve(2),
    )

    assert decision["retain"] is True
    assert decision["simplify"] is False
    assert (
        decision["representation_mode"]
        == "source_detail"
    )


def test_city_composition_lod_preserves_city_narrative_hierarchy():
    elements = (
        AtlasUrbanFabricElement(
            element_id="landmark_1",
            semantic_class="landmark",
            product_priority=1.0,
        ),
        AtlasUrbanFabricElement(
            element_id="rail_1",
            semantic_class="railway",
            product_priority=0.80,
        ),
        AtlasUrbanFabricElement(
            element_id="park_1",
            semantic_class="park",
            product_priority=0.70,
        ),
        AtlasUrbanFabricElement(
            element_id="water_1",
            semantic_class="water",
            product_priority=0.75,
        ),
        AtlasUrbanFabricElement(
            element_id="building_1",
            semantic_class="generic_building",
            product_priority=0.35,
        ),
        AtlasUrbanFabricElement(
            element_id="isolated_1",
            semantic_class="isolated_building",
            product_priority=0.25,
        ),
        AtlasUrbanFabricElement(
            element_id="path_1",
            semantic_class="minor_path",
            product_priority=0.15,
        ),
    )

    result = AtlasCityCompositionLoDResolver.resolve_scene(
        elements=elements,
        product_size_mm=110.0,
        scene_morphology="dense_urban",
        lod_level=AtlasLoDLevelCatalog.resolve(1),
        printability_by_element_id={
            "landmark_1": True,
            "rail_1": True,
            "park_1": True,
            "water_1": True,
            "building_1": True,
            "isolated_1": True,
            "path_1": False,
        },
        landmark_proximity_by_element_id={
            "landmark_1": 0.0,
            "rail_1": 80.0,
            "park_1": 120.0,
            "water_1": 120.0,
            "building_1": 90.0,
            "isolated_1": 180.0,
            "path_1": 200.0,
        },
    )

    assert result["decisions"]["landmark_1"]["retain"] is True
    assert result["decisions"]["rail_1"]["retain"] is True
    assert result["decisions"]["park_1"]["retain"] is True
    assert result["decisions"]["water_1"]["retain"] is True

    assert (
        result["decisions"]["building_1"]["representation_mode"]
        == "simplified_mass"
    )

    assert (
        result["decisions"]["isolated_1"]["representation_mode"]
        == "simplified_mass"
    )

    assert result["decisions"]["path_1"]["retain"] is False

    assert (
        result["decisions"]["landmark_1"]["narrative_priority"]
        > result["decisions"]["rail_1"]["narrative_priority"]
        > result["decisions"]["building_1"]["narrative_priority"]
        > result["decisions"]["path_1"]["narrative_priority"]
    )
