from CORE.atlas_semantic_relief_component import (
    AtlasSemanticReliefComponent,
)
from CORE.atlas_semantic_relief_repetition import (
    AtlasSemanticReliefRepetition,
)
from CORE.atlas_semantic_relief_scene import (
    AtlasSemanticReliefScene,
)


def _synthetic_multi_use_case_scene():
    facade = AtlasSemanticReliefComponent(
        component_id="Main Facade",
        semantic_class="Architecture",
        geometry_source_kind="Parametric Primitive",
        output_modes=("Relief", "Assembled Landmark"),
    )
    portrait = AtlasSemanticReliefComponent(
        component_id="Portrait Head",
        semantic_class="Identity Portrait",
        geometry_source_kind="Canonical Face Head",
        output_modes=("Relief",),
    )
    figure = AtlasSemanticReliefComponent(
        component_id="Guardian Figure",
        semantic_class="Figurative Sculpture",
        geometry_source_kind="Catalog Component",
        output_modes=("Relief", "Assembled Landmark"),
    )
    kit_window = AtlasSemanticReliefComponent(
        component_id="Nave Window Module",
        semantic_class="Modular Kit Part",
        geometry_source_kind="Parametric Primitive",
        parent_component_id="Main Facade",
        repetition=AtlasSemanticReliefRepetition(
            repeat_group_id="Nave Windows",
            quantity=12,
            spacing_mm=(8.0, 0.0, 0.0),
            interchangeable=True,
        ),
        output_modes=("Modular Kit",),
    )

    return AtlasSemanticReliefScene(
        scene_id="Multi Use Case Fixture",
        components=(facade, portrait, figure, kit_window),
    )


def test_semantic_relief_scene_represents_all_phase_one_use_cases():
    scene = _synthetic_multi_use_case_scene()

    assert tuple(
        component.semantic_class
        for component in scene.root_components()
    ) == (
        "architecture",
        "identity_portrait",
        "figurative_sculpture",
    )
    assert scene.children_for_id("Main Facade")[0].semantic_class == (
        "modular_kit_part"
    )
    assert scene.component_for_id("Nave Window Module").repetition.quantity == 12
    assert scene.component_for_id("Portrait Head").geometry_source_kind == (
        "canonical_face_head"
    )
