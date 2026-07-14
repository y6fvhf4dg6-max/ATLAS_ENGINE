# CORE/atlas_foundation_scene_builder.py

from CORE.atlas_scene import AtlasScene
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
from CORE.atlas_castle_building_profiler import (
    AtlasCastleBuildingProfiler,
)
from CORE.atlas_castle_footprint_regularizer import (
    AtlasCastleFootprintRegularizer,
)
from CORE.atlas_building_part_hierarchy_profiler import (
    AtlasBuildingPartHierarchyProfiler,
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
            if castle_only and not getattr(
                atlas_building,
                "is_castle_building",
                False,
            ):
                skipped_buildings += 1
                record_building_rejection("outside_castle_scope")
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
