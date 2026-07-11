# CORE/atlas_foundation_first_engine.py

from CORE.atlas_local_osm_reader import AtlasLocalOSMReader
from CORE.atlas_scale_engine import AtlasScaleEngine
from CORE.atlas_coordinate_engine import AtlasCoordinateEngine
from CORE.atlas_terrain_pipeline import AtlasTerrainPipeline
from CORE.atlas_foundation_scene_builder import AtlasFoundationSceneBuilder
from CORE.atlas_debug_reporter import AtlasDebugReporter
from CORE.atlas_road_foundation_builder import AtlasRoadFoundationBuilder
from CORE.atlas_park_foundation_builder import AtlasParkFoundationBuilder
from CORE.atlas_tree_foundation_builder import AtlasTreeFoundationBuilder
from CORE.atlas_nature_pipeline import AtlasNaturePipeline
from CORE.atlas_castle_wall_builder import AtlasCastleWallBuilder
from CORE.atlas_castle_shell_builder import AtlasCastleShellBuilder
from CORE.atlas_castle_tower_cap_builder import (
    AtlasCastleTowerCapBuilder,
)
from EXPORT.atlas_stl_writer import AtlasSTLWriter


class AtlasFoundationFirstEngine:
    """
    ATLAS Foundation-First Engine v0.4

    Akış:
    PBF
      ↓
    Terrain
      ↓
    Buildings / Roads / Parks / Trees
      ↓
    Independent castle walls
      ↓
    Multipolygon castle shells
      ↓
    STL

    Kale davranışı:
    - barrier=city_wall gibi bağımsız surlar Wall Builder ile üretilir
    - relation outer/inner geometrileri Shell Builder ile tek kabuk yapılır
    - relation sınırları ayrıca ikinci kez sur olarak üretilmez
    """

    VERSION = "0.4"
    BASE_PLATE_HEIGHT_MM = 0.80

    @staticmethod
    def generate_city_stl(
        pbf_path,
        bbox,
        output_path,
        target_size_mm=200,
        bed_width_mm=256,
        bed_depth_mm=256,
        margin_mm=15,
        max_buildings=None,
        min_points=4,
        max_points=300,
        z_scale=5500,
        terrain_provider_name="srtm",
        debug=True,
    ):
        data = AtlasLocalOSMReader.read(
            pbf_path,
            bbox,
        )

        raw_buildings = data.get("buildings", [])
        trees = data.get("trees", [])
        roads = data.get("roads", [])
        pedestrian_paths = data.get(
            "pedestrian_paths",
            [],
        )
        parks = data.get("parks", [])
        waters = data.get("waters", [])
        castles = data.get("castles", [])
        castle_walls = data.get(
            "castle_walls",
            [],
        )
        defensive_towers = data.get(
            "defensive_towers",
            [],
        )

        nature_data = AtlasNaturePipeline.fetch(
            bbox=bbox,
            provider_names=("worldcover",),
            debug=debug,
        )

        trees.extend(nature_data.get("trees", []))

        # Relation sınırları Castle Shell Builder tarafından
        # tek kabuk olarak üretilecektir. Bunları ayrıca sur
        # şeridi olarak üretmek çift geometri oluşturur.
        independent_castle_walls = [
            wall for wall in castle_walls if not wall.get("source_relation_id")
        ]

        relation_castle_walls = [
            wall for wall in castle_walls if wall.get("source_relation_id")
        ]

        if debug:
            print("")
            print("=" * 70)
            print(
                "ATLAS FOUNDATION-FIRST ENGINE "
                f"v{AtlasFoundationFirstEngine.VERSION}"
            )
            print("=" * 70)
            print(f"Reader buildings        : " f"{len(raw_buildings)}")
            print(f"Reader trees            : " f"{len(trees)}")
            print(f"Reader roads            : " f"{len(roads)}")
            print(f"Reader pedestrian paths : " f"{len(pedestrian_paths)}")
            print(f"Reader parks            : " f"{len(parks)}")
            print(f"Reader waters           : " f"{len(waters)}")
            print(f"Reader castles          : " f"{len(castles)}")
            print(f"Reader castle walls     : " f"{len(castle_walls)}")
            print(f"Independent walls       : " f"{len(independent_castle_walls)}")
            print(f"Relation wall records   : " f"{len(relation_castle_walls)}")
            print(f"Reader defensive towers : " f"{len(defensive_towers)}")
            print("=" * 70)

        xy_scale = AtlasScaleEngine.calculate_xy_scale_from_bbox(
            bbox=bbox,
            target_size_mm=target_size_mm,
            bed_width_mm=bed_width_mm,
            bed_depth_mm=bed_depth_mm,
            margin_mm=margin_mm,
            debug=debug,
        )

        south, west, _north, _east = bbox

        coordinate_engine = AtlasCoordinateEngine(
            origin_lat=south,
            origin_lon=west,
            xy_scale=xy_scale,
            z_scale=z_scale,
        )

        terrain_slab = AtlasTerrainPipeline.build_terrain_slab(
            bbox=bbox,
            target_size_mm=target_size_mm,
            z_scale=z_scale,
            base_z=(AtlasFoundationFirstEngine.BASE_PLATE_HEIGHT_MM),
            bottom_z=0.0,
            grid_size=25,
            terrain_provider_name=(terrain_provider_name),
            debug=debug,
        )

        scene = AtlasFoundationSceneBuilder.build_scene(
            raw_buildings=raw_buildings,
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_slab,
            bbox=bbox,
            target_size_mm=target_size_mm,
            bed_width_mm=bed_width_mm,
            bed_depth_mm=bed_depth_mm,
            margin_mm=margin_mm,
            xy_scale=xy_scale,
            z_scale=z_scale,
            max_buildings=max_buildings,
            min_points=min_points,
            max_points=max_points,
            debug=debug,
        )

        building_meshes = scene.get_all_meshes()

        road_meshes = AtlasRoadFoundationBuilder.build_roads(
            roads=roads,
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_slab,
            debug=debug,
        )

        park_meshes = AtlasParkFoundationBuilder.build_parks(
            parks=parks,
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_slab,
            debug=debug,
        )

        tree_meshes = AtlasTreeFoundationBuilder.build_trees(
            trees=trees,
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_slab,
            debug=debug,
        )

        castle_wall_meshes = AtlasCastleWallBuilder.build_walls(
            castle_walls=(independent_castle_walls),
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_slab,
            debug=debug,
        )

        castle_shell_meshes = AtlasCastleShellBuilder.build_shells(
            castles=castles,
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_slab,
            debug=debug,
        )
        castle_tower_cap_meshes = AtlasCastleTowerCapBuilder.build_caps(
            castles=castles,
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_slab,
            debug=debug,
        )

        meshes = [terrain_slab]
        meshes.extend(building_meshes)
        meshes.extend(road_meshes)
        meshes.extend(park_meshes)
        meshes.extend(tree_meshes)
        meshes.extend(castle_wall_meshes)
        meshes.extend(castle_shell_meshes)
        meshes.extend(castle_tower_cap_meshes)

        triangle_count = AtlasDebugReporter.count_triangles(meshes)

        if debug:
            print("")
            print("=" * 70)
            print("FOUNDATION-FIRST FINAL REPORT")
            print("=" * 70)
            print("Terrain meshes     : 1")
            print(f"Building meshes    : " f"{len(building_meshes)}")
            print(f"Road meshes        : " f"{len(road_meshes)}")
            print(f"Park meshes        : " f"{len(park_meshes)}")
            print(f"Tree meshes        : " f"{len(tree_meshes)}")
            print(f"Castle wall meshes : " f"{len(castle_wall_meshes)}")
            print(f"Castle shell meshes: " f"{len(castle_shell_meshes)}")
            print(f"Castle tower caps  : " f"{len(castle_tower_cap_meshes)}")
            print(f"Total meshes       : " f"{len(meshes)}")
            print(f"Triangles          : " f"{triangle_count}")
            print("=" * 70)

        AtlasSTLWriter.write(
            meshes,
            output_path,
        )

        if debug:
            print("")
            print("=" * 70)
            print("ATLAS FOUNDATION-FIRST " "STL EXPORTED")
            print("=" * 70)
            print(f"Output    : {output_path}")
            print(f"XY scale  : {xy_scale:.2f}")
            print(f"Meshes    : {len(meshes)}")
            print(f"Triangles : {triangle_count}")
            print("=" * 70)

        return {
            "output_path": output_path,
            "reader_buildings": len(raw_buildings),
            "reader_trees": len(trees),
            "reader_roads": len(roads),
            "reader_pedestrian_paths": len(pedestrian_paths),
            "reader_parks": len(parks),
            "reader_waters": len(waters),
            "reader_castles": len(castles),
            "reader_castle_walls": len(castle_walls),
            "reader_independent_castle_walls": len(independent_castle_walls),
            "reader_relation_castle_walls": len(relation_castle_walls),
            "reader_defensive_towers": len(defensive_towers),
            "buildings": len(building_meshes),
            "castle_wall_meshes": len(castle_wall_meshes),
            "castle_shell_meshes": len(castle_shell_meshes),
            "castle_tower_cap_meshes": len(castle_tower_cap_meshes),
            "meshes": len(meshes),
            "triangles": triangle_count,
            "xy_scale": xy_scale,
            "mode": "foundation_first",
        }
