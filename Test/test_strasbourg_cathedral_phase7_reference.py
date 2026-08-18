import pytest

from CORE.atlas_strasbourg_cathedral_phase7_reference import (
    STRASBOURG_CATHEDRAL_PHASE7_REFERENCE,
)


def test_strasbourg_phase7_reference_contract_is_locked():
    reference = STRASBOURG_CATHEDRAL_PHASE7_REFERENCE

    assert reference["reference_id"] == (
        "strasbourg_cathedral_central_portal_phase7_v1"
    )
    assert reference["site_name"] == (
        "Cathédrale Notre-Dame de Strasbourg"
    )
    assert reference["surface_role"] == (
        "west_facade_central_portal"
    )
    assert reference["image_size"] == (
        1333,
        2000,
    )
    assert reference["sha256"] == (
        "e9315eca500ef296c33016ad4c576a5e65dde1828d04885bd5a01ab24abcaeef"
    )
    assert reference["license_id"] == "CC-BY-2.0"
    assert reference["provenance"] == (
        "Wikimedia Commons / jeffowenphotos"
    )

    assert set(
        reference["required_semantic_roles"]
    ) == {
        "recessed_opening",
        "raised_ornament",
        "figurative_or_emblematic_feature",
        "inscription_or_panel",
    }

    assert reference["minimum_depth_band_count"] == 3


def test_strasbourg_phase7_reference_builds_architectural_relief_input():
    from CORE.atlas_architectural_relief_input import (
        AtlasArchitecturalReliefInput,
    )
    from CORE.atlas_relief_product_profile_catalog import (
        ARCHITECTURAL_STONE_FACADE,
    )
    from CORE.atlas_strasbourg_cathedral_phase7_reference import (
        build_strasbourg_cathedral_phase7_input,
    )

    contract = build_strasbourg_cathedral_phase7_input()

    assert isinstance(
        contract,
        AtlasArchitecturalReliefInput,
    )
    assert contract.product_profile is (
        ARCHITECTURAL_STONE_FACADE
    )
    assert contract.architectural_kind == (
        "gothic_stone_facade"
    )
    assert contract.image_path.as_posix().endswith(
        "strasbourg_cathedral_central_portal_reference.jpg"
    )


def test_strasbourg_phase7_semantic_graph_covers_required_real_facade_roles():
    from CORE.atlas_semantic_relief_component import (
        AtlasSemanticReliefComponent,
    )
    from CORE.atlas_strasbourg_cathedral_phase7_reference import (
        build_strasbourg_cathedral_phase7_semantic_components,
    )

    components = (
        build_strasbourg_cathedral_phase7_semantic_components()
    )

    assert components
    assert all(
        isinstance(
            component,
            AtlasSemanticReliefComponent,
        )
        for component in components
    )

    by_id = {
        component.component_id: component
        for component in components
    }

    required_ids = {
        "strasbourg.central_portal.opening",
        "strasbourg.central_portal.archivolt",
        "strasbourg.central_portal.figurative_tympanum",
        "strasbourg.central_portal.panel",
    }
    assert required_ids <= set(by_id)

    assert (
        by_id[
            "strasbourg.central_portal.opening"
        ].semantic_class
        == "opening.recessed_rect_v1"
    )
    assert (
        by_id[
            "strasbourg.central_portal.archivolt"
        ].semantic_class
        == "archivolt.round_v1"
    )
    assert (
        by_id[
            "strasbourg.central_portal.figurative_tympanum"
        ].semantic_class
        == "plaque.figurative_rect_v1"
    )
    assert (
        by_id[
            "strasbourg.central_portal.panel"
        ].semantic_class
        == "panel.inscription_rect_v1"
    )

    assert len(
        {
            component.depth_band
            for component in components
        }
    ) >= 3

    assert {
        component.target_surface_id
        for component in components
    } == {
        "strasbourg.central_portal.facade_surface"
    }

    assert {
        component.projection_mode
        for component in components
    } == {
        "oriented_planar"
    }

    assert all(
        component.source_reference
        == "strasbourg_cathedral_central_portal_phase7_v1"
        for component in components
    )


