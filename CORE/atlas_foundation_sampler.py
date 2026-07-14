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
    def sample_polygon(
        terrain_mesh,
        footprint_points,
        sample_grid=5,
    ):
        if not footprint_points or len(footprint_points) < 3:
            return []

        if sample_grid < 2:
            sample_grid = 2

        xs = [point[0] for point in footprint_points]
        ys = [point[1] for point in footprint_points]

        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)

        values = []

        for row in range(sample_grid):
            y = min_y + (
                (max_y - min_y)
                * row
                / (sample_grid - 1)
            )

            for col in range(sample_grid):
                x = min_x + (
                    (max_x - min_x)
                    * col
                    / (sample_grid - 1)
                )

                if not AtlasFoundationSampler._point_in_polygon(
                    x=x,
                    y=y,
                    polygon=footprint_points,
                ):
                    continue

                values.append(
                    AtlasFoundationSampler.terrain_z_at_xy(
                        terrain_mesh=terrain_mesh,
                        x=x,
                        y=y,
                    )
                )

        return values

    @staticmethod
    def _point_in_polygon(
        x,
        y,
        polygon,
    ):
        inside = False
        count = len(polygon)
        previous_index = count - 1

        for index in range(count):
            x1, y1 = polygon[index]
            x2, y2 = polygon[previous_index]

            if AtlasFoundationSampler._point_on_segment(
                x=x,
                y=y,
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
            ):
                return True

            crosses = (
                (y1 > y) != (y2 > y)
                and x
                < (
                    (x2 - x1)
                    * (y - y1)
                    / ((y2 - y1) or 1e-15)
                    + x1
                )
            )

            if crosses:
                inside = not inside

            previous_index = index

        return inside

    @staticmethod
    def _point_on_segment(
        x,
        y,
        x1,
        y1,
        x2,
        y2,
        tolerance=1e-9,
    ):
        cross = (
            (x - x1) * (y2 - y1)
            - (y - y1) * (x2 - x1)
        )

        if abs(cross) > tolerance:
            return False

        return (
            min(x1, x2) - tolerance
            <= x
            <= max(x1, x2) + tolerance
            and min(y1, y2) - tolerance
            <= y
            <= max(y1, y2) + tolerance
        )


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
