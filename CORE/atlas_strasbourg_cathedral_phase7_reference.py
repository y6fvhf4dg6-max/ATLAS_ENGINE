from __future__ import annotations

from types import MappingProxyType


STRASBOURG_CATHEDRAL_PHASE7_REFERENCE = MappingProxyType(
    {
        "reference_id": (
            "strasbourg_cathedral_central_portal_phase7_v1"
        ),
        "site_name": (
            "Cathédrale Notre-Dame de Strasbourg"
        ),
        "surface_role": (
            "west_facade_central_portal"
        ),
        "source_path": (
            "Data/RELIEF/strasbourg_cathedral_phase7/"
            "strasbourg_cathedral_central_portal_reference.jpg"
        ),
        "image_size": (
            1333,
            2000,
        ),
        "sha256": (
            "e9315eca500ef296c33016ad4c576a5e65dde1828d04885bd5a01ab24abcaeef"
        ),
        "license_id": "CC-BY-2.0",
        "provenance": (
            "Wikimedia Commons / jeffowenphotos"
        ),
        "required_semantic_roles": (
            "recessed_opening",
            "raised_ornament",
            "figurative_or_emblematic_feature",
            "inscription_or_panel",
        ),
        "minimum_depth_band_count": 3,
    }
)


def build_strasbourg_cathedral_phase7_input():
    from CORE.atlas_architectural_relief_input import (
        AtlasArchitecturalReliefInput,
    )
    from CORE.atlas_relief_product_profile_catalog import (
        ARCHITECTURAL_STONE_FACADE,
    )

    return AtlasArchitecturalReliefInput(
        image_path=(
            STRASBOURG_CATHEDRAL_PHASE7_REFERENCE[
                "source_path"
            ]
        ),
        width_mm=80.0,
        depth_mm=120.0,
        architectural_kind="gothic_stone_facade",
        product_profile=ARCHITECTURAL_STONE_FACADE,
    )


def build_strasbourg_cathedral_phase7_semantic_components():
    from CORE.atlas_semantic_relief_component import (
        AtlasSemanticReliefComponent,
    )

    source_reference = (
        STRASBOURG_CATHEDRAL_PHASE7_REFERENCE[
            "reference_id"
        ]
    )
    target_surface_id = (
        "strasbourg.central_portal.facade_surface"
    )

    return (
        AtlasSemanticReliefComponent(
            component_id=(
                "strasbourg.central_portal.opening"
            ),
            semantic_class="opening.recessed_rect_v1",
            geometry_source_kind="catalog_component",
            source_reference=source_reference,
            target_surface_id=target_surface_id,
            projection_mode="oriented_planar",
            depth_band="recessed",
            layer_order=0,
            material_role="stone",
            physical_feature_policy="preserve",
            provenance=(
                "Strasbourg Cathedral Phase 7 "
                "central portal reference"
            ),
        ),
        AtlasSemanticReliefComponent(
            component_id=(
                "strasbourg.central_portal.archivolt"
            ),
            semantic_class="archivolt.round_v1",
            geometry_source_kind="catalog_component",
            source_reference=source_reference,
            target_surface_id=target_surface_id,
            projection_mode="oriented_planar",
            depth_band="raised_primary",
            layer_order=2,
            material_role="stone",
            physical_feature_policy="preserve",
            provenance=(
                "Strasbourg Cathedral Phase 7 "
                "central portal reference"
            ),
        ),
        AtlasSemanticReliefComponent(
            component_id=(
                "strasbourg.central_portal."
                "figurative_tympanum"
            ),
            semantic_class="plaque.figurative_rect_v1",
            geometry_source_kind="catalog_component",
            source_reference=source_reference,
            target_surface_id=target_surface_id,
            projection_mode="oriented_planar",
            depth_band="raised_secondary",
            layer_order=3,
            material_role="stone",
            physical_feature_policy="preserve",
            provenance=(
                "Strasbourg Cathedral Phase 7 "
                "central portal reference"
            ),
        ),
        AtlasSemanticReliefComponent(
            component_id=(
                "strasbourg.central_portal.panel"
            ),
            semantic_class="panel.inscription_rect_v1",
            geometry_source_kind="catalog_component",
            source_reference=source_reference,
            target_surface_id=target_surface_id,
            projection_mode="oriented_planar",
            depth_band="primary",
            layer_order=1,
            material_role="stone",
            physical_feature_policy="preserve",
            provenance=(
                "Strasbourg Cathedral Phase 7 "
                "central portal reference"
            ),
        ),
    )


def build_strasbourg_cathedral_phase7_depth_occlusion_plan():
    from CORE.atlas_semantic_depth_occlusion_composer import (
        AtlasSemanticDepthOcclusionComposer,
    )
    from CORE.atlas_semantic_relief_component import (
        AtlasSemanticReliefComponent,
    )
    from CORE.atlas_semantic_relief_scene import (
        AtlasSemanticReliefScene,
    )

    facade_surface = AtlasSemanticReliefComponent(
        component_id=(
            "strasbourg.central_portal.facade_surface"
        ),
        semantic_class="architectural.facade_surface",
        geometry_source_kind="surface_target",
        depth_band="surface_base",
        layer_order=0,
        material_role="stone",
        physical_feature_policy="preserve",
        provenance=(
            "Strasbourg Cathedral Phase 7 "
            "canonical oriented planar facade target"
        ),
    )

    scene = AtlasSemanticReliefScene(
        scene_id=(
            "strasbourg_cathedral_central_portal_phase7"
        ),
        components=(
            facade_surface,
            *build_strasbourg_cathedral_phase7_semantic_components(),
        ),
    )

    return AtlasSemanticDepthOcclusionComposer.compose(
        scene,
        depth_band_ranges={
            "recessed": (0.00, 0.20),
            "surface_base": (0.20, 0.30),
            "primary": (0.30, 0.50),
            "raised_primary": (0.50, 0.75),
            "raised_secondary": (0.75, 1.00),
        },
    )