def test_strasbourg_phase7_builds_real_semantic_product_on_oriented_facade_target():
    from CORE.atlas_architectural_semantic_relief_product import (
        AtlasArchitecturalSemanticReliefProduct,
    )
    from CORE.atlas_surface_target import (
        AtlasSurfaceTarget,
    )
    from CORE.atlas_strasbourg_cathedral_phase7_reference import (
        build_strasbourg_cathedral_phase7_product,
        build_strasbourg_cathedral_phase7_semantic_components,
    )

    components = (
        build_strasbourg_cathedral_phase7_semantic_components()
    )
    product = (
        build_strasbourg_cathedral_phase7_product()
    )

    assert isinstance(
        product,
        AtlasArchitecturalSemanticReliefProduct,
    )
    assert isinstance(
        product.surface_target,
        AtlasSurfaceTarget,
    )

    assert product.product_id == (
        "strasbourg_cathedral_central_portal_phase7_v1"
    )
    assert product.target_surface_id == (
        "strasbourg.central_portal.facade_surface"
    )
    assert product.projection_mode == (
        "oriented_planar"
    )

    assert product.component_ids == tuple(
        component.semantic_class
        for component in components
    )
    assert product.depth_bands == tuple(
        component.depth_band
        for component in components
    )

    assert (
        product.surface_target.minimum_depth_mm
        == 0.0
    )
    assert (
        product.surface_target.maximum_depth_mm
        == 1.8
    )

    assert product.phase7_semantic_content_ready is True


def test_strasbourg_phase7_binds_required_semantic_roles_to_catalog_instances():
    from CORE.atlas_architectural_ornament_catalog import (
        AtlasArchitecturalOrnamentInstance,
    )
    from CORE.atlas_strasbourg_cathedral_phase7_reference import (
        build_strasbourg_cathedral_phase7_catalog_instances,
    )

    instances = (
        build_strasbourg_cathedral_phase7_catalog_instances()
    )

    assert set(instances) == {
        "strasbourg.central_portal.opening",
        "strasbourg.central_portal.archivolt",
        "strasbourg.central_portal.figurative_tympanum",
        "strasbourg.central_portal.panel",
    }

    assert all(
        isinstance(
            instance,
            AtlasArchitecturalOrnamentInstance,
        )
        for instance in instances.values()
    )

    assert instances[
        "strasbourg.central_portal.opening"
    ].component_id == "opening.recessed_rect_v1"

    assert instances[
        "strasbourg.central_portal.archivolt"
    ].component_id == "archivolt.round_v1"

    assert instances[
        "strasbourg.central_portal.figurative_tympanum"
    ].component_id == "plaque.figurative_rect_v1"

    assert instances[
        "strasbourg.central_portal.panel"
    ].component_id == "panel.inscription_rect_v1"

    assert all(
        instance.occurrence_id == component_id
        for component_id, instance
        in instances.items()
    )


def test_strasbourg_phase7_builds_closed_real_component_meshes_from_catalog_instances():
    from CORE.atlas_mesh_validator import (
        AtlasMeshValidator,
    )
    from CORE.atlas_strasbourg_cathedral_phase7_reference import (
        build_strasbourg_cathedral_phase7_component_meshes,
    )

    meshes = (
        build_strasbourg_cathedral_phase7_component_meshes()
    )

    assert set(meshes) == {
        "strasbourg.central_portal.opening",
        "strasbourg.central_portal.archivolt",
        "strasbourg.central_portal.figurative_tympanum",
        "strasbourg.central_portal.panel",
    }

    expected_semantic_classes = {
        "strasbourg.central_portal.opening": (
            "opening.recessed_rect_v1"
        ),
        "strasbourg.central_portal.archivolt": (
            "archivolt.round_v1"
        ),
        "strasbourg.central_portal.figurative_tympanum": (
            "plaque.figurative_rect_v1"
        ),
        "strasbourg.central_portal.panel": (
            "panel.inscription_rect_v1"
        ),
    }

    for occurrence_id, mesh in meshes.items():
        assert mesh["occurrence_id"] == occurrence_id
        assert (
            mesh["semantic_class"]
            == expected_semantic_classes[occurrence_id]
        )
        assert mesh["triangles"]

        report = AtlasMeshValidator._topology_report(
            mesh
        )

        assert report["open_edge_count"] == 0
        assert report["non_manifold_edge_count"] == 0


