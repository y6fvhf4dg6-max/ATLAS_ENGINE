from __future__ import annotations

import pytest

from CORE.atlas_architectural_ornament_catalog import (
    AtlasArchitecturalOrnamentCatalogEntry,
    build_default_architectural_ornament_catalog,
)


def test_arch_catalog_entry_preserves_canonical_identity_and_production_contract():
    entry = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="arch.round_v1",
        version="1.0.0",
        semantic_class="arch",
        style_tags=("round_arch", "generic"),
        parameter_names=(
            "width_mm",
            "height_mm",
            "depth_mm",
            "embed_mm",
            "arch_segments",
        ),
        anchor_names=(
            "center",
            "spring_left",
            "spring_right",
            "apex",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
        ),
        minimum_printable_profile={
            "minimum_width_mm": 0.6,
            "minimum_depth_mm": 0.18,
        },
        material_role="architectural_ornament",
        repetition_mode="repeatable",
        symmetry="bilateral",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "facade_arch_mesher",
        },
        geometry_producer="AtlasFacadeArchMesher",
    )

    assert entry.component_id == "arch.round_v1"
    assert entry.version == "1.0.0"
    assert entry.semantic_class == "arch"
    assert entry.style_tags == (
        "round_arch",
        "generic",
    )
    assert entry.supported_projection_modes == (
        "flat_plane",
        "oriented_planar",
        "bilinear_surface",
    )
    assert entry.minimum_printable_profile[
        "minimum_width_mm"
    ] == 0.6
    assert entry.material_role == "architectural_ornament"
    assert entry.repetition_mode == "repeatable"
    assert entry.symmetry == "bilateral"
    assert entry.output_eligibility == (
        "assembled",
        "relief",
        "kit",
    )
    assert entry.license_id == "atlas_internal_v1"
    assert entry.provenance["source_system"] == "facade_arch_mesher"
    assert entry.geometry_producer == "AtlasFacadeArchMesher"


def test_architectural_ornament_catalog_registers_and_resolves_canonical_entry():
    from CORE.atlas_architectural_ornament_catalog import (
        AtlasArchitecturalOrnamentCatalog,
    )

    entry = AtlasArchitecturalOrnamentCatalogEntry(
        component_id="arch.round_v1",
        version="1.0.0",
        semantic_class="arch",
        style_tags=("round_arch", "generic"),
        parameter_names=(
            "width_mm",
            "height_mm",
            "depth_mm",
            "embed_mm",
            "arch_segments",
        ),
        anchor_names=(
            "center",
            "spring_left",
            "spring_right",
            "apex",
        ),
        supported_projection_modes=(
            "flat_plane",
            "oriented_planar",
            "bilinear_surface",
        ),
        minimum_printable_profile={
            "minimum_width_mm": 0.6,
            "minimum_depth_mm": 0.18,
        },
        material_role="architectural_ornament",
        repetition_mode="repeatable",
        symmetry="bilateral",
        output_eligibility=(
            "assembled",
            "relief",
            "kit",
        ),
        license_id="atlas_internal_v1",
        provenance={
            "source_system": "facade_arch_mesher",
        },
        geometry_producer="AtlasFacadeArchMesher",
    )

    catalog = AtlasArchitecturalOrnamentCatalog(
        entries=(entry,),
    )

    resolved = catalog.get(
        component_id="arch.round_v1",
        version="1.0.0",
    )

    assert resolved is entry
    assert catalog.component_ids == (
        "arch.round_v1",
    )


def test_architectural_ornament_catalog_rejects_duplicate_component_version():
    from CORE.atlas_architectural_ornament_catalog import (
        AtlasArchitecturalOrnamentCatalog,
    )

    def make_entry():
        return AtlasArchitecturalOrnamentCatalogEntry(
            component_id="arch.round_v1",
            version="1.0.0",
            semantic_class="arch",
            style_tags=("round_arch", "generic"),
            parameter_names=(
                "width_mm",
                "height_mm",
                "depth_mm",
                "embed_mm",
                "arch_segments",
            ),
            anchor_names=(
                "center",
                "spring_left",
                "spring_right",
                "apex",
            ),
            supported_projection_modes=(
                "flat_plane",
                "oriented_planar",
                "bilinear_surface",
            ),
            minimum_printable_profile={
                "minimum_width_mm": 0.6,
                "minimum_depth_mm": 0.18,
            },
            material_role="architectural_ornament",
            repetition_mode="repeatable",
            symmetry="bilateral",
            output_eligibility=(
                "assembled",
                "relief",
                "kit",
            ),
            license_id="atlas_internal_v1",
            provenance={
                "source_system": "facade_arch_mesher",
            },
            geometry_producer="AtlasFacadeArchMesher",
        )

    with pytest.raises(
        ValueError,
        match="duplicate architectural ornament catalog entry",
    ):
        AtlasArchitecturalOrnamentCatalog(
            entries=(
                make_entry(),
                make_entry(),
            ),
        )


def test_default_architectural_ornament_catalog_contains_round_arch_v1():
    from CORE.atlas_architectural_ornament_catalog import (
        build_default_architectural_ornament_catalog,
    )

    catalog = build_default_architectural_ornament_catalog()

    entry = catalog.get(
        component_id="arch.round_v1",
        version="1.0.0",
    )

    assert entry.semantic_class == "arch"
    assert entry.geometry_producer == "AtlasFacadeArchMesher"
    assert entry.provenance["source_system"] == "facade_arch_mesher"
    assert entry.repetition_mode == "repeatable"
    assert entry.symmetry == "bilateral"
    assert "relief" in entry.output_eligibility
    assert "kit" in entry.output_eligibility


def test_default_architectural_ornament_catalog_contains_cornice_band_v1():
    from CORE.atlas_architectural_ornament_catalog import (
        build_default_architectural_ornament_catalog,
    )

    catalog = build_default_architectural_ornament_catalog()

    entry = catalog.get(
        component_id="cornice.band_v1",
        version="1.0.0",
    )

    assert entry.semantic_class == "cornice"
    assert entry.geometry_producer == "AtlasFacadeCorniceMesher"
    assert entry.provenance["source_system"] == "facade_cornice_mesher"
    assert entry.repetition_mode == "repeatable"
    assert entry.symmetry == "linear"
    assert "assembled" in entry.output_eligibility
    assert "relief" in entry.output_eligibility
    assert "kit" in entry.output_eligibility


def test_catalog_entry_rejects_duplicate_parameter_and_anchor_names():
    with pytest.raises(
        ValueError,
        match="parameter_names.*unique",
    ):
        AtlasArchitecturalOrnamentCatalogEntry(
            component_id="arch.invalid_v1",
            version="1.0.0",
            semantic_class="arch",
            style_tags=("generic",),
            parameter_names=(
                "width_mm",
                "width_mm",
            ),
            anchor_names=(
                "center",
                "apex",
            ),
            supported_projection_modes=(
                "flat_plane",
            ),
            minimum_printable_profile={
                "minimum_width_mm": 0.6,
            },
            material_role="architectural_ornament",
            repetition_mode="repeatable",
            symmetry="bilateral",
            output_eligibility=(
                "relief",
            ),
            license_id="atlas_internal_v1",
            provenance={
                "source_system": "test",
            },
            geometry_producer="AtlasFacadeArchMesher",
        )

    with pytest.raises(
        ValueError,
        match="anchor_names.*unique",
    ):
        AtlasArchitecturalOrnamentCatalogEntry(
            component_id="arch.invalid_anchor_v1",
            version="1.0.0",
            semantic_class="arch",
            style_tags=("generic",),
            parameter_names=(
                "width_mm",
                "height_mm",
            ),
            anchor_names=(
                "center",
                "center",
            ),
            supported_projection_modes=(
                "flat_plane",
            ),
            minimum_printable_profile={
                "minimum_width_mm": 0.6,
            },
            material_role="architectural_ornament",
            repetition_mode="repeatable",
            symmetry="bilateral",
            output_eligibility=(
                "relief",
            ),
            license_id="atlas_internal_v1",
            provenance={
                "source_system": "test",
            },
            geometry_producer="AtlasFacadeArchMesher",
        )


