# CORE/atlas_foundation_first_engine.py

from CORE.atlas_local_osm_reader import AtlasLocalOSMReader
from CORE.atlas_scale_engine import AtlasScaleEngine
from CORE.atlas_coordinate_engine import AtlasCoordinateEngine
from CORE.atlas_terrain_pipeline import AtlasTerrainPipeline
from CORE.atlas_foundation_scene_builder import (
    AtlasFoundationSceneBuilder,
)
from CORE.atlas_debug_reporter import AtlasDebugReporter
from CORE.atlas_road_foundation_builder import (
    AtlasRoadFoundationBuilder,
)
from CORE.atlas_park_foundation_builder import (
    AtlasParkFoundationBuilder,
)
from CORE.atlas_tree_foundation_builder import (
    AtlasTreeFoundationBuilder,
)
from CORE.atlas_nature_pipeline import AtlasNaturePipeline
from CORE.atlas_castle_wall_builder import (
    AtlasCastleWallBuilder,
)
from CORE.atlas_castle_geometry_classifier import (
    AtlasCastleGeometryClassifier,
)
from CORE.atlas_castle_shell_builder import (
    AtlasCastleShellBuilder,
)
from CORE.atlas_castle_tower_cap_builder import (
    AtlasCastleTowerCapBuilder,
)
from CORE.atlas_castle_focus_engine import (
    AtlasCastleFocusEngine,
)
from CORE.atlas_coastline_water_builder import (
    AtlasCoastlineWaterBuilder,
)
from CORE.atlas_water_foundation_builder import (
    AtlasWaterFoundationBuilder,
)
from EXPORT.atlas_stl_writer import AtlasSTLWriter


class AtlasFoundationFirstEngine:
    """
    ATLAS Foundation-First Engine v0.5

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

    v0.5:
    - İsteğe bağlı castle-focus bbox desteği
    - Sabit XY ölçeğinde dikdörtgen terrain desteği
    - Eski kare terrain davranışı varsayılan olarak korunur
    """

    VERSION = "0.5"
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
        nature_provider_names=("worldcover",),
        castle_only=False,
        castle_focus=False,
        castle_focus_padding_m=10.0,
        fixed_xy_scale=5500.0,
        debug=True,
    ):
        source_bbox = bbox

        data = AtlasLocalOSMReader.read(
            pbf_path,
            source_bbox,
        )

        raw_buildings = data.get(
            "buildings",
            [],
        )

        trees = data.get(
            "trees",
            [],
        )

        roads = data.get(
            "roads",
            [],
        )

        pedestrian_paths = data.get(
            "pedestrian_paths",
            [],
        )

        parks = data.get(
            "parks",
            [],
        )

        waters = data.get(
            "waters",
            [],
        )

        coastlines = data.get(
            "coastlines",
            [],
        )

        castles = data.get(
            "castles",
            [],
        )

        castle_walls = data.get(
            "castle_walls",
            [],
        )

        defensive_towers = data.get(
            "defensive_towers",
            [],
        )

        nature_data = AtlasNaturePipeline.fetch(
            bbox=source_bbox,
            provider_names=nature_provider_names,
            debug=debug,
        )

        trees.extend(
            nature_data.get(
                "trees",
                [],
            )
        )

        castle_geometry = AtlasCastleGeometryClassifier.classify(
            castles=castles,
            castle_walls=castle_walls,
            debug=debug,
        )

        shell_castles = castle_geometry["shell_castles"]

        independent_castle_walls = castle_geometry["independent_castle_walls"]

        relation_castle_walls = castle_geometry["relation_castle_walls"]

        inferred_perimeter_walls = castle_geometry["inferred_perimeter_walls"]

        unknown_castles = castle_geometry["unknown_castles"]

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
            print(f"Inferred perimeter walls: " f"{len(inferred_perimeter_walls)}")
            print(f"Unknown castles         : " f"{len(unknown_castles)}")
            print(f"Reader defensive towers : " f"{len(defensive_towers)}")
            print("=" * 70)

        working_bbox = source_bbox
        size_x_mm = None
        size_y_mm = None
        focus_result = None

        use_castle_focus = bool(castle_focus)

        if use_castle_focus:
            focus_result = AtlasCastleFocusEngine.calculate_focus_bbox(
                raw_buildings=raw_buildings,
                castles=castles,
                independent_castle_walls=(independent_castle_walls),
                shell_castles=shell_castles,
                source_bbox=source_bbox,
                min_points=min_points,
                max_points=max_points,
                padding_m=castle_focus_padding_m,
                debug=debug,
            )

            working_bbox = focus_result["bbox"]

        if use_castle_focus and castle_only:
            fixed_dimensions = AtlasScaleEngine.calculate_dimensions_from_scale(
                bbox=working_bbox,
                xy_scale=fixed_xy_scale,
                debug=debug,
            )

            xy_scale = fixed_dimensions["xy_scale"]

            size_x_mm = fixed_dimensions["size_x_mm"]

            size_y_mm = fixed_dimensions["size_y_mm"]

        else:
            xy_scale = AtlasScaleEngine.calculate_xy_scale_from_bbox(
                bbox=working_bbox,
                target_size_mm=target_size_mm,
                bed_width_mm=bed_width_mm,
                bed_depth_mm=bed_depth_mm,
                margin_mm=margin_mm,
                debug=debug,
            )

        south, west, _north, _east = working_bbox

        coordinate_engine = AtlasCoordinateEngine(
            origin_lat=south,
            origin_lon=west,
            xy_scale=xy_scale,
            z_scale=z_scale,
        )

        terrain_slab = AtlasTerrainPipeline.build_terrain_slab(
            bbox=working_bbox,
            target_size_mm=target_size_mm,
            size_x_mm=size_x_mm,
            size_y_mm=size_y_mm,
            z_scale=z_scale,
            base_z=(AtlasFoundationFirstEngine.BASE_PLATE_HEIGHT_MM),
            bottom_z=0.0,
            grid_size=25,
            terrain_provider_name=(terrain_provider_name),
            debug=debug,
        )

        coastline_water_polygons = (
            AtlasCoastlineWaterBuilder.build_water_polygons(
                coastlines=coastlines,
                bbox=working_bbox,
                debug=debug,
            )
        )

        water_meshes = (
            AtlasWaterFoundationBuilder.build_coastline_water_meshes(
                water_polygons=coastline_water_polygons,
                coordinate_engine=coordinate_engine,
                terrain_mesh=terrain_slab,
                debug=debug,
            )
        )

        scene = AtlasFoundationSceneBuilder.build_scene(
            raw_buildings=raw_buildings,
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_slab,
            castles=castles,
            bbox=working_bbox,
            target_size_mm=target_size_mm,
            bed_width_mm=bed_width_mm,
            bed_depth_mm=bed_depth_mm,
            margin_mm=margin_mm,
            xy_scale=xy_scale,
            z_scale=z_scale,
            max_buildings=max_buildings,
            min_points=min_points,
            max_points=max_points,
            castle_only=castle_only,
            debug=debug,
        )

        building_meshes = scene.get_all_meshes()

        if castle_only:
            road_input = []
            park_input = []
            tree_input = []
        else:
            road_input = [
                *roads,
                *pedestrian_paths,
            ]

            park_input = parks
            tree_input = trees

        road_meshes = AtlasRoadFoundationBuilder.build_roads(
            roads=road_input,
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_slab,
            debug=debug,
        )

        park_meshes = AtlasParkFoundationBuilder.build_parks(
            parks=park_input,
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_slab,
            debug=debug,
        )

        tree_meshes = AtlasTreeFoundationBuilder.build_trees(
            trees=tree_input,
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
            castles=shell_castles,
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_slab,
            debug=debug,
        )

        castle_tower_cap_meshes = AtlasCastleTowerCapBuilder.build_caps(
            castles=shell_castles,
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_slab,
            debug=debug,
        )

        meshes = [terrain_slab]

        meshes.extend(building_meshes)

        meshes.extend(road_meshes)

        meshes.extend(park_meshes)

        meshes.extend(tree_meshes)

        meshes.extend(water_meshes)

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
            print(f"Water meshes       : " f"{len(water_meshes)}")
            print(f"Castle wall meshes : " f"{len(castle_wall_meshes)}")
            print(f"Castle shell meshes: " f"{len(castle_shell_meshes)}")
            print(f"Castle tower caps  : " f"{len(castle_tower_cap_meshes)}")
            print(f"Total meshes       : " f"{len(meshes)}")
            print(f"Triangles          : " f"{triangle_count}")
            print(f"Castle focus       : " f"{use_castle_focus}")
            print(f"XY scale           : " f"1:{xy_scale:.2f}")

            if size_x_mm is not None:
                print(f"Terrain width      : " f"{size_x_mm:.2f} mm")

            if size_y_mm is not None:
                print(f"Terrain depth      : " f"{size_y_mm:.2f} mm")

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
            print(f"XY scale  : 1:{xy_scale:.2f}")
            print(f"Meshes    : {len(meshes)}")
            print(f"Triangles : {triangle_count}")
            print("=" * 70)

        terrain_metadata = terrain_slab.get(
            "metadata",
            {},
        )

        return {
            "output_path": output_path,
            "reader_buildings": len(raw_buildings),
            "reader_trees": len(trees),
            "reader_roads": len(roads),
            "reader_pedestrian_paths": len(pedestrian_paths),
            "reader_parks": len(parks),
            "reader_waters": len(waters),
            "reader_coastlines": len(coastlines),
            "reader_castles": len(castles),
            "reader_castle_walls": len(castle_walls),
            "reader_independent_castle_walls": len(independent_castle_walls),
            "reader_relation_castle_walls": len(relation_castle_walls),
            "reader_defensive_towers": len(defensive_towers),
            "buildings": len(building_meshes),
            "water_meshes": len(water_meshes),
            "castle_wall_meshes": len(castle_wall_meshes),
            "castle_shell_meshes": len(castle_shell_meshes),
            "castle_tower_cap_meshes": len(castle_tower_cap_meshes),
            "meshes": len(meshes),
            "mesh_groups": {
                "terrain": [terrain_slab],
                "buildings": building_meshes,
                "roads": road_meshes,
                "parks": park_meshes,
                "trees": tree_meshes,
                "waters": water_meshes,
                "castle_walls": (castle_wall_meshes),
                "castle_shells": (castle_shell_meshes),
                "castle_tower_caps": (castle_tower_cap_meshes),
            },
            "triangles": triangle_count,
            "xy_scale": xy_scale,
            "source_bbox": source_bbox,
            "working_bbox": working_bbox,
            "castle_focus": use_castle_focus,
            "castle_focus_result": focus_result,
            "terrain_size_x_mm": (
                terrain_metadata.get(
                    "size_x_mm",
                    terrain_metadata.get("size_mm"),
                )
            ),
            "terrain_size_y_mm": (
                terrain_metadata.get(
                    "size_y_mm",
                    terrain_metadata.get("size_mm"),
                )
            ),
            "mode": "foundation_first",
        }