def test_strasbourg_phase7_projects_real_component_meshes_to_canonical_facade_target():
    from CORE.atlas_strasbourg_cathedral_phase7_reference import (
        build_strasbourg_cathedral_phase7_projected_component_meshes,
    )

    projected = (
        build_strasbourg_cathedral_phase7_projected_component_meshes()
    )

    assert set(projected) == {
        "strasbourg.central_portal.opening",
        "strasbourg.central_portal.archivolt",
        "strasbourg.central_portal.figurative_tympanum",
        "strasbourg.central_portal.panel",
    }

    for occurrence_id, result in projected.items():
        assert result["target_surface_id"] == (
            "strasbourg.central_portal.facade_surface"
        )
        if occurrence_id == (
            "strasbourg.central_portal.panel"
        ):
            assert result["projection_mode"] == "flat_plane"
            assert result["surface_id"] == (
                "strasbourg.central_portal.opening_floor"
            )
            assert result["nested_target_surface_id"] == (
                "strasbourg.central_portal.opening_floor"
            )
            assert result["nested_target_component_id"] == (
                "strasbourg.central_portal.opening"
            )
        else:
            assert result["projection_mode"] == "oriented_planar"
            assert result["surface_id"] == (
                "strasbourg.central_portal.facade_surface"
            )
        assert result["depth_envelope_violation_count"] == 0
        assert result["clipped_triangle_count"] == 0
        assert result["winding_audited"] is True
        assert result["winding_preserved"] is True
        assert result["winding_violation_count"] == 0

        mesh = result["mesh"]

        assert mesh["occurrence_id"] == occurrence_id
        assert mesh["semantic_class"]
        assert mesh["triangles"]


def test_strasbourg_phase7_recessed_opening_projects_inward_while_raised_components_project_outward():
    from CORE.atlas_strasbourg_cathedral_phase7_reference import (
        build_strasbourg_cathedral_phase7_product,
        build_strasbourg_cathedral_phase7_projected_component_meshes,
    )

    product = build_strasbourg_cathedral_phase7_product()
    projected = (
        build_strasbourg_cathedral_phase7_projected_component_meshes()
    )

    normal = product.surface_target.outward_normal
    origin = product.surface_target.origin

    def signed_depths(result):
        return [
            sum(
                (float(point[index]) - origin[index])
                * normal[index]
                for index in range(3)
            )
            for triangle in result["mesh"]["triangles"]
            for point in triangle
        ]

    opening_depths = signed_depths(
        projected["strasbourg.central_portal.opening"]
    )

    assert min(opening_depths) < 0.0
    assert max(opening_depths) <= 1e-9

    for occurrence_id in (
        "strasbourg.central_portal.archivolt",
        "strasbourg.central_portal.figurative_tympanum",
    ):
        depths = signed_depths(projected[occurrence_id])

        assert min(depths) >= -1e-9
        assert max(depths) > 0.0

    panel_depths = signed_depths(
        projected["strasbourg.central_portal.panel"]
    )

    assert min(panel_depths) < 0.0
    assert max(panel_depths) < 0.0
    assert max(panel_depths) > min(opening_depths)

def test_strasbourg_phase7_composes_projected_geometry_into_four_semantic_depth_levels():
    from CORE.atlas_strasbourg_cathedral_phase7_reference import (
        build_strasbourg_cathedral_phase7_depth_occlusion_plan,
        build_strasbourg_cathedral_phase7_product,
        build_strasbourg_cathedral_phase7_projected_component_meshes,
    )

    plan = build_strasbourg_cathedral_phase7_depth_occlusion_plan()

    assert plan["conflicts"] == ()

    semantic_items = tuple(
        item
        for item in plan["ordered_components"]
        if item["component_id"].startswith(
            "strasbourg.central_portal."
        )
        and item["component_id"] != (
            "strasbourg.central_portal.facade_surface"
        )
    )

    assert tuple(
        item["component_id"]
        for item in semantic_items
    ) == (
        "strasbourg.central_portal.opening",
        "strasbourg.central_portal.panel",
        "strasbourg.central_portal.archivolt",
        "strasbourg.central_portal.figurative_tympanum",
    )

    assert tuple(
        item["depth_band"]
        for item in semantic_items
    ) == (
        "recessed",
        "primary",
        "raised_primary",
        "raised_secondary",
    )

    assert tuple(
        item["local_relief_range"]
        for item in semantic_items
    ) == (
        (0.00, 0.20),
        (0.30, 0.50),
        (0.50, 0.75),
        (0.75, 1.00),
    )

    product = build_strasbourg_cathedral_phase7_product()
    projected = (
        build_strasbourg_cathedral_phase7_projected_component_meshes()
    )

    origin = product.surface_target.origin
    normal = product.surface_target.outward_normal

    def peak_signed_depth(occurrence_id):
        return max(
            sum(
                (float(point[index]) - origin[index])
                * normal[index]
                for index in range(3)
            )
            for triangle in projected[
                occurrence_id
            ]["mesh"]["triangles"]
            for point in triangle
        )

    peaks = (
        peak_signed_depth(
            "strasbourg.central_portal.opening"
        ),
        peak_signed_depth(
            "strasbourg.central_portal.panel"
        ),
        peak_signed_depth(
            "strasbourg.central_portal.archivolt"
        ),
        peak_signed_depth(
            "strasbourg.central_portal.figurative_tympanum"
        ),
    )

    assert peaks[0] <= 1e-9
    assert -0.80 < peaks[1] < 0.0
    assert peaks[2] > 0.0
    assert peaks[3] > 0.0
    assert abs(peaks[2] - peaks[3]) > 1e-9


