"""
ATLAS Engine

Module : Terrain Engine
Version: 0.3
Status : Development

Purpose:
Generate solid printable terrain STL from DEM elevation data.
"""

from atlas_geocoder import geocode_address
from atlas_dem import get_dem_grid
from atlas_stl_writer import stl_writer_info


ADDRESS = "Frankfurt Römer"
GRID_SIZE = 16
MODEL_SIZE_MM = 200
BASE_THICKNESS_MM = 3
TERRAIN_MAX_HEIGHT_MM = 18
OUTPUT_PATH = "STL/ATLAS_TERRAIN_v0_3.stl"


class AtlasTerrainEngine:

    def __init__(self, address):
        self.address = address
        self.latitude = None
        self.longitude = None
        self.dem_grid = []
        self.vertices = []
        self.faces = []

    def resolve_location(self):
        self.latitude, self.longitude = geocode_address(self.address)

    def load_dem(self):
        self.dem_grid = get_dem_grid(
            self.latitude,
            self.longitude,
            grid_size=GRID_SIZE
        )

    def normalize_elevation(self, elevation, min_elevation, max_elevation):
        if max_elevation == min_elevation:
            return 0

        return ((elevation - min_elevation) / (max_elevation - min_elevation)) * TERRAIN_MAX_HEIGHT_MM

    def build_mesh(self):
        flat_elevations = [e for row in self.dem_grid for e in row]

        min_elevation = min(flat_elevations)
        max_elevation = max(flat_elevations)

        step = MODEL_SIZE_MM / (GRID_SIZE - 1)

        # Üst yüzey
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = col * step
                y = row * step
                z = BASE_THICKNESS_MM + self.normalize_elevation(
                    self.dem_grid[row][col],
                    min_elevation,
                    max_elevation
                )
                self.vertices.append((x, y, z))

        top_count = len(self.vertices)

        # Alt taban
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = col * step
                y = row * step
                z = 0
                self.vertices.append((x, y, z))

        # Üst yüzey üçgenleri
        for row in range(GRID_SIZE - 1):
            for col in range(GRID_SIZE - 1):
                tl = row * GRID_SIZE + col
                tr = tl + 1
                bl = (row + 1) * GRID_SIZE + col
                br = bl + 1

                self.faces.append((tl, bl, tr))
                self.faces.append((tr, bl, br))

        # Alt yüzey üçgenleri
        for row in range(GRID_SIZE - 1):
            for col in range(GRID_SIZE - 1):
                tl = top_count + row * GRID_SIZE + col
                tr = tl + 1
                bl = top_count + (row + 1) * GRID_SIZE + col
                br = bl + 1

                self.faces.append((tl, tr, bl))
                self.faces.append((tr, br, bl))

        # Yan duvarlar
        for i in range(GRID_SIZE - 1):
            # üst kenar
            self.add_side(i, i + 1, top_count + i, top_count + i + 1)

            # alt kenar
            a = (GRID_SIZE - 1) * GRID_SIZE + i
            b = a + 1
            self.add_side(a, b, top_count + a, top_count + b)

            # sol kenar
            a = i * GRID_SIZE
            b = (i + 1) * GRID_SIZE
            self.add_side(a, b, top_count + a, top_count + b)

            # sağ kenar
            a = i * GRID_SIZE + (GRID_SIZE - 1)
            b = (i + 1) * GRID_SIZE + (GRID_SIZE - 1)
            self.add_side(a, b, top_count + a, top_count + b)

    def add_side(self, top_a, top_b, bottom_a, bottom_b):
        self.faces.append((top_a, bottom_a, top_b))
        self.faces.append((top_b, bottom_a, bottom_b))

    def export_stl(self):
        stl_writer_info(
            self.vertices,
            self.faces,
            OUTPUT_PATH
        )

    def build(self):
        print()
        print("=" * 60)
        print("ATLAS TERRAIN ENGINE v0.3")
        print("=" * 60)

        print("Adres:", self.address)

        print("1. Konum çözülüyor...")
        self.resolve_location()
        print("Enlem :", self.latitude)
        print("Boylam:", self.longitude)
        print()

        print("2. DEM verisi alınıyor...")
        self.load_dem()
        print("DEM satır:", len(self.dem_grid))
        print("DEM sütun:", len(self.dem_grid[0]))
        print()

        print("3. Solid terrain mesh oluşturuluyor...")
        self.build_mesh()
        print("Vertices:", len(self.vertices))
        print("Faces   :", len(self.faces))
        print()

        print("4. STL export...")
        self.export_stl()

        print()
        print("ATLAS_TERRAIN_v0_3.stl OLUŞTU ✅")
        print("=" * 60)


def main():
    engine = AtlasTerrainEngine(ADDRESS)
    engine.build()


if __name__ == "__main__":
    main()