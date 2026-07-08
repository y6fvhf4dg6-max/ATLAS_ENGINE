"""
ATLAS Engine

Module : Terrain Sampler
Version: 1.0
Status : Development

Purpose:
Sample terrain height at any x/y model coordinate.
Used by roads, rivers, parks, buildings and future detail layers.
"""


class AtlasTerrainSampler:

    def __init__(self, terrain_vertices, grid_size, model_size_mm):
        self.terrain_vertices = terrain_vertices
        self.grid_size = grid_size
        self.model_size_mm = model_size_mm
        self.step = model_size_mm / (grid_size - 1)

    def clamp(self, value, min_value, max_value):
        return max(min_value, min(value, max_value))

    def get_vertex_height(self, row, col):
        row = self.clamp(row, 0, self.grid_size - 1)
        col = self.clamp(col, 0, self.grid_size - 1)

        index = row * self.grid_size + col

        if index < 0 or index >= len(self.terrain_vertices):
            return 0.0

        return self.terrain_vertices[index][2]

    def get_height_nearest(self, x, y):
        col = round(x / self.step)
        row = round(y / self.step)

        return self.get_vertex_height(row, col)

    def get_height_bilinear(self, x, y):
        # x/y değerlerini terrain sınırları içinde tut
        x = self.clamp(x, 0.0, self.model_size_mm)
        y = self.clamp(y, 0.0, self.model_size_mm)

        grid_x = x / self.step
        grid_y = y / self.step

        col0 = int(grid_x)
        row0 = int(grid_y)

        col1 = min(col0 + 1, self.grid_size - 1)
        row1 = min(row0 + 1, self.grid_size - 1)

        tx = grid_x - col0
        ty = grid_y - row0

        h00 = self.get_vertex_height(row0, col0)
        h10 = self.get_vertex_height(row0, col1)
        h01 = self.get_vertex_height(row1, col0)
        h11 = self.get_vertex_height(row1, col1)

        h0 = h00 * (1 - tx) + h10 * tx
        h1 = h01 * (1 - tx) + h11 * tx

        return h0 * (1 - ty) + h1 * ty

    def get_height(self, x, y):
        return self.get_height_bilinear(x, y)


def main():
    print("=" * 60)
    print("ATLAS TERRAIN SAMPLER v1.0")
    print("=" * 60)
    print("Hazır.")
    print("Sampling method: bilinear")
    print("=" * 60)


if __name__ == "__main__":
    main()