def test_strasbourg_archivolt_projects_as_band_without_covering_portal_center():
    from dataclasses import replace

    import numpy as np

    from CORE.atlas_projected_semantic_mesh_depth_rasterizer import (
        AtlasProjectedSemanticMeshDepthRasterizer,
    )
    from CORE.atlas_strasbourg_cathedral_phase7_reference import (
        build_strasbourg_cathedral_phase7_product,
        build_strasbourg_cathedral_phase7_projected_component_meshes,
    )

    rows = 480
    columns = 320
    width_mm = 80.0
    depth_mm = 120.0

    product = build_strasbourg_cathedral_phase7_product()
    projected = (
        build_strasbourg_cathedral_phase7_projected_component_meshes()
    )

    archivolt = (
        AtlasProjectedSemanticMeshDepthRasterizer.rasterize(
            mesh=projected[
                "strasbourg.central_portal.archivolt"
            ]["mesh"],
            target=product.surface_target,
            width_mm=width_mm,
            depth_mm=depth_mm,
            rows=rows,
            columns=columns,
        )
    )

    opening_target = replace(
        product.surface_target,
        relief_polarity="inward",
    )

    opening = (
        AtlasProjectedSemanticMeshDepthRasterizer.rasterize(
            mesh=projected[
                "strasbourg.central_portal.opening"
            ]["mesh"],
            target=opening_target,
            width_mm=width_mm,
            depth_mm=depth_mm,
            rows=rows,
            columns=columns,
        )
    )

    opening_rows, opening_columns = np.nonzero(
        opening["coverage_map"]
    )

    opening_center_row = int(
        round(
            (
                float(opening_rows.min())
                + float(opening_rows.max())
            )
            / 2.0
        )
    )

    opening_center_column = int(
        round(
            (
                float(opening_columns.min())
                + float(opening_columns.max())
            )
            / 2.0
        )
    )

    assert opening["coverage_map"][
        opening_center_row,
        opening_center_column,
    ]

    assert not archivolt["coverage_map"][
        opening_center_row,
        opening_center_column,
    ]


def test_strasbourg_projected_components_follow_accepted_real_photo_registration():
    from dataclasses import replace

    import numpy as np

    from CORE.atlas_projected_semantic_mesh_depth_rasterizer import (
        AtlasProjectedSemanticMeshDepthRasterizer,
    )
    from CORE.atlas_strasbourg_cathedral_phase7_reference import (
        build_strasbourg_cathedral_phase7_product,
        build_strasbourg_cathedral_phase7_projected_component_meshes,
    )

    rows = 480
    columns = 320
    width_mm = 80.0
    depth_mm = 120.0

    reference_width_px = 1333.0
    reference_height_px = 2000.0

    def u_mm(x_px):
        return (
            x_px
            / reference_width_px
            * width_mm
        )

    def v_mm(y_px):
        # Photo Y grows downward; facade V grows upward.
        return (
            1.0
            - y_px / reference_height_px
        ) * depth_mm

    expected_bounds = {
        "strasbourg.central_portal.opening": (
            u_mm(485),
            u_mm(820),
            v_mm(1810),
            v_mm(1480),
        ),
        "strasbourg.central_portal.archivolt": (
            u_mm(285),
            u_mm(1045),
            v_mm(1475),
            v_mm(1010),
        ),
        "strasbourg.central_portal.figurative_tympanum": (
            u_mm(495),
            u_mm(837),
            v_mm(1460),
            v_mm(1160),
        ),
        "strasbourg.central_portal.panel": (
            u_mm(580),
            u_mm(655),
            v_mm(1700),
            v_mm(1625),
        ),
    }

    product = build_strasbourg_cathedral_phase7_product()
    projected = (
        build_strasbourg_cathedral_phase7_projected_component_meshes()
    )

    tolerance_mm = 3.0

    for occurrence_id, expected in expected_bounds.items():
        target = product.surface_target

        if occurrence_id == (
            "strasbourg.central_portal.opening"
        ):
            target = replace(
                target,
                relief_polarity="inward",
            )

        raster = (
            AtlasProjectedSemanticMeshDepthRasterizer
            .rasterize(
                mesh=projected[occurrence_id]["mesh"],
                target=target,
                width_mm=width_mm,
                depth_mm=depth_mm,
                rows=rows,
                columns=columns,
            )
        )

        covered_rows, covered_columns = np.nonzero(
            raster["coverage_map"]
        )

        actual = (
            float(covered_columns.min())
            / (columns - 1)
            * width_mm,
            float(covered_columns.max())
            / (columns - 1)
            * width_mm,
            float(covered_rows.min())
            / (rows - 1)
            * depth_mm,
            float(covered_rows.max())
            / (rows - 1)
            * depth_mm,
        )

        for actual_value, expected_value in zip(
            actual,
            expected,
            strict=True,
        ):
            assert abs(
                actual_value - expected_value
            ) <= tolerance_mm, (
                f"{occurrence_id}: "
                f"actual={actual}, expected={expected}"
            )



