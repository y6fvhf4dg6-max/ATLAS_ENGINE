from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_semantic_relief_component import (
    AtlasSemanticReliefComponent,
)
from CORE.atlas_semantic_relief_transform import (
    AtlasSemanticReliefTransform,
)


def test_semantic_relief_component_normalizes_canonical_identity():
    component = AtlasSemanticReliefComponent(
        component_id=" Main Portal ",
        semantic_class=" Architectural Portal ",
        geometry_source_kind=" Parametric Primitive ",
    )

    assert component.component_id == "main_portal"
    assert component.semantic_class == "architectural_portal"
    assert component.geometry_source_kind == "parametric_primitive"

    with pytest.raises(FrozenInstanceError):
        component.component_id = "changed"

def test_semantic_relief_component_normalizes_parent_identity():
    child = AtlasSemanticReliefComponent(
        component_id="Portal Angel",
        semantic_class="Figurative Ornament",
        geometry_source_kind="Catalog Component",
        parent_component_id=" Main Portal ",
    )
    root = AtlasSemanticReliefComponent(
        component_id="Main Portal",
        semantic_class="Architectural Portal",
        geometry_source_kind="Parametric Primitive",
    )

    assert child.parent_component_id == "main_portal"
    assert root.parent_component_id is None

def test_semantic_relief_component_preserves_source_reference():
    component = AtlasSemanticReliefComponent(
        component_id="Portal Angel",
        semantic_class="Figurative Ornament",
        geometry_source_kind="Catalog Component",
        source_reference=" Catalog/Angel-A.V2 ",
    )
    generated = AtlasSemanticReliefComponent(
        component_id="Generated Panel",
        semantic_class="Architectural Panel",
        geometry_source_kind="Parametric Primitive",
    )

    assert component.source_reference == "Catalog/Angel-A.V2"
    assert generated.source_reference is None

def test_semantic_relief_component_normalizes_surface_projection():
    component = AtlasSemanticReliefComponent(
        component_id="Portal Angel",
        semantic_class="Figurative Ornament",
        geometry_source_kind="Catalog Component",
        target_surface_id=" Main Portal Face ",
        projection_mode=" Oriented Planar ",
    )
    free_component = AtlasSemanticReliefComponent(
        component_id="Standalone Statue",
        semantic_class="Figurative Sculpture",
        geometry_source_kind="Catalog Component",
    )

    assert component.target_surface_id == "main_portal_face"
    assert component.projection_mode == "oriented_planar"
    assert free_component.target_surface_id is None
    assert free_component.projection_mode == "none"

@pytest.mark.parametrize(
    "kwargs",
    (
        {"target_surface_id": "Facade"},
        {"projection_mode": "Oriented Planar"},
    ),
)
def test_semantic_relief_component_rejects_incomplete_projection_target(
    kwargs,
):
    with pytest.raises(ValueError, match="target_surface_id.*projection_mode"):
        AtlasSemanticReliefComponent(
            component_id="Portal Angel",
            semantic_class="Figurative Ornament",
            geometry_source_kind="Catalog Component",
            **kwargs,
        )

def test_semantic_relief_component_normalizes_depth_order():
    component = AtlasSemanticReliefComponent(
        component_id="Portal Angel",
        semantic_class="Figurative Ornament",
        geometry_source_kind="Catalog Component",
        depth_band=" Foreground Ornament ",
        layer_order=3,
    )
    default_component = AtlasSemanticReliefComponent(
        component_id="Main Wall",
        semantic_class="Architectural Surface",
        geometry_source_kind="Parametric Primitive",
    )

    assert component.depth_band == "foreground_ornament"
    assert component.layer_order == 3
    assert default_component.depth_band == "primary"
    assert default_component.layer_order == 0

@pytest.mark.parametrize(
    "layer_order",
    (True, -1, 1.5, "1"),
)
def test_semantic_relief_component_rejects_invalid_layer_order(
    layer_order,
):
    with pytest.raises(ValueError, match="layer_order"):
        AtlasSemanticReliefComponent(
            component_id="Portal Angel",
            semantic_class="Figurative Ornament",
            geometry_source_kind="Catalog Component",
            layer_order=layer_order,
        )

