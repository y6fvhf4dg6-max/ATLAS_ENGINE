# CORE/atlas_foundation_sampler.py


class AtlasFoundationSampler:
    """
    ATLAS Foundation Sampler v0.1

    Görev:
    - Terrain mesh üzerindeki XY noktasından Z değeri okumak.
    - Foundation-first mimarisinde terrain'i tek gerçek zemin kabul etmek.

    Not:
    Bu sınıf bina üretmez.
    Bu sınıf foundation mesh üretmez.
    Sadece terrain yükseklik örnekler.
    """

    @staticmethod
    def terrain_z_at_xy(terrain_mesh, x, y):
        top_points = terrain_mesh.get("top_points")

        if not top_points:
            return 0.0

        grid_size = len(top_points)
        size_mm = terrain_mesh.get("metadata", {}).get("size_mm", 200.0)

        x = max(0.0, min(size_mm, x))
        y = max(0.0, min(size_mm, y))

        gx = (x / size_mm) * (grid_size - 1)
        gy = (y / size_mm) * (grid_size - 1)

        x0 = int(gx)
        y0 = int(gy)

        x1 = min(x0 + 1, grid_size - 1)
        y1 = min(y0 + 1, grid_size - 1)

        tx = gx - x0
        ty = gy - y0

        z00 = top_points[y0][x0][2]
        z10 = top_points[y0][x1][2]
        z01 = top_points[y1][x0][2]
        z11 = top_points[y1][x1][2]

        z0 = z00 * (1.0 - tx) + z10 * tx
        z1 = z01 * (1.0 - tx) + z11 * tx

        return z0 * (1.0 - ty) + z1 * ty

    @staticmethod
    def sample_bounds(terrain_mesh, bounds, sample_grid=5):
        if sample_grid < 2:
            sample_grid = 2

        values = []

        for row in range(sample_grid):
            y = bounds["min_y"] + (
                (bounds["max_y"] - bounds["min_y"]) * row / (sample_grid - 1)
            )

            for col in range(sample_grid):
                x = bounds["min_x"] + (
                    (bounds["max_x"] - bounds["min_x"]) * col / (sample_grid - 1)
                )

                values.append(
                    AtlasFoundationSampler.terrain_z_at_xy(
                        terrain_mesh=terrain_mesh,
                        x=x,
                        y=y,
                    )
                )

        return values