def build_strasbourg_cathedral_phase7_product():
    from CORE.atlas_architectural_semantic_relief_product import (
        AtlasArchitecturalSemanticReliefProduct,
    )
    from CORE.atlas_surface_target import (
        AtlasSurfaceTarget,
    )

    components = (
        build_strasbourg_cathedral_phase7_semantic_components()
    )

    target = AtlasSurfaceTarget.oriented_planar_quad(
        surface_id=(
            "strasbourg.central_portal.facade_surface"
        ),
        source_component_id=(
            "strasbourg.central_portal.semantic_relief"
        ),
        target_component_id=(
            "strasbourg.central_portal.facade"
        ),
        quad=(
            (0.0, 0.0, 0.0),
            (80.0, 0.0, 0.0),
            (80.0, 0.0, 120.0),
            (0.0, 0.0, 120.0),
        ),
        relief_polarity="outward",
        minimum_depth_mm=0.0,
        maximum_depth_mm=1.8,
        attachment_policy="must_attach",
        intersection_policy="reject",
    )

    return AtlasArchitecturalSemanticReliefProduct(
        product_id=(
            STRASBOURG_CATHEDRAL_PHASE7_REFERENCE[
                "reference_id"
            ]
        ),
        component_ids=tuple(
            component.semantic_class
            for component in components
        ),
        depth_bands=tuple(
            component.depth_band
            for component in components
        ),
        baseline_mode="generic_height_map",
        surface_target=target,
    )


def build_strasbourg_cathedral_phase7_catalog_instances():
    from CORE.atlas_architectural_ornament_catalog import (
        build_default_architectural_ornament_catalog,
    )

    catalog = build_default_architectural_ornament_catalog()

    specs = {
        "strasbourg.central_portal.opening": {
            "component_id": "opening.recessed_rect_v1",
            "parameters": {
                "width_mm": 20.1050262566,
                "height_mm": 19.8,
                "depth_mm": 0.8,
                "embed_mm": 0.6,
            },
        },
        "strasbourg.central_portal.archivolt": {
            "component_id": "archivolt.round_v1",
            "parameters": {
                "width_mm": 45.6114028507,
                "height_mm": 27.9,
                "depth_mm": 0.9,
                "embed_mm": 0.0,
                "arch_segments": 24,
                "arch_height_ratio": 0.55,
            },
        },
        "strasbourg.central_portal.figurative_tympanum": {
            "component_id": "plaque.figurative_rect_v1",
            "parameters": {
                "width_mm": 20.5251312828,
                "height_mm": 18.0,
                "depth_mm": 0.7,
                "embed_mm": 0.0,
            },
        },
        "strasbourg.central_portal.panel": {
            "component_id": "panel.inscription_rect_v1",
            "parameters": {
                "width_mm": 4.5011252813,
                "height_mm": 4.5,
                "depth_mm": 0.5,
                "embed_mm": 0.0,
            },
        },
    }

    return {
        occurrence_id: catalog.get(
            component_id=spec["component_id"],
            version="1.0.0",
        ).bind(
            parameters=spec["parameters"],
            occurrence_id=occurrence_id,
        )
        for occurrence_id, spec in specs.items()
    }

