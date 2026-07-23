# CORE/atlas_scene_builder.py

from CORE.atlas_scene import AtlasScene
from CORE.atlas_building import AtlasBuilding
from CORE.atlas_mesh_builder import AtlasMeshBuilder
from CORE.road_mesh_builder import AtlasRoadMeshBuilder
from CORE.atlas_foundation_first_pipeline import AtlasFoundationFirstPipeline
from CORE.atlas_building_roof_metadata_profiler import (
    AtlasBuildingRoofMetadataProfiler,
)


class AtlasSceneBuilder:
    """
    ATLAS Scene Builder v1.3

    Bu sürüm:
    - base_plate katmanını üretir
    - roads katmanını üretir
    - buildings katmanını üretir
    - Z katman sırasını düzeltir
    """

    BASE_PLATE_HEIGHT_MM = 0.80
    ROAD_Z_OFFSET_MM = 0.82
    BUILDING_Z_OFFSET_MM = 0.85

    @staticmethod
    def build_scene(
        raw_buildings,
        coordinate_engine,
        bbox=None,
        target_size_mm=None,
        bed_width_mm=None,
        bed_depth_mm=None,
        margin_mm=None,
        xy_scale=None,
        z_scale=None,
        max_buildings=None,
        min_points=4,
        max_points=80,
        roads=None,
        debug=True,
    ):
        scene = AtlasScene(
            bbox=bbox,
            target_size_mm=target_size_mm,
            bed_width_mm=bed_width_mm,
            bed_depth_mm=bed_depth_mm,
            margin_mm=margin_mm,
            xy_scale=xy_scale,
            z_scale=z_scale,
            mode="area_first_product",
        )

        accepted_buildings = 0
        skipped_buildings = 0

        building_roof_profile_counts = {}
        building_roof_decision_source_counts = {}

        for raw_building in raw_buildings:
            if max_buildings is not None and accepted_buildings >= max_buildings:
                break

            if not AtlasSceneBuilder._is_raw_building_usable(
                raw_building,
                min_points=min_points,
                max_points=max_points,
            ):
                skipped_buildings += 1
                continue

            atlas_building = AtlasSceneBuilder._to_atlas_building(raw_building)

            mesh = AtlasMeshBuilder.build_mesh(
                atlas_building,
                coordinate_engine,
            )

            if mesh:
                raw_tags = raw_building.get("tags", {})
                is_building_part = (
                    raw_tags.get("building:part") is not None
                )

                mesh = AtlasBuildingRoofMetadataProfiler.attach(
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

                scene.add_building_mesh(mesh)
                accepted_buildings += 1
            else:
                skipped_buildings += 1

        scene.metadata["building_report"] = {
            "accepted": accepted_buildings,
            "skipped": skipped_buildings,
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
        }

        road_meshes = []

        if roads:
            road_meshes = AtlasRoadMeshBuilder.build_roads(
                roads=roads,
                coordinate_engine=coordinate_engine,
                debug=debug,
            )

            for road_mesh in road_meshes:
                road_mesh = AtlasSceneBuilder._offset_mesh_z(
                    road_mesh,
                    AtlasSceneBuilder.ROAD_Z_OFFSET_MM,
                )
                scene.add_road_mesh(road_mesh)

        if debug:
            print("")
            print("=" * 60)
            print("ATLAS SCENE BUILDER REPORT")
            print("=" * 60)
            print(f"Base plate        : {scene.count_layer_meshes('base_plate')}")
            print(f"Accepted buildings: {accepted_buildings}")
            print(f"Skipped buildings : {skipped_buildings}")
            print(
                "City roof profiles : "
                f"{dict(sorted(building_roof_profile_counts.items()))}"
            )
            print(
                "Roof decisions      : "
                f"{dict(sorted(building_roof_decision_source_counts.items()))}"
            )
            print(f"Building meshes   : {scene.count_layer_meshes('buildings')}")
            print(f"Road meshes       : {scene.count_layer_meshes('roads')}")
            print(f"Total meshes      : {scene.count_all_meshes()}")
            print(f"Triangles         : {scene.count_triangles()}")
            print("=" * 60)
            print("")

        return scene

    @staticmethod
    def _offset_mesh_z(mesh, offset_z):
        if not mesh:
            return mesh

        new_mesh = {
            "bottom": [],
            "top": [],
            "walls": [],
            "triangles": [],
        }

        for key in ["type"]:
            if key in mesh:
                new_mesh[key] = mesh[key]

        for point in mesh.get("bottom", []):
            new_mesh["bottom"].append(
                AtlasSceneBuilder._offset_point_z(point, offset_z)
            )

        for point in mesh.get("top", []):
            new_mesh["top"].append(AtlasSceneBuilder._offset_point_z(point, offset_z))

        for wall in mesh.get("walls", []):
            new_wall = []

            for point in wall:
                new_wall.append(AtlasSceneBuilder._offset_point_z(point, offset_z))

            new_mesh["walls"].append(tuple(new_wall))

        for triangle in mesh.get("triangles", []):
            new_triangle = []

            for point in triangle:
                new_triangle.append(AtlasSceneBuilder._offset_point_z(point, offset_z))

            new_mesh["triangles"].append(tuple(new_triangle))

        return new_mesh

    @staticmethod
    def _offset_point_z(point, offset_z):
        x, y, z = point
        return (x, y, z + offset_z)

    @staticmethod
    def _is_raw_building_usable(raw_building, min_points, max_points):
        geometry = raw_building.get("geometry", [])

        if not geometry:
            return False

        if len(geometry) < min_points:
            return False

        if len(geometry) > max_points:
            return False

        return True

    @staticmethod
    def _to_atlas_building(raw_building):
        return AtlasBuilding(
            building_id=raw_building.get("id", "unknown"),
            source="local_pbf",
            geometry=raw_building.get("geometry", []),
            tags=raw_building.get("tags", {}),
        )
