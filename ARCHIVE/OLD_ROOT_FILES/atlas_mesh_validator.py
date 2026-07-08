"""
ATLAS Engine 2.0

Module : Mesh Validator
Version: 2.1
Status : Quality Control

Purpose:
Validate multiple ATLAS STL files layer by layer.
"""

from collections import defaultdict
from stl import mesh


INPUT_STL_FILES = [
    ("Terrain only", "STL/ATLAS_TERRAIN_v0_3.stl"),
    ("Buildings + Terrain", "STL/ATLAS_CORE_v0_2_BUILDINGS.stl"),
    ("Roads only", "STL/ATLAS_ROADS_v0_4_TERRAIN.stl"),
    ("Final Scene", "STL/ATLAS_CORE_v0_3_BUILDINGS_ROADS.stl"),
    ("Final Cleaned v0.4", "STL/ATLAS_CORE_v0_4_CLEANED.stl"),
]


class AtlasMeshValidator:

    def __init__(self, points, faces):
        self.points = points
        self.faces = faces

    def count_degenerate_faces(self):
        count = 0

        for face in self.faces:
            a, b, c = face

            if a == b or b == c or a == c:
                count += 1

        return count

    def count_duplicate_faces(self):
        seen = set()
        duplicate_count = 0

        for face in self.faces:
            normalized = tuple(sorted(face))

            if normalized in seen:
                duplicate_count += 1
            else:
                seen.add(normalized)

        return duplicate_count

    def get_edge_usage(self):
        edge_usage = defaultdict(int)

        for face in self.faces:
            a, b, c = face

            edges = [
                tuple(sorted((a, b))),
                tuple(sorted((b, c))),
                tuple(sorted((c, a))),
            ]

            for edge in edges:
                edge_usage[edge] += 1

        return edge_usage

    def get_open_edges(self):
        edge_usage = self.get_edge_usage()

        return [
            edge
            for edge, count in edge_usage.items()
            if count == 1
        ]

    def count_open_edges(self):
        return len(self.get_open_edges())

    def count_non_manifold_edges(self):
        edge_usage = self.get_edge_usage()

        non_manifold_edges = [
            edge
            for edge, count in edge_usage.items()
            if count > 2
        ]

        return len(non_manifold_edges)

    def validate(self):
        return {
            "points": len(self.points),
            "faces": len(self.faces),
            "degenerate_faces": self.count_degenerate_faces(),
            "duplicate_faces": self.count_duplicate_faces(),
            "open_edges": self.count_open_edges(),
            "non_manifold_edges": self.count_non_manifold_edges(),
        }


def load_stl_as_indexed_mesh(filename):
    stl_mesh = mesh.Mesh.from_file(filename)

    points = []
    faces = []
    point_index = {}

    def get_point_id(point):
        key = (
            round(float(point[0]), 5),
            round(float(point[1]), 5),
            round(float(point[2]), 5),
        )

        if key not in point_index:
            point_index[key] = len(points)
            points.append(key)

        return point_index[key]

    for triangle in stl_mesh.vectors:
        face = (
            get_point_id(triangle[0]),
            get_point_id(triangle[1]),
            get_point_id(triangle[2]),
        )

        faces.append(face)

    return points, faces


def print_validation_report(name, filename):
    print()
    print("=" * 70)
    print("LAYER:", name)
    print("FILE :", filename)
    print("=" * 70)

    try:
        points, faces = load_stl_as_indexed_mesh(filename)

        validator = AtlasMeshValidator(points, faces)
        result = validator.validate()

        print("Nokta sayısı          :", result["points"])
        print("Yüzey sayısı          :", result["faces"])
        print("Bozuk üçgen           :", result["degenerate_faces"])
        print("Tekrarlı yüzey        :", result["duplicate_faces"])
        print("Açık kenar            :", result["open_edges"])
        print("Non-manifold kenar    :", result["non_manifold_edges"])

        if (
            result["degenerate_faces"] == 0
            and result["duplicate_faces"] == 0
            and result["open_edges"] == 0
            and result["non_manifold_edges"] == 0
        ):
            print("Mesh durumu           : GEÇERLİ ✅")
        else:
            print("Mesh durumu           : KONTROL GEREKİYOR ⚠️")

    except FileNotFoundError:
        print("Dosya bulunamadı.")
    except Exception as error:
        print("Hata:", error)


def main():
    print()
    print("=" * 70)
    print("ATLAS MESH VALIDATOR v2.1 - LAYER REPORT")
    print("=" * 70)

    for name, filename in INPUT_STL_FILES:
        print_validation_report(name, filename)

    print()
    print("=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()