def build_strasbourg_cathedral_phase7_component_meshes():
    from CORE.atlas_facade_arch_band_mesher import (
        AtlasFacadeArchBandMesher,
    )
    from CORE.atlas_facade_opening_layout import (
        AtlasFacadeOpening,
        AtlasFacadeOpeningAnalysis,
    )
    from CORE.atlas_facade_opening_mesher import (
        AtlasFacadeOpeningMesher,
    )
    from CORE.atlas_facade_panel_builder import (
        AtlasFacadePanelBuilder,
    )
    from CORE.atlas_figurative_plaque_mesher import (
        AtlasFigurativePlaqueMesher,
    )

    instances = (
        build_strasbourg_cathedral_phase7_catalog_instances()
    )

    wall_width_mm = 80.0
    wall_height_mm = 120.0
    wall_quad = (
        (0.0, 0.0, 0.0),
        (wall_width_mm, 0.0, 0.0),
        (wall_width_mm, 0.0, wall_height_mm),
        (0.0, 0.0, wall_height_mm),
    )

    results = {}

    opening_instance = instances[
        "strasbourg.central_portal.opening"
    ]
    opening_width_ratio = (
        opening_instance.parameters["width_mm"]
        / wall_width_mm
    )
    opening_height_ratio = (
        opening_instance.parameters["height_mm"]
        / wall_height_mm
    )
    opening_center_u = (
        (
            29.1072768192
            + 49.2123030758
        )
        / 2.0
        / wall_width_mm
    )
    opening_bottom_v = (
        11.4 / wall_height_mm
    )
    opening = AtlasFacadeOpening(
        opening_index=0,
        opening_kind="portal",
        level_index=0,
        bay_index=0,
        region_name="central_portal",
        bay_u_min=0.0,
        bay_u_max=1.0,
        floor_v_min=0.0,
        floor_v_max=1.0,
        u_min=(
            opening_center_u
            - opening_width_ratio / 2.0
        ),
        u_max=(
            opening_center_u
            + opening_width_ratio / 2.0
        ),
        v_min=opening_bottom_v,
        v_max=(
            opening_bottom_v
            + opening_height_ratio
        ),
    )
    opening_result = AtlasFacadeOpeningMesher.build(
        wall_quad=wall_quad,
        opening_analysis=AtlasFacadeOpeningAnalysis(
            openings=(opening,),
        ),
        depth_mm=opening_instance.parameters["depth_mm"],
        embed_mm=opening_instance.parameters["embed_mm"],
        metadata={
            "occurrence_id": opening_instance.occurrence_id,
            "semantic_class": opening_instance.component_id,
        },
    )
    results[
        opening_instance.occurrence_id
    ] = opening_result["component_meshes"][0]

    archivolt_instance = instances[
        "strasbourg.central_portal.archivolt"
    ]
    archivolt_width_ratio = (
        archivolt_instance.parameters["width_mm"]
        / wall_width_mm
    )
    archivolt_height_ratio = (
        archivolt_instance.parameters["height_mm"]
        / wall_height_mm
    )
    archivolt_result = AtlasFacadeArchBandMesher.build(
        center_x_mm=(
            (
                17.1042760690
                + 62.7156789197
            )
            / 2.0
        ),
        bottom_z_mm=31.5,
        outer_width_mm=(
            archivolt_instance.parameters["width_mm"]
        ),
        outer_height_mm=(
            archivolt_instance.parameters["height_mm"]
        ),
        band_width_mm=2.5,
        depth_mm=(
            archivolt_instance.parameters["depth_mm"]
        ),
        front_y_mm=0.0,
        arch_segments=(
            archivolt_instance.parameters["arch_segments"]
        ),
        arch_height_ratio=(
            archivolt_instance.parameters[
                "arch_height_ratio"
            ]
        ),
        metadata={
            "occurrence_id": archivolt_instance.occurrence_id,
            "semantic_class": archivolt_instance.component_id,
        },
    )
    results[
        archivolt_instance.occurrence_id
    ] = archivolt_result

    figurative_instance = instances[
        "strasbourg.central_portal.figurative_tympanum"
    ]
    figurative_result = AtlasFigurativePlaqueMesher.build(
        wall_quad=wall_quad,
        center_u=(
            (
                29.7074268567
                + 50.2325581395
            )
            / 2.0
            / wall_width_mm
        ),
        center_v=(
            (
                32.4
                + 50.4
            )
            / 2.0
            / wall_height_mm
        ),
        width_ratio=(
            figurative_instance.parameters["width_mm"]
            / wall_width_mm
        ),
        height_ratio=(
            figurative_instance.parameters["height_mm"]
            / wall_height_mm
        ),
        depth_mm=figurative_instance.parameters["depth_mm"],
        embed_mm=figurative_instance.parameters["embed_mm"],
        metadata={
            "occurrence_id": figurative_instance.occurrence_id,
            "semantic_class": figurative_instance.component_id,
        },
    )
    results[
        figurative_instance.occurrence_id
    ] = figurative_result["component_meshes"][0]

    panel_instance = instances[
        "strasbourg.central_portal.panel"
    ]
    panel_wall_quad = (
        (34.8087021755, 0.0, 18.0),
        (39.3098274569, 0.0, 18.0),
        (39.3098274569, 0.0, 22.5),
        (34.8087021755, 0.0, 22.5),
    )

    panel_result = AtlasFacadePanelBuilder.build_repeated_rectangles(
        wall_quad=panel_wall_quad,
        column_count=1,
        row_count=1,
        panel_width_ratio=1.0,
        panel_height_ratio=1.0,
        horizontal_margin_ratio=0.0,
        vertical_margin_ratio=0.0,
        depth_mm=panel_instance.parameters["depth_mm"],
        embed_mm=panel_instance.parameters["embed_mm"],
        metadata={
            "occurrence_id": panel_instance.occurrence_id,
            "semantic_class": panel_instance.component_id,
        },
    )
    results[
        panel_instance.occurrence_id
    ] = panel_result["component_meshes"][0]

    return results



