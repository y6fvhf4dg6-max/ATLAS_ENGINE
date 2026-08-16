from CORE.atlas_semantic_relief_component import (
    AtlasSemanticReliefComponent,
)
from CORE.atlas_semantic_relief_scene import (
    AtlasSemanticReliefScene,
)
from CORE.atlas_semantic_depth_occlusion_composer import (
    AtlasSemanticDepthOcclusionComposer,
)


def test_composer_builds_deterministic_back_to_front_semantic_depth_plan():
    scene = AtlasSemanticReliefScene(
        scene_id="Cathedral Portal Depth Fixture",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Back Wall",
                semantic_class="Architectural Surface",
                geometry_source_kind="Parametric Primitive",
                depth_band="Background Wall",
                layer_order=0,
                occlusion_policy="Opaque",
                material_role="Historic Stone",
            ),
            AtlasSemanticReliefComponent(
                component_id="Portal Arch",
                semantic_class="Architectural Arch",
                geometry_source_kind="Parametric Primitive",
                depth_band="Middle Arch",
                layer_order=1,
                occlusion_policy="Occludes Lower Layers",
                material_role="Historic Stone",
            ),
            AtlasSemanticReliefComponent(
                component_id="Portal Angel",
                semantic_class="Figurative Ornament",
                geometry_source_kind="Catalog Component",
                depth_band="Foreground Ornament",
                layer_order=2,
                occlusion_policy="Occludes Lower Layers",
                material_role="Carved Stone",
            ),
        ),
    )

    result = AtlasSemanticDepthOcclusionComposer.compose(
        scene,
        depth_band_ranges={
            "Background Wall": (0.00, 0.25),
            "Middle Arch": (0.35, 0.60),
            "Foreground Ornament": (0.70, 1.00),
        },
    )

    assert result["type"] == (
        "semantic_depth_occlusion_plan"
    )

    assert result["scene_id"] == (
        "cathedral_portal_depth_fixture"
    )

    assert tuple(
        item["component_id"]
        for item in result["ordered_components"]
    ) == (
        "back_wall",
        "portal_arch",
        "portal_angel",
    )

    assert tuple(
        item["local_relief_range"]
        for item in result["ordered_components"]
    ) == (
        (0.00, 0.25),
        (0.35, 0.60),
        (0.70, 1.00),
    )

    assert result["ordered_components"][2] == {
        "component_id": "portal_angel",
        "geometry_boundary_id": "portal_angel",
        "semantic_class": "figurative_ornament",
        "depth_band": "foreground_ornament",
        "local_relief_range": (0.70, 1.00),
        "layer_order": 2,
        "occlusion_policy": "occludes_lower_layers",
        "material_role": "carved_stone",
        "parent_component_id": None,
        "inherited_depth_band": False,
        "depth_relation": None,
    }

    assert result["conflicts"] == ()
    assert result["operator_overrides"] == ()

    assert "triangles" not in result
    assert "mesh" not in result

import pytest


def test_composer_rejects_overlapping_depth_band_ranges():
    scene = AtlasSemanticReliefScene(
        scene_id="Overlapping Depth Bands",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Back Wall",
                semantic_class="Architectural Surface",
                geometry_source_kind="Parametric Primitive",
                depth_band="Background",
            ),
            AtlasSemanticReliefComponent(
                component_id="Portal Arch",
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


def test_composer_allows_touching_depth_band_ranges():
    scene = AtlasSemanticReliefScene(
        scene_id="Touching Depth Bands",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Back Wall",
                semantic_class="Architectural Surface",
                geometry_source_kind="Parametric Primitive",
                depth_band="Background",
            ),
            AtlasSemanticReliefComponent(
                component_id="Portal Arch",
                semantic_class="Architectural Arch",
                geometry_source_kind="Parametric Primitive",
                depth_band="Middle",
            ),
        ),
    )

    result = AtlasSemanticDepthOcclusionComposer.compose(
        scene,
        depth_band_ranges={
            "Background": (0.00, 0.40),
            "Middle": (0.40, 0.70),
        },
    )

    assert tuple(
        item["depth_band"]
        for item in result["ordered_components"]
    ) == (
        "background",
        "middle",
    )


