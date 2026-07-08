# CORE/atlas_foundation_engine.py


class AtlasFoundationEngine:
    """
    ATLAS Foundation Engine v0.1

    Görev:
    Binaların eğimli terrain üzerinde havada kalmasını önlemek.

    v0.1:
    - Her bina mesh'i için XY footprint bounds hesaplar.
    - Footprint altında terrain yüksekliğini örnekler.
    - En düşük güvenli terrain z değerini seçer.
    - Binayı terrain içine hafif gömecek offset döndürür.

    Not:
    Bu sürüm platform mesh üretmez.
    Sadece bina Z yerleşimi için güvenli foundation kotu hesaplar.
    """

    DEFAULT_EMBED_DEPTH_MM = 0.30
    DEFAULT_SAMPLE_GRID = 3

    @staticmethod
    def calculate_foundation_z(
        mesh,
        terrain_mesh,
        scene_origin_x,
        scene_origin_y,
        embed_depth_mm=DEFAULT_EMBED_DEPTH_MM,
        sample_grid=DEFAULT_SAMPLE_GRID,
    ):
        bounds = AtlasFoundationEngine._mesh_xy_bounds(mesh)

        if bounds is None:
            return 0.0

        sample_points = AtlasFoundationEngine._sample_points_from_bounds(
            bounds=bounds,
            sample_grid=sample_grid,
        )

        terrain_values = []

        for x, y in sample_points:
            local_x = x - scene_origin_x
            local_y = y - scene_origin_y

            terrain_z = AtlasFoundationEngine._terrain_z_at_xy(
                terrain_mesh=terrain_mesh,
                x=local_x,
                y=local_y,
            )

            terrain_values.append(terrain_z)

        if not terrain_values:
            return 0.0

        terrain_values = sorted(terrain_values)

        bounds_width = bounds["max_x"] - bounds["min_x"]
        bounds_depth = bounds["max_y"] - bounds["min_y"]
        bounds_area = bounds_width * bounds_depth

        if bounds_area >= 80.0:
            index = int(len(terrain_values) * 0.50)
            index = min(index, len(terrain_values) - 1)
            selected_terrain_z = terrain_values[index]
        else:
            selected_terrain_z = min(terrain_values)

        foundation_z = selected_terrain_z - embed_depth_mm

        if foundation_z < 0.0:
            foundation_z = 0.0

        return foundation_z

    @staticmethod
    def _mesh_xy_bounds(mesh):
        points = []

        points.extend(mesh.get("bottom", []))
        points.extend(mesh.get("top", []))

        for triangle in mesh.get("triangles", []):
            points.extend(triangle)

        if not points:
            return None

        xs = [point[0] for point in points]
        ys = [point[1] for point in points]

        return {
            "min_x": min(xs),
            "max_x": max(xs),
            "min_y": min(ys),
            "max_y": max(ys),
        }

    @staticmethod
    def _sample_points_from_bounds(bounds, sample_grid):
        points = []

        if sample_grid < 2:
            sample_grid = 2

        for row in range(sample_grid):
            y = bounds["min_y"] + (
                (bounds["max_y"] - bounds["min_y"]) * row / (sample_grid - 1)
            )

            for col in range(sample_grid):
                x = bounds["min_x"] + (
                    (bounds["max_x"] - bounds["min_x"]) * col / (sample_grid - 1)
                )

                points.append((x, y))

        return points

    @staticmethod
    def _terrain_z_at_xy(terrain_mesh, x, y):
        top_points = terrain_mesh.get("top_points")

        if not top_points:
            return 0.0

        grid_size = len(top_points)
        size_mm = terrain_mesh.get("metadata", {}).get("size_mm", 200.0)

        x = max(0.0, min(size_mm, x))
        y = max(0.0, min(size_mm, y))

        col = round((x / size_mm) * (grid_size - 1))
        row = round((y / size_mm) * (grid_size - 1))

        col = max(0, min(grid_size - 1, col))
        row = max(0, min(grid_size - 1, row))

        return top_points[row][col][2]