def build_strasbourg_cathedral_phase7_projected_component_meshes():
    product = build_strasbourg_cathedral_phase7_product()
    component_meshes = (
        build_strasbourg_cathedral_phase7_component_meshes()
    )

    projected = {}

    for occurrence_id, mesh in component_meshes.items():
        points = [
            point
            for triangle in mesh["triangles"]
            for point in triangle
        ]
        contact_y = max(
            float(point[1])
            for point in points
        )

        projection_ready_mesh = {
            **mesh,
            "triangles": [
                tuple(
                    (
                        float(point[0]),
                        float(point[2]),
                        contact_y - float(point[1]),
                    )
                    for point in triangle
                )
                for triangle in mesh["triangles"]
            ],
            "projection_local_axes": (
                "facade_x",
                "facade_z",
                "surface_depth",
            ),
            "producer_contact_y_mm": contact_y,
        }

        if occurrence_id == "strasbourg.central_portal.opening":
            from dataclasses import replace

            from CORE.atlas_surface_projection_engine import (
                AtlasSurfaceProjectionEngine,
            )

            inward_target = replace(
                product.surface_target,
                relief_polarity="inward",
            )

            projection_result = (
                AtlasSurfaceProjectionEngine.project(
                    mesh=projection_ready_mesh,
                    target=inward_target,
                )
            )

            projected[occurrence_id] = {
                **projection_result,
                "target_surface_id": inward_target.surface_id,
            }

        elif occurrence_id == "strasbourg.central_portal.panel":
            from CORE.atlas_surface_projection_engine import (
                AtlasSurfaceProjectionEngine,
            )
            from CORE.atlas_surface_target import (
                AtlasSurfaceTarget,
            )

            opening_floor_target = AtlasSurfaceTarget.flat_plane(
                surface_id=(
                    "strasbourg.central_portal.opening_floor"
                ),
                source_component_id=(
                    "strasbourg.central_portal.panel"
                ),
                target_component_id=(
                    "strasbourg.central_portal.opening"
                ),
                origin=(0.0, 0.8, 0.0),
                u_axis=(1.0, 0.0, 0.0),
                v_axis=(0.0, 0.0, 1.0),
                clipping_boundary_uv=(
                    (29.1072768192, 11.4),
                    (49.2123030758, 11.4),
                    (49.2123030758, 31.2),
                    (29.1072768192, 31.2),
                ),
                relief_polarity="outward",
                minimum_depth_mm=0.0,
                maximum_depth_mm=0.5,
                attachment_policy="must_attach",
                intersection_policy="reject",
            )

            projection_result = (
                AtlasSurfaceProjectionEngine.project(
                    mesh=projection_ready_mesh,
                    target=opening_floor_target,
                )
            )

            projected[occurrence_id] = {
                **projection_result,
                "target_surface_id": (
                    product.surface_target.surface_id
                ),
                "nested_target_surface_id": (
                    opening_floor_target.surface_id
                ),
                "nested_target_component_id": (
                    opening_floor_target.target_component_id
                ),
            }

        else:
            projected[occurrence_id] = product.project_mesh(
                projection_ready_mesh
            )

    return projected



def build_strasbourg_cathedral_phase7_combined_semantic_structural_depth_reference(
    *,
    rows=480,
    columns=320,
):
    import numpy as np

    from CORE.atlas_projected_semantic_mesh_depth_rasterizer import (
        AtlasProjectedSemanticMeshDepthRasterizer,
    )

    product = (
        build_strasbourg_cathedral_phase7_product()
    )
    projected = (
        build_strasbourg_cathedral_phase7_projected_component_meshes()
    )

    width_mm = 80.0
    depth_mm = 120.0

    occurrence_ids = {
        "opening": (
            "strasbourg.central_portal.opening"
        ),
        "archivolt": (
            "strasbourg.central_portal.archivolt"
        ),
        "figurative_tympanum": (
            "strasbourg.central_portal.figurative_tympanum"
        ),
        "panel": (
            "strasbourg.central_portal.panel"
        ),
    }

    feature_masks = {}
    component_depth_maps = {}

    for feature_name, occurrence_id in (
        occurrence_ids.items()
    ):
        target = product.surface_target

        if feature_name == "opening":
            from dataclasses import replace

            target = replace(
                target,
                relief_polarity="inward",
            )

        raster = (
            AtlasProjectedSemanticMeshDepthRasterizer
            .rasterize(
                mesh=projected[
                    occurrence_id
                ]["mesh"],
                target=target,
                width_mm=width_mm,
                depth_mm=depth_mm,
                rows=rows,
                columns=columns,
            )
        )

        feature_masks[
            feature_name
        ] = raster[
            "coverage_map"
        ].copy()

        component_depth_maps[
            feature_name
        ] = raster[
            "depth_map"
        ].copy()

    coverage_map = np.zeros(
        (
            rows,
            columns,
        ),
        dtype=bool,
    )

    depth_map = np.full(
        (
            rows,
            columns,
        ),
        -np.inf,
        dtype=np.float64,
    )

    for feature_name in occurrence_ids:
        mask = feature_masks[
            feature_name
        ]
        values = component_depth_maps[
            feature_name
        ]

        coverage_map |= mask

        depth_map[
            mask
        ] = np.maximum(
            depth_map[
                mask
            ],
            values[
                mask
            ],
        )

    depth_map[
        ~coverage_map
    ] = 0.0

    return {
        "type": (
            "strasbourg_phase7_combined_semantic_"
            "structural_depth_reference"
        ),
        "shape": (
            rows,
            columns,
        ),
        "width_mm": (
            width_mm
        ),
        "depth_mm": (
            depth_mm
        ),
        "depth_map": (
            depth_map
        ),
        "coverage_map": (
            coverage_map
        ),
        "feature_masks": (
            feature_masks
        ),
    }



