# CORE/atlas_terrain_mesh_generator.py


class AtlasTerrainMeshGenerator:
    """
    ATLAS Terrain Mesh Generator v0.2

    Produces terrain meshes from any terrain provider.

    Provider can be:
    - Flat
    - SRTM
    - Copernicus
    - LiDAR

    v0.2:
    - Builds height grid once
    - Builds surface mesh
    - Builds closed printable terrain slab
    - Keeps metadata for future road/building/water placement
    """

    DEFAULT_GRID_SIZE = 25
    DEFAULT_BASE_Z = 0.80
    DEFAULT_BOTTOM_Z = 0.0

    @staticmethod
    def build_height_grid(terrain_provider, bbox, grid_size=DEFAULT_GRID_SIZE):
        south, west, north, east = bbox

        heights = []

        for row in range(grid_size):
            lat = south + (north - south) * (row / (grid_size - 1))
            row_values = []

            for col in range(grid_size):
                lon = west + (east - west) * (col / (grid_size - 1))
                height = terrain_provider.get_height(lat, lon)

                if height is None:
                    height = 0.0

                row_values.append(height)

            heights.append(row_values)

        flat_heights = [height for row_values in heights for height in row_values]

        return {
            "heights": heights,
            "min_height_m": min(flat_heights),
            "max_height_m": max(flat_heights),
            "delta_height_m": max(flat_heights) - min(flat_heights),
        }

    @staticmethod
    def build_points_from_grid(
        height_grid,
        size_mm=200.0,
        grid_size=DEFAULT_GRID_SIZE,
        z_scale=5500.0,
        base_z=DEFAULT_BASE_Z,
    ):
        heights = height_grid["heights"]
        min_height = height_grid["min_height_m"]

        points = []

        for row in range(grid_size):
            y = size_mm * (row / (grid_size - 1))
            point_row = []

            for col in range(grid_size):
                x = size_mm * (col / (grid_size - 1))

                height = heights[row][col]
                z = base_z + ((height - min_height) / z_scale) * 1000.0

                point_row.append((x, y, z))

            points.append(point_row)

        return points

    @staticmethod
    def build_surface_triangles(points, grid_size):
        triangles = []

        for row in range(grid_size - 1):
            for col in range(grid_size - 1):
                p00 = points[row][col]
                p10 = points[row][col + 1]
                p01 = points[row + 1][col]
                p11 = points[row + 1][col + 1]

                triangles.append((p00, p10, p11))
                triangles.append((p00, p11, p01))

        return triangles

    @staticmethod
    def build_bottom_points(size_mm, grid_size, bottom_z=DEFAULT_BOTTOM_Z):
        bottom_points = []

        for row in range(grid_size):
            y = size_mm * (row / (grid_size - 1))
            bottom_row = []

            for col in range(grid_size):
                x = size_mm * (col / (grid_size - 1))
                bottom_row.append((x, y, bottom_z))

            bottom_points.append(bottom_row)

        return bottom_points

    @staticmethod
    def build_bottom_triangles(bottom_points, grid_size):
        triangles = []

        for row in range(grid_size - 1):
            for col in range(grid_size - 1):
                p00 = bottom_points[row][col]
                p10 = bottom_points[row][col + 1]
                p01 = bottom_points[row + 1][col]
                p11 = bottom_points[row + 1][col + 1]

                triangles.append((p00, p11, p10))
                triangles.append((p00, p01, p11))

        return triangles

    @staticmethod
    def build_side_wall_triangles(top_points, bottom_points, grid_size):
        triangles = []

        # South and north walls
        for col in range(grid_size - 1):
            # south
            top_1 = top_points[0][col]
            top_2 = top_points[0][col + 1]
            bot_1 = bottom_points[0][col]
            bot_2 = bottom_points[0][col + 1]

            triangles.append((bot_1, bot_2, top_2))
            triangles.append((bot_1, top_2, top_1))

            # north
            top_1 = top_points[-1][col]
            top_2 = top_points[-1][col + 1]
            bot_1 = bottom_points[-1][col]
            bot_2 = bottom_points[-1][col + 1]

            triangles.append((bot_1, top_2, bot_2))
            triangles.append((bot_1, top_1, top_2))

        # West and east walls
        for row in range(grid_size - 1):
            # west
            top_1 = top_points[row][0]
            top_2 = top_points[row + 1][0]
            bot_1 = bottom_points[row][0]
            bot_2 = bottom_points[row + 1][0]

            triangles.append((bot_1, top_2, bot_2))
            triangles.append((bot_1, top_1, top_2))

            # east
            top_1 = top_points[row][-1]
            top_2 = top_points[row + 1][-1]
            bot_1 = bottom_points[row][-1]
            bot_2 = bottom_points[row + 1][-1]

            triangles.append((bot_1, bot_2, top_2))
            triangles.append((bot_1, top_2, top_1))

        return triangles

    @staticmethod
    def build_surface_mesh(
        terrain_provider,
        bbox,
        size_mm=200.0,
        grid_size=DEFAULT_GRID_SIZE,
        z_scale=5500.0,
        base_z=DEFAULT_BASE_Z,
    ):
        height_grid = AtlasTerrainMeshGenerator.build_height_grid(
            terrain_provider=terrain_provider,
            bbox=bbox,
            grid_size=grid_size,
        )

        top_points = AtlasTerrainMeshGenerator.build_points_from_grid(
            height_grid=height_grid,
            size_mm=size_mm,
            grid_size=grid_size,
            z_scale=z_scale,
            base_z=base_z,
        )

        triangles = AtlasTerrainMeshGenerator.build_surface_triangles(
            points=top_points,
            grid_size=grid_size,
        )

        return {
            "type": "terrain_surface",
            "triangles": triangles,
            "metadata": {
                "bbox": bbox,
                "grid_size": grid_size,
                "size_mm": size_mm,
                "z_scale": z_scale,
                "base_z": base_z,
                "bottom_z": None,
                "closed": False,
                "min_height_m": height_grid["min_height_m"],
                "max_height_m": height_grid["max_height_m"],
                "delta_height_m": height_grid["delta_height_m"],
                "triangle_count": len(triangles),
            },
            "grid": height_grid,
            "top_points": top_points,
        }

    @staticmethod
    def build_closed_slab_mesh(
        terrain_provider,
        bbox,
        size_mm=200.0,
        grid_size=DEFAULT_GRID_SIZE,
        z_scale=5500.0,
        base_z=DEFAULT_BASE_Z,
        bottom_z=DEFAULT_BOTTOM_Z,
    ):
        surface_mesh = AtlasTerrainMeshGenerator.build_surface_mesh(
            terrain_provider=terrain_provider,
            bbox=bbox,
            size_mm=size_mm,
            grid_size=grid_size,
            z_scale=z_scale,
            base_z=base_z,
        )

        top_points = surface_mesh["top_points"]

        bottom_points = AtlasTerrainMeshGenerator.build_bottom_points(
            size_mm=size_mm,
            grid_size=grid_size,
            bottom_z=bottom_z,
        )

        triangles = []

        triangles.extend(
            AtlasTerrainMeshGenerator.build_surface_triangles(
                points=top_points,
                grid_size=grid_size,
            )
        )

        triangles.extend(
            AtlasTerrainMeshGenerator.build_bottom_triangles(
                bottom_points=bottom_points,
                grid_size=grid_size,
            )
        )

        triangles.extend(
            AtlasTerrainMeshGenerator.build_side_wall_triangles(
                top_points=top_points,
                bottom_points=bottom_points,
                grid_size=grid_size,
            )
        )

        metadata = dict(surface_mesh["metadata"])
        metadata["bottom_z"] = bottom_z
        metadata["closed"] = True
        metadata["triangle_count"] = len(triangles)

        return {
            "type": "terrain_closed_slab",
            "triangles": triangles,
            "metadata": metadata,
            "grid": surface_mesh["grid"],
            "top_points": top_points,
            "bottom_points": bottom_points,
        }
