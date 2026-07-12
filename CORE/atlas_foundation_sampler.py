# CORE/atlas_foundation_sampler.py


class AtlasFoundationSampler:
    """
    ATLAS Foundation Sampler v0.2

    Görev:
    - Terrain mesh üzerindeki XY noktasından Z değeri okumak.
    - Foundation-first mimarisinde terrain'i tek gerçek zemin kabul etmek.

    v0.2:
    - Dikdörtgen terrain boyutlarını destekler.
    - size_x_mm ve size_y_mm bulunmazsa eski size_mm değerini kullanır.

    Not:
    Bu sınıf bina üretmez.
    Bu sınıf foundation mesh üretmez.
    Sadece terrain yükseklik örnekler.
    """

    @staticmethod
    def terrain_z_at_xy(
        terrain_mesh,
        x,
        y,
    ):
        top_points = terrain_mesh.get("top_points")

        if not top_points:
            return 0.0

        row_count = len(top_points)
        column_count = len(top_points[0])

        metadata = terrain_mesh.get(
            "metadata",
            {},
        )

        legacy_size_mm = float(
            metadata.get(
                "size_mm",
                200.0,
            )
        )

        size_x_mm = float(
            metadata.get(
                "size_x_mm",
                legacy_size_mm,
            )
        )

        size_y_mm = float(
            metadata.get(
                "size_y_mm",
                legacy_size_mm,
            )
        )

        if size_x_mm <= 0.0:
            size_x_mm = legacy_size_mm

        if size_y_mm <= 0.0:
            size_y_mm = legacy_size_mm

        x = max(
            0.0,
            min(
                size_x_mm,
                x,
            ),
        )

        y = max(
            0.0,
            min(
                size_y_mm,
                y,
            ),
        )

        gx = x / size_x_mm * (column_count - 1)

        gy = y / size_y_mm * (row_count - 1)

        x0 = int(gx)
        y0 = int(gy)

        x1 = min(
            x0 + 1,
            column_count - 1,
        )

        y1 = min(
            y0 + 1,
            row_count - 1,
        )

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
    def sample_bounds(
        terrain_mesh,
        bounds,
        sample_grid=5,
    ):
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