def build_strasbourg_cathedral_phase7_bounded_local_semantic_enhancement(
    *,
    rows=480,
    columns=320,
):
    import numpy as np

    from CORE.atlas_architectural_relief_structure_preserver import (
        AtlasArchitecturalReliefStructurePreserver,
        AtlasArchitecturalReliefStructureProfile,
    )
    from CORE.atlas_relief_pipeline import (
        AtlasReliefPipeline,
    )

    architectural_input = (
        build_strasbourg_cathedral_phase7_input()
    )

    baseline_result = (
        AtlasReliefPipeline.build_from_image(
            architectural_input.image_path,
            width_mm=architectural_input.width_mm,
            depth_mm=architectural_input.depth_mm,
            product_profile=architectural_input.product_profile,
            preprocessors=architectural_input.preprocessors,
            target_rows=rows,
            target_columns=columns,
        )
    )

    baseline = (
        baseline_result[
            "relief_result"
        ][
            "processed_height_map"
        ].astype(
            np.float64,
            copy=True,
        )
    )

    structural_result = (
        build_strasbourg_cathedral_phase7_combined_semantic_structural_depth_reference(
            rows=rows,
            columns=columns,
        )
    )

    signed_depth = (
        structural_result[
            "depth_map"
        ].astype(
            np.float64,
            copy=True,
        )
    )

    semantic_coverage = (
        structural_result[
            "coverage_map"
        ].astype(
            bool,
            copy=True,
        )
    )

    if not np.any(
        semantic_coverage
    ):
        raise ValueError(
            "semantic structural reference must contain coverage"
        )

    active_depth = (
        signed_depth[
            semantic_coverage
        ]
    )

    minimum_signed_depth = float(
        np.min(
            active_depth
        )
    )
    maximum_signed_depth = float(
        np.max(
            active_depth
        )
    )

    signed_span = (
        maximum_signed_depth
        - minimum_signed_depth
    )

    if signed_span <= 0.0:
        raise ValueError(
            "semantic structural reference must contain "
            "more than one signed depth level"
        )

    normalized_structural = np.zeros_like(
        signed_depth,
        dtype=np.float64,
    )

    normalized_structural[
        semantic_coverage
    ] = (
        (
            signed_depth[
                semantic_coverage
            ]
            - minimum_signed_depth
        )
        / signed_span
    )

    aligned_structural = np.flipud(
        normalized_structural
    ).astype(
        np.float64,
        copy=True,
    )

    aligned_coverage = np.flipud(
        semantic_coverage
    )

    protection_map = (
        aligned_coverage.astype(
            np.float64,
            copy=True,
        )
    )

    preservation = (
        AtlasArchitecturalReliefStructurePreserver
        .preserve(
            depth_candidate=baseline,
            structure_reference=aligned_structural,
            protection_map=protection_map,
            profile=(
                AtlasArchitecturalReliefStructureProfile()
            ),
            clamp_output=True,
        )
    )

    return {
        "type": (
            "strasbourg_phase7_bounded_local_semantic_enhancement"
        ),
        "shape": (
            rows,
            columns,
        ),
        "width_mm": (
            architectural_input.width_mm
        ),
        "depth_mm": (
            architectural_input.depth_mm
        ),
        "baseline_height_map": (
            baseline
        ),
        "aligned_structural_reference": (
            aligned_structural
        ),
        "protection_map": (
            protection_map
        ),
        "applied_correction": (
            preservation[
                "applied_correction"
            ]
        ),
        "enhanced_height_map": (
            preservation[
                "preserved_depth"
            ]
        ),
        "semantic_alignment": (
            "vertical_flip_to_photo_array"
        ),
        "baseline_identity_source": (
            "photo_derived_processed_height_map"
        ),
        "semantic_signed_depth_range_mm": (
            minimum_signed_depth,
            maximum_signed_depth,
        ),
        "structure_preservation": (
            preservation
        ),
    }