def test_semantic_relief_component_normalizes_physical_roles():
    component = AtlasSemanticReliefComponent(
        component_id="Portal Angel",
        semantic_class="Figurative Ornament",
        geometry_source_kind="Catalog Component",
        material_role=" Historic Stone ",
        physical_feature_policy=" Enlarge If Needed ",
    )
    default_component = AtlasSemanticReliefComponent(
        component_id="Main Wall",
        semantic_class="Architectural Surface",
        geometry_source_kind="Parametric Primitive",
    )

    assert component.material_role == "historic_stone"
    assert component.physical_feature_policy == "enlarge_if_needed"
    assert default_component.material_role == "unassigned"
    assert default_component.physical_feature_policy == "preserve"

def test_semantic_relief_component_normalizes_output_modes():
    component = AtlasSemanticReliefComponent(
        component_id="Portal Angel",
        semantic_class="Figurative Ornament",
        geometry_source_kind="Catalog Component",
        output_modes=(
            " Flat Relief ",
            " Assembled Landmark ",
            " Modular Kit ",
        ),
    )
    default_component = AtlasSemanticReliefComponent(
        component_id="Main Wall",
        semantic_class="Architectural Surface",
        geometry_source_kind="Parametric Primitive",
    )

    assert component.output_modes == (
        "flat_relief",
        "assembled_landmark",
        "modular_kit",
    )
    assert default_component.output_modes == ("relief",)

@pytest.mark.parametrize(
    "output_modes",
    (
        (),
        ("relief", " Relief "),
        "relief",
    ),
)
def test_semantic_relief_component_rejects_invalid_output_modes(
    output_modes,
):
    with pytest.raises(ValueError, match="output_modes"):
        AtlasSemanticReliefComponent(
            component_id="Portal Angel",
            semantic_class="Figurative Ornament",
            geometry_source_kind="Catalog Component",
            output_modes=output_modes,
        )

def test_semantic_relief_component_preserves_provenance_confidence():
    component = AtlasSemanticReliefComponent(
        component_id="Portal Angel",
        semantic_class="Figurative Ornament",
        geometry_source_kind="Catalog Component",
        provenance=" Catalog Audit 2026-08 ",
        confidence=0.75,
    )
    default_component = AtlasSemanticReliefComponent(
        component_id="Main Wall",
        semantic_class="Architectural Surface",
        geometry_source_kind="Parametric Primitive",
    )

    assert component.provenance == "Catalog Audit 2026-08"
    assert component.confidence == 0.75
    assert default_component.provenance == "unspecified"
    assert default_component.confidence == 1.0

@pytest.mark.parametrize(
    "confidence",
    (True, -0.1, 1.1, float("nan"), "invalid"),
)
def test_semantic_relief_component_rejects_invalid_confidence(
    confidence,
):
    with pytest.raises(ValueError, match="confidence"):
        AtlasSemanticReliefComponent(
            component_id="Portal Angel",
            semantic_class="Figurative Ornament",
            geometry_source_kind="Catalog Component",
            confidence=confidence,
        )

def test_semantic_relief_component_preserves_validated_transform():
    transform = AtlasSemanticReliefTransform(
        translation_mm=(4.0, 12.0, 1.2),
        rotation_degrees_xyz=(0.0, 0.0, 15.0),
        dimensions_mm=(12.0, 24.5, 3.0),
    )
    component = AtlasSemanticReliefComponent(
        component_id="Portal Angel",
        semantic_class="Figurative Ornament",
        geometry_source_kind="Catalog Component",
        transform=transform,
    )

    assert component.transform is transform

def test_semantic_relief_component_rejects_unvalidated_transform():
    with pytest.raises(TypeError, match="transform"):
        AtlasSemanticReliefComponent(
            component_id="Portal Angel",
            semantic_class="Figurative Ornament",
            geometry_source_kind="Catalog Component",
            transform={
                "translation_mm": (0.0, 0.0, 0.0),
                "dimensions_mm": (12.0, 24.5, 3.0),
            },
        )
