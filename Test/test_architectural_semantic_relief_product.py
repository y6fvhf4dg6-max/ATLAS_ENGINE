from CORE.atlas_architectural_semantic_relief_product import (
    AtlasArchitecturalSemanticReliefProduct,
)


def test_architectural_semantic_relief_product_requires_phase7_semantic_content():
    product = AtlasArchitecturalSemanticReliefProduct(
        product_id="phase7_reference_facade_v1",
        target_surface_id="reference_facade",
        component_ids=(
            "opening.recessed_rect_v1",
            "rosette.circular_v1",
            "plaque.figurative_rect_v1",
            "panel.inscription_rect_v1",
        ),
        depth_bands=(
            "recessed",
            "base",
            "raised",
        ),
        baseline_mode="generic_height_map",
        projection_mode="oriented_planar",
    )

    assert product.product_id == "phase7_reference_facade_v1"
    assert product.target_surface_id == "reference_facade"
    assert product.baseline_mode == "generic_height_map"
    assert product.projection_mode == "oriented_planar"

    assert product.has_recessed_opening
    assert product.has_raised_ornament
    assert product.has_figurative_or_emblematic_feature
    assert product.has_inscription_or_panel
    assert product.has_minimum_depth_band_count

    assert product.phase7_semantic_content_ready


def test_architectural_semantic_relief_product_uses_real_surface_target():
    from CORE.atlas_surface_target import (
        AtlasSurfaceTarget,
    )

    target = AtlasSurfaceTarget.oriented_planar_quad(
        surface_id="reference_facade",
        source_component_id="reference_building",
        target_component_id="reference_facade",
        quad=(
            (0.0, 0.0, 0.0),
            (12.0, 0.0, 0.0),
            (12.0, 0.0, 8.0),
            (0.0, 0.0, 8.0),
        ),
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=2.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    product = AtlasArchitecturalSemanticReliefProduct(
        product_id="phase7_reference_facade_v1",
        surface_target=target,
        component_ids=(
            "opening.recessed_rect_v1",
            "rosette.circular_v1",
            "plaque.figurative_rect_v1",
            "panel.inscription_rect_v1",
        ),
        depth_bands=(
            "recessed",
            "base",
            "raised",
        ),
        baseline_mode="generic_height_map",
    )

    assert product.surface_target is target
    assert product.target_surface_id == "reference_facade"
    assert product.projection_mode == "oriented_planar"
    assert product.phase7_semantic_content_ready


def test_architectural_semantic_relief_product_projects_mesh_to_real_target():
    from CORE.atlas_surface_target import (
        AtlasSurfaceTarget,
    )

    target = AtlasSurfaceTarget.oriented_planar_quad(
        surface_id="reference_facade",
        source_component_id="reference_building",
        target_component_id="reference_facade",
        quad=(
            (2.0, 3.0, 1.0),
            (8.0, 3.0, 1.0),
            (8.0, 3.0, 9.0),
            (2.0, 3.0, 9.0),
        ),
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=1.5,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    product = AtlasArchitecturalSemanticReliefProduct(
        product_id="phase7_reference_facade_v1",
        surface_target=target,
        component_ids=(
            "opening.recessed_rect_v1",
            "rosette.circular_v1",
            "plaque.figurative_rect_v1",
            "panel.inscription_rect_v1",
        ),
        depth_bands=(
            "recessed",
            "base",
            "raised",
        ),
        baseline_mode="generic_height_map",
    )

    result = product.project_mesh(
        {
            "type": "phase7_semantic_relief",
            "triangles": [
                (
                    (1.0, 2.0, 0.0),
                    (3.0, 2.0, 0.0),
                    (1.0, 4.0, 1.0),
                ),
            ],
        }
    )

    assert result["projection_mode"] == "oriented_planar"
    assert result["target_surface_id"] == "reference_facade"

    triangle = result["mesh"]["triangles"][0]

    assert triangle[0] == (3.0, 3.0, 3.0)
    assert triangle[1] == (5.0, 3.0, 3.0)
    assert triangle[2] == (3.0, 2.0, 5.0)


def test_phase7_product_ready_requires_comparison_pass_and_operator_visual_acceptance():
    from CORE.atlas_surface_target import (
        AtlasSurfaceTarget,
    )

    target = AtlasSurfaceTarget.oriented_planar_quad(
        surface_id="reference_facade",
        source_component_id="reference_building",
        target_component_id="reference_facade",
        quad=(
            (0.0, 0.0, 0.0),
            (12.0, 0.0, 0.0),
            (12.0, 0.0, 8.0),
            (0.0, 0.0, 8.0),
        ),
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=2.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    product = AtlasArchitecturalSemanticReliefProduct(
        product_id="phase7_reference_facade_v1",
        surface_target=target,
        component_ids=(
            "opening.recessed_rect_v1",
            "rosette.circular_v1",
            "plaque.figurative_rect_v1",
            "panel.inscription_rect_v1",
        ),
        depth_bands=(
            "recessed",
            "base",
            "raised",
        ),
        baseline_mode="generic_height_map",
    )

    comparison_report = {
        "type": "architectural_semantic_relief_comparison_report",
        "status": "PASS",
        "semantic_more_readable": True,
    }

    assert product.is_phase7_product_ready(
        comparison_report=comparison_report,
        operator_visual_accepted=False,
    ) is False

    assert product.is_phase7_product_ready(
        comparison_report=comparison_report,
        operator_visual_accepted=True,
    ) is True


def test_phase7_product_ready_requires_physical_coupon_acceptance():
    from CORE.atlas_surface_target import (
        AtlasSurfaceTarget,
    )

    target = AtlasSurfaceTarget.oriented_planar_quad(
        surface_id="reference_facade",
        source_component_id="reference_building",
        target_component_id="reference_facade",
        quad=(
            (0.0, 0.0, 0.0),
            (12.0, 0.0, 0.0),
            (12.0, 0.0, 8.0),
            (0.0, 0.0, 8.0),
        ),
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=2.0,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    product = AtlasArchitecturalSemanticReliefProduct(
        product_id="phase7_reference_facade_v1",
        surface_target=target,
        component_ids=(
            "opening.recessed_rect_v1",
            "rosette.circular_v1",
            "plaque.figurative_rect_v1",
            "panel.inscription_rect_v1",
        ),
        depth_bands=(
            "recessed",
            "base",
            "raised",
        ),
        baseline_mode="generic_height_map",
    )

    comparison_report = {
        "type": "architectural_semantic_relief_comparison_report",
        "status": "PASS",
        "semantic_more_readable": True,
    }

    assert product.is_phase7_product_ready(
        comparison_report=comparison_report,
        operator_visual_accepted=True,
        physical_coupon_accepted=False,
    ) is False

    assert product.is_phase7_product_ready(
        comparison_report=comparison_report,
        operator_visual_accepted=True,
        physical_coupon_accepted=True,
    ) is True
