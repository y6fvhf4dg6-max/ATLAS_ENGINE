# CORE/atlas_scene.py


class AtlasScene:
    """
    ATLAS Scene v1.0

    ATLAS'ın merkezi sahne nesnesidir.

    Bu sınıf STL değildir.
    Bu sınıf mesh değildir.
    Bu sınıf ürün sahnesidir.

    Sahne; seçilen alan içindeki tüm üretilebilir katmanları temsil eder:
    - buildings
    - roads
    - water
    - terrain
    - trees
    - pois
    - base_plate
    """

    def __init__(
        self,
        bbox=None,
        target_size_mm=None,
        bed_width_mm=None,
        bed_depth_mm=None,
        margin_mm=None,
        xy_scale=None,
        z_scale=None,
        mode="area_first_product",
    ):
        self.metadata = {
            "engine": "ATLAS",
            "scene_version": "1.0",
            "mode": mode,
        }

        self.bbox = bbox

        self.product = {
            "target_size_mm": target_size_mm,
            "bed_width_mm": bed_width_mm,
            "bed_depth_mm": bed_depth_mm,
            "margin_mm": margin_mm,
        }

        self.scale = {
            "xy_scale": xy_scale,
            "z_scale": z_scale,
        }

        self.layers = {
            "base_plate": [],
            "terrain": [],
            "water": [],
            "roads": [],
            "buildings": [],
            "trees": [],
            "pois": [],
        }

    def add_building_mesh(self, mesh):
        if mesh:
            self.layers["buildings"].append(mesh)

    def add_building_meshes(self, meshes):
        for mesh in meshes:
            self.add_building_mesh(mesh)

    def add_base_plate_mesh(self, mesh):
        if mesh:
            self.layers["base_plate"].append(mesh)

    def add_terrain_mesh(self, mesh):
        if mesh:
            self.layers["terrain"].append(mesh)

    def add_water_mesh(self, mesh):
        if mesh:
            self.layers["water"].append(mesh)

    def add_road_mesh(self, mesh):
        if mesh:
            self.layers["roads"].append(mesh)

    def add_tree_mesh(self, mesh):
        if mesh:
            self.layers["trees"].append(mesh)

    def add_poi_mesh(self, mesh):
        if mesh:
            self.layers["pois"].append(mesh)

    def get_all_meshes(self):
        meshes = []

        layer_order = [
            "base_plate",
            "terrain",
            "water",
            "roads",
            "buildings",
            "trees",
            "pois",
        ]

        for layer_name in layer_order:
            meshes.extend(self.layers.get(layer_name, []))

        return meshes

    def count_layer_meshes(self, layer_name):
        return len(self.layers.get(layer_name, []))

    def count_all_meshes(self):
        return len(self.get_all_meshes())

    def count_triangles(self):
        total = 0

        for mesh in self.get_all_meshes():
            if isinstance(mesh, dict):
                if mesh.get("triangles"):
                    total += len(mesh["triangles"])
                elif mesh.get("faces"):
                    total += len(mesh["faces"])

        return total

    def summary(self):
        return {
            "metadata": self.metadata,
            "bbox": self.bbox,
            "product": self.product,
            "scale": self.scale,
            "layers": {
                "base_plate": self.count_layer_meshes("base_plate"),
                "terrain": self.count_layer_meshes("terrain"),
                "water": self.count_layer_meshes("water"),
                "roads": self.count_layer_meshes("roads"),
                "buildings": self.count_layer_meshes("buildings"),
                "trees": self.count_layer_meshes("trees"),
                "pois": self.count_layer_meshes("pois"),
            },
            "total_meshes": self.count_all_meshes(),
            "total_triangles": self.count_triangles(),
        }

    def print_summary(self):
        summary = self.summary()

        print("")
        print("=" * 60)
        print("ATLAS SCENE SUMMARY")
        print("=" * 60)
        print(f"Mode          : {summary['metadata']['mode']}")
        print(f"Target size   : {summary['product']['target_size_mm']} mm")
        print(f"XY scale      : {summary['scale']['xy_scale']}")
        print(f"Z scale       : {summary['scale']['z_scale']}")
        print("-" * 60)

        for layer_name, count in summary["layers"].items():
            print(f"{layer_name:12}: {count}")

        print("-" * 60)
        print(f"Total meshes  : {summary['total_meshes']}")
        print(f"Triangles     : {summary['total_triangles']}")
        print("=" * 60)
        print("")