def test_strasbourg_phase7_door_panel_is_nested_inside_recessed_opening():
    from dataclasses import replace

    import numpy as np

    from CORE.atlas_projected_semantic_mesh_depth_rasterizer import (
        AtlasProjectedSemanticMeshDepthRasterizer,
    )
    from CORE.atlas_strasbourg_cathedral_phase7_reference import (
        build_strasbourg_cathedral_phase7_product,
        build_strasbourg_cathedral_phase7_projected_component_meshes,
    )

    rows = 480
    columns = 320
    width_mm = 80.0
    depth_mm = 120.0

    reference_width_px = 1333.0
    reference_height_px = 2000.0

    def u_mm(x_px):
        return (
            x_px
            / reference_width_px
            * width_mm
        )

    def v_mm(y_px):
        return (
            1.0
            - y_px / reference_height_px
        ) * depth_mm

    product = build_strasbourg_cathedral_phase7_product()
    projected = (
        build_strasbourg_cathedral_phase7_projected_component_meshes()
    )

    opening_target = replace(
        product.surface_target,
        relief_polarity="inward",
    )

    opening = (
        AtlasProjectedSemanticMeshDepthRasterizer.rasterize(
            mesh=projected[
                "strasbourg.central_portal.opening"
            ]["mesh"],
            target=opening_target,
            width_mm=width_mm,
            depth_mm=depth_mm,
            rows=rows,
            columns=columns,
        )
    )

    panel = (
        AtlasProjectedSemanticMeshDepthRasterizer.rasterize(
            mesh=projected[
                "strasbourg.central_portal.panel"
            ]["mesh"],
            target=product.surface_target,
            width_mm=width_mm,
            depth_mm=depth_mm,
            rows=rows,
            columns=columns,
        )
    )

    archivolt = (
        AtlasProjectedSemanticMeshDepthRasterizer.rasterize(
            mesh=projected[
                "strasbourg.central_portal.archivolt"
            ]["mesh"],
            target=product.surface_target,
            width_mm=width_mm,
            depth_mm=depth_mm,
            rows=rows,
            columns=columns,
        )
    )

    figurative = (
        AtlasProjectedSemanticMeshDepthRasterizer.rasterize(
            mesh=projected[
                "strasbourg.central_portal.figurative_tympanum"
            ]["mesh"],
            target=product.surface_target,
            width_mm=width_mm,
            depth_mm=depth_mm,
            rows=rows,
            columns=columns,
        )
    )

    panel_rows, panel_columns = np.nonzero(
        panel["coverage_map"]
    )

    actual_bounds = (
        float(panel_columns.min())
        / (columns - 1)
        * width_mm,
        float(panel_columns.max())
        / (columns - 1)
        * width_mm,
        float(panel_rows.min())
        / (rows - 1)
        * depth_mm,
        float(panel_rows.max())
        / (rows - 1)
        * depth_mm,
    )

    expected_bounds = (
        u_mm(580),
        u_mm(655),
        v_mm(1700),
        v_mm(1625),
    )

    tolerance_mm = 1.5

    for actual_value, expected_value in zip(
        actual_bounds,
        expected_bounds,
        strict=True,
    ):
        assert abs(
            actual_value - expected_value
        ) <= tolerance_mm

    panel_coverage = panel["coverage_map"]

    assert np.all(
        opening["coverage_map"][panel_coverage]
    )

    assert not np.any(
        archivolt["coverage_map"]
        & panel_coverage
    )

    assert not np.any(
        figurative["coverage_map"]
        & panel_coverage
    )

    opening_depth = opening["depth_map"][
        opening["coverage_map"]
    ]
    panel_depth = panel["depth_map"][
        panel_coverage
    ]

    assert np.max(opening_depth) < 0.0
    assert np.min(panel_depth) > np.max(opening_depth)
    assert np.max(panel_depth) < 0.0



