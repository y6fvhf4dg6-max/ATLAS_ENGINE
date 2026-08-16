from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_semantic_relief_component import (
    AtlasSemanticReliefComponent,
)
from CORE.atlas_semantic_relief_scene import (
    AtlasSemanticReliefScene,
)


def test_semantic_relief_scene_normalizes_identity_and_preserves_components():
    component = AtlasSemanticReliefComponent(
        component_id="Main Portal",
        semantic_class="Architectural Portal",
        geometry_source_kind="Parametric Primitive",
    )
    scene = AtlasSemanticReliefScene(
        scene_id=" Cathedral Facade ",
        components=(component,),
    )

    assert scene.scene_id == "cathedral_facade"
    assert scene.components == (component,)

    with pytest.raises(FrozenInstanceError):
        scene.scene_id = "changed"

def test_semantic_relief_scene_requires_components():
    with pytest.raises(ValueError, match="components"):
        AtlasSemanticReliefScene(
            scene_id="Empty Scene",
            components=(),
        )

def test_semantic_relief_scene_rejects_unvalidated_components():
    with pytest.raises(TypeError, match="components"):
        AtlasSemanticReliefScene(
            scene_id="Cathedral Facade",
            components=(
                {
                    "component_id": "main_portal",
                    "semantic_class": "architectural_portal",
                },
            ),
        )

def test_semantic_relief_scene_rejects_duplicate_component_identity():
    with pytest.raises(ValueError, match="duplicate.*component_id"):
        AtlasSemanticReliefScene(
            scene_id="Cathedral Facade",
            components=(
                AtlasSemanticReliefComponent(
                    component_id="Main Portal",
                    semantic_class="Architectural Portal",
                    geometry_source_kind="Parametric Primitive",
                ),
                AtlasSemanticReliefComponent(
                    component_id=" main portal ",
                    semantic_class="Figurative Ornament",
                    geometry_source_kind="Catalog Component",
                ),
            ),
        )

def test_semantic_relief_scene_rejects_missing_parent_reference():
    with pytest.raises(ValueError, match="parent_component_id"):
        AtlasSemanticReliefScene(
            scene_id="Cathedral Facade",
            components=(
                AtlasSemanticReliefComponent(
                    component_id="Portal Angel",
                    semantic_class="Figurative Ornament",
                    geometry_source_kind="Catalog Component",
                    parent_component_id="Missing Portal",
                ),
            ),
        )

def test_semantic_relief_scene_rejects_missing_target_surface_reference():
    with pytest.raises(ValueError, match="target_surface_id"):
        AtlasSemanticReliefScene(
            scene_id="Cathedral Facade",
            components=(
                AtlasSemanticReliefComponent(
                    component_id="Portal Angel",
                    semantic_class="Figurative Ornament",
                    geometry_source_kind="Catalog Component",
                    target_surface_id="Missing Portal Face",
                    projection_mode="Oriented Planar",
                ),
            ),
        )

def test_semantic_relief_scene_rejects_self_parent_reference():
    with pytest.raises(ValueError, match="parent.*itself"):
        AtlasSemanticReliefScene(
            scene_id="Cathedral Facade",
            components=(
                AtlasSemanticReliefComponent(
                    component_id="Main Portal",
                    semantic_class="Architectural Portal",
                    geometry_source_kind="Parametric Primitive",
                    parent_component_id="Main Portal",
                ),
            ),
        )

def test_semantic_relief_scene_rejects_parent_cycle():
    with pytest.raises(ValueError, match="parent.*cycle"):
        AtlasSemanticReliefScene(
            scene_id="Cyclic Scene",
            components=(
                AtlasSemanticReliefComponent(
                    component_id="Component A",
                    semantic_class="Architectural Part",
                    geometry_source_kind="Parametric Primitive",
                    parent_component_id="Component B",
                ),
                AtlasSemanticReliefComponent(
                    component_id="Component B",
                    semantic_class="Architectural Part",
                    geometry_source_kind="Parametric Primitive",
                    parent_component_id="Component A",
                ),
            ),
        )

def test_semantic_relief_scene_resolves_component_by_normalized_identity():
    portal = AtlasSemanticReliefComponent(
        component_id="Main Portal",
        semantic_class="Architectural Portal",
        geometry_source_kind="Parametric Primitive",
    )
    angel = AtlasSemanticReliefComponent(
        component_id="Portal Angel",
        semantic_class="Figurative Ornament",
        geometry_source_kind="Catalog Component",
        parent_component_id="Main Portal",
        target_surface_id="Main Portal",
        projection_mode="Oriented Planar",
    )
    scene = AtlasSemanticReliefScene(
        scene_id="Cathedral Facade",
        components=(portal, angel),
    )

    assert scene.component_for_id(" Portal Angel ") is angel

def test_semantic_relief_scene_resolves_direct_children():
    portal = AtlasSemanticReliefComponent(
        component_id="Main Portal",
        semantic_class="Architectural Portal",
        geometry_source_kind="Parametric Primitive",
    )
    angel = AtlasSemanticReliefComponent(
        component_id="Portal Angel",
        semantic_class="Figurative Ornament",
        geometry_source_kind="Catalog Component",
        parent_component_id="Main Portal",
    )
    inscription = AtlasSemanticReliefComponent(
        component_id="Portal Inscription",
        semantic_class="Text Ornament",
        geometry_source_kind="Vector Extrusion",
        parent_component_id="Main Portal",
    )
    scene = AtlasSemanticReliefScene(
        scene_id="Cathedral Facade",
        components=(portal, angel, inscription),
    )

    assert scene.children_for_id(" Main Portal ") == (
        angel,
        inscription,
    )
    assert scene.children_for_id("Portal Angel") == ()

def test_semantic_relief_scene_resolves_target_surface_components():
    surface = AtlasSemanticReliefComponent(
        component_id="Main Portal Face",
        semantic_class="Architectural Surface",
        geometry_source_kind="Parametric Primitive",
    )
    angel = AtlasSemanticReliefComponent(
        component_id="Portal Angel",
        semantic_class="Figurative Ornament",
        geometry_source_kind="Catalog Component",
        target_surface_id="Main Portal Face",
        projection_mode="Oriented Planar",
    )
    inscription = AtlasSemanticReliefComponent(
        component_id="Portal Inscription",
        semantic_class="Text Ornament",
        geometry_source_kind="Vector Extrusion",
        target_surface_id="Main Portal Face",
        projection_mode="Oriented Planar",
    )
    scene = AtlasSemanticReliefScene(
        scene_id="Cathedral Facade",
        components=(surface, angel, inscription),
    )

    assert scene.components_for_target_surface(
        " Main Portal Face "
    ) == (
        angel,
        inscription,
    )

def test_semantic_relief_scene_resolves_root_components():
    facade = AtlasSemanticReliefComponent(
        component_id="Main Facade",
        semantic_class="Architectural Surface",
        geometry_source_kind="Parametric Primitive",
    )
    statue = AtlasSemanticReliefComponent(
        component_id="Standalone Statue",
        semantic_class="Figurative Sculpture",
        geometry_source_kind="Catalog Component",
    )
    portal = AtlasSemanticReliefComponent(
        component_id="Main Portal",
        semantic_class="Architectural Portal",
        geometry_source_kind="Parametric Primitive",
        parent_component_id="Main Facade",
    )
    scene = AtlasSemanticReliefScene(
        scene_id="Cathedral Facade",
        components=(facade, portal, statue),
    )

    assert scene.root_components() == (
        facade,
        statue,
    )