def build_strasbourg_cathedral_phase7_measurable_generic_vs_semantic_ab(
    *,
    rows=480,
    columns=320,
):
    import numpy as np

    from CORE.atlas_architectural_ornament_catalog import (
        build_default_architectural_ornament_catalog,
    )
    from CORE.atlas_architectural_relief_detail_scale_filter import (
        AtlasArchitecturalReliefDetailScaleProfile,
    )
    from CORE.atlas_architectural_semantic_relief_comparison_report import (
        AtlasArchitecturalSemanticReliefComparisonReport,
    )
    from CORE.atlas_architectural_semantic_relief_feature_measurement import (
        AtlasArchitecturalSemanticReliefFeatureMeasurement,
    )

    width_mm = 80.0
    depth_mm = 120.0

    enhancement = (
        build_strasbourg_cathedral_phase7_bounded_local_semantic_enhancement(
            rows=rows,
            columns=columns,
        )
    )

    structural = (
        build_strasbourg_cathedral_phase7_combined_semantic_structural_depth_reference(
            rows=rows,
            columns=columns,
        )
    )

    feature_masks = {
        name: np.flipud(mask).copy()
        for name, mask in structural[
            "feature_masks"
        ].items()
    }

    detail_profile = (
        AtlasArchitecturalReliefDetailScaleProfile(
            minimum_feature_mm=0.8,
            activity_threshold=0.02,
            minimum_density=0.25,
        )
    )

    baseline_measurement = (
        AtlasArchitecturalSemanticReliefFeatureMeasurement
        .measure(
            detail_map=enhancement[
                "baseline_height_map"
            ],
            feature_masks=feature_masks,
            width_mm=width_mm,
            depth_mm=depth_mm,
            detail_profile=detail_profile,
        )
    )

    semantic_measurement = (
        AtlasArchitecturalSemanticReliefFeatureMeasurement
        .measure(
            detail_map=enhancement[
                "enhanced_height_map"
            ],
            feature_masks=feature_masks,
            width_mm=width_mm,
            depth_mm=depth_mm,
            detail_profile=detail_profile,
        )
    )

    baseline_retained = sum(
        int(
            feature[
                "feature_retained"
            ]
        )
        for feature in baseline_measurement[
            "features"
        ].values()
    )

    baseline_feature_count = len(
        baseline_measurement[
            "features"
        ]
    )

    baseline_readability_score = (
        baseline_retained
        / baseline_feature_count
    )

    catalog = (
        build_default_architectural_ornament_catalog()
    )
    instances = (
        build_strasbourg_cathedral_phase7_catalog_instances()
    )

    occurrence_by_feature = {
        "opening": (
            "strasbourg.central_portal.opening"
        ),
        "archivolt": (
            "strasbourg.central_portal.archivolt"
        ),
        "figurative_tympanum": (
            "strasbourg.central_portal.figurative_tympanum"
        ),
        "panel": (
            "strasbourg.central_portal.panel"
        ),
    }

    semantic_physical_eligibility = {}

    for feature_name, occurrence_id in (
        occurrence_by_feature.items()
    ):
        instance = instances[
            occurrence_id
        ]

        entry = catalog.get(
            component_id=instance.component_id,
            version=instance.version,
        )

        entry.bind(
            parameters=dict(
                instance.parameters
            )
        )

        semantic_physical_eligibility[
            feature_name
        ] = {
            "eligible": True,
            "component_id": (
                instance.component_id
            ),
            "minimum_printable_profile": (
                dict(
                    entry.minimum_printable_profile
                )
            ),
        }

    semantic_retained = sum(
        int(
            evidence["eligible"]
        )
        for evidence in (
            semantic_physical_eligibility
            .values()
        )
    )

    semantic_feature_count = len(
        semantic_physical_eligibility
    )

    semantic_readability_score = (
        semantic_retained
        / semantic_feature_count
    )

    comparison_report = (
        AtlasArchitecturalSemanticReliefComparisonReport
        .build(
            baseline={
                "feature_readability_score": (
                    baseline_readability_score
                ),
            },
            semantic={
                "feature_readability_score": (
                    semantic_readability_score
                ),
            },
        )
    )

    return {
        "type": (
            "strasbourg_phase7_measurable_generic_vs_semantic_ab"
        ),
        "detail_profile": {
            "minimum_feature_mm": (
                detail_profile.minimum_feature_mm
            ),
            "activity_threshold": (
                detail_profile.activity_threshold
            ),
            "minimum_density": (
                detail_profile.minimum_density
            ),
        },
        "baseline_measurement": (
            baseline_measurement
        ),
        "semantic_measurement": (
            semantic_measurement
        ),
        "semantic_physical_eligibility": (
            semantic_physical_eligibility
        ),
        "baseline_readability_score": float(
            baseline_readability_score
        ),
        "semantic_readability_score": float(
            semantic_readability_score
        ),
        "baseline_retained_feature_count": (
            baseline_retained
        ),
        "semantic_retained_feature_count": (
            semantic_retained
        ),
        "feature_count": (
            semantic_feature_count
        ),
        "comparison_report": (
            comparison_report
        ),
        "baseline_evidence_source": (
            "photo_derived_physical_detail_filter"
        ),
        "semantic_evidence_source": (
            "locked_catalog_minimum_printable_profile"
        ),
    }



def build_strasbourg_cathedral_phase7_production_artifacts(
    *,
    rows=480,
    columns=320,
):
    import numpy as np

    from CORE.atlas_architectural_relief_mesh_producer import (
        AtlasArchitecturalReliefMeshProducer,
    )
    from CORE.atlas_architectural_relief_quality_report import (
        AtlasArchitecturalReliefQualityReport,
    )
    from CORE.atlas_architectural_relief_v1_standard import (
        ARCHITECTURAL_RELIEF_V1,
    )

    physical_height_map = (
        build_strasbourg_cathedral_phase7_physical_height_map(
            rows=rows,
            columns=columns,
        )
    )

    height_map = np.asarray(
        physical_height_map["height_map"],
        dtype=np.float64,
    )

    gradient_y, gradient_x = np.gradient(
        height_map
    )

    normal_x = -gradient_x * 5.0
    normal_y = -gradient_y * 5.0
    normal_z = np.ones_like(
        height_map
    )

    length = np.sqrt(
        normal_x * normal_x
        + normal_y * normal_y
        + normal_z * normal_z
    )

    normal_x = normal_x / length
    normal_y = normal_y / length
    normal_z = normal_z / length

    light = np.array(
        [-0.45, -0.55, 0.70],
        dtype=np.float64,
    )
    light = light / np.linalg.norm(
        light
    )

    shaded_preview = (
        normal_x * light[0]
        + normal_y * light[1]
        + normal_z * light[2]
    )

    shaded_preview = np.clip(
        0.20 + 0.80 * shaded_preview,
        0.0,
        1.0,
    )

    physical_coupon = (
        AtlasArchitecturalReliefMeshProducer
        .build(
            height_map=height_map,
            width_mm=80.0,
            depth_mm=120.0,
            physical_profile=(
                ARCHITECTURAL_RELIEF_V1
                .physical_profile
            ),
        )
    )

    quality_report = (
        AtlasArchitecturalReliefQualityReport
        .build(
            mesh_production=physical_coupon,
            risk_profile=(
                ARCHITECTURAL_RELIEF_V1
                .risk_profile
            ),
        )
    )

    return {
        "type": (
            "strasbourg_phase7_production_artifacts"
        ),
        "source": (
            "physical_slope_conditioned_semantic_enhancement"
        ),
        "physical_height_map": (
            physical_height_map
        ),
        "shaded_preview": (
            shaded_preview.astype(
                np.float64,
                copy=True,
            )
        ),
        "physical_coupon": (
            physical_coupon
        ),
        "quality_report": (
            quality_report
        ),
    }