def test_strasbourg_phase7_builds_combined_semantic_structural_depth_reference():
    import numpy as np

    from CORE.atlas_strasbourg_cathedral_phase7_reference import (
        build_strasbourg_cathedral_phase7_combined_semantic_structural_depth_reference,
    )

    result = (
        build_strasbourg_cathedral_phase7_combined_semantic_structural_depth_reference(
            rows=480,
            columns=320,
        )
    )

    assert result["type"] == (
        "strasbourg_phase7_combined_semantic_structural_depth_reference"
    )
    assert result["shape"] == (480, 320)
    assert result["width_mm"] == 80.0
    assert result["depth_mm"] == 120.0

    depth_map = result["depth_map"]
    coverage_map = result["coverage_map"]
    feature_masks = result["feature_masks"]

    assert depth_map.shape == (480, 320)
    assert coverage_map.shape == (480, 320)

    assert set(feature_masks) == {
        "opening",
        "archivolt",
        "figurative_tympanum",
        "panel",
    }

    for mask in feature_masks.values():
        assert mask.shape == (480, 320)
        assert np.any(mask)

    union = np.zeros_like(
        coverage_map,
        dtype=bool,
    )

    for mask in feature_masks.values():
        union |= mask

    np.testing.assert_array_equal(
        coverage_map,
        union,
    )

    opening_only = (
        feature_masks["opening"]
        & ~feature_masks["panel"]
    )

    assert np.any(opening_only)

    np.testing.assert_allclose(
        depth_map[opening_only],
        -0.8,
        atol=1e-9,
    )

    panel_region = feature_masks["panel"]

    assert np.all(
        feature_masks["opening"][panel_region]
    )

    np.testing.assert_allclose(
        depth_map[panel_region],
        -0.3,
        atol=1e-9,
    )

    archivolt_figurative_overlap = (
        feature_masks["archivolt"]
        & feature_masks["figurative_tympanum"]
    )

    assert np.any(
        archivolt_figurative_overlap
    )

    np.testing.assert_allclose(
        depth_map[
            archivolt_figurative_overlap
        ],
        0.9,
        atol=1e-9,
    )

    np.testing.assert_allclose(
        np.min(
            depth_map[coverage_map]
        ),
        -0.8,
        atol=1e-9,
    )

    np.testing.assert_allclose(
        np.max(
            depth_map[coverage_map]
        ),
        0.9,
        atol=1e-9,
    )



def test_strasbourg_phase7_builds_bounded_local_semantic_enhancement():
    import numpy as np

    from CORE.atlas_strasbourg_cathedral_phase7_reference import (
        build_strasbourg_cathedral_phase7_bounded_local_semantic_enhancement,
    )

    result = (
        build_strasbourg_cathedral_phase7_bounded_local_semantic_enhancement(
            rows=480,
            columns=320,
        )
    )

    assert result["type"] == (
        "strasbourg_phase7_bounded_local_semantic_enhancement"
    )

    baseline = result["baseline_height_map"]
    enhanced = result["enhanced_height_map"]
    structural = result["aligned_structural_reference"]
    protection = result["protection_map"]
    correction = result["applied_correction"]

    assert baseline.shape == (480, 320)
    assert enhanced.shape == baseline.shape
    assert structural.shape == baseline.shape
    assert protection.shape == baseline.shape
    assert correction.shape == baseline.shape

    assert float(np.min(baseline)) >= 0.0
    assert float(np.max(baseline)) <= 1.0
    assert float(np.min(enhanced)) >= 0.0
    assert float(np.max(enhanced)) <= 1.0

    active = protection > 0.0
    inactive = ~active

    assert np.any(active)
    assert np.any(inactive)

    np.testing.assert_array_equal(
        enhanced[inactive],
        baseline[inactive],
    )

    np.testing.assert_array_equal(
        correction[inactive],
        np.zeros_like(
            correction[inactive]
        ),
    )

    assert np.any(
        np.abs(
            correction[active]
        ) > 1e-12
    )

    assert float(
        np.max(
            np.abs(
                correction
            )
        )
    ) <= 0.05 + 1e-12

    assert float(
        np.min(
            structural[active]
        )
    ) >= 0.0

    assert float(
        np.max(
            structural[active]
        )
    ) <= 1.0

    assert result["semantic_alignment"] == (
        "vertical_flip_to_photo_array"
    )

    assert result["baseline_identity_source"] == (
        "photo_derived_processed_height_map"
    )