def test_composer_rejects_missing_component_depth_band_configuration():
    scene = AtlasSemanticReliefScene(
        scene_id="Missing Depth Band",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Portal Angel",
                semantic_class="Figurative Ornament",
                geometry_source_kind="Catalog Component",
                depth_band="Foreground Ornament",
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="has no configured range",
    ):
        AtlasSemanticDepthOcclusionComposer.compose(
            scene,
            depth_band_ranges={
                "Background": (0.00, 0.30),
            },
        )


def test_composer_order_is_deterministic_inside_same_depth_band():
    scene = AtlasSemanticReliefScene(
        scene_id="Same Band Ordering",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Angel B",
                semantic_class="Figurative Ornament",
                geometry_source_kind="Catalog Component",
                depth_band="Foreground",
                layer_order=2,
            ),
            AtlasSemanticReliefComponent(
                component_id="Angel A",
                semantic_class="Figurative Ornament",
                geometry_source_kind="Catalog Component",
                depth_band="Foreground",
                layer_order=1,
            ),
        ),
    )

    first = AtlasSemanticDepthOcclusionComposer.compose(
        scene,
        depth_band_ranges={
            "Foreground": (0.70, 1.00),
        },
    )
    second = AtlasSemanticDepthOcclusionComposer.compose(
        scene,
        depth_band_ranges={
            "Foreground": (0.70, 1.00),
        },
    )

    assert first == second
    assert tuple(
        item["component_id"]
        for item in first["ordered_components"]
    ) == (
        "angel_a",
        "angel_b",
    )


def test_child_inherits_parent_depth_band_when_declared_primary():
    scene = AtlasSemanticReliefScene(
        scene_id="Parent Child Depth Inheritance",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Portal",
                semantic_class="Architectural Surface",
                geometry_source_kind="Parametric Primitive",
                depth_band="Middle",
                layer_order=1,
            ),
            AtlasSemanticReliefComponent(
                component_id="Portal Inscription",
                semantic_class="Architectural Ornament",
                geometry_source_kind="Catalog Component",
                parent_component_id="Portal",
                depth_band="Primary",
                layer_order=2,
            ),
        ),
    )

    result = AtlasSemanticDepthOcclusionComposer.compose(
        scene,
        depth_band_ranges={
            "Background": (0.00, 0.30),
            "Middle": (0.40, 0.70),
            "Foreground": (0.80, 1.00),
        },
    )

    child = next(
        item
        for item in result["ordered_components"]
        if item["component_id"]
        == "portal_inscription"
    )

    assert child["depth_band"] == "middle"
    assert child["local_relief_range"] == (
        0.40,
        0.70,
    )
    assert child["inherited_depth_band"] is True


def test_explicit_child_depth_band_does_not_inherit_parent():
    scene = AtlasSemanticReliefScene(
        scene_id="Explicit Child Depth",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Portal",
                semantic_class="Architectural Surface",
                geometry_source_kind="Parametric Primitive",
                depth_band="Middle",
            ),
            AtlasSemanticReliefComponent(
                component_id="Portal Angel",
                semantic_class="Figurative Ornament",
                geometry_source_kind="Catalog Component",
                parent_component_id="Portal",
                depth_band="Foreground",
            ),
        ),
    )

    result = AtlasSemanticDepthOcclusionComposer.compose(
        scene,
        depth_band_ranges={
            "Middle": (0.40, 0.70),
            "Foreground": (0.80, 1.00),
        },
    )

    child = next(
        item
        for item in result["ordered_components"]
        if item["component_id"]
        == "portal_angel"
    )

    assert child["depth_band"] == "foreground"
    assert child["inherited_depth_band"] is False


