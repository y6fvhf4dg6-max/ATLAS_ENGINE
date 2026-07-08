"""
ATLAS Engine 2.0

Module : Context
Version: 0.1
Status : Architecture Foundation

Purpose:
Shared state object for the whole ATLAS pipeline.

Rule:
Terrain, bounds, sampler, roads, buildings and scene data
must be created once and shared through this context.
"""


class AtlasContext:

    def __init__(self, address, product, model_size_mm):
        self.address = address
        self.product = product
        self.model_size_mm = model_size_mm

        # Location
        self.latitude = None
        self.longitude = None
        self.bounds = None

        # Raw data
        self.osm_building_data = None
        self.osm_road_data = None
        self.node_lookup_buildings = None
        self.node_lookup_roads = None

        # Terrain
        self.terrain_vertices = []
        self.terrain_faces = []
        self.terrain_sampler = None

        # Scene
        self.scene_points = []
        self.scene_faces = []

        # Counters
        self.building_checked_count = 0
        self.building_valid_count = 0
        self.building_skipped_count = 0

        self.road_checked_count = 0
        self.road_valid_count = 0
        self.road_skipped_count = 0

    def info(self):
        print()
        print("=" * 60)
        print("ATLAS CONTEXT v0.1")
        print("=" * 60)
        print("Adres :", self.address)
        print("Ürün  :", self.product["name"])
        print("Model :", self.model_size_mm, "mm")
        print()
        print("Latitude :", self.latitude)
        print("Longitude:", self.longitude)
        print("Bounds   :", self.bounds)
        print()
        print("Terrain vertices:", len(self.terrain_vertices))
        print("Terrain faces   :", len(self.terrain_faces))
        print("Scene points    :", len(self.scene_points))
        print("Scene faces     :", len(self.scene_faces))
        print("=" * 60)


def main():
    from atlas_config import PRODUCT_PROFILES, DEFAULT_PRODUCT

    context = AtlasContext(
        address="Frankfurt Römer",
        product=PRODUCT_PROFILES[DEFAULT_PRODUCT],
        model_size_mm=200
    )

    context.info()


if __name__ == "__main__":
    main()