def test_strasbourg_phase7_builds_measurable_generic_vs_semantic_ab():
    from CORE.atlas_strasbourg_cathedral_phase7_reference import (
        build_strasbourg_cathedral_phase7_measurable_generic_vs_semantic_ab,
    )

    result = (
        build_strasbourg_cathedral_phase7_measurable_generic_vs_semantic_ab(
            rows=480,
            columns=320,
        )
    )

    assert result["type"] == (
        "strasbourg_phase7_measurable_generic_vs_semantic_ab"
    )

    assert result["detail_profile"] == {
        "minimum_feature_mm": 0.8,
        "activity_threshold": 0.02,
        "minimum_density": 0.25,
    }

    assert set(result["baseline_measurement"]["features"]) == {
        "opening",
        "archivolt",
        "figurative_tympanum",
        "panel",
    }

    assert set(result["semantic_measurement"]["features"]) == {
        "opening",
        "archivolt",
        "figurative_tympanum",
        "panel",
    }

    assert 0.0 <= result["baseline_readability_score"] <= 1.0
    assert 0.0 <= result["semantic_readability_score"] <= 1.0

    assert result["semantic_readability_score"] > (
        result["baseline_readability_score"]
    )

    comparison = result["comparison_report"]

    assert comparison["type"] == (
        "architectural_semantic_relief_comparison_report"
    )
    assert comparison["semantic_more_readable"] is True
    assert comparison["status"] == "PASS"
    assert comparison["readability_delta"] > 0.0



def test_strasbourg_phase7_builds_production_artifacts():
    import numpy as np

    from CORE.atlas_strasbourg_cathedral_phase7_reference import (
        build_strasbourg_cathedral_phase7_production_artifacts,
    )

    result = (
        build_strasbourg_cathedral_phase7_production_artifacts(
            rows=480,
            columns=320,
        )
    )

    assert result["type"] == (
        "strasbourg_phase7_production_artifacts"
    )

    preview = result["shaded_preview"]

    assert preview.shape == (480, 320)
    assert np.isfinite(preview).all()
    assert float(preview.min()) >= 0.0
    assert float(preview.max()) <= 1.0

    production = result["physical_coupon"]

    assert (
        production["physical_profile"].name
        == "architectural-relief-v1"
    )
    assert (
        production["physical_profile"].base_thickness_mm
        == 0.8
    )
    assert (
        production["physical_profile"].relief_height_mm
        == 1.8
    )
    assert (
        production["physical_profile"].target_sample_spacing_mm
        == 0.25
    )

    assert production["is_printable_topology"] is True

    topology = production["topology_report"]

    assert topology["open_edge_count"] == 0
    assert topology["non_manifold_edge_count"] == 0

    assert (
        production["triangle_count"]
        == production["expected_triangle_count"]
    )

    mesh = production["mesh"]

    assert mesh["width_mm"] == 80.0
    assert mesh["depth_mm"] == 120.0
    assert mesh["base_thickness_mm"] == 0.8
    assert mesh["relief_height_mm"] == 1.8

    assert result["source"] == (
        "physical_slope_conditioned_semantic_enhancement"
    )

    assert result["physical_height_map"]["conditioning_mode"] == (
        "print_ready_triangle_slope_limit"
    )

    quality = result["quality_report"]

    assert quality["status"] == "PASS"
    assert quality["is_print_ready"] is True
    assert quality["issue_count"] == 0
    assert (
        quality["general_quality_report"]["maximum_slope_degrees"]
        <= 55.0 + 1e-9
    )



