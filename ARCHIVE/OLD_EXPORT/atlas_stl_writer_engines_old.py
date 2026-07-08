"""
ATLAS Engine

Module : STL Writer
Version: 0.1
Status : Development

Purpose:
Writes 3D mesh points and triangular faces into an ASCII STL file.
"""


def write_stl(points_3d, faces, output_path, solid_name="ATLAS_MODEL"):
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(f"solid {solid_name}\n")

        for face in faces:
            p1 = points_3d[face[0]]
            p2 = points_3d[face[1]]
            p3 = points_3d[face[2]]

            file.write("  facet normal 0 0 0\n")
            file.write("    outer loop\n")
            file.write(f"      vertex {p1[0]} {p1[1]} {p1[2]}\n")
            file.write(f"      vertex {p2[0]} {p2[1]} {p2[2]}\n")
            file.write(f"      vertex {p3[0]} {p3[1]} {p3[2]}\n")
            file.write("    endloop\n")
            file.write("  endfacet\n")

        file.write(f"endsolid {solid_name}\n")


def stl_writer_info(points_3d, faces, output_path):
    write_stl(
        points_3d,
        faces,
        output_path,
        solid_name="ATLAS_FIRST_BUILDING"
    )

    print("ATLAS STL Writer v0.1")
    print("STL dosyası oluşturuldu:", output_path)
    print("3D nokta sayısı:", len(points_3d))
    print("Yüzey üçgen sayısı:", len(faces))


if __name__ == "__main__":
    sample_points = [
        (0, 0, 0),
        (20, 0, 0),
        (20, 20, 0),
        (0, 20, 0),
        (0, 0, 10),
        (20, 0, 10),
        (20, 20, 10),
        (0, 20, 10),
    ]

    sample_faces = [
        (0, 1, 2),
        (0, 2, 3),
        (4, 6, 5),
        (4, 7, 6),
        (0, 1, 5),
        (0, 5, 4),
    ]

    stl_writer_info(
        sample_points,
        sample_faces,
        "STL/ATLAS_STL_WRITER_TEST.stl"
    )