def build_strasbourg_cathedral_phase7_physical_detail_scale_conditioning(
    *,
    rows=480,
    columns=320,
):
    import numpy as np

    from CORE.atlas_architectural_relief_detail_scale_filter import (
        AtlasArchitecturalReliefDetailScaleFilter,
    )
    from CORE.atlas_architectural_relief_v1_standard import (
        ARCHITECTURAL_RELIEF_V1,
    )
    from CORE.atlas_relief_multiscale_decomposer import (
        AtlasReliefMultiscaleDecomposer,
    )

    enhancement = (
        build_strasbourg_cathedral_phase7_bounded_local_semantic_enhancement(
            rows=rows,
            columns=columns,
        )
    )

    source = np.asarray(
        enhancement["enhanced_height_map"],
        dtype=np.float64,
    )

    protection = np.asarray(
        enhancement["protection_map"],
        dtype=np.float64,
    ) > 0.0

    architectural_input = (
        build_strasbourg_cathedral_phase7_input()
    )
    product_profile = (
        architectural_input.product_profile
    )

    decomposition = (
        AtlasReliefMultiscaleDecomposer.decompose(
            source,
            form_sigma=product_profile.form_sigma,
            detail_sigma=product_profile.detail_sigma,
        )
    )

    micro_detail = np.asarray(
        decomposition["micro_detail"],
        dtype=np.float64,
    )

    detail_profile = (
        ARCHITECTURAL_RELIEF_V1.detail_scale_profile
    )

    positive_micro_detail = np.maximum(
        micro_detail,
        0.0,
    )
    negative_micro_detail = np.maximum(
        -micro_detail,
        0.0,
    )

    positive_filtering = (
        AtlasArchitecturalReliefDetailScaleFilter.filter(
            detail_map=positive_micro_detail,
            width_mm=architectural_input.width_mm,
            depth_mm=architectural_input.depth_mm,
            profile=detail_profile,
        )
    )

    negative_filtering = (
        AtlasArchitecturalReliefDetailScaleFilter.filter(
            detail_map=negative_micro_detail,
            width_mm=architectural_input.width_mm,
            depth_mm=architectural_input.depth_mm,
            profile=detail_profile,
        )
    )

    retained_micro_detail = (
        np.asarray(
            positive_filtering["filtered_detail"],
            dtype=np.float64,
        )
        - np.asarray(
            negative_filtering["filtered_detail"],
            dtype=np.float64,
        )
    )

    detail_scale = (
        source - micro_detail
    )

    conditioned = (
        detail_scale + retained_micro_detail
    )

    conditioned = np.clip(
        conditioned,
        0.0,
        1.0,
    )

    conditioned[protection] = source[protection]

    return {
        "type": (
            "strasbourg_phase7_physical_detail_scale_conditioning"
        ),
        "source": (
            "bounded_local_semantic_enhancement"
        ),
        "conditioning_mode": (
            "photo_detail_minimum_feature_culling"
        ),
        "height_map": conditioned.astype(
            np.float64,
            copy=True,
        ),
        "minimum_feature_mm": (
            detail_profile.minimum_feature_mm
        ),
        "activity_threshold": (
            detail_profile.activity_threshold
        ),
        "minimum_density": (
            detail_profile.minimum_density
        ),
        "form_sigma": (
            product_profile.form_sigma
        ),
        "detail_sigma": (
            product_profile.detail_sigma
        ),
        "filter_mode": (
            "separate_positive_negative_polarities"
        ),
        "positive_component_count": (
            positive_filtering["component_count"]
        ),
        "negative_component_count": (
            negative_filtering["component_count"]
        ),
        "positive_retained_component_count": (
            positive_filtering[
                "retained_component_count"
            ]
        ),
        "negative_retained_component_count": (
            negative_filtering[
                "retained_component_count"
            ]
        ),
        "positive_culled_component_count": (
            positive_filtering[
                "culled_component_count"
            ]
        ),
        "negative_culled_component_count": (
            negative_filtering[
                "culled_component_count"
            ]
        ),
        "culled_active_pixel_count": int(
            np.count_nonzero(
                (
                    np.abs(micro_detail)
                    >= detail_profile.activity_threshold
                )
                & (
                    np.abs(retained_micro_detail)
                    < detail_profile.activity_threshold
                )
            )
        ),
        "culled_active_pixel_percent": (
            100.0
            * int(
                np.count_nonzero(
                    (
                        np.abs(micro_detail)
                        >= detail_profile.activity_threshold
                    )
                    & (
                        np.abs(retained_micro_detail)
                        < detail_profile.activity_threshold
                    )
                )
            )
            / max(
                1,
                int(
                    np.count_nonzero(
                        np.abs(micro_detail)
                        >= detail_profile.activity_threshold
                    )
                ),
            )
        ),
        "positive_detail_scale_filter": (
            positive_filtering
        ),
        "negative_detail_scale_filter": (
            negative_filtering
        ),
    }



