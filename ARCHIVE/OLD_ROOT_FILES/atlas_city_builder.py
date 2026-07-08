"""
ATLAS Engine

Module : City Builder
Version: 0.7
Status : Development

Purpose:
Builds combined city scene:
Terrain + Buildings + Height Engine + Terrain Offset + STL Export

Fix:
Buildings are placed slightly above terrain surface to avoid sinking.
"""

from atlas_area import calculate_area_bounds
from atlas_buildings import fetch_buildings_from_osm, count_building_ways, is_building_way
from atlas_config import PRODUCT_PROFILES, DEFAULT_PRODUCT
from atlas_extrusion import extrude_mesh
from atlas_geocoder import geocode_address
from atlas_geometry import build_node_lookup, resolve_node_coordinates
from atlas_height_engine import get_final_model_height_mm
from atlas_mesh_builder import triangulate_polygon
from atlas_model_space import coordinates_to_model_points
from atlas_scene_builder import create_empty_scene, add_mesh_to_scene, scene_info
from atlas_stl_writer import stl_writer_info
from atlas_terrain_engine import AtlasTerrainEngine, GRID_SIZE


ADDRESS = "Frankfurt Römer"
MODEL_SIZE_MM = 200
MAX_BUILDINGS = 150
BUILDING_TERRAIN_OFFSET_MM = 0.35
OUTPUT_PATH = "STL/ATLAS_CITY_BUILDER_v0_7_TERRAIN_OFFSET.stl"


class AtlasCityBuilder:

    def __init__(self, address):
        self.address = address
        self.product = PRODUCT_PROFILES[DEFAULT_PRODUCT]

        self.latitude = None
        self.longitude = None
        self.bounds = None

        self.osm_data = None
        self.node_lookup = None
        self.building_count = 0

        self.terrain_engine = None
        self.scene_points = []
        self.scene_faces = []

        self.checked_count = 0
        self.valid_count = 0
        self.skipped_count = 0

    def resolve_location(self):
        self.latitude, self.longitude = geocode_address(self.address)

    def calculate_bounds(self):
        self.bounds = calculate_area_bounds(
            self.latitude,
            self.longitude,
            self.product["real_size_m"]
        )

    def build_terrain(self):
        self.terrain_engine = AtlasTerrainEngine(self.address)
        self.terrain_engine.resolve_location()
        self.terrain_engine.load_dem()
        self.terrain_engine.build_mesh()

    def fetch_buildings(self):
        self.osm_data = fetch_buildings_from_osm(self.bounds)
        self.node_lookup = build_node_lookup(self.osm_data)
        self.building_count = count_building_ways(self.osm_data)

    def get_building_height(self, tags):
        return get_final_model_height_mm(
            tags,
            real_size_m=self.product["real_size_m"],
            model_size_mm=MODEL_SIZE_MM
        )

    def sample_terrain_height(self, x, y):
        step = MODEL_SIZE_MM / (GRID_SIZE - 1)

        col = round(x / step)
        row = round(y / step)

        col = max(0, min(GRID_SIZE - 1, col))
        row = max(0, min(GRID_SIZE - 1, row))

        index = row * GRID_SIZE + col

        return self.terrain_engine.vertices[index][2]

    def shift_mesh_z(self, points_3d, base_z):
        shifted = []

        for x, y, z in points_3d:
            shifted.append((x, y, z + base_z))

        return shifted

    def build_scene(self):
        self.scene_points, self.scene_faces = create_empty_scene()

        add_mesh_to_scene(
            self.scene_points,
            self.scene_faces,
            self.terrain_engine.vertices,
            self.terrain_engine.faces
        )

        for element in self.osm_data["elements"]:
            if not is_building_way(element):
                continue

            self.checked_count += 1

            if self.valid_count >= MAX_BUILDINGS:
                break

            try:
                coordinates = resolve_node_coordinates(
                    element["nodes"],
                    self.node_lookup
                )

                model_points = coordinates_to_model_points(
                    coordinates,
                    self.bounds,
                    MODEL_SIZE_MM
                )

                polygon, vertices, triangles = triangulate_polygon(model_points)

                center_x = polygon.centroid.x
                center_y = polygon.centroid.y

                terrain_z = self.sample_terrain_height(center_x, center_y)

                building_base_z = terrain_z + BUILDING_TERRAIN_OFFSET_MM

                height_data = self.get_building_height(element["tags"])
                height_mm = height_data["final_model_height_mm"]

                points_3d, faces = extrude_mesh(
                    vertices,
                    triangles,
                    height_mm
                )

                points_3d = self.shift_mesh_z(
                    points_3d,
                    building_base_z
                )

                add_mesh_to_scene(
                    self.scene_points,
                    self.scene_faces,
                    points_3d,
                    faces
                )

                self.valid_count += 1

                print(
                    "OK:",
                    self.valid_count,
                    "| OSM:",
                    element["id"],
                    "| Tür:",
                    element["tags"]["building"],
                    "| Terrain Z:",
                    round(terrain_z, 2),
                    "mm",
                    "| Base Z:",
                    round(building_base_z, 2),
                    "mm",
                    "| Height:",
                    round(height_mm, 2),
                    "mm"
                )

            except Exception as error:
                self.skipped_count += 1
                print("Atlandı:", element.get("id"), "|", error)

    def export_scene(self):
        stl_writer_info(
            self.scene_points,
            self.scene_faces,
            OUTPUT_PATH
        )

    def build(self):
        print()
        print("=" * 60)
        print("ATLAS CITY BUILDER v0.7 - TERRAIN OFFSET")
        print("=" * 60)

        print("Adres :", self.address)
        print("Ürün  :", self.product["name"])
        print("Model :", MODEL_SIZE_MM, "mm")
        print("Maksimum bina:", MAX_BUILDINGS)
        print("Bina zemin offset:", BUILDING_TERRAIN_OFFSET_MM, "mm")
        print("Çıktı :", OUTPUT_PATH)
        print()

        print("1. Geocoder çalışıyor...")
        self.resolve_location()
        print("Enlem  :", self.latitude)
        print("Boylam :", self.longitude)
        print()

        print("2. Alan sınırları hesaplanıyor...")
        self.calculate_bounds()
        print("North:", self.bounds["north"])
        print("South:", self.bounds["south"])
        print("East :", self.bounds["east"])
        print("West :", self.bounds["west"])
        print()

        print("3. Terrain oluşturuluyor...")
        self.build_terrain()
        print("Terrain vertices:", len(self.terrain_engine.vertices))
        print("Terrain faces   :", len(self.terrain_engine.faces))
        print()

        print("4. OSM bina verisi alınıyor...")
        self.fetch_buildings()
        print("Node lookup sayısı:", len(self.node_lookup))
        print("Bina sayısı:", self.building_count)
        print("Toplam OSM elemanı:", len(self.osm_data["elements"]))
        print()

        print("5. Terrain + Building sahnesi oluşturuluyor...")
        self.build_scene()
        print()

        print("6. Sahne özeti")
        scene_info(self.scene_points, self.scene_faces)
        print("Denenen bina sayısı :", self.checked_count)
        print("Geçerli bina sayısı :", self.valid_count)
        print("Atlanan bina sayısı :", self.skipped_count)
        print()

        print("7. STL export")
        self.export_scene()

        print()
        print("ATLAS CITY BUILDER v0.7 TAMAMLANDI ✅")
        print("=" * 60)


def main():
    builder = AtlasCityBuilder(ADDRESS)
    builder.build()


if __name__ == "__main__":
    main()