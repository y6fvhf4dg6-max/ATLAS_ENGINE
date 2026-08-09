from CORE.atlas_city_composition_scene_adapter import (
    AtlasCityCompositionSceneAdapter,
)


def test_city_composition_scene_adapter_builds_general_urban_fabric_scene():
    scene = AtlasCityCompositionSceneAdapter.build_scene(
        landmarks=(
            {
                "id": 1,
                "tags": {"historic": "monument"},
            },
        ),
        roads=(
            {
                "id": 2,
                "road_type": "primary",
                "tags": {"highway": "primary"},
            },
        ),
        buildings=(
            {
                "id": 3,
                "tags": {"building": "yes"},
            },
        ),
        parks=(
            {
                "id": 4,
                "tags": {"leisure": "park"},
            },
        ),
        waters=(
            {
                "id": 5,
                "tags": {"natural": "water"},
            },
        ),
        linear_infrastructure=(
            {
                "id": 6,
                "semantic_class": "railway",
                "tags": {"railway": "rail"},
            },
        ),
    )

    assert tuple(
        element.semantic_class
        for element in scene.elements
    ) == (
        "landmark",
        "major_road",
        "generic_building",
        "park",
        "water",
        "railway",
    )

    assert tuple(
        element.source_id
        for element in scene.elements
    ) == (
        1,
        2,
        3,
        4,
        5,
        6,
    )


def test_city_composition_scene_adapter_assigns_narrative_product_priorities():
    scene = AtlasCityCompositionSceneAdapter.build_scene(
        landmarks=({"id": 1, "tags": {}},),
        roads=(
            {
                "id": 2,
                "road_type": "primary",
                "tags": {"highway": "primary"},
            },
        ),
        buildings=({"id": 3, "tags": {"building": "yes"}},),
    )

    priorities = {
        element.semantic_class: element.product_priority
        for element in scene.elements
    }

    assert priorities["landmark"] > priorities["major_road"]
    assert priorities["major_road"] > priorities["generic_building"]