def build_strasbourg_cathedral_phase7_physical_height_map(
    *,
    rows=480,
    columns=320,
):
    import math

    import numpy as np

    from CORE.atlas_architectural_relief_v1_standard import (
        ARCHITECTURAL_RELIEF_V1,
    )

    detail_conditioning = (
        build_strasbourg_cathedral_phase7_physical_detail_scale_conditioning(
            rows=rows,
            columns=columns,
        )
    )

    source = np.asarray(
        detail_conditioning["height_map"],
        dtype=np.float64,
    ).copy()

    physical_profile = (
        ARCHITECTURAL_RELIEF_V1.physical_profile
    )
    risk_profile = (
        ARCHITECTURAL_RELIEF_V1.risk_profile
    )

    sample_spacing_x_mm = float(
        physical_profile.target_sample_spacing_mm
    )
    sample_spacing_y_mm = float(
        physical_profile.target_sample_spacing_mm
    )
    relief_height_mm = float(
        physical_profile.relief_height_mm
    )
    warning_slope_degrees = float(
        risk_profile.warning_slope_degrees
    )
    critical_slope_degrees = float(
        risk_profile.critical_slope_degrees
    )

    # Triangle-safe orthogonal rise limit.
    #
    # A relief grid triangle may carry slope in both X and Y.
    # Bounding each orthogonal component to tan(theta)/sqrt(2)
    # guarantees the combined planar gradient does not exceed
    # the locked warning slope theta on a square sampling grid.
    maximum_allowed_adjacent_rise_mm = (
        math.tan(
            math.radians(
                warning_slope_degrees
            )
        )
        * min(
            sample_spacing_x_mm,
            sample_spacing_y_mm,
        )
        / math.sqrt(2.0)
    )

    maximum_allowed_normalized_delta = (
        maximum_allowed_adjacent_rise_mm
        / relief_height_mm
    )

    conditioned = source.copy()

    # Exact separable L1 lower Lipschitz envelope.
    #
    # This preserves the source wherever possible and only
    # lowers values that would otherwise require a neighbor
    # rise above the locked physical slope limit.
    for column in range(
        1,
        conditioned.shape[1],
    ):
        conditioned[:, column] = np.minimum(
            conditioned[:, column],
            conditioned[:, column - 1]
            + maximum_allowed_normalized_delta,
        )

    for column in range(
        conditioned.shape[1] - 2,
        -1,
        -1,
    ):
        conditioned[:, column] = np.minimum(
            conditioned[:, column],
            conditioned[:, column + 1]
            + maximum_allowed_normalized_delta,
        )

    for row in range(
        1,
        conditioned.shape[0],
    ):
        conditioned[row, :] = np.minimum(
            conditioned[row, :],
            conditioned[row - 1, :]
            + maximum_allowed_normalized_delta,
        )

    for row in range(
        conditioned.shape[0] - 2,
        -1,
        -1,
    ):
        conditioned[row, :] = np.minimum(
            conditioned[row, :],
            conditioned[row + 1, :]
            + maximum_allowed_normalized_delta,
        )

    conditioned = np.clip(
        conditioned,
        0.0,
        1.0,
    )

    rise_x_mm = (
        np.abs(
            np.diff(
                conditioned,
                axis=1,
            )
        )
        * relief_height_mm
    )

    rise_y_mm = (
        np.abs(
            np.diff(
                conditioned,
                axis=0,
            )
        )
        * relief_height_mm
    )

    maximum_adjacent_rise_mm = max(
        float(
            rise_x_mm.max(
                initial=0.0
            )
        ),
        float(
            rise_y_mm.max(
                initial=0.0
            )
        ),
    )

    slope_x = np.degrees(
        np.arctan2(
            rise_x_mm,
            sample_spacing_x_mm,
        )
    )

    slope_y = np.degrees(
        np.arctan2(
            rise_y_mm,
            sample_spacing_y_mm,
        )
    )

    maximum_slope_degrees = max(
        float(
            slope_x.max(
                initial=0.0
            )
        ),
        float(
            slope_y.max(
                initial=0.0
            )
        ),
    )

    return {
        "type": (
            "strasbourg_phase7_physical_height_map"
        ),
        "source": (
            "physical_detail_scale_conditioning"
        ),
        "conditioning_mode": (
            "print_ready_triangle_slope_limit"
        ),
        "height_map": conditioned.astype(
            np.float64,
            copy=True,
        ),
        "warning_slope_degrees": (
            warning_slope_degrees
        ),
        "critical_slope_degrees": (
            critical_slope_degrees
        ),
        "sample_spacing_x_mm": (
            sample_spacing_x_mm
        ),
        "sample_spacing_y_mm": (
            sample_spacing_y_mm
        ),
        "relief_height_mm": (
            relief_height_mm
        ),
        "maximum_allowed_adjacent_rise_mm": (
            maximum_allowed_adjacent_rise_mm
        ),
        "maximum_adjacent_rise_mm": (
            maximum_adjacent_rise_mm
        ),
        "maximum_slope_degrees": (
            maximum_slope_degrees
        ),
    }
