def scale_dem_grid(dem_grid, model_size=100, base_thickness=3, terrain_height=18):
    rows = len(dem_grid)
    cols = len(dem_grid[0])

    min_elevation = min(min(row) for row in dem_grid)
    max_elevation = max(max(row) for row in dem_grid)
    elevation_range = max_elevation - min_elevation

    x_step = model_size / (cols - 1)
    y_step = model_size / (rows - 1)

    scaled_grid = []

    for row_index, row in enumerate(dem_grid):
        scaled_row = []

        for col_index, elevation in enumerate(row):
            x = col_index * x_step
            y = row_index * y_step
            z = base_thickness + ((elevation - min_elevation) / elevation_range) * terrain_height

            scaled_row.append((x, y, z))

        scaled_grid.append(scaled_row)

    return scaled_grid


if __name__ == "__main__":
    test_dem_grid = [
        [94.0, 95.0, 91.0, 92.0],
        [102.0, 101.0, 100.0, 101.0],
        [106.0, 109.0, 106.0, 107.0],
        [106.0, 106.0, 103.0, 106.0],
    ]

    scaled = scale_dem_grid(test_dem_grid)

    for row in scaled:
        print(row)