def test_catalog_entry_rejects_invalid_minimum_printable_profile_values():
    with pytest.raises(
        ValueError,
        match="minimum_printable_profile.*positive",
    ):
        AtlasArchitecturalOrnamentCatalogEntry(
            component_id="arch.invalid_profile_v1",
            version="1.0.0",
            semantic_class="arch",
            style_tags=("generic",),
            parameter_names=(
                "width_mm",
                "height_mm",
            ),
            anchor_names=(
                "center",
                "apex",
            ),
            supported_projection_modes=(
                "flat_plane",
            ),
            minimum_printable_profile={
                "minimum_width_mm": 0.0,
                "minimum_depth_mm": -0.1,
            },
            material_role="architectural_ornament",
            repetition_mode="repeatable",
            symmetry="bilateral",
            output_eligibility=(
                "relief",
            ),
            license_id="atlas_internal_v1",
            provenance={
                "source_system": "test",
            },
            geometry_producer="AtlasFacadeArchMesher",
        )


def test_catalog_entry_rejects_unknown_projection_mode():
    with pytest.raises(
        ValueError,
        match="supported_projection_modes.*unsupported",
    ):
        AtlasArchitecturalOrnamentCatalogEntry(
            component_id="arch.invalid_projection_v1",
            version="1.0.0",
            semantic_class="arch",
            style_tags=("generic",),
            parameter_names=(
                "width_mm",
                "height_mm",
            ),
            anchor_names=(
                "center",
                "apex",
            ),
            supported_projection_modes=(
                "flat_plane",
                "teleport_surface",
            ),
            minimum_printable_profile={
                "minimum_width_mm": 0.6,
            },
            material_role="architectural_ornament",
            repetition_mode="repeatable",
            symmetry="bilateral",
            output_eligibility=(
                "relief",
            ),
            license_id="atlas_internal_v1",
            provenance={
                "source_system": "test",
            },
            geometry_producer="AtlasFacadeArchMesher",
        )


def test_catalog_entry_rejects_unknown_output_eligibility():
    with pytest.raises(
        ValueError,
        match="output_eligibility.*unsupported",
    ):
        AtlasArchitecturalOrnamentCatalogEntry(
            component_id="arch.invalid_output_v1",
            version="1.0.0",
            semantic_class="arch",
            style_tags=("generic",),
            parameter_names=(
                "width_mm",
                "height_mm",
            ),
            anchor_names=(
                "center",
                "apex",
            ),
            supported_projection_modes=(
                "flat_plane",
            ),
            minimum_printable_profile={
                "minimum_width_mm": 0.6,
            },
            material_role="architectural_ornament",
            repetition_mode="repeatable",
            symmetry="bilateral",
            output_eligibility=(
                "relief",
                "hologram",
            ),
            license_id="atlas_internal_v1",
            provenance={
                "source_system": "test",
            },
            geometry_producer="AtlasFacadeArchMesher",
        )


def test_catalog_entry_binds_deterministic_parameterized_instance():
    entry = build_default_architectural_ornament_catalog().get(
        component_id="arch.round_v1",
        version="1.0.0",
    )

    first = entry.bind(
        parameters={
            "width_mm": 8.0,
            "height_mm": 6.0,
            "depth_mm": 0.24,
            "embed_mm": 0.04,
            "arch_segments": 12,
        },
    )
    second = entry.bind(
        parameters={
            "width_mm": 8.0,
            "height_mm": 6.0,
            "depth_mm": 0.24,
            "embed_mm": 0.04,
            "arch_segments": 12,
        },
    )

    assert first == second
    assert first.component_id == "arch.round_v1"
    assert first.version == "1.0.0"
    assert first.parameters["width_mm"] == 8.0
    assert first.parameters["height_mm"] == 6.0
    assert first.geometry_producer == "AtlasFacadeArchMesher"


def test_catalog_entry_bind_rejects_non_positive_numeric_dimensions():
    entry = build_default_architectural_ornament_catalog().get(
        component_id="arch.round_v1",
        version="1.0.0",
    )

    with pytest.raises(
        ValueError,
        match="width_mm.*positive",
    ):
        entry.bind(
            parameters={
                "width_mm": 0.0,
                "height_mm": 6.0,
                "depth_mm": 0.24,
                "embed_mm": 0.04,
                "arch_segments": 12,
            },
        )


def test_same_catalog_component_binds_different_sizes_deterministically():
    entry = build_default_architectural_ornament_catalog().get(
        component_id="arch.round_v1",
        version="1.0.0",
    )

    small = entry.bind(
        parameters={
            "width_mm": 6.0,
            "height_mm": 4.0,
            "depth_mm": 0.20,
            "embed_mm": 0.04,
            "arch_segments": 8,
        },
    )
    large = entry.bind(
        parameters={
            "width_mm": 12.0,
            "height_mm": 8.0,
            "depth_mm": 0.30,
            "embed_mm": 0.04,
            "arch_segments": 16,
        },
    )

    assert small.component_id == large.component_id == "arch.round_v1"
    assert small.version == large.version == "1.0.0"
    assert small != large
    assert small.parameters["width_mm"] == 6.0
    assert large.parameters["width_mm"] == 12.0

    assert entry.bind(parameters=dict(small.parameters)) == small
    assert entry.bind(parameters=dict(large.parameters)) == large


def test_repeated_catalog_instances_preserve_canonical_identity_with_distinct_occurrences():
    entry = build_default_architectural_ornament_catalog().get(
        component_id="cornice.band_v1",
        version="1.0.0",
    )

    parameters = {
        "band_height_mm": 0.6,
        "depth_mm": 0.28,
        "embed_mm": 0.04,
    }

    first = entry.bind(
        parameters=parameters,
        occurrence_id="facade_north_cornice_01",
    )
    second = entry.bind(
        parameters=parameters,
        occurrence_id="facade_north_cornice_02",
    )

    assert first.component_id == second.component_id == "cornice.band_v1"
    assert first.version == second.version == "1.0.0"
    assert first.parameters == second.parameters
    assert first.occurrence_id == "facade_north_cornice_01"
    assert second.occurrence_id == "facade_north_cornice_02"
    assert first != second


def test_round_arch_catalog_entry_geometry_passes_existing_topology_gate():
    from CORE.atlas_facade_arch_mesher import (
        AtlasFacadeArchMesher,
    )
    from CORE.atlas_facade_opening_layout import (
        AtlasFacadeOpeningAnalysis,
        AtlasFacadeOpening,
    )
    from CORE.atlas_mesh_validator import (
        AtlasMeshValidator,
    )

    entry = build_default_architectural_ornament_catalog().get(
        component_id="arch.round_v1",
        version="1.0.0",
    )

    instance = entry.bind(
        parameters={
            "width_mm": 6.0,
            "height_mm": 5.0,
            "depth_mm": 0.24,
            "embed_mm": 0.04,
            "arch_segments": 8,
        },
    )

    opening = AtlasFacadeOpening(
        opening_index=0,
        opening_kind="arch",
        level_index=0,
        bay_index=0,
        region_name="catalog_acceptance",
        bay_u_min=0.0,
        bay_u_max=1.0,
        floor_v_min=0.0,
        floor_v_max=1.0,
        u_min=0.0,
        u_max=1.0,
        v_min=0.0,
        v_max=1.0,
    )

    analysis = AtlasFacadeOpeningAnalysis(
        openings=(opening,),
    )

    result = AtlasFacadeArchMesher.build(
        wall_quad=(
            (0.0, 0.0, 0.0),
            (instance.parameters["width_mm"], 0.0, 0.0),
            (
                instance.parameters["width_mm"],
                0.0,
                instance.parameters["height_mm"],
            ),
            (0.0, 0.0, instance.parameters["height_mm"]),
        ),
        opening_analysis=analysis,
        depth_mm=instance.parameters["depth_mm"],
        embed_mm=instance.parameters["embed_mm"],
        arch_segments=instance.parameters["arch_segments"],
    )

    assert len(result["component_meshes"]) == 1

    report = AtlasMeshValidator._topology_report(
        result["component_meshes"][0]
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_cornice_catalog_entry_geometry_passes_existing_topology_gate():
    from CORE.atlas_facade_cornice_layout import (
        AtlasFacadeCorniceLayout,
    )
    from CORE.atlas_facade_cornice_mesher import (
        AtlasFacadeCorniceMesher,
    )
    from CORE.atlas_facade_region_analyzer import (
        AtlasFacadeRegionAnalyzer,
    )
    from CORE.atlas_mesh_validator import (
        AtlasMeshValidator,
    )

    entry = build_default_architectural_ornament_catalog().get(
        component_id="cornice.band_v1",
        version="1.0.0",
    )

    instance = entry.bind(
        parameters={
            "band_height_mm": 0.6,
            "depth_mm": 0.28,
            "embed_mm": 0.04,
        },
    )

    region_analysis = AtlasFacadeRegionAnalyzer.analyze(
        tags={
            "building:levels": "4",
        },
        total_height_m=14.0,
    )

    cornice_analysis = AtlasFacadeCorniceLayout.create(
        region_analysis=region_analysis,
        include_top_cornice=False,
    )

    result = AtlasFacadeCorniceMesher.build(
        wall_quad=(
            (0.0, 0.0, 0.0),
            (12.0, 0.0, 0.0),
            (12.0, 0.0, 14.0),
            (0.0, 0.0, 14.0),
        ),
        cornice_analysis=cornice_analysis,
        band_height_mm=instance.parameters["band_height_mm"],
        depth_mm=instance.parameters["depth_mm"],
        embed_mm=instance.parameters["embed_mm"],
    )

    assert result["component_meshes"]

    for component in result["component_meshes"]:
        report = AtlasMeshValidator._topology_report(
            component
        )

        assert report["open_edge_count"] == 0
        assert report["non_manifold_edge_count"] == 0


def test_round_arch_bind_rejects_below_minimum_printable_width():
    entry = build_default_architectural_ornament_catalog().get(
        component_id="arch.round_v1",
        version="1.0.0",
    )

    with pytest.raises(
        ValueError,
        match="minimum printable profile",
    ):
        entry.bind(
            parameters={
                "width_mm": 0.4,
                "height_mm": 4.0,
                "depth_mm": 0.20,
                "embed_mm": 0.04,
                "arch_segments": 8,
            },
        )


def test_default_catalog_contains_recessed_rectangular_opening_v1():
    catalog = build_default_architectural_ornament_catalog()

    entry = catalog.get(
        component_id="opening.recessed_rect_v1",
        version="1.0.0",
    )

    assert entry.semantic_class == "recessed_opening"
    assert entry.geometry_producer == "AtlasFacadeOpeningMesher"
    assert entry.provenance["source_system"] == "facade_opening_mesher"
    assert entry.parameter_names == (
        "width_mm",
        "height_mm",
        "depth_mm",
        "embed_mm",
    )
    assert entry.anchor_names == (
        "center",
        "bottom_left",
        "bottom_right",
        "top_right",
        "top_left",
    )
    assert "flat_plane" in entry.supported_projection_modes
    assert "oriented_planar" in entry.supported_projection_modes
    assert "bilinear_surface" in entry.supported_projection_modes
    assert "relief" in entry.output_eligibility
    assert "kit" in entry.output_eligibility


def test_default_catalog_contains_circular_medallion_v1():
    catalog = build_default_architectural_ornament_catalog()

    entry = catalog.get(
        component_id="medallion.circular_v1",
        version="1.0.0",
    )

    assert entry.semantic_class == "medallion"
    assert entry.geometry_producer == "AtlasFacadeCircularPanelBuilder"
    assert (
        entry.provenance["source_system"]
        == "facade_circular_panel_builder"
    )
    assert entry.parameter_names == (
        "diameter_mm",
        "depth_mm",
        "embed_mm",
        "segments",
    )
    assert entry.anchor_names == (
        "center",
    )
    assert "flat_plane" in entry.supported_projection_modes
    assert "oriented_planar" in entry.supported_projection_modes
    assert "bilinear_surface" in entry.supported_projection_modes
    assert "relief" in entry.output_eligibility
    assert "kit" in entry.output_eligibility


def test_medallion_catalog_entry_geometry_passes_existing_topology_gate():
    from CORE.atlas_facade_circular_panel_builder import (
        AtlasFacadeCircularPanelBuilder,
    )
    from CORE.atlas_mesh_validator import (
        AtlasMeshValidator,
    )

    entry = build_default_architectural_ornament_catalog().get(
        component_id="medallion.circular_v1",
        version="1.0.0",
    )

    instance = entry.bind(
        parameters={
            "diameter_mm": 8.0,
            "depth_mm": 0.24,
            "embed_mm": 0.04,
            "segments": 16,
        },
    )

    wall_width_mm = 20.0
    wall_height_mm = 20.0

    result = AtlasFacadeCircularPanelBuilder.build(
        wall_quad=(
            (0.0, 0.0, 0.0),
            (wall_width_mm, 0.0, 0.0),
            (wall_width_mm, 0.0, wall_height_mm),
            (0.0, 0.0, wall_height_mm),
        ),
        center_u=0.5,
        center_v=0.5,
        diameter_ratio=(
            instance.parameters["diameter_mm"]
            / min(
                wall_width_mm,
                wall_height_mm,
            )
        ),
        depth_mm=instance.parameters["depth_mm"],
        embed_mm=instance.parameters["embed_mm"],
        segments=instance.parameters["segments"],
    )

    report = AtlasMeshValidator._topology_report(
        result
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_default_catalog_contains_rectangular_inscription_panel_v1():
    catalog = build_default_architectural_ornament_catalog()

    entry = catalog.get(
        component_id="panel.inscription_rect_v1",
        version="1.0.0",
    )

    assert entry.semantic_class == "inscription_panel"
    assert entry.geometry_producer == "AtlasFacadePanelBuilder"
    assert entry.provenance["source_system"] == "facade_panel_builder"
    assert entry.parameter_names == (
        "width_mm",
        "height_mm",
        "depth_mm",
        "embed_mm",
    )
    assert entry.anchor_names == (
        "center",
        "bottom_left",
        "bottom_right",
        "top_right",
        "top_left",
    )
    assert entry.repetition_mode == "repeatable"
    assert entry.symmetry == "bilateral"
    assert "flat_plane" in entry.supported_projection_modes
    assert "oriented_planar" in entry.supported_projection_modes
    assert "bilinear_surface" in entry.supported_projection_modes
    assert "relief" in entry.output_eligibility
    assert "kit" in entry.output_eligibility


def test_inscription_panel_catalog_entry_geometry_passes_existing_topology_gate():
    from CORE.atlas_facade_panel_builder import (
        AtlasFacadePanelBuilder,
    )
    from CORE.atlas_mesh_validator import (
        AtlasMeshValidator,
    )

    entry = build_default_architectural_ornament_catalog().get(
        component_id="panel.inscription_rect_v1",
        version="1.0.0",
    )

    instance = entry.bind(
        parameters={
            "width_mm": 8.0,
            "height_mm": 3.0,
            "depth_mm": 0.24,
            "embed_mm": 0.04,
        },
    )

    wall_width_mm = 12.0
    wall_height_mm = 8.0

    result = AtlasFacadePanelBuilder.build_repeated_rectangles(
        wall_quad=(
            (0.0, 0.0, 0.0),
            (wall_width_mm, 0.0, 0.0),
            (wall_width_mm, 0.0, wall_height_mm),
            (0.0, 0.0, wall_height_mm),
        ),
        column_count=1,
        row_count=1,
        panel_width_ratio=(
            instance.parameters["width_mm"]
            / wall_width_mm
        ),
        panel_height_ratio=(
            instance.parameters["height_mm"]
            / wall_height_mm
        ),
        horizontal_margin_ratio=0.0,
        vertical_margin_ratio=0.0,
        depth_mm=instance.parameters["depth_mm"],
        embed_mm=instance.parameters["embed_mm"],
    )

    assert len(result["component_meshes"]) == 1

    report = AtlasMeshValidator._topology_report(
        result["component_meshes"][0]
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_default_catalog_contains_rectangular_portal_surround_v1():
    catalog = build_default_architectural_ornament_catalog()

    entry = catalog.get(
        component_id="portal.surround_rect_v1",
        version="1.0.0",
    )

    assert entry.semantic_class == "portal_surround"
    assert entry.geometry_producer == "AtlasFacadePortalSurroundMesher"
    assert (
        entry.provenance["source_system"]
        == "facade_portal_surround_mesher"
    )
    assert entry.parameter_names == (
        "width_mm",
        "height_mm",
        "surround_width_mm",
        "depth_mm",
        "embed_mm",
    )
    assert entry.anchor_names == (
        "center",
        "threshold_center",
        "lintel_center",
    )
    assert entry.repetition_mode == "repeatable"
    assert entry.symmetry == "bilateral"
    assert "flat_plane" in entry.supported_projection_modes
    assert "oriented_planar" in entry.supported_projection_modes
    assert "bilinear_surface" in entry.supported_projection_modes
    assert "relief" in entry.output_eligibility
    assert "kit" in entry.output_eligibility


def test_portal_surround_catalog_entry_geometry_passes_existing_topology_gate():
    from CORE.atlas_facade_bay_analyzer import (
        AtlasFacadeBayAnalyzer,
    )
    from CORE.atlas_facade_opening_layout import (
        AtlasFacadeOpeningLayout,
    )
    from CORE.atlas_facade_portal_surround_mesher import (
        AtlasFacadePortalSurroundMesher,
    )
    from CORE.atlas_facade_region_analyzer import (
        AtlasFacadeRegionAnalyzer,
    )
    from CORE.atlas_mesh_validator import (
        AtlasMeshValidator,
    )

    entry = build_default_architectural_ornament_catalog().get(
        component_id="portal.surround_rect_v1",
        version="1.0.0",
    )

    instance = entry.bind(
        parameters={
            "width_mm": 4.8,
            "height_mm": 5.6,
            "surround_width_mm": 0.8,
            "depth_mm": 0.24,
            "embed_mm": 0.04,
        },
    )

    region_analysis = AtlasFacadeRegionAnalyzer.analyze(
        tags={
            "building:levels": "1",
        },
        total_height_m=7.0,
    )
    bay_analysis = AtlasFacadeBayAnalyzer.analyze(
        region_analysis=region_analysis,
        bay_count=1,
    )
    opening_analysis = AtlasFacadeOpeningLayout.create_uniform(
        bay_analysis=bay_analysis,
        opening_kind="portal",
        horizontal_margin_ratio=0.30,
        vertical_margin_ratio=0.10,
    )

    result = AtlasFacadePortalSurroundMesher.build(
        wall_quad=(
            (0.0, 0.0, 0.0),
            (12.0, 0.0, 0.0),
            (12.0, 0.0, 7.0),
            (0.0, 0.0, 7.0),
        ),
        opening_analysis=opening_analysis,
        surround_width_ratio=(
            instance.parameters["surround_width_mm"]
            / instance.parameters["width_mm"]
        ),
        depth_mm=instance.parameters["depth_mm"],
        embed_mm=instance.parameters["embed_mm"],
    )

    assert result["portal_count"] == 1
    assert len(result["component_meshes"]) == 3

    for component in result["component_meshes"]:
        report = AtlasMeshValidator._topology_report(
            component
        )

        assert report["open_edge_count"] == 0
        assert report["non_manifold_edge_count"] == 0


def test_default_catalog_contains_rectangular_pilaster_v1():
    catalog = build_default_architectural_ornament_catalog()

    entry = catalog.get(
        component_id="pilaster.rect_v1",
        version="1.0.0",
    )

    assert entry.semantic_class == "pilaster"
    assert entry.geometry_producer == "AtlasFacadePilasterMesher"
    assert (
        entry.provenance["source_system"]
        == "facade_pilaster_mesher"
    )
    assert entry.parameter_names == (
        "width_mm",
        "height_mm",
        "depth_mm",
        "embed_mm",
    )
    assert entry.anchor_names == (
        "center",
        "base_center",
        "top_center",
    )
    assert entry.repetition_mode == "repeatable"
    assert entry.symmetry == "bilateral"
    assert "flat_plane" in entry.supported_projection_modes
    assert "oriented_planar" in entry.supported_projection_modes
    assert "bilinear_surface" in entry.supported_projection_modes
    assert "assembled" in entry.output_eligibility
    assert "relief" in entry.output_eligibility
    assert "kit" in entry.output_eligibility


def test_pilaster_catalog_entry_geometry_passes_existing_topology_gate():
    from CORE.atlas_facade_pilaster_mesher import (
        AtlasFacadePilasterMesher,
    )
    from CORE.atlas_mesh_validator import (
        AtlasMeshValidator,
    )

    entry = build_default_architectural_ornament_catalog().get(
        component_id="pilaster.rect_v1",
        version="1.0.0",
    )

    instance = entry.bind(
        parameters={
            "width_mm": 1.2,
            "height_mm": 5.6,
            "depth_mm": 0.24,
            "embed_mm": 0.04,
        },
    )

    wall_width_mm = 12.0
    wall_height_mm = 7.0

    result = AtlasFacadePilasterMesher.build(
        wall_quad=(
            (0.0, 0.0, 0.0),
            (wall_width_mm, 0.0, 0.0),
            (wall_width_mm, 0.0, wall_height_mm),
            (0.0, 0.0, wall_height_mm),
        ),
        center_u=0.5,
        width_ratio=(
            instance.parameters["width_mm"]
            / wall_width_mm
        ),
        v_min=(
            (wall_height_mm - instance.parameters["height_mm"])
            / 2.0
            / wall_height_mm
        ),
        v_max=(
            1.0
            - (
                (wall_height_mm - instance.parameters["height_mm"])
                / 2.0
                / wall_height_mm
            )
        ),
        depth_mm=instance.parameters["depth_mm"],
        embed_mm=instance.parameters["embed_mm"],
    )

    assert result["pilaster_count"] == 1

    report = AtlasMeshValidator._topology_report(
        result["component_meshes"][0]
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_default_catalog_contains_classical_round_column_v1():
    catalog = build_default_architectural_ornament_catalog()

    entry = catalog.get(
        component_id="column.classical_round_v1",
        version="1.0.0",
    )

    assert entry.semantic_class == "column"
    assert entry.geometry_producer == "AtlasClassicalColonnadeBuilder"
    assert (
        entry.provenance["source_system"]
        == "classical_colonnade"
    )
    assert entry.parameter_names == (
        "diameter_mm",
        "height_mm",
        "segments",
    )
    assert entry.anchor_names == (
        "center",
        "base_center",
        "top_center",
    )
    assert entry.repetition_mode == "repeatable"
    assert entry.symmetry == "radial"
    assert "flat_plane" in entry.supported_projection_modes
    assert "oriented_planar" in entry.supported_projection_modes
    assert "assembled" in entry.output_eligibility
    assert "relief" in entry.output_eligibility
    assert "kit" in entry.output_eligibility


def test_classical_round_column_catalog_entry_geometry_passes_existing_topology_gate():
    from CORE.atlas_classical_colonnade_builder import (
        AtlasClassicalColonnadeBuilder,
    )
    from CORE.atlas_mesh_validator import (
        AtlasMeshValidator,
    )

    entry = build_default_architectural_ornament_catalog().get(
        component_id="column.classical_round_v1",
        version="1.0.0",
    )

    instance = entry.bind(
        parameters={
            "diameter_mm": 1.2,
            "height_mm": 3.0,
            "segments": 12,
        },
    )

    result = AtlasClassicalColonnadeBuilder.build_along_polyline(
        path_points=(
            (0.0, 0.0),
            (4.0, 0.0),
        ),
        base_z=0.0,
        column_radius_mm=(
            instance.parameters["diameter_mm"]
            / 2.0
        ),
        column_height_mm=instance.parameters["height_mm"],
        target_spacing_mm=4.0,
        column_segments=instance.parameters["segments"],
        include_endpoints=True,
    )

    assert result["column_count"] == 2

    for component in result["component_meshes"]:
        assert component["component_type"] == "classical_column"
        assert component["source_system"] == "classical_colonnade"

        report = AtlasMeshValidator._topology_report(
            component
        )

        assert report["open_edge_count"] == 0
        assert report["non_manifold_edge_count"] == 0


def test_default_catalog_contains_classical_round_column_base_v1():
    catalog = build_default_architectural_ornament_catalog()

    entry = catalog.get(
        component_id="column_base.classical_round_v1",
        version="1.0.0",
    )

    assert entry.semantic_class == "column_base"
    assert entry.geometry_producer == "AtlasClassicalColumnDetailMesher"
    assert (
        entry.provenance["source_system"]
        == "classical_column_detail_mesher"
    )
    assert entry.parameter_names == (
        "diameter_mm",
        "height_mm",
        "segments",
    )
    assert entry.anchor_names == (
        "center",
        "bottom_center",
        "top_center",
    )
    assert entry.repetition_mode == "repeatable"
    assert entry.symmetry == "radial"
    assert "assembled" in entry.output_eligibility
    assert "relief" in entry.output_eligibility
    assert "kit" in entry.output_eligibility


def test_default_catalog_contains_classical_round_column_capital_v1():
    catalog = build_default_architectural_ornament_catalog()

    entry = catalog.get(
        component_id="column_capital.classical_round_v1",
        version="1.0.0",
    )

    assert entry.semantic_class == "column_capital"
    assert entry.geometry_producer == "AtlasClassicalColumnDetailMesher"
    assert (
        entry.provenance["source_system"]
        == "classical_column_detail_mesher"
    )
    assert entry.parameter_names == (
        "diameter_mm",
        "height_mm",
        "segments",
    )
    assert entry.anchor_names == (
        "center",
        "bottom_center",
        "top_center",
    )
    assert entry.repetition_mode == "repeatable"
    assert entry.symmetry == "radial"
    assert "assembled" in entry.output_eligibility
    assert "relief" in entry.output_eligibility
    assert "kit" in entry.output_eligibility


def test_classical_column_base_and_capital_catalog_entries_pass_topology_gate():
    from CORE.atlas_classical_column_detail_mesher import (
        AtlasClassicalColumnDetailMesher,
    )
    from CORE.atlas_mesh_validator import (
        AtlasMeshValidator,
    )

    catalog = build_default_architectural_ornament_catalog()

    base_entry = catalog.get(
        component_id="column_base.classical_round_v1",
        version="1.0.0",
    )
    capital_entry = catalog.get(
        component_id="column_capital.classical_round_v1",
        version="1.0.0",
    )

    base_instance = base_entry.bind(
        parameters={
            "diameter_mm": 1.6,
            "height_mm": 0.4,
            "segments": 12,
        },
    )
    capital_instance = capital_entry.bind(
        parameters={
            "diameter_mm": 1.8,
            "height_mm": 0.5,
            "segments": 12,
        },
    )

    result = AtlasClassicalColumnDetailMesher.build(
        center_x=0.0,
        center_y=0.0,
        shaft_base_z=0.4,
        shaft_top_z=3.4,
        base_diameter_mm=base_instance.parameters["diameter_mm"],
        base_height_mm=base_instance.parameters["height_mm"],
        capital_diameter_mm=capital_instance.parameters["diameter_mm"],
        capital_height_mm=capital_instance.parameters["height_mm"],
        segments=base_instance.parameters["segments"],
    )

    assert result["base"]["detail_role"] == "base"
    assert result["capital"]["detail_role"] == "capital"

    for component in (
        result["base"],
        result["capital"],
    ):
        report = AtlasMeshValidator._topology_report(
            component
        )

        assert report["open_edge_count"] == 0
        assert report["non_manifold_edge_count"] == 0


def test_default_catalog_contains_generic_frieze_band_v1():
    catalog = build_default_architectural_ornament_catalog()

    entry = catalog.get(
        component_id="frieze.band_v1",
        version="1.0.0",
    )

    assert entry.semantic_class == "frieze"
    assert entry.geometry_producer == "AtlasFacadePanelBuilder"
    assert entry.provenance["source_system"] == "facade_panel_builder"
    assert entry.parameter_names == (
        "width_mm",
        "height_mm",
        "depth_mm",
        "embed_mm",
    )
    assert entry.anchor_names == (
        "center",
        "start",
        "end",
    )
    assert entry.repetition_mode == "repeatable"
    assert entry.symmetry == "linear"
    assert "flat_plane" in entry.supported_projection_modes
    assert "oriented_planar" in entry.supported_projection_modes
    assert "bilinear_surface" in entry.supported_projection_modes
    assert "assembled" in entry.output_eligibility
    assert "relief" in entry.output_eligibility
    assert "kit" in entry.output_eligibility


def test_frieze_band_catalog_entry_geometry_passes_existing_topology_gate():
    from CORE.atlas_facade_panel_builder import (
        AtlasFacadePanelBuilder,
    )
    from CORE.atlas_mesh_validator import (
        AtlasMeshValidator,
    )

    entry = build_default_architectural_ornament_catalog().get(
        component_id="frieze.band_v1",
        version="1.0.0",
    )

    instance = entry.bind(
        parameters={
            "width_mm": 10.0,
            "height_mm": 0.8,
            "depth_mm": 0.24,
            "embed_mm": 0.04,
        },
    )

    wall_width_mm = 12.0
    wall_height_mm = 7.0

    result = AtlasFacadePanelBuilder.build_repeated_rectangles(
        wall_quad=(
            (0.0, 0.0, 0.0),
            (wall_width_mm, 0.0, 0.0),
            (wall_width_mm, 0.0, wall_height_mm),
            (0.0, 0.0, wall_height_mm),
        ),
        column_count=1,
        row_count=1,
        panel_width_ratio=(
            instance.parameters["width_mm"]
            / wall_width_mm
        ),
        panel_height_ratio=(
            instance.parameters["height_mm"]
            / wall_height_mm
        ),
        horizontal_margin_ratio=0.0,
        vertical_margin_ratio=0.0,
        depth_mm=instance.parameters["depth_mm"],
        embed_mm=instance.parameters["embed_mm"],
        metadata={
            "component_type": "facade_frieze",
            "source_system": "facade_panel_builder",
        },
    )

    assert len(result["component_meshes"]) == 1

    component = result["component_meshes"][0]

    assert component["component_type"] == "facade_frieze"
    assert component["source_system"] == "facade_panel_builder"

    report = AtlasMeshValidator._topology_report(
        component
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_default_catalog_contains_circular_rosette_v1():
    catalog = build_default_architectural_ornament_catalog()

    entry = catalog.get(
        component_id="rosette.circular_v1",
        version="1.0.0",
    )

    assert entry.semantic_class == "rosette"
    assert entry.geometry_producer == "AtlasFacadeCircularPanelBuilder"
    assert (
        entry.provenance["source_system"]
        == "facade_circular_panel_builder"
    )
    assert entry.parameter_names == (
        "diameter_mm",
        "depth_mm",
        "embed_mm",
        "segments",
    )
    assert entry.anchor_names == (
        "center",
    )
    assert entry.repetition_mode == "repeatable"
    assert entry.symmetry == "radial"
    assert "flat_plane" in entry.supported_projection_modes
    assert "oriented_planar" in entry.supported_projection_modes
    assert "bilinear_surface" in entry.supported_projection_modes
    assert "relief" in entry.output_eligibility
    assert "kit" in entry.output_eligibility


def test_rosette_catalog_entry_geometry_passes_existing_topology_gate():
    from CORE.atlas_facade_circular_panel_builder import (
        AtlasFacadeCircularPanelBuilder,
    )
    from CORE.atlas_mesh_validator import (
        AtlasMeshValidator,
    )

    entry = build_default_architectural_ornament_catalog().get(
        component_id="rosette.circular_v1",
        version="1.0.0",
    )

    instance = entry.bind(
        parameters={
            "diameter_mm": 6.0,
            "depth_mm": 0.24,
            "embed_mm": 0.04,
            "segments": 16,
        },
    )

    wall_width_mm = 16.0
    wall_height_mm = 16.0

    result = AtlasFacadeCircularPanelBuilder.build(
        wall_quad=(
            (0.0, 0.0, 0.0),
            (wall_width_mm, 0.0, 0.0),
            (wall_width_mm, 0.0, wall_height_mm),
            (0.0, 0.0, wall_height_mm),
        ),
        center_u=0.5,
        center_v=0.5,
        diameter_ratio=(
            instance.parameters["diameter_mm"]
            / min(
                wall_width_mm,
                wall_height_mm,
            )
        ),
        depth_mm=instance.parameters["depth_mm"],
        embed_mm=instance.parameters["embed_mm"],
        segments=instance.parameters["segments"],
        metadata={
            "component_type": "facade_rosette",
        },
    )

    assert result["component_type"] == "facade_rosette"
    assert result["source_system"] == "facade_circular_panel_builder"

    report = AtlasMeshValidator._topology_report(
        result
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_default_catalog_contains_geometric_polygon_ornament_v1():
    catalog = build_default_architectural_ornament_catalog()

    entry = catalog.get(
        component_id="ornament.geometric_polygon_v1",
        version="1.0.0",
    )

    assert entry.semantic_class == "geometric_ornament"
    assert entry.geometry_producer == "AtlasGeometricOrnamentMesher"
    assert (
        entry.provenance["source_system"]
        == "geometric_ornament_mesher"
    )
    assert entry.parameter_names == (
        "width_mm",
        "height_mm",
        "depth_mm",
    )
    assert entry.anchor_names == (
        "center",
    )
    assert entry.repetition_mode == "repeatable"
    assert entry.symmetry == "custom"
    assert "flat_plane" in entry.supported_projection_modes
    assert "oriented_planar" in entry.supported_projection_modes
    assert "bilinear_surface" in entry.supported_projection_modes
    assert "assembled" in entry.output_eligibility
    assert "relief" in entry.output_eligibility
    assert "kit" in entry.output_eligibility


def test_geometric_polygon_ornament_catalog_entry_passes_topology_gate():
    from CORE.atlas_geometric_ornament_mesher import (
        AtlasGeometricOrnamentMesher,
    )
    from CORE.atlas_mesh_validator import (
        AtlasMeshValidator,
    )

    entry = build_default_architectural_ornament_catalog().get(
        component_id="ornament.geometric_polygon_v1",
        version="1.0.0",
    )

    instance = entry.bind(
        parameters={
            "width_mm": 2.0,
            "height_mm": 2.0,
            "depth_mm": 0.24,
        },
    )

    half_width = instance.parameters["width_mm"] / 2.0
    half_height = instance.parameters["height_mm"] / 2.0

    result = AtlasGeometricOrnamentMesher.build(
        outline_points=(
            (-half_width, 0.0),
            (-0.3 * half_width, -0.3 * half_height),
            (0.0, -half_height),
            (0.3 * half_width, -0.3 * half_height),
            (half_width, 0.0),
            (0.3 * half_width, 0.3 * half_height),
            (0.0, half_height),
            (-0.3 * half_width, 0.3 * half_height),
        ),
        base_z=0.0,
        depth_mm=instance.parameters["depth_mm"],
    )

    assert result["component_type"] == "geometric_ornament"
    assert result["source_system"] == "geometric_ornament_mesher"

    report = AtlasMeshValidator._topology_report(
        result
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_default_catalog_contains_floral_radial_ornament_v1():
    catalog = build_default_architectural_ornament_catalog()

    entry = catalog.get(
        component_id="ornament.floral_radial_v1",
        version="1.0.0",
    )

    assert entry.semantic_class == "floral_ornament"
    assert entry.geometry_producer == "AtlasFloralOrnamentMesher"
    assert (
        entry.provenance["source_system"]
        == "floral_ornament_mesher"
    )
    assert entry.parameter_names == (
        "outer_diameter_mm",
        "inner_ratio",
        "petal_count",
        "depth_mm",
    )
    assert entry.anchor_names == (
        "center",
    )
    assert entry.repetition_mode == "repeatable"
    assert entry.symmetry == "radial"
    assert "flat_plane" in entry.supported_projection_modes
    assert "oriented_planar" in entry.supported_projection_modes
    assert "bilinear_surface" in entry.supported_projection_modes
    assert "assembled" in entry.output_eligibility
    assert "relief" in entry.output_eligibility
    assert "kit" in entry.output_eligibility


def test_floral_radial_ornament_catalog_entry_passes_topology_gate():
    from CORE.atlas_floral_ornament_mesher import (
        AtlasFloralOrnamentMesher,
    )
    from CORE.atlas_mesh_validator import (
        AtlasMeshValidator,
    )

    entry = build_default_architectural_ornament_catalog().get(
        component_id="ornament.floral_radial_v1",
        version="1.0.0",
    )

    instance = entry.bind(
        parameters={
            "outer_diameter_mm": 4.0,
            "inner_ratio": 0.45,
            "petal_count": 8,
            "depth_mm": 0.24,
        },
    )

    result = AtlasFloralOrnamentMesher.build(
        center_x=0.0,
        center_y=0.0,
        outer_diameter_mm=instance.parameters["outer_diameter_mm"],
        inner_ratio=instance.parameters["inner_ratio"],
        petal_count=instance.parameters["petal_count"],
        base_z=0.0,
        depth_mm=instance.parameters["depth_mm"],
    )

    assert result["component_type"] == "floral_ornament"
    assert result["source_system"] == "floral_ornament_mesher"
    assert result["petal_count"] == 8

    report = AtlasMeshValidator._topology_report(
        result
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_default_catalog_contains_recessed_arch_niche_v1():
    catalog = build_default_architectural_ornament_catalog()

    entry = catalog.get(
        component_id="niche.recessed_arch_v1",
        version="1.0.0",
    )

    assert entry.semantic_class == "statue_niche"
    assert entry.geometry_producer == "AtlasRecessedArchNicheMesher"
    assert (
        entry.provenance["source_system"]
        == "recessed_arch_niche_mesher"
    )
    assert entry.parameter_names == (
        "width_mm",
        "height_mm",
        "spring_height_mm",
        "recess_depth_mm",
        "arch_segments",
    )
    assert entry.anchor_names == (
        "center",
        "bottom_center",
        "spring_center",
        "top_center",
    )
    assert entry.repetition_mode == "repeatable"
    assert entry.symmetry == "bilateral"
    assert "flat_plane" in entry.supported_projection_modes
    assert "oriented_planar" in entry.supported_projection_modes
    assert "bilinear_surface" in entry.supported_projection_modes
    assert "assembled" in entry.output_eligibility
    assert "relief" in entry.output_eligibility
    assert "kit" in entry.output_eligibility


def test_recessed_arch_niche_catalog_entry_passes_topology_gate():
    from CORE.atlas_recessed_arch_niche_mesher import (
        AtlasRecessedArchNicheMesher,
    )
    from CORE.atlas_mesh_validator import (
        AtlasMeshValidator,
    )

    entry = build_default_architectural_ornament_catalog().get(
        component_id="niche.recessed_arch_v1",
        version="1.0.0",
    )

    instance = entry.bind(
        parameters={
            "width_mm": 3.0,
            "height_mm": 4.0,
            "spring_height_mm": 2.8,
            "recess_depth_mm": 0.4,
            "arch_segments": 8,
        },
    )

    result = AtlasRecessedArchNicheMesher.build(
        center_x=0.0,
        center_z=2.0,
        width_mm=instance.parameters["width_mm"],
        height_mm=instance.parameters["height_mm"],
        spring_height_mm=instance.parameters["spring_height_mm"],
        recess_depth_mm=instance.parameters["recess_depth_mm"],
        front_y=0.0,
        arch_segments=instance.parameters["arch_segments"],
    )

    assert result["component_type"] == "recessed_arch_niche"
    assert result["source_system"] == "recessed_arch_niche_mesher"

    report = AtlasMeshValidator._topology_report(
        result
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_default_catalog_contains_round_archivolt_v1():
    catalog = build_default_architectural_ornament_catalog()

    entry = catalog.get(
        component_id="archivolt.round_v1",
        version="1.0.0",
    )

    assert entry.semantic_class == "archivolt"
    assert entry.geometry_producer == "AtlasFacadeArchMesher"
    assert (
        entry.provenance["source_system"]
        == "facade_arch_mesher"
    )
    assert entry.parameter_names == (
        "width_mm",
        "height_mm",
        "depth_mm",
        "embed_mm",
        "arch_segments",
        "arch_height_ratio",
    )
    assert entry.anchor_names == (
        "center",
        "spring_left",
        "spring_right",
        "apex",
    )
    assert entry.repetition_mode == "repeatable"
    assert entry.symmetry == "bilateral"
    assert "flat_plane" in entry.supported_projection_modes
    assert "oriented_planar" in entry.supported_projection_modes
    assert "bilinear_surface" in entry.supported_projection_modes
    assert "assembled" in entry.output_eligibility
    assert "relief" in entry.output_eligibility
    assert "kit" in entry.output_eligibility


def test_round_archivolt_catalog_entry_geometry_passes_existing_topology_gate():
    from CORE.atlas_facade_arch_mesher import (
        AtlasFacadeArchMesher,
    )
    from CORE.atlas_facade_bay_analyzer import (
        AtlasFacadeBayAnalyzer,
    )
    from CORE.atlas_facade_opening_layout import (
        AtlasFacadeOpeningLayout,
    )
    from CORE.atlas_facade_region_analyzer import (
        AtlasFacadeRegionAnalyzer,
    )
    from CORE.atlas_mesh_validator import (
        AtlasMeshValidator,
    )

    entry = build_default_architectural_ornament_catalog().get(
        component_id="archivolt.round_v1",
        version="1.0.0",
    )

    instance = entry.bind(
        parameters={
            "width_mm": 3.0,
            "height_mm": 3.0,
            "depth_mm": 0.24,
            "embed_mm": 0.04,
            "arch_segments": 8,
            "arch_height_ratio": 1.0,
        },
    )

    region_analysis = AtlasFacadeRegionAnalyzer.analyze(
        tags={
            "building:levels": "1",
        },
        total_height_m=6.0,
    )

    bay_analysis = AtlasFacadeBayAnalyzer.analyze(
        region_analysis=region_analysis,
        bay_count=1,
    )

    opening_analysis = AtlasFacadeOpeningLayout.create_uniform(
        bay_analysis=bay_analysis,
        opening_kind="arch",
        horizontal_margin_ratio=0.25,
        vertical_margin_ratio=0.20,
    )

    result = AtlasFacadeArchMesher.build(
        wall_quad=(
            (0.0, 0.0, 0.0),
            (6.0, 0.0, 0.0),
            (6.0, 0.0, 6.0),
            (0.0, 0.0, 6.0),
        ),
        opening_analysis=opening_analysis,
        depth_mm=instance.parameters["depth_mm"],
        embed_mm=instance.parameters["embed_mm"],
        arch_segments=instance.parameters["arch_segments"],
        arch_height_ratio=instance.parameters["arch_height_ratio"],
        metadata={
            "component_type": "facade_archivolt",
            "source_system": "facade_arch_mesher",
        },
    )

    assert result["arch_count"] == 1

    component = result["component_meshes"][0]

    assert component["component_type"] == "facade_archivolt"
    assert component["source_system"] == "facade_arch_mesher"

    report = AtlasMeshValidator._topology_report(
        component
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_default_catalog_contains_mullion_transom_tracery_v1():
    catalog = build_default_architectural_ornament_catalog()

    entry = catalog.get(
        component_id="tracery.mullion_transom_v1",
        version="1.0.0",
    )

    assert entry.semantic_class == "tracery"
    assert entry.geometry_producer == "AtlasFacadeTraceryMesher"
    assert (
        entry.provenance["source_system"]
        == "facade_tracery_mesher"
    )
    assert entry.parameter_names == (
        "width_mm",
        "height_mm",
        "mullion_width_mm",
        "transom_height_mm",
        "depth_mm",
        "embed_mm",
    )
    assert entry.anchor_names == (
        "center",
        "bottom_center",
        "top_center",
    )
    assert entry.repetition_mode == "repeatable"
    assert entry.symmetry == "bilateral"
    assert "flat_plane" in entry.supported_projection_modes
    assert "oriented_planar" in entry.supported_projection_modes
    assert "bilinear_surface" in entry.supported_projection_modes
    assert "assembled" in entry.output_eligibility
    assert "relief" in entry.output_eligibility
    assert "kit" in entry.output_eligibility


def test_mullion_transom_tracery_catalog_entry_passes_topology_gate():
    from CORE.atlas_facade_tracery_mesher import (
        AtlasFacadeTraceryMesher,
    )
    from CORE.atlas_mesh_validator import (
        AtlasMeshValidator,
    )

    entry = build_default_architectural_ornament_catalog().get(
        component_id="tracery.mullion_transom_v1",
        version="1.0.0",
    )

    instance = entry.bind(
        parameters={
            "width_mm": 3.0,
            "height_mm": 3.6,
            "mullion_width_mm": 0.6,
            "transom_height_mm": 0.6,
            "depth_mm": 0.24,
            "embed_mm": 0.04,
        },
    )

    wall_width_mm = 6.0
    wall_height_mm = 6.0

    result = AtlasFacadeTraceryMesher.build(
        wall_quad=(
            (0.0, 0.0, 0.0),
            (wall_width_mm, 0.0, 0.0),
            (wall_width_mm, 0.0, wall_height_mm),
            (0.0, 0.0, wall_height_mm),
        ),
        u_min=0.25,
        u_max=0.75,
        v_min=0.20,
        v_max=0.80,
        mullion_width_ratio=(
            instance.parameters["mullion_width_mm"]
            / instance.parameters["width_mm"]
        ),
        transom_height_ratio=(
            instance.parameters["transom_height_mm"]
            / instance.parameters["height_mm"]
        ),
        depth_mm=instance.parameters["depth_mm"],
        embed_mm=instance.parameters["embed_mm"],
    )

    assert result["tracery_count"] == 2

    for component in result["component_meshes"]:
        assert component["component_type"] == "facade_tracery"
        assert component["source_system"] == "facade_tracery_mesher"

        report = AtlasMeshValidator._topology_report(
            component
        )

        assert report["open_edge_count"] == 0
        assert report["non_manifold_edge_count"] == 0


def test_default_catalog_contains_triangular_tympanum_v1():
    catalog = build_default_architectural_ornament_catalog()

    entry = catalog.get(
        component_id="tympanum.triangular_v1",
        version="1.0.0",
    )

    assert entry.semantic_class == "tympanum"
    assert entry.geometry_producer == "AtlasTympanumMesher"
    assert (
        entry.provenance["source_system"]
        == "tympanum_mesher"
    )
    assert entry.parameter_names == (
        "width_mm",
        "height_mm",
        "depth_mm",
    )
    assert entry.anchor_names == (
        "center",
        "base_left",
        "base_right",
        "apex",
    )
    assert entry.repetition_mode == "repeatable"
    assert entry.symmetry == "bilateral"
    assert "flat_plane" in entry.supported_projection_modes
    assert "oriented_planar" in entry.supported_projection_modes
    assert "bilinear_surface" in entry.supported_projection_modes
    assert "assembled" in entry.output_eligibility
    assert "relief" in entry.output_eligibility
    assert "kit" in entry.output_eligibility


def test_default_catalog_contains_rectangular_molding_band_v1():
    catalog = build_default_architectural_ornament_catalog()

    entry = catalog.get(
        component_id="molding.rectangular_band_v1",
        version="1.0.0",
    )

    assert entry.semantic_class == "molding"
    assert entry.geometry_producer == "AtlasFacadeMoldingMesher"
    assert (
        entry.provenance["source_system"]
        == "facade_molding_mesher"
    )
    assert entry.parameter_names == (
        "width_mm",
        "height_mm",
        "depth_mm",
        "embed_mm",
    )
    assert entry.anchor_names == (
        "center",
        "start",
        "end",
    )
    assert entry.repetition_mode == "repeatable"
    assert entry.symmetry == "bilateral"
    assert "flat_plane" in entry.supported_projection_modes
    assert "oriented_planar" in entry.supported_projection_modes
    assert "bilinear_surface" in entry.supported_projection_modes
    assert "assembled" in entry.output_eligibility
    assert "relief" in entry.output_eligibility
    assert "kit" in entry.output_eligibility


def test_default_catalog_contains_figurative_rect_plaque_v1():
    catalog = build_default_architectural_ornament_catalog()

    entry = catalog.get(
        component_id="plaque.figurative_rect_v1",
        version="1.0.0",
    )

    assert entry.semantic_class == "figurative_plaque"
    assert entry.geometry_producer == "AtlasFigurativePlaqueMesher"
    assert (
        entry.provenance["source_system"]
        == "figurative_plaque_mesher"
    )
    assert entry.parameter_names == (
        "width_mm",
        "height_mm",
        "depth_mm",
        "embed_mm",
    )
    assert entry.anchor_names == (
        "center",
        "bottom_center",
        "top_center",
    )
    assert entry.repetition_mode == "repeatable"
    assert entry.symmetry == "bilateral"
    assert "flat_plane" in entry.supported_projection_modes
    assert "oriented_planar" in entry.supported_projection_modes
    assert "bilinear_surface" in entry.supported_projection_modes
    assert "assembled" in entry.output_eligibility
    assert "relief" in entry.output_eligibility
    assert "kit" in entry.output_eligibility


def test_default_catalog_contains_repeatable_surface_units_v1():
    catalog = build_default_architectural_ornament_catalog()

    expectations = (
        (
            "surface_unit.brick_v1",
            "brick",
        ),
        (
            "surface_unit.stone_block_v1",
            "stone_block",
        ),
        (
            "surface_unit.roof_tile_v1",
            "roof_tile",
        ),
    )

    for component_id, unit_kind in expectations:
        entry = catalog.get(
            component_id=component_id,
            version="1.0.0",
        )

        assert entry.semantic_class == "repeatable_surface_unit"
        assert (
            entry.geometry_producer
            == "AtlasRepeatableSurfaceUnitMesher"
        )
        assert (
            entry.provenance["source_system"]
            == "repeatable_surface_unit_mesher"
        )
        assert entry.provenance["unit_kind"] == unit_kind
        assert entry.parameter_names == (
            "width_mm",
            "height_mm",
            "depth_mm",
        )
        assert entry.anchor_names == (
            "center",
        )
        assert entry.repetition_mode == "repeatable"
        assert entry.symmetry == "bilateral"
        assert "flat_plane" in entry.supported_projection_modes
        assert "oriented_planar" in entry.supported_projection_modes
        assert "bilinear_surface" in entry.supported_projection_modes
        assert "assembled" in entry.output_eligibility
        assert "relief" in entry.output_eligibility
        assert "kit" in entry.output_eligibility
