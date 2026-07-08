import numpy as np
from stl import mesh


def export_stl(points, triangles, output_path):
    terrain_mesh = mesh.Mesh(np.zeros(len(triangles), dtype=mesh.Mesh.dtype))

    for i, triangle in enumerate(triangles):
        for j in range(3):
            terrain_mesh.vectors[i][j] = points[triangle[j]]

    terrain_mesh.save(output_path)

    return output_path


if __name__ == "__main__":
    test_points = [
        (0, 0, 94.0),
        (0, 1, 95.0),
        (0, 2, 91.0),
        (0, 3, 92.0),
        (1, 0, 102.0),
        (1, 1, 101.0),
        (1, 2, 100.0),
        (1, 3, 101.0),
        (2, 0, 106.0),
        (2, 1, 109.0),
        (2, 2, 106.0),
        (2, 3, 107.0),
        (3, 0, 106.0),
        (3, 1, 106.0),
        (3, 2, 103.0),
        (3, 3, 106.0),
    ]

    test_triangles = [
        (0, 4, 1),
        (1, 4, 5),
        (1, 5, 2),
        (2, 5, 6),
        (2, 6, 3),
        (3, 6, 7),
        (4, 8, 5),
        (5, 8, 9),
        (5, 9, 6),
        (6, 9, 10),
        (6, 10, 7),
        (7, 10, 11),
        (8, 12, 9),
        (9, 12, 13),
        (9, 13, 10),
        (10, 13, 14),
        (10, 14, 11),
        (11, 14, 15),
    ]

    output_file = export_stl(
        test_points,
        test_triangles,
        "STL/test_export_from_function.stl"
    )

    print("STL oluşturuldu:", output_file)