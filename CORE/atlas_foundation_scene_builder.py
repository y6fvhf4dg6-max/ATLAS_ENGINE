# CORE/atlas_foundation_scene_builder.py

from CORE.atlas_scene import AtlasScene
from CORE.atlas_foundation_first_pipeline import AtlasFoundationFirstPipeline


class AtlasFoundationSceneBuilder:
    """
    ATLAS Foundation Scene Builder v0.1

    Yeni Foundation-First mimarisi için sahne oluşturucu.

    Akış:
    terrain hazır
        ↓
    raw building
        ↓
    atlas building
        ↓
    foundation-first pipeline
        ↓
    building mesh
        ↓
    scene
    """

    @staticmethod
    def build_scene(
        raw_buildings,
        coordinate_engine,
        terrain_mesh,
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
        debug=True,
    ):
        from CORE.atlas_scene_builder import AtlasSceneBuilder

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
        skipped_buildings = 0

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

            mesh = AtlasFoundationFirstPipeline.build_building_mesh(
                building=atlas_building,
                coordinate_engine=coordinate_engine,
                terrain_mesh=terrain_mesh,
                sample_grid=5,
                embed_depth_mm=0.30,
            )

            if mesh:
                scene.add_building_mesh(mesh)
                accepted_buildings += 1
            else:
                skipped_buildings += 1

        if debug:
            print("")
            print("=" * 70)
            print("ATLAS FOUNDATION SCENE BUILDER REPORT")
            print("=" * 70)
            print(f"Accepted buildings : {accepted_buildings}")
            print(f"Skipped buildings  : {skipped_buildings}")
            print("=" * 70)

        return scene
