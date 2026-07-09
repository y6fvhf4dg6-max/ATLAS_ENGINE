# CORE/atlas_foundation_first_engine.py

from CORE.atlas_local_osm_reader import AtlasLocalOSMReader
from CORE.atlas_scale_engine import AtlasScaleEngine
from CORE.atlas_coordinate_engine import AtlasCoordinateEngine
from CORE.atlas_terrain_pipeline import AtlasTerrainPipeline
from CORE.atlas_foundation_scene_builder import AtlasFoundationSceneBuilder
from CORE.atlas_debug_reporter import AtlasDebugReporter
from EXPORT.atlas_stl_writer import AtlasSTLWriter


class AtlasFoundationFirstEngine:
    """
    ATLAS Foundation-First Engine v0.3

    Akış:
    PBF
      ↓
    Terrain
      ↓
    Foundation
      ↓
    Building
      ↓
    Scene
      ↓
    STL
    """

    VERSION = "0.3"
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
        data = AtlasLocalOSMReader.read(pbf_path, bbox)

        raw_buildings = data.get("buildings", [])
        trees = data.get("trees", [])
        roads = data.get("roads", [])
        pedestrian_paths = data.get("pedestrian_paths", [])

        if debug:
            print("")
            print("=" * 70)
            print("ATLAS FOUNDATION-FIRST ENGINE v0.3")
            print("=" * 70)
            print(f"Reader buildings        : {len(raw_buildings)}")
            print(f"Reader trees            : {len(trees)}")
            print(f"Reader roads            : {len(roads)}")
            print(f"Reader pedestrian paths : {len(pedestrian_paths)}")

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
            base_z=AtlasFoundationFirstEngine.BASE_PLATE_HEIGHT_MM,
            bottom_z=0.0,
            grid_size=25,
            terrain_provider_name=terrain_provider_name,
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

        meshes = [terrain_slab]
        meshes.extend(building_meshes)

        if debug:
            print("")
            print("=" * 70)
            print("FOUNDATION-FIRST FINAL REPORT")
            print("=" * 70)
            print(f"Terrain meshes   : 1")
            print(f"Building meshes  : {len(building_meshes)}")
            print(f"Total meshes     : {len(meshes)}")
            print(f"Triangles        : {AtlasDebugReporter.count_triangles(meshes)}")
            print("=" * 70)

        AtlasSTLWriter.write(meshes, output_path)

        if debug:
            print("")
            print("=" * 70)
            print("ATLAS FOUNDATION-FIRST STL EXPORTED")
            print("=" * 70)
            print(f"Output    : {output_path}")
            print(f"XY scale  : {xy_scale:.2f}")
            print(f"Meshes    : {len(meshes)}")
            print(f"Triangles : {AtlasDebugReporter.count_triangles(meshes)}")
            print("=" * 70)

        return {
            "output_path": output_path,
            "reader_buildings": len(raw_buildings),
            "reader_trees": len(trees),
            "reader_roads": len(roads),
            "reader_pedestrian_paths": len(pedestrian_paths),
            "buildings": len(building_meshes),
            "meshes": len(meshes),
            "triangles": AtlasDebugReporter.count_triangles(meshes),
            "xy_scale": xy_scale,
            "mode": "foundation_first",
        }