def test_nested_primary_child_inherits_first_explicit_ancestor_depth_band():
    scene = AtlasSemanticReliefScene(
        scene_id="Nested Depth Inheritance",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Portal",
                semantic_class="Architectural Surface",
                geometry_source_kind="Parametric Primitive",
                depth_band="Middle",
            ),
            AtlasSemanticReliefComponent(
                component_id="Portal Frame",
                semantic_class="Architectural Ornament",
                geometry_source_kind="Catalog Component",
                parent_component_id="Portal",
                depth_band="Primary",
            ),
            AtlasSemanticReliefComponent(
                component_id="Inscription",
                semantic_class="Architectural Ornament",
                geometry_source_kind="Catalog Component",
                parent_component_id="Portal Frame",
                depth_band="Primary",
            ),
        ),
    )

    result = AtlasSemanticDepthOcclusionComposer.compose(
        scene,
        depth_band_ranges={
            "Middle": (0.40, 0.70),
        },
    )

    resolved = {
        item["component_id"]: item
        for item in result["ordered_components"]
    }

    assert resolved["portal_frame"]["depth_band"] == "middle"
    assert resolved["portal_frame"]["inherited_depth_band"] is True

    assert resolved["inscription"]["depth_band"] == "middle"
    assert resolved["inscription"]["inherited_depth_band"] is True


def test_root_primary_component_requires_explicit_primary_range():
    scene = AtlasSemanticReliefScene(
        scene_id="Root Primary",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Root Surface",
                semantic_class="Architectural Surface",
                geometry_source_kind="Parametric Primitive",
                depth_band="Primary",
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="has no configured range: primary",
    ):
        AtlasSemanticDepthOcclusionComposer.compose(
            scene,
            depth_band_ranges={
                "Middle": (0.40, 0.70),
            },
        )


def test_composer_reports_invalid_occlusion_direction_conflict():
    scene = AtlasSemanticReliefScene(
        scene_id="Invalid Occlusion Direction",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Back Wall",
                semantic_class="Architectural Surface",
                geometry_source_kind="Parametric Primitive",
                depth_band="Background",
                layer_order=0,
                occlusion_policy="Occludes Lower Layers",
            ),
            AtlasSemanticReliefComponent(
                component_id="Portal Arch",
                semantic_class="Architectural Arch",
                geometry_source_kind="Parametric Primitive",
                depth_band="Foreground",
                layer_order=1,
                occlusion_policy="Opaque",
            ),
        ),
    )

    result = AtlasSemanticDepthOcclusionComposer.compose(
        scene,
        depth_band_ranges={
            "Background": (0.00, 0.30),
            "Foreground": (0.70, 1.00),
        },
    )

    assert result["conflicts"] == (
        {
            "type": "invalid_occlusion_direction",
            "component_id": "back_wall",
            "occlusion_policy": "occludes_lower_layers",
            "reason": (
                "component has no lower semantic layer to occlude"
            ),
        },
    )


def test_foreground_occlusion_of_lower_layers_is_valid():
    scene = AtlasSemanticReliefScene(
        scene_id="Valid Foreground Occlusion",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Back Wall",
                semantic_class="Architectural Surface",
                geometry_source_kind="Parametric Primitive",
                depth_band="Background",
                layer_order=0,
                occlusion_policy="Opaque",
            ),
            AtlasSemanticReliefComponent(
                component_id="Portal Angel",
                semantic_class="Figurative Ornament",
                geometry_source_kind="Catalog Component",
                depth_band="Foreground",
                layer_order=1,
                occlusion_policy="Occludes Lower Layers",
            ),
        ),
    )

    result = AtlasSemanticDepthOcclusionComposer.compose(
        scene,
        depth_band_ranges={
            "Background": (0.00, 0.30),
            "Foreground": (0.70, 1.00),
        },
    )

    assert result["conflicts"] == ()


def test_composer_records_explicit_semantic_embed_relation_without_meshing():
    scene = AtlasSemanticReliefScene(
        scene_id="Semantic Embed Relation",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Portal",
                semantic_class="Architectural Surface",
                geometry_source_kind="Parametric Primitive",
                depth_band="Middle",
                material_role="Historic Stone",
            ),
            AtlasSemanticReliefComponent(
                component_id="Inscription",
                semantic_class="Architectural Ornament",
                geometry_source_kind="Catalog Component",
                parent_component_id="Portal",
                depth_band="Foreground",
                material_role="Historic Stone",
            ),
        ),
    )

    result = AtlasSemanticDepthOcclusionComposer.compose(
        scene,
        depth_band_ranges={
            "Middle": (0.30, 0.60),
            "Foreground": (0.70, 1.00),
        },
        depth_relations={
            "Inscription": {
                "mode": "Embed",
                "depth_amount": 0.08,
            },
        },
    )

    inscription = next(
        item
        for item in result["ordered_components"]
        if item["component_id"] == "inscription"
    )

    assert inscription["depth_relation"] == {
        "mode": "embed",
        "depth_amount": 0.08,
        "parent_component_id": "portal",
    }

    assert inscription["material_role"] == "historic_stone"

    assert "triangles" not in result
    assert "mesh" not in result


