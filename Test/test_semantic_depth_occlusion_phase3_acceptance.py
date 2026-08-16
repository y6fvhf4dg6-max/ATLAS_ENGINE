import pytest

from CORE.atlas_semantic_depth_occlusion_composer import (
    AtlasSemanticDepthOcclusionComposer,
)
from CORE.atlas_semantic_relief_component import (
    AtlasSemanticReliefComponent,
)
from CORE.atlas_semantic_relief_scene import (
    AtlasSemanticReliefScene,
)


def test_phase3_orders_wall_arch_inscription_and_angel_back_to_front():
    scene = AtlasSemanticReliefScene(
        scene_id="Phase 3 Layer Acceptance",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Back Wall",
                semantic_class="Architectural Surface",
                geometry_source_kind="Parametric Primitive",
                depth_band="Background",
                layer_order=0,
            ),
            AtlasSemanticReliefComponent(
                component_id="Portal Arch",
                semantic_class="Architectural Arch",
                geometry_source_kind="Parametric Primitive",
                depth_band="Middle",
                layer_order=1,
                occlusion_policy="Occludes Lower Layers",
            ),
            AtlasSemanticReliefComponent(
                component_id="Inscription",
                semantic_class="Architectural Ornament",
                geometry_source_kind="Catalog Component",
                parent_component_id="Portal Arch",
                depth_band="Foreground",
                layer_order=2,
                occlusion_policy="Occludes Lower Layers",
            ),
            AtlasSemanticReliefComponent(
                component_id="Portal Angel",
                semantic_class="Figurative Ornament",
                geometry_source_kind="Catalog Component",
                parent_component_id="Portal Arch",
                depth_band="Foreground",
                layer_order=3,
                occlusion_policy="Occludes Lower Layers",
            ),
        ),
    )

    result = AtlasSemanticDepthOcclusionComposer.compose(
        scene,
        depth_band_ranges={
            "Background": (0.00, 0.25),
            "Middle": (0.35, 0.60),
            "Foreground": (0.70, 1.00),
        },
    )

    assert tuple(
        item["component_id"]
        for item in result["ordered_components"]
    ) == (
        "back_wall",
        "portal_arch",
        "inscription",
        "portal_angel",
    )


def test_phase3_rejects_overlapping_depth_bands():
    scene = AtlasSemanticReliefScene(
        scene_id="Phase 3 Overlap Acceptance",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Wall",
                semantic_class="Architectural Surface",
                geometry_source_kind="Parametric Primitive",
                depth_band="Background",
            ),
            AtlasSemanticReliefComponent(
                component_id="Arch",
                semantic_class="Architectural Arch",
                geometry_source_kind="Parametric Primitive",
                depth_band="Middle",
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="overlap",
    ):
        AtlasSemanticDepthOcclusionComposer.compose(
            scene,
            depth_band_ranges={
                "Background": (0.00, 0.50),
                "Middle": (0.40, 0.70),
            },
        )


def test_phase3_rejects_parent_cycle_before_composition():
    with pytest.raises(
        ValueError,
        match="parent.*cycle",
    ):
        AtlasSemanticReliefScene(
            scene_id="Phase 3 Cycle Acceptance",
            components=(
                AtlasSemanticReliefComponent(
                    component_id="A",
                    semantic_class="Architectural Part",
                    geometry_source_kind="Parametric Primitive",
                    parent_component_id="B",
                ),
                AtlasSemanticReliefComponent(
                    component_id="B",
                    semantic_class="Architectural Part",
                    geometry_source_kind="Parametric Primitive",
                    parent_component_id="A",
                ),
            ),
        )


def test_phase3_rejects_physically_impossible_embed():
    scene = AtlasSemanticReliefScene(
        scene_id="Phase 3 Embed Acceptance",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Wall",
                semantic_class="Architectural Surface",
                geometry_source_kind="Parametric Primitive",
                depth_band="Middle",
            ),
            AtlasSemanticReliefComponent(
                component_id="Inscription",
                semantic_class="Architectural Ornament",
                geometry_source_kind="Catalog Component",
                parent_component_id="Wall",
                depth_band="Foreground",
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="impossible embed",
    ):
        AtlasSemanticDepthOcclusionComposer.compose(
            scene,
            depth_band_ranges={
                "Middle": (0.30, 0.60),
                "Foreground": (0.70, 0.90),
            },
            depth_relations={
                "Inscription": {
                    "mode": "embed",
                    "depth_amount": 0.20,
                },
            },
        )


def test_phase3_composition_plan_is_deterministic_and_mesh_free():
    scene = AtlasSemanticReliefScene(
        scene_id="Phase 3 Determinism Acceptance",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Wall",
                semantic_class="Architectural Surface",
                geometry_source_kind="Parametric Primitive",
                depth_band="Background",
            ),
            AtlasSemanticReliefComponent(
                component_id="Angel",
                semantic_class="Figurative Ornament",
                geometry_source_kind="Catalog Component",
                depth_band="Foreground",
                layer_order=1,
                occlusion_policy="Occludes Lower Layers",
            ),
        ),
    )

    kwargs = {
        "depth_band_ranges": {
            "Background": (0.00, 0.30),
            "Foreground": (0.70, 1.00),
        },
        "operator_overrides": {
            "Angel": {
                "depth_band": "Foreground",
            },
        },
    }

    first = AtlasSemanticDepthOcclusionComposer.compose(
        scene,
        **kwargs,
    )
    second = AtlasSemanticDepthOcclusionComposer.compose(
        scene,
        **kwargs,
    )

    assert first == second
    assert "mesh" not in first
    assert "triangles" not in first

    for item in first["ordered_components"]:
        assert "mesh" not in item
        assert "triangles" not in item