def test_strasbourg_phase7_physical_detail_scale_conditioning_culls_subscale_photo_detail():
    import numpy as np

    from CORE.atlas_strasbourg_cathedral_phase7_reference import (
        build_strasbourg_cathedral_phase7_bounded_local_semantic_enhancement,
        build_strasbourg_cathedral_phase7_physical_detail_scale_conditioning,
    )

    enhancement = (
        build_strasbourg_cathedral_phase7_bounded_local_semantic_enhancement(
            rows=480,
            columns=320,
        )
    )

    result = (
        build_strasbourg_cathedral_phase7_physical_detail_scale_conditioning(
            rows=480,
            columns=320,
        )
    )

    conditioned = result["height_map"]
    source = enhancement["enhanced_height_map"]
    protection = enhancement["protection_map"].astype(bool)

    assert conditioned.shape == source.shape
    assert np.isfinite(conditioned).all()
    assert float(conditioned.min()) >= 0.0
    assert float(conditioned.max()) <= 1.0

    assert result["source"] == (
        "bounded_local_semantic_enhancement"
    )
    assert result["conditioning_mode"] == (
        "photo_detail_minimum_feature_culling"
    )
    assert result["minimum_feature_mm"] == pytest.approx(0.8)

    assert result["filter_mode"] == (
        "separate_positive_negative_polarities"
    )

    assert result["positive_component_count"] > 0
    assert result["negative_component_count"] > 0
    assert result["positive_culled_component_count"] > 0
    assert result["negative_culled_component_count"] > 0

    assert result["culled_active_pixel_count"] > 30000
    assert result["culled_active_pixel_percent"] > 30.0

    # Semantic structural protection must remain exact.
    assert np.array_equal(
        conditioned[protection],
        source[protection],
    )

    # Product-facing conditioning must actually remove
    # some photo-derived subscale detail.
    assert np.count_nonzero(
        np.abs(conditioned - source) > 0.0
    ) > 0


def test_strasbourg_phase7_physical_slope_conditioning_respects_locked_risk_limit():
    import numpy as np

    from CORE.atlas_strasbourg_cathedral_phase7_reference import (
        build_strasbourg_cathedral_phase7_bounded_local_semantic_enhancement,
        build_strasbourg_cathedral_phase7_physical_height_map,
    )

    enhancement = (
        build_strasbourg_cathedral_phase7_bounded_local_semantic_enhancement(
            rows=480,
            columns=320,
        )
    )

    result = (
        build_strasbourg_cathedral_phase7_physical_height_map(
            rows=480,
            columns=320,
        )
    )

    conditioned = result["height_map"]
    source = enhancement["enhanced_height_map"]

    assert conditioned.shape == source.shape
    assert np.isfinite(conditioned).all()
    assert float(conditioned.min()) >= 0.0
    assert float(conditioned.max()) <= 1.0

    assert result["source"] == (
        "physical_detail_scale_conditioning"
    )
    assert result["conditioning_mode"] == (
        "print_ready_triangle_slope_limit"
    )

    assert result["warning_slope_degrees"] == 55.0
    assert result["critical_slope_degrees"] == 75.0
    assert result["sample_spacing_x_mm"] == pytest.approx(0.25)
    assert result["sample_spacing_y_mm"] == pytest.approx(0.25)

    assert result["maximum_adjacent_rise_mm"] <= (
        result["maximum_allowed_adjacent_rise_mm"] + 1e-9
    )

    assert result["maximum_slope_degrees"] <= 55.0 + 1e-9

    from CORE.atlas_architectural_relief_mesh_producer import (
        AtlasArchitecturalReliefMeshProducer,
    )
    from CORE.atlas_architectural_relief_quality_report import (
        AtlasArchitecturalReliefQualityReport,
    )
    from CORE.atlas_architectural_relief_v1_standard import (
        ARCHITECTURAL_RELIEF_V1,
    )

    production = AtlasArchitecturalReliefMeshProducer.build(
        height_map=conditioned,
        width_mm=80.0,
        depth_mm=120.0,
        physical_profile=(
            ARCHITECTURAL_RELIEF_V1.physical_profile
        ),
    )

    quality = AtlasArchitecturalReliefQualityReport.build(
        mesh_production=production,
        risk_profile=ARCHITECTURAL_RELIEF_V1.risk_profile,
    )

    assert quality["status"] == "PASS"
    assert quality["is_print_ready"] is True
    assert quality["issue_count"] == 0

    assert (
        quality["general_quality_report"]["maximum_slope_degrees"]
        <= 55.0 + 1e-9
    )

    # Conditioning is product-facing and must not mutate
    # the semantic source height map.
    assert np.array_equal(
        enhancement["enhanced_height_map"],
        source,
    )

    assert np.any(
        np.abs(conditioned - source) > 0.0
    )