@pytest.mark.parametrize(
    "mode",
    (
        "embed",
        "recess",
        "raised",
    ),
)
def test_non_contact_depth_relation_requires_positive_depth_amount(
    mode,
):
    scene = AtlasSemanticReliefScene(
        scene_id="Depth Relation Amount Required",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Wall",
                semantic_class="Architectural Surface",
                geometry_source_kind="Parametric Primitive",
                depth_band="Middle",
            ),
            AtlasSemanticReliefComponent(
                component_id="Detail",
                semantic_class="Architectural Ornament",
                geometry_source_kind="Catalog Component",
                parent_component_id="Wall",
                depth_band="Foreground",
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="depth_amount",
    ):
        AtlasSemanticDepthOcclusionComposer.compose(
            scene,
            depth_band_ranges={
                "Middle": (0.30, 0.60),
                "Foreground": (0.70, 1.00),
            },
            depth_relations={
                "Detail": {
                    "mode": mode,
                },
            },
        )


def test_contact_relation_rejects_depth_amount():
    scene = AtlasSemanticReliefScene(
        scene_id="Contact Relation",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Wall",
                semantic_class="Architectural Surface",
                geometry_source_kind="Parametric Primitive",
                depth_band="Middle",
            ),
            AtlasSemanticReliefComponent(
                component_id="Detail",
                semantic_class="Architectural Ornament",
                geometry_source_kind="Catalog Component",
                parent_component_id="Wall",
                depth_band="Foreground",
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="contact",
    ):
        AtlasSemanticDepthOcclusionComposer.compose(
            scene,
            depth_band_ranges={
                "Middle": (0.30, 0.60),
                "Foreground": (0.70, 1.00),
            },
            depth_relations={
                "Detail": {
                    "mode": "contact",
                    "depth_amount": 0.05,
                },
            },
        )


@pytest.mark.parametrize(
    "mode",
    (
        "embed",
        "recess",
        "raised",
    ),
)
def test_attached_depth_relation_requires_parent_component(
    mode,
):
    scene = AtlasSemanticReliefScene(
        scene_id="Orphan Relation",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Orphan Detail",
                semantic_class="Architectural Ornament",
                geometry_source_kind="Catalog Component",
                depth_band="Foreground",
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="parent",
    ):
        AtlasSemanticDepthOcclusionComposer.compose(
            scene,
            depth_band_ranges={
                "Foreground": (0.70, 1.00),
            },
            depth_relations={
                "Orphan Detail": {
                    "mode": mode,
                    "depth_amount": 0.05,
                },
            },
        )


