"""
ATLAS Engine 2.0

Module : Core
Version: 0.7
Status : Local PBF + Water + Adaptive Detail

Purpose:
Central pipeline coordinator for ATLAS Engine.
"""

from atlas_area import calculate_area_bounds
from atlas_building_engine import AtlasBuildingEngine
from atlas_buildings import count_building_ways
from atlas_config import PRODUCT_PROFILES, DEFAULT_PRODUCT
from atlas_context import AtlasContext
from atlas_detail_engine import AtlasDetailEngine
from atlas_export_engine import AtlasExportEngine
from atlas_geocoder import geocode_address
from atlas_local_osm import (
    get_buildings_and_lookup_from_items,
    get_roads_and_lookup_from_items,
    get_water_and_lookup_from_items,
)
from ENGINES.mesh.atlas_mesh_repair import AtlasMeshRepair
from atlas_landmark_context import AtlasLandmarkContext
from atlas_mesh_cleaner import AtlasMeshCleaner
from atlas_road_engine import AtlasRoadEngine
from atlas_roads import count_road_ways
from atlas_scene_engine import AtlasSceneEngine
from atlas_terrain_engine import AtlasTerrainEngine, GRID_SIZE
from atlas_terrain_sampler import AtlasTerrainSampler
from atlas_water_engine import AtlasWaterEngine
from atlas_pbf_cache import AtlasPBFCache
from atlas_config import ACTIVE_CONTINENT, ACTIVE_COUNTRY, ACTIVE_CITY, ACTIVE_ADDRESS
from atlas_world import get_city_pbf_path


ADDRESS = ACTIVE_ADDRESS
MODEL_SIZE_MM = 200
OUTPUT_PATH = "STL/ATLAS_CORE_v0_7_ADAPTIVE_DETAIL.stl"


