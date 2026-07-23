# CORE/atlas_foundation_scene_builder.py

from CORE.atlas_scene import AtlasScene
from CORE.atlas_building_analyzer import AtlasBuildingAnalyzer
from CORE.atlas_building_roof_profiler import (
    AtlasBuildingRoofProfiler,
)
from CORE.atlas_foundation_first_pipeline import (
    AtlasFoundationFirstPipeline,
)
from CORE.atlas_castle_roof_builder import (
    AtlasCastleRoofBuilder,
)
from CORE.atlas_castle_gable_roof_builder import (
    AtlasCastleGableRoofBuilder,
)
from CORE.atlas_castle_multi_gable_roof_builder import (
    AtlasCastleMultiGableRoofBuilder,
)
from CORE.atlas_monument_dome_roof_builder import (
    AtlasMonumentDomeRoofBuilder,
)
from CORE.atlas_minaret_roof_builder import (
    AtlasMinaretRoofBuilder,
)
from CORE.atlas_minaret_balcony_builder import (
    AtlasMinaretBalconyBuilder,
)
from CORE.atlas_castle_building_profiler import (
    AtlasCastleBuildingProfiler,
)
from CORE.atlas_castle_footprint_regularizer import (
    AtlasCastleFootprintRegularizer,
)
from CORE.atlas_building_part_hierarchy_profiler import (
    AtlasBuildingPartHierarchyProfiler,
)
from CORE.atlas_ancient_theatre_profiler import (
    AtlasAncientTheatreProfiler,
)
from CORE.atlas_ancient_theatre_stage_builder import (
    AtlasAncientTheatreStageBuilder,
)
from CORE.atlas_ancient_theatre_stage_facade_builder import (
    AtlasAncientTheatreStageFacadeBuilder,
)
from CORE.atlas_ancient_theatre_cavea_builder import (
    AtlasAncientTheatreCaveaBuilder,
)
from CORE.atlas_ancient_theatre_upper_gallery_builder import (
    AtlasAncientTheatreUpperGalleryBuilder,
)


class AtlasFoundationSceneBuilder:
    """
    ATLAS Foundation Scene Builder v0.3

    Foundation-first bina sahnesini üretir.

    v0.3:
    - Kale sınırı içindeki binaları otomatik sınıflandırır
    - Eksik yüksekliklerde kale profiline göre fallback uygular
    - Kulelere piramidal/sivri çatı uygular
    - Basit şapel ve kale kanatlarına tek beşik çatı uygular
    - Karmaşık kale kanatlarına çok parçalı beşik çatı uygular
    """

    @staticmethod
    def _building_roof_metadata(
        atlas_building,
        is_building_part,
    ):
        if getattr(
            atlas_building,
            "is_castle_building",
            False,
        ):
            return None

        oriented_aspect_ratio = (
            AtlasBuildingAnalyzer.oriented_aspect_ratio(
                atlas_building
            )
        )
        rectangularity = (
            AtlasBuildingAnalyzer.rectangularity(
                atlas_building
            )
        )

        if (
            oriented_aspect_ratio <= 0.0
            or not 0.0 <= rectangularity <= 1.0
        ):
            return {
                "building_roof_profile": "flat",
                "building_roof_decision_source": "fallback",
                "building_oriented_aspect_ratio": (
                    oriented_aspect_ratio
                ),
                "building_rectangularity": rectangularity,
            }

        decision = AtlasBuildingRoofProfiler.classify(
            roof_shape=getattr(
                atlas_building,
                "roof_type",
                None,
            ),
            aspect_ratio=oriented_aspect_ratio,
            rectangularity=rectangularity,
            is_building_part=is_building_part,
        )

        return {
            "building_roof_profile": decision[
                "roof_profile"
            ],
            "building_roof_decision_source": decision[
                "decision_source"
            ],
            "building_oriented_aspect_ratio": (
                oriented_aspect_ratio
            ),
            "building_rectangularity": rectangularity,
        }

    @staticmethod
    def _attach_building_roof_metadata(
        mesh,
        atlas_building,
        is_building_part,
        profile_counts,
        decision_source_counts,
    ):
        metadata = (
            AtlasFoundationSceneBuilder
            ._building_roof_metadata(
                atlas_building=atlas_building,
                is_building_part=is_building_part,
            )
        )

        if metadata is None:
            return mesh

        mesh.update(metadata)

        profile = metadata["building_roof_profile"]
        decision_source = metadata[
            "building_roof_decision_source"
        ]

        profile_counts[profile] = (
            profile_counts.get(profile, 0)
            + 1
        )

        decision_source_counts[decision_source] = (
            decision_source_counts.get(
                decision_source,
                0,
            )
            + 1
        )

        return mesh

    @staticmethod
    def build_scene(
        raw_buildings,
        coordinate_engine,
        terrain_mesh,
        castles=None,
        bbox=None,
        target_size_mm=None,
        bed_width_mm=None,
        bed_depth_mm=None,
        margin_mm=None,
        xy_scale=None,
        z_scale=None,
        max_buildings=None,
        min_points=4,
        max_points=300,
        castle_only=False,
        debug=True,
    ):
        from CORE.atlas_scene_builder import (
            AtlasSceneBuilder,
        )

        if castles is None:
            castles = []

        building_part_hierarchy = (
            AtlasBuildingPartHierarchyProfiler.analyze(
                raw_buildings
            )
        )

        mesh_buildings = building_part_hierarchy[
            "mesh_buildings"
        ]

        if debug:
            hierarchy_summary = building_part_hierarchy[
                "summary"
            ]

            print()
            print("=" * 70)
            print("ATLAS BUILDING PART HIERARCHY REPORT")
            print("=" * 70)
            print(
                "Parents with parts       : "
                f"{hierarchy_summary['parent_with_parts_count']}"
            )
            print(
                "Assigned building parts  : "
                f"{hierarchy_summary['assigned_building_part_count']}"
            )
            print(
                "Unassigned building parts: "
                f"{hierarchy_summary['unassigned_building_part_count']}"
            )
            print(
                "Parent part counts       : "
                f"{hierarchy_summary['parent_part_counts']}"
            )
            print(
                "Suppressed parents       : "
                f"{hierarchy_summary['suppressed_parent_count']}"
            )
            print(
                "Suppressed parent IDs    : "
                f"{building_part_hierarchy['suppressed_parent_ids']}"
            )
            print(
                "Mesh building records    : "
                f"{hierarchy_summary['mesh_building_count']}"
            )

        scene = AtlasScene(
            bbox=bbox,
            target_size_mm=target_size_mm,
            bed_width_mm=bed_width_mm,
            bed_depth_mm=bed_depth_mm,
            margin_mm=margin_mm,
            xy_scale=xy_scale,
            z_scale=z_scale,
            mode="foundation_first",
        )

        accepted_buildings = 0
        accepted_main_buildings = 0
        accepted_building_parts = 0
        rejected_building_parts = 0
        skipped_buildings = 0
        castle_buildings = 0

        building_rejection_counts = {}

        def record_building_rejection(reason):
            rejection_reason = reason or "unknown_rejection"

            building_rejection_counts[rejection_reason] = (
                building_rejection_counts.get(
                    rejection_reason,
                    0,
                )
                + 1
            )

        castle_profile_counts = {}
        building_roof_profile_counts = {}
        building_roof_decision_source_counts = {}

        tower_roof_count = 0
        gable_roof_count = 0
        multi_gable_roof_count = 0
        multi_gable_piece_count = 0

        suppressed_parent_ids = set(
            building_part_hierarchy[
                "suppressed_parent_ids"
            ]
        )

        parent_foundation_z_cache = {}

        for parent_id in suppressed_parent_ids:
            parent_data = building_part_hierarchy[
                "parents"
            ].get(parent_id)

            if not parent_data:
                continue

            raw_parent = parent_data["parent"]

            prepared_parent = (
                AtlasCastleFootprintRegularizer.prepare(
                    raw_building=raw_parent,
                    castles=castles,
                )
            )

            atlas_parent = (
                AtlasSceneBuilder._to_atlas_building(
                    prepared_parent
                )
            )

            atlas_parent = (
                AtlasCastleBuildingProfiler.apply_to_building(
                    atlas_building=atlas_parent,
                    raw_building=prepared_parent,
                    castles=castles,
                )
            )

            parent_diagnostics = {}

            parent_reference_mesh = (
                AtlasFoundationFirstPipeline.build_building_mesh(
                    building=atlas_parent,
                    coordinate_engine=coordinate_engine,
                    terrain_mesh=terrain_mesh,
                    sample_grid=5,
                    embed_depth_mm=0.30,
                    diagnostics=parent_diagnostics,
                )
            )

            if parent_reference_mesh is None:
                continue

            parent_foundation_z_cache[parent_id] = (
                parent_reference_mesh["foundation_z"]
            )

        for raw_building in mesh_buildings:
            if max_buildings is not None and accepted_buildings >= max_buildings:
                break

            raw_tags = raw_building.get(
                "tags",
                {},
            )
            is_building_part = (
                raw_tags.get("building:part") is not None
            )

            if bbox is not None and not (
                AtlasFoundationSceneBuilder._geometry_intersects_bbox(
                    geometry=raw_building.get("geometry", []),
                    bbox=bbox,
                )
            ):
                skipped_buildings += 1
                record_building_rejection("outside_bbox")
                continue

            if not AtlasSceneBuilder._is_raw_building_usable(
                raw_building,
                min_points=min_points,
                max_points=max_points,
            ):
                skipped_buildings += 1
                record_building_rejection("raw_building_unusable")
                continue

            prepared_building = AtlasCastleFootprintRegularizer.prepare(
                raw_building=raw_building,
                castles=castles,
            )

            atlas_building = AtlasSceneBuilder._to_atlas_building(prepared_building)

            atlas_building = AtlasCastleBuildingProfiler.apply_to_building(
                atlas_building=atlas_building,
                raw_building=prepared_building,
                castles=castles,
            )

            atlas_building = AtlasAncientTheatreProfiler.apply_to_building(
                atlas_building=atlas_building,
                raw_building=prepared_building,
            )
            if castle_only and not getattr(
                atlas_building,
                "is_castle_building",
                False,
            ):
                skipped_buildings += 1
                record_building_rejection("outside_castle_scope")
                continue

            if getattr(
                atlas_building,
                "is_ancient_theatre",
                False,
            ):
                theatre_diagnostics = {}

                stage_mesh = (
                    AtlasAncientTheatreStageBuilder.build(
                        raw_building=prepared_building,
                        coordinate_engine=coordinate_engine,
                        terrain_mesh=terrain_mesh,
                        diagnostics=theatre_diagnostics,
                    )
                )

                if not stage_mesh:
                    skipped_buildings += 1

                    record_building_rejection(
                        theatre_diagnostics.get(
                            "reason",
                            "ancient_theatre_stage_failed",
                        )
                    )

                    continue

                cavea_diagnostics = {}

                cavea_mesh = (
                    AtlasAncientTheatreCaveaBuilder
                    .build(
                        raw_building=prepared_building,
                        coordinate_engine=(
                            coordinate_engine
                        ),
                        terrain_mesh=terrain_mesh,
                        diagnostics=cavea_diagnostics,
                    )
                )

                if not cavea_mesh:
                    skipped_buildings += 1

                    record_building_rejection(
                        cavea_diagnostics.get(
                            "reason",
                            "ancient_theatre_cavea_failed",
                        )
                    )

                    continue

                upper_gallery_mesh = (
                    AtlasAncientTheatreUpperGalleryBuilder
                    .build(
                        cavea_mesh=cavea_mesh,
                    )
                )

                stage_facade_mesh = (
                    AtlasAncientTheatreStageFacadeBuilder
                    .build(
                        stage_mesh=stage_mesh,
                    )
                )

                stage_mesh["source_id"] = (
                    raw_building.get("id")
                )
                stage_mesh["architectural_role"] = (
                    "ancient_theatre_stage"
                )

                cavea_mesh["source_id"] = (
                    raw_building.get("id")
                )
                cavea_mesh["architectural_role"] = (
                    "ancient_theatre_cavea"
                )

                scene.add_building_mesh(stage_mesh)
                scene.add_building_mesh(cavea_mesh)

                if stage_facade_mesh:
                    stage_facade_mesh["source_id"] = (
                        raw_building.get("id")
                    )
                    stage_facade_mesh[
                        "architectural_role"
                    ] = (
                        "ancient_theatre_stage_facade"
                    )

                    scene.add_building_mesh(
                        stage_facade_mesh
                    )

                if upper_gallery_mesh:
                    upper_gallery_mesh["source_id"] = (
                        raw_building.get("id")
                    )
                    upper_gallery_mesh[
                        "architectural_role"
                    ] = (
                        "ancient_theatre_upper_gallery"
                    )

                    scene.add_building_mesh(
                        upper_gallery_mesh
                    )

                accepted_buildings += 1
                accepted_main_buildings += 1

                continue

            building_diagnostics = {}

            foundation_z_override = None

            if is_building_part:
                parent_id = building_part_hierarchy[
                    "part_to_parent"
                ].get(
                    raw_building.get("id")
                )

                foundation_z_override = (
                    parent_foundation_z_cache.get(
                        parent_id
                    )
                )

            mesh = AtlasFoundationFirstPipeline.build_building_mesh(
                building=atlas_building,
                coordinate_engine=coordinate_engine,
                terrain_mesh=terrain_mesh,
                sample_grid=5,
                embed_depth_mm=0.30,
                foundation_z_override=foundation_z_override,
                diagnostics=building_diagnostics,
            )

            if not mesh:
                skipped_buildings += 1

                if is_building_part:
                    rejected_building_parts += 1

                record_building_rejection(
                    building_diagnostics.get(
                        "reason",
                        "mesh_generation_failed",
                    )
                )
                continue

            tags = prepared_building.get(
                "tags",
                {},
            )

            mesh["source_id"] = raw_building.get("id")

            mesh["name"] = tags.get("name")

            mesh["estimated_height_m"] = atlas_building.estimated_height

            mesh["castle_profile"] = getattr(
                atlas_building,
                "castle_profile",
                None,
            )

            mesh["castle_roof_profile"] = getattr(
                atlas_building,
                "castle_roof_profile",
                None,
            )

            mesh["is_castle_building"] = getattr(
                atlas_building,
                "is_castle_building",
                False,
            )

            mesh = (
                AtlasFoundationSceneBuilder
                ._attach_building_roof_metadata(
                    mesh=mesh,
                    atlas_building=atlas_building,
                    is_building_part=is_building_part,
                    profile_counts=(
                        building_roof_profile_counts
                    ),
                    decision_source_counts=(
                        building_roof_decision_source_counts
                    ),
                )
            )

            if not mesh["is_castle_building"]:
                mesh = AtlasMinaretRoofBuilder.apply(
                    mesh=mesh,
                    tower_type=tags.get("tower:type"),
                    roof_shape=tags.get("roof:shape"),
                    roof_height_m=tags.get("roof:height"),
                    coordinate_engine=coordinate_engine,
                )

                minaret_component_records = (
                    building_part_hierarchy[
                        "minaret_components_by_minaret"
                    ].get(
                        raw_building.get("id"),
                        [],
                    )
                )

                minaret_component_meshes = []

                for component_record in minaret_component_records:
                    component_building = (
                        AtlasSceneBuilder._to_atlas_building(
                            component_record
                        )
                    )

                    component_diagnostics = {}

                    component_mesh = (
                        AtlasFoundationFirstPipeline
                        .build_building_mesh(
                            building=component_building,
                            coordinate_engine=coordinate_engine,
                            terrain_mesh=terrain_mesh,
                            sample_grid=5,
                            embed_depth_mm=0.30,
                            foundation_z_override=mesh.get(
                                "foundation_z"
                            ),
                            diagnostics=component_diagnostics,
                        )
                    )

                    if component_mesh is None:
                        continue

                    component_mesh["source_id"] = (
                        component_record.get("id")
                    )
                    component_mesh[
                        "minaret_component_type"
                    ] = "balcony_ring"

                    minaret_component_meshes.append(
                        component_mesh
                    )

                mesh = AtlasMinaretBalconyBuilder.attach(
                    minaret_mesh=mesh,
                    component_meshes=(
                        minaret_component_meshes
                    ),
                )

                mesh = AtlasMonumentDomeRoofBuilder.apply(
                    mesh=mesh,
                    roof_shape=tags.get("roof:shape"),
                    roof_height_m=tags.get("roof:height"),
                    coordinate_engine=coordinate_engine,
                    total_height_m=tags.get("height"),
                    min_height_m=tags.get("min_height"),
                )

            if mesh["is_castle_building"]:
                castle_buildings += 1

                profile_name = mesh["castle_profile"] or "unknown"

                castle_profile_counts[profile_name] = (
                    castle_profile_counts.get(
                        profile_name,
                        0,
                    )
                    + 1
                )

                mesh = AtlasCastleRoofBuilder.apply(
                    mesh=mesh,
                    castle_profile=mesh["castle_profile"],
                )

                mesh = AtlasCastleGableRoofBuilder.apply(
                    mesh=mesh,
                    castle_profile=mesh["castle_profile"],
                )

                mesh = AtlasCastleMultiGableRoofBuilder.apply(
                    mesh=mesh,
                    castle_profile=mesh["castle_profile"],
                )

                if mesh.get("castle_roof_applied"):
                    tower_roof_count += 1

                if mesh.get("castle_gable_roof_applied"):
                    gable_roof_count += 1

                if mesh.get("castle_multi_gable_roof_applied"):
                    multi_gable_roof_count += 1

                    piece_count = int(
                        mesh.get(
                            "multi_gable_roof_piece_count",
                            0,
                        )
                    )

                    multi_gable_piece_count += piece_count

                    if debug:
                        print(
                            "  MULTI-GABLE",
                            mesh.get("source_id"),
                            mesh.get("name"),
                            "pieces:",
                            piece_count,
                        )

                    if debug and mesh.get("source_id") == 282888752:
                        print(
                            "  CHAPEL-ROOF-RECORDS",
                            mesh.get(
                                "multi_gable_roof_records",
                                [],
                            ),
                        )
                has_any_roof = (
                    mesh.get("castle_roof_applied")
                    or mesh.get("castle_gable_roof_applied")
                    or mesh.get("castle_multi_gable_roof_applied")
                )

                if debug and not has_any_roof:
                    print(
                        "  NO-ROOF",
                        mesh.get("source_id"),
                        mesh.get("name"),
                        "profile:",
                        mesh.get("castle_profile"),
                        "top_points:",
                        len(mesh.get("top", [])),
                    )

            scene.add_building_mesh(mesh)

            accepted_buildings += 1

            if is_building_part:
                accepted_building_parts += 1
            else:
                accepted_main_buildings += 1

        scene.metadata["building_report"] = {
            "accepted": accepted_buildings,
            "accepted_main_buildings": accepted_main_buildings,
            "accepted_building_parts": accepted_building_parts,
            "rejected_building_parts": rejected_building_parts,
            "skipped": skipped_buildings,
            "castle_buildings": castle_buildings,
            "building_roof_profiles": dict(
                sorted(
                    building_roof_profile_counts.items()
                )
            ),
            "building_roof_decision_sources": dict(
                sorted(
                    building_roof_decision_source_counts.items()
                )
            ),
            "rejection_counts": dict(
                sorted(building_rejection_counts.items())
            ),
        }

        if debug:
            print("")
            print("=" * 70)
            print("ATLAS FOUNDATION SCENE BUILDER REPORT")
            print("=" * 70)

            print(f"Accepted buildings : " f"{accepted_buildings}")

            print(
                f"  main buildings   : "
                f"{accepted_main_buildings}"
            )

            print(
                f"  building parts   : "
                f"{accepted_building_parts}"
            )

            print(
                f"Rejected parts      : "
                f"{rejected_building_parts}"
            )

            print(f"Skipped buildings  : " f"{skipped_buildings}")

            for reason in sorted(building_rejection_counts):
                print(
                    f"  rejected/{reason:<30}: "
                    f"{building_rejection_counts[reason]}"
                )

            print(f"Castle buildings   : " f"{castle_buildings}")

            print(
                "City roof profiles : "
                f"{dict(sorted(building_roof_profile_counts.items()))}"
            )

            print(
                "Roof decisions      : "
                f"{dict(sorted(building_roof_decision_source_counts.items()))}"
            )

            for profile_name in sorted(castle_profile_counts):
                print(
                    f"  {profile_name:<24}: " f"{castle_profile_counts[profile_name]}"
                )

            print(f"Tower roofs        : " f"{tower_roof_count}")

            print(f"Single gable roofs : " f"{gable_roof_count}")

            print(f"Multi-gable roofs  : " f"{multi_gable_roof_count}")

            print(f"Multi-gable pieces : " f"{multi_gable_piece_count}")

            print("=" * 70)

        return scene

    @staticmethod
    def _geometry_intersects_bbox(geometry, bbox):
        if not geometry or bbox is None:
            return False

        points = [
            point
            for point in geometry
            if point is not None and len(point) >= 2
        ]

        if not points:
            return False

        geometry_south = min(float(point[0]) for point in points)
        geometry_west = min(float(point[1]) for point in points)
        geometry_north = max(float(point[0]) for point in points)
        geometry_east = max(float(point[1]) for point in points)

        south, west, north, east = bbox

        return not (
            geometry_north < south
            or geometry_south > north
            or geometry_east < west
            or geometry_west > east
        )
