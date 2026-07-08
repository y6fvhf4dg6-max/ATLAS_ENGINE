"""
ATLAS Engine

Module : Extrusion Engine
Version: 0.1
Status : Development

Purpose:
Converts a 2D triangle mesh into a simple 3D extruded building mesh.
"""


def extrude_mesh(vertices, triangles, height_mm):
    
    if len(vertices) > 1 and tuple(vertices[0]) == tuple(vertices[-1]):
        vertices = vertices[:-1]
    points_3d = []    
    # Alt yüzey noktaları
    for x, y in vertices:
        points_3d.append((float(x), float(y), 0.0))

    # Üst yüzey noktaları
    for x, y in vertices:
        points_3d.append((float(x), float(y), float(height_mm)))

    vertex_count = len(vertices)
    faces = []

    # Alt yüzey
    for i in range(0, len(triangles), 3):
        faces.append((
            int(triangles[i]),
            int(triangles[i + 1]),
            int(triangles[i + 2]),
        ))

    # Üst yüzey
    for i in range(0, len(triangles), 3):
        faces.append((
            int(triangles[i]) + vertex_count,
            int(triangles[i + 2]) + vertex_count,
            int(triangles[i + 1]) + vertex_count,
        ))

    # Yan yüzeyler
    for i in range(vertex_count):
        next_i = (i + 1) % vertex_count

        bottom_1 = i
        bottom_2 = next_i
        top_1 = i + vertex_count
        top_2 = next_i + vertex_count

        faces.append((bottom_1, bottom_2, top_2))
        faces.append((bottom_1, top_2, top_1))

    return points_3d, faces


def extrusion_info(vertices, triangles, height_mm):
    points_3d, faces = extrude_mesh(vertices, triangles, height_mm)

    print("ATLAS Extrusion Engine v0.1")
    print("Yükseklik:", height_mm, "mm")
    print("3D nokta sayısı:", len(points_3d))
    print("Yüzey üçgen sayısı:", len(faces))

    return points_3d, faces


if __name__ == "__main__":
    sample_vertices = [
        (20, 20),
        (180, 20),
        (180, 180),
        (20, 180),
    ]

    sample_triangles = [0, 1, 2, 0, 2, 3]

    extrusion_info(
        sample_vertices,
        sample_triangles,
        10
    )