class AtlasCore:

    def __init__(self, address):
        self.context = AtlasContext(
            address=address,
            product=PRODUCT_PROFILES[DEFAULT_PRODUCT],
            model_size_mm=MODEL_SIZE_MM
        )

        self.context.scene = AtlasSceneEngine()
        self.pbf_cache = AtlasPBFCache()
        self.context.osm_water_data = None
        self.context.node_lookup_water = None
        self.context.water_count = 0

        self.context.detail_engine = AtlasDetailEngine(
            real_world_size_m=self.context.product["real_size_m"],
            model_size_mm=self.context.model_size_mm
        )

    def resolve_location(self):
        latitude, longitude = geocode_address(self.context.address)
        self.context.latitude = latitude
        self.context.longitude = longitude

        print()
        print("Adres    :", self.context.address)
        print("Enlem    :", self.context.latitude)
        print("Boylam   :", self.context.longitude)
        print()

    def calculate_bounds(self):
        self.context.bounds = calculate_area_bounds(
            self.context.latitude,
            self.context.longitude,
            self.context.product["real_size_m"]
        )
        print("Bounds:", self.context.bounds)
        print()

        pbf_path = get_city_pbf_path(
            ACTIVE_CONTINENT,
            ACTIVE_COUNTRY,
            ACTIVE_CITY
        )

        self.pbf_cache.load(
            pbf_path,
            self.context.bounds
        )

    def build_terrain(self):
        terrain_engine = AtlasTerrainEngine(self.context.address)

        terrain_engine.resolve_location()
        terrain_engine.load_dem()
        terrain_engine.build_mesh()

        self.context.terrain_vertices = terrain_engine.vertices
        self.context.terrain_faces = terrain_engine.faces

        self.context.terrain_sampler = AtlasTerrainSampler(
            self.context.terrain_vertices,
            GRID_SIZE,
            self.context.model_size_mm
        )

        self.context.scene.add_mesh(
            self.context.terrain_vertices,
            self.context.terrain_faces,
            layer_name="terrain"
        )

    

    def fetch_buildings(self):
        (
            self.context.osm_building_data,
            self.context.node_lookup_buildings,
        ) = get_buildings_and_lookup_from_items(
            self.pbf_cache.buildings
        )

        self.context.building_count = count_building_ways(
            self.context.osm_building_data
        )    

    def build_landmark_context(self):

        landmark_context = AtlasLandmarkContext(
            bounds=self.context.bounds,
            model_size_mm=self.context.model_size_mm,
            node_lookup=self.context.node_lookup_buildings
        )

        landmark_context.build_from_osm(
        self.context.osm_building_data
        )

        self.context.landmark_context = landmark_context    

    def build_buildings(self):
        building_engine = AtlasBuildingEngine(self.context)
        building_engine.build()

    def fetch_roads(self):
        (
            self.context.osm_road_data,
            self.context.node_lookup_roads,
        ) = get_roads_and_lookup_from_items(
            self.pbf_cache.roads
        )

        self.context.road_count = count_road_ways(
            self.context.osm_road_data
        )

    def build_roads(self):
        road_engine = AtlasRoadEngine(self.context)
        road_engine.build()

    def fetch_water(self):
        (
            self.context.osm_water_data,
            self.context.node_lookup_water,
        ) = get_water_and_lookup_from_items(
            self.pbf_cache.water
        )

        self.context.water_count = len(
            self.context.osm_water_data.get("elements", [])
        )

    def build_water(self):
        water_engine = AtlasWaterEngine(self.context)
        water_engine.build()

    def clean_scene_mesh(self):
        cleaner = AtlasMeshCleaner(
            self.context.scene.points,
            self.context.scene.faces
        )

        cleaned_points, cleaned_faces = cleaner.clean()

        self.context.scene.points = cleaned_points
        self.context.scene.faces = cleaned_faces

    def export(self):
        self.clean_scene_mesh()

        repair = AtlasMeshRepair(
            self.context.scene.points,
            self.context.scene.faces
        )

        repair.report()

        repaired_points, repaired_faces = repair.repair()

        self.context.scene.points = repaired_points
        self.context.scene.faces = repaired_faces

        exporter = AtlasExportEngine(self.context.scene)

        exporter.export_stl(
            OUTPUT_PATH,
            solid_name="ATLAS_CORE_ADAPTIVE_DETAIL"
        )

    def build(self):
        print()
        print("=" * 60)
        print("ATLAS CORE v0.7 - ADAPTIVE DETAIL")
        print("=" * 60)

        print("0. Adaptive Detail hesaplanıyor...")
        self.context.detail_engine.report()
        print()

        print("1. Konum çözülüyor...")
        self.resolve_location()
        print("Enlem :", self.context.latitude)
        print("Boylam:", self.context.longitude)
        print()

        print("2. Alan sınırları hesaplanıyor...")
        self.calculate_bounds()
        print("North:", self.context.bounds["north"])
        print("South:", self.context.bounds["south"])
        print("East :", self.context.bounds["east"])
        print("West :", self.context.bounds["west"])
        print()

        print("3. Scene oluşturuluyor...")
        self.context.scene.create_scene()
        print("Scene hazır:", self.context.scene is not None)
        print()

        print("4. Terrain oluşturuluyor...")
        self.build_terrain()
        print("Terrain vertices:", len(self.context.terrain_vertices))
        print("Terrain faces   :", len(self.context.terrain_faces))
        print()

        print("5. Local PBF bina verisi alınıyor...")
        self.fetch_buildings()
        print("Bina node lookup:", len(self.context.node_lookup_buildings))
        print("Bina sayısı:", self.context.building_count)
        print()

        print("6. Landmark Context oluşturuluyor...")
        self.build_landmark_context()
        print()

        print("7. Building Engine çalışıyor...")
        self.build_buildings()
        print()

        print("8. Local PBF yol verisi alınıyor...")
        self.fetch_roads()
        print("Yol node lookup:", len(self.context.node_lookup_roads))
        print("Yol sayısı:", self.context.road_count)
        print()

        print("9. Road Engine çalışıyor...")
        self.build_roads()
        print()

        print("10. Local PBF su verisi alınıyor...")
        self.fetch_water()
        print("Su node lookup:", len(self.context.node_lookup_water))
        print("Su öğesi sayısı:", self.context.water_count)
        print()

        print("11. Water Engine çalışıyor...")
        self.build_water()
        print()

        print("12. Scene özeti")
        self.context.scene.info()
        print()

        print("13. Export öncesi Mesh Cleaner")
        print()

        print("14. Export")
        self.export()

        print()
        print("ATLAS CORE v0.7 TAMAMLANDI ✅")
        print("=" * 60)


def main():
    core = AtlasCore(ADDRESS)
    core.build()


if __name__ == "__main__":
    main()