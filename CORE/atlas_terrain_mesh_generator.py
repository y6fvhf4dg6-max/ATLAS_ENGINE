# CORE/atlas_terrain_mesh_generator.py


class AtlasTerrainMeshGenerator:
    """
    ATLAS Terrain Mesh Generator v0.3

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

    v0.3:
    - Supports rectangular terrain dimensions
    - Keeps legacy square size_mm behavior
    - Supports independent size_x_mm and size_y_mm values
    """

    DEFAULT_GRID_SIZE = 25
    DEFAULT_BASE_Z = 0.80
    DEFAULT_BOTTOM_Z = 0.0

    @staticmethod
    def smooth_heights(
        heights,
        passes=1,
    ):
        if not heights:
            return []

        current = [
            [float(value) for value in row]
            for row in heights
        ]

        pass_count = max(
            0,
            int(passes),
        )

        for _ in range(pass_count):
            row_count = len(current)

            smoothed = []

            for row_index, row in enumerate(current):
                column_count = len(row)
                smoothed_row = []

                for column_index in range(column_count):
                    is_boundary = (
                        row_index == 0
                        or row_index == row_count - 1
                        or column_index == 0
                        or column_index == column_count - 1
                    )

                    if is_boundary:
                        smoothed_row.append(
                            current[row_index][column_index]
                        )
                        continue

                    neighbor_values = []

                    for row_offset in (-1, 0, 1):
                        neighbor_row = row_index + row_offset

                        if not 0 <= neighbor_row < row_count:
                            continue

                        neighbor_column_count = len(
                            current[neighbor_row]
                        )

                        for column_offset in (-1, 0, 1):
                            neighbor_column = (
                                column_index
                                + column_offset
                            )

                            if not (
                                0
                                <= neighbor_column
                                < neighbor_column_count
                            ):
                                continue

                            neighbor_values.append(
                                current[neighbor_row][neighbor_column]
                            )

                    smoothed_row.append(
                        sum(neighbor_values)
                        / len(neighbor_values)
                    )

                smoothed.append(smoothed_row)

            current = smoothed

        return current

    @staticmethod
    def build_height_grid(
        terrain_provider,
        bbox,
        grid_size=DEFAULT_GRID_SIZE,
    ):
        south, west, north, east = bbox

        heights = []
        missing_samples = []

        for row in range(grid_size):
            lat = south + ((north - south) * (row / (grid_size - 1)))

            row_values = []

            for col in range(grid_size):
                lon = west + ((east - west) * (col / (grid_size - 1)))

                height = terrain_provider.get_height(
                    lat,
                    lon,
                )

                if height is None:
                    missing_samples.append(
                        (
                            lat,
                            lon,
                        )
                    )

                    row_values.append(None)
                else:
                    row_values.append(float(height))

            heights.append(row_values)

        valid_heights = [
            height
            for row_values in heights
            for height in row_values
            if height is not None
        ]

        total_sample_count = grid_size * grid_size

        missing_sample_count = len(missing_samples)

        if not valid_heights:
            provider_name = terrain_provider.__class__.__name__

            raise RuntimeError(
                "Terrain height data unavailable. "
                f"Provider={provider_name}, "
                f"bbox={bbox}, "
                f"missing_samples="
                f"{missing_sample_count}/"
                f"{total_sample_count}. "
                "Required DEM/SRTM data must be "
                "downloaded before STL generation."
            )

        fallback_height = min(valid_heights)

        normalized_heights = []

        for row_values in heights:
            normalized_row = []

            for height in row_values:
                if height is None:
                    normalized_row.append(fallback_height)
                else:
                    normalized_row.append(height)

            normalized_heights.append(normalized_row)

        min_height = min(valid_heights)

        max_height = max(valid_heights)

        return {
            "heights": normalized_heights,
            "min_height_m": min_height,
            "max_height_m": max_height,
            "delta_height_m": (max_height - min_height),
            "sample_count": total_sample_count,
            "missing_sample_count": (missing_sample_count),
        }

    @staticmethod
    def build_points_from_grid(
        height_grid,
        size_mm=200.0,
        size_x_mm=None,
        size_y_mm=None,
        grid_size=DEFAULT_GRID_SIZE,
        z_scale=5500.0,
        base_z=DEFAULT_BASE_Z,
    ):
        heights = height_grid["heights"]
        min_height = height_grid["min_height_m"]

        if size_x_mm is None:
            size_x_mm = size_mm

        if size_y_mm is None:
            size_y_mm = size_mm

        points = []

        for row in range(grid_size):
            y = size_y_mm * (row / (grid_size - 1))

            point_row = []

            for col in range(grid_size):
                x = size_x_mm * (col / (grid_size - 1))

                height = heights[row][col]

                z = base_z + ((height - min_height) / z_scale) * 1000.0

                point_row.append(
                    (
                        x,
                        y,
                        z,
                    )
                )

            points.append(point_row)

        return points

    @staticmethod
    def build_surface_triangles(
        points,
        grid_size,
    ):
        triangles = []

        for row in range(grid_size - 1):
            for col in range(grid_size - 1):
                p00 = points[row][col]
                p10 = points[row][col + 1]
                p01 = points[row + 1][col]
                p11 = points[row + 1][col + 1]

                triangles.append(
                    (
                        p00,
                        p10,
                        p11,
                    )
                )

                triangles.append(
                    (
                        p00,
                        p11,
                        p01,
                    )
                )

        return triangles

    @staticmethod
    def build_bottom_points(
        size_mm,
        grid_size,
        bottom_z=DEFAULT_BOTTOM_Z,
        size_x_mm=None,
        size_y_mm=None,
    ):
        if size_x_mm is None:
            size_x_mm = size_mm

        if size_y_mm is None:
            size_y_mm = size_mm

        bottom_points = []

        for row in range(grid_size):
            y = size_y_mm * (row / (grid_size - 1))

            bottom_row = []

            for col in range(grid_size):
                x = size_x_mm * (col / (grid_size - 1))

                bottom_row.append(
                    (
                        x,
                        y,
                        bottom_z,
                    )
                )

            bottom_points.append(bottom_row)

        return bottom_points

    @staticmethod
    def build_bottom_triangles(
        bottom_points,
        grid_size,
    ):
        triangles = []

        for row in range(grid_size - 1):
            for col in range(grid_size - 1):
                p00 = bottom_points[row][col]
                p10 = bottom_points[row][col + 1]
                p01 = bottom_points[row + 1][col]
                p11 = bottom_points[row + 1][col + 1]

                triangles.append(
                    (
                        p00,
                        p11,
                        p10,
                    )
                )

                triangles.append(
                    (
                        p00,
                        p01,
                        p11,
                    )
                )

        return triangles

    @staticmethod
    def build_side_wall_triangles(
        top_points,
        bottom_points,
        grid_size,
    ):
        triangles = []

        # South and north walls
        for col in range(grid_size - 1):
            # South wall
            top_1 = top_points[0][col]
            top_2 = top_points[0][col + 1]
            bot_1 = bottom_points[0][col]
            bot_2 = bottom_points[0][col + 1]

            triangles.append(
                (
                    bot_1,
                    bot_2,
                    top_2,
                )
            )

            triangles.append(
                (
                    bot_1,
                    top_2,
                    top_1,
                )
            )

            # North wall
            top_1 = top_points[-1][col]
            top_2 = top_points[-1][col + 1]
            bot_1 = bottom_points[-1][col]
            bot_2 = bottom_points[-1][col + 1]

            triangles.append(
                (
                    bot_1,
                    top_2,
                    bot_2,
                )
            )

            triangles.append(
                (
                    bot_1,
                    top_1,
                    top_2,
                )
            )

        # West and east walls
        for row in range(grid_size - 1):
            # West wall
            top_1 = top_points[row][0]
            top_2 = top_points[row + 1][0]
            bot_1 = bottom_points[row][0]
            bot_2 = bottom_points[row + 1][0]

            triangles.append(
                (
                    bot_1,
                    top_2,
                    bot_2,
                )
            )

            triangles.append(
                (
                    bot_1,
                    top_1,
                    top_2,
                )
            )

            # East wall
            top_1 = top_points[row][-1]
            top_2 = top_points[row + 1][-1]
            bot_1 = bottom_points[row][-1]
            bot_2 = bottom_points[row + 1][-1]

            triangles.append(
                (
                    bot_1,
                    bot_2,
                    top_2,
                )
            )

            triangles.append(
                (
                    bot_1,
                    top_2,
                    top_1,
                )
            )

        return triangles

    @staticmethod
    def build_surface_mesh(
        terrain_provider,
        bbox,
        size_mm=200.0,
        size_x_mm=None,
        size_y_mm=None,
        grid_size=DEFAULT_GRID_SIZE,
        z_scale=5500.0,
        base_z=DEFAULT_BASE_Z,
        smoothing_passes=0,
    ):
        if size_x_mm is None:
            size_x_mm = size_mm

        if size_y_mm is None:
            size_y_mm = size_mm

        height_grid = AtlasTerrainMeshGenerator.build_height_grid(
            terrain_provider=terrain_provider,
            bbox=bbox,
            grid_size=grid_size,
        )

        smoothing_passes = max(
            0,
            int(smoothing_passes),
        )

        if smoothing_passes > 0:
            smoothed_heights = (
                AtlasTerrainMeshGenerator.smooth_heights(
                    heights=height_grid["heights"],
                    passes=smoothing_passes,
                )
            )

            flat_heights = [
                height
                for row in smoothed_heights
                for height in row
            ]

            min_height_m = min(flat_heights)
            max_height_m = max(flat_heights)

            height_grid["heights"] = smoothed_heights
            height_grid["min_height_m"] = min_height_m
            height_grid["max_height_m"] = max_height_m
            height_grid["delta_height_m"] = (
                max_height_m
                - min_height_m
            )

        top_points = AtlasTerrainMeshGenerator.build_points_from_grid(
            height_grid=height_grid,
            size_mm=size_mm,
            size_x_mm=size_x_mm,
            size_y_mm=size_y_mm,
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
                "size_x_mm": size_x_mm,
                "size_y_mm": size_y_mm,
                "z_scale": z_scale,
                "base_z": base_z,
                "bottom_z": None,
                "closed": False,
                "min_height_m": height_grid["min_height_m"],
                "max_height_m": height_grid["max_height_m"],
                "delta_height_m": height_grid["delta_height_m"],
                "smoothing_passes": smoothing_passes,
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
        size_x_mm=None,
        size_y_mm=None,
        grid_size=DEFAULT_GRID_SIZE,
        z_scale=5500.0,
        base_z=DEFAULT_BASE_Z,
        bottom_z=DEFAULT_BOTTOM_Z,
        smoothing_passes=0,
    ):
        if size_x_mm is None:
            size_x_mm = size_mm

        if size_y_mm is None:
            size_y_mm = size_mm

        surface_mesh = AtlasTerrainMeshGenerator.build_surface_mesh(
            terrain_provider=terrain_provider,
            bbox=bbox,
            size_mm=size_mm,
            size_x_mm=size_x_mm,
            size_y_mm=size_y_mm,
            grid_size=grid_size,
            z_scale=z_scale,
            base_z=base_z,
            smoothing_passes=smoothing_passes,
        )

        top_points = surface_mesh["top_points"]

        bottom_points = AtlasTerrainMeshGenerator.build_bottom_points(
            size_mm=size_mm,
            size_x_mm=size_x_mm,
            size_y_mm=size_y_mm,
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