def test_composer_rejects_physically_impossible_embed():
    scene = AtlasSemanticReliefScene(
        scene_id="Impossible Embed",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Portal",
                semantic_class="Architectural Surface",
                geometry_source_kind="Parametric Primitive",
                depth_band="Middle",
            ),
            AtlasSemanticReliefComponent(
                component_id="Inscription",
                semantic_class="Architectural Ornament",
                geometry_source_kind="Catalog Component",
                parent_component_id="Portal",
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


def test_material_boundary_remains_separate_from_geometry_boundary():
    scene = AtlasSemanticReliefScene(
        scene_id="Material Geometry Boundary Separation",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Portal Wall",
                semantic_class="Architectural Surface",
                geometry_source_kind="Parametric Primitive",
                depth_band="Middle",
                layer_order=0,
                material_role="Historic Stone",
            ),
            AtlasSemanticReliefComponent(
                component_id="Portal Arch",
                semantic_class="Architectural Arch",
                geometry_source_kind="Catalog Component",
                depth_band="Middle",
                layer_order=1,
                material_role="Historic Stone",
            ),
            AtlasSemanticReliefComponent(
                component_id="Inscription",
                semantic_class="Architectural Ornament",
                geometry_source_kind="Catalog Component",
                depth_band="Middle",
                layer_order=2,
                material_role="Painted Stone",
            ),
        ),
    )

    result = AtlasSemanticDepthOcclusionComposer.compose(
        scene,
        depth_band_ranges={
            "Middle": (0.30, 0.70),
        },
    )

    components = result["ordered_components"]

    assert tuple(
        item["geometry_boundary_id"]
        for item in components
    ) == (
        "portal_wall",
        "portal_arch",
        "inscription",
    )

    assert tuple(
        item["material_role"]
        for item in components
    ) == (
        "historic_stone",
        "historic_stone",
        "painted_stone",
    )

    assert components[0]["geometry_boundary_id"] != (
        components[1]["geometry_boundary_id"]
    )

    assert components[0]["material_role"] == (
        components[1]["material_role"]
    )

    assert "merged_geometry" not in result
    assert "triangles" not in result
    assert "mesh" not in result


def test_composer_records_deterministic_operator_depth_band_override():
    scene = AtlasSemanticReliefScene(
        scene_id="Operator Override",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Back Wall",
                semantic_class="Architectural Surface",
                geometry_source_kind="Parametric Primitive",
                depth_band="Background",
            ),
            AtlasSemanticReliefComponent(
                component_id="Portal Angel",
                semantic_class="Figurative Ornament",
                geometry_source_kind="Catalog Component",
                depth_band="Middle",
                layer_order=1,
            ),
        ),
    )

    result = AtlasSemanticDepthOcclusionComposer.compose(
        scene,
        depth_band_ranges={
            "Background": (0.00, 0.30),
            "Middle": (0.40, 0.60),
            "Foreground": (0.70, 1.00),
        },
        operator_overrides={
            "Portal Angel": {
                "depth_band": "Foreground",
            },
        },
    )

    angel = next(
        item
        for item in result["ordered_components"]
        if item["component_id"] == "portal_angel"
    )

    assert angel["depth_band"] == "foreground"
    assert angel["local_relief_range"] == (
        0.70,
        1.00,
    )

    assert result["operator_overrides"] == (
        {
            "component_id": "portal_angel",
            "field": "depth_band",
            "original_value": "middle",
            "override_value": "foreground",
        },
    )


def test_operator_override_is_deterministic():
    scene = AtlasSemanticReliefScene(
        scene_id="Deterministic Override",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Wall",
                semantic_class="Architectural Surface",
                geometry_source_kind="Parametric Primitive",
                depth_band="Background",
            ),
        ),
    )

    kwargs = {
        "depth_band_ranges": {
            "Background": (0.00, 0.30),
            "Foreground": (0.70, 1.00),
        },
        "operator_overrides": {
            "Wall": {
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


def test_operator_override_rejects_unknown_component():
    scene = AtlasSemanticReliefScene(
        scene_id="Unknown Override Component",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Wall",
                semantic_class="Architectural Surface",
                geometry_source_kind="Parametric Primitive",
                depth_band="Background",
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="unknown component",
    ):
        AtlasSemanticDepthOcclusionComposer.compose(
            scene,
            depth_band_ranges={
                "Background": (0.00, 0.30),
                "Foreground": (0.70, 1.00),
            },
            operator_overrides={
                "Missing": {
                    "depth_band": "Foreground",
                },
            },
        )


def test_operator_override_rejects_unsupported_field():
    scene = AtlasSemanticReliefScene(
        scene_id="Unsupported Override Field",
        components=(
            AtlasSemanticReliefComponent(
                component_id="Wall",
                semantic_class="Architectural Surface",
                geometry_source_kind="Parametric Primitive",
                depth_band="Background",
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="unsupported operator override field",
    ):
        AtlasSemanticDepthOcclusionComposer.compose(
            scene,
            depth_band_ranges={
                "Background": (0.00, 0.30),
            },
            operator_overrides={
                "Wall": {
                    "material_role": "Metal",
                },
            },
        )
