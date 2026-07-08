def build_mesh(scaled_grid, base_height=0):
    points = []
    triangles = []

    rows = len(scaled_grid)
    cols = len(scaled_grid[0])

    # Üst yüzey noktaları
    for row in scaled_grid:
        for point in row:
            points.append(point)

    top_point_count = len(points)

    # Alt taban noktaları
    for row in scaled_grid:
        for x, y, z in row:
            points.append((x, y, base_height))

    # Üst yüzey üçgenleri
    for row in range(rows - 1):
        for col in range(cols - 1):
            top_left = row * cols + col
            top_right = top_left + 1
            bottom_left = (row + 1) * cols + col
            bottom_right = bottom_left + 1

            triangles.append((top_left, bottom_left, top_right))
            triangles.append((top_right, bottom_left, bottom_right))

    # Alt yüzey üçgenleri
    for row in range(rows - 1):
        for col in range(cols - 1):
            top_left = top_point_count + row * cols + col
            top_right = top_left + 1
            bottom_left = top_point_count + (row + 1) * cols + col
            bottom_right = bottom_left + 1

            triangles.append((top_left, top_right, bottom_left))
            triangles.append((top_right, bottom_right, bottom_left))

    # Sol ve sağ yan duvarlar
    for row in range(rows - 1):
        # sol
        top_a = row * cols
        top_b = (row + 1) * cols
        base_a = top_point_count + row * cols
        base_b = top_point_count + (row + 1) * cols

        triangles.append((top_a, base_a, top_b))
        triangles.append((top_b, base_a, base_b))

        # sağ
        top_a = row * cols + (cols - 1)
        top_b = (row + 1) * cols + (cols - 1)
        base_a = top_point_count + row * cols + (cols - 1)
        base_b = top_point_count + (row + 1) * cols + (cols - 1)

        triangles.append((top_a, top_b, base_a))
        triangles.append((top_b, base_b, base_a))

    # Ön ve arka yan duvarlar
    for col in range(cols - 1):
        # ön
        top_a = col
        top_b = col + 1
        base_a = top_point_count + col
        base_b = top_point_count + col + 1

        triangles.append((top_a, top_b, base_a))
        triangles.append((top_b, base_b, base_a))

        # arka
        top_a = (rows - 1) * cols + col
        top_b = (rows - 1) * cols + col + 1
        base_a = top_point_count + (rows - 1) * cols + col
        base_b = top_point_count + (rows - 1) * cols + col + 1

        triangles.append((top_a, base_a, top_b))
        triangles.append((top_b, base_a, base_b))

    return points, triangles


if __name__ == "__main__":
    test_scaled_grid = [
        [(0.0, 0.0, 6.0), (33.33, 0.0, 7.0), (66.66, 0.0, 3.0), (100.0, 0.0, 4.0)],
        [(0.0, 33.33, 14.0), (33.33, 33.33, 13.0), (66.66, 33.33, 12.0), (100.0, 33.33, 13.0)],
        [(0.0, 66.66, 18.0), (33.33, 66.66, 21.0), (66.66, 66.66, 18.0), (100.0, 66.66, 19.0)],
        [(0.0, 100.0, 18.0), (33.33, 100.0, 18.0), (66.66, 100.0, 15.0), (100.0, 100.0, 18.0)],
    ]

    points, triangles = build_mesh(test_scaled_grid)

    print("Toplam nokta sayısı:", len(points))
    print("Toplam üçgen sayısı:", len(triangles))
    print("İlk nokta:", points[0])
    print("Son nokta:", points[-1])