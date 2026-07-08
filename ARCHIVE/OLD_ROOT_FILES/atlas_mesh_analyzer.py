"""
ATLAS Engine 2.0

Module : Mesh Analyzer
Version: 1.0
Status : Quality Diagnosis

Purpose:
Analyze STL mesh problems and report where they occur.

This module does not clean or repair.
It only diagnoses.
"""

from collections import defaultdict
from stl import mesh


INPUT_STL = "STL/ATLAS_CORE_v0_3_BUILDINGS_ROADS.stl"
SAMPLE_LIMIT = 20


def load_stl_as_indexed_mesh(filename):
    print("STL yükleniyor:", filename)

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


class AtlasMeshAnalyzer:

    def __init__(self, points, faces):
        self.points = points
        self.faces = faces

    def find_degenerate_faces(self):
        results = []

        for face_index, face in enumerate(self.faces):
            a, b, c = face

            if a == b or b == c or a == c:
                results.append((face_index, face))

        return results

    def find_duplicate_faces(self):
        seen = {}
        duplicates = []

        for face_index, face in enumerate(self.faces):
            normalized = tuple(sorted(face))

            if normalized in seen:
                duplicates.append(
                    {
                        "face_index": face_index,
                        "duplicate_of": seen[normalized],
                        "face": face,
                    }
                )
            else:
                seen[normalized] = face_index

        return duplicates

    def get_edge_usage(self):
        edge_usage = defaultdict(list)

        for face_index, face in enumerate(self.faces):
            a, b, c = face

            edges = [
                tuple(sorted((a, b))),
                tuple(sorted((b, c))),
                tuple(sorted((c, a))),
            ]

            for edge in edges:
                edge_usage[edge].append(face_index)

        return edge_usage

    def find_open_edges(self):
        edge_usage = self.get_edge_usage()

        return [
            {
                "edge": edge,
                "faces": faces,
            }
            for edge, faces in edge_usage.items()
            if len(faces) == 1
        ]

    def find_non_manifold_edges(self):
        edge_usage = self.get_edge_usage()

        return [
            {
                "edge": edge,
                "faces": faces,
                "usage_count": len(faces),
            }
            for edge, faces in edge_usage.items()
            if len(faces) > 2
        ]

    def print_vertex(self, vertex_id):
        if vertex_id < 0 or vertex_id >= len(self.points):
            return "INVALID"

        return self.points[vertex_id]

    def report(self):
        degenerate_faces = self.find_degenerate_faces()
        duplicate_faces = self.find_duplicate_faces()
        open_edges = self.find_open_edges()
        non_manifold_edges = self.find_non_manifold_edges()

        print()
        print("=" * 70)
        print("ATLAS MESH ANALYZER v1.0")
        print("=" * 70)

        print("Nokta sayısı       :", len(self.points))
        print("Yüzey sayısı       :", len(self.faces))
        print("Bozuk üçgen        :", len(degenerate_faces))
        print("Tekrarlı yüzey     :", len(duplicate_faces))
        print("Açık kenar         :", len(open_edges))
        print("Non-manifold kenar :", len(non_manifold_edges))

        print()
        print("=" * 70)
        print("BOZUK ÜÇGEN ÖRNEKLERİ")
        print("=" * 70)

        for face_index, face in degenerate_faces[:SAMPLE_LIMIT]:
            print("Face:", face_index, "|", face)
            print("Vertices:")
            for vertex_id in face:
                print(" ", vertex_id, "=", self.print_vertex(vertex_id))
            print("-" * 40)

        if not degenerate_faces:
            print("Bozuk üçgen yok.")

        print()
        print("=" * 70)
        print("TEKRARLI YÜZEY ÖRNEKLERİ")
        print("=" * 70)

        for item in duplicate_faces[:SAMPLE_LIMIT]:
            print(
                "Face:",
                item["face_index"],
                "| Duplicate of:",
                item["duplicate_of"],
                "|",
                item["face"]
            )
            print("-" * 40)

        if not duplicate_faces:
            print("Tekrarlı yüzey yok.")

        print()
        print("=" * 70)
        print("AÇIK KENAR ÖRNEKLERİ")
        print("=" * 70)

        for item in open_edges[:SAMPLE_LIMIT]:
            edge = item["edge"]
            print("Edge:", edge, "| Used by faces:", item["faces"])
            print("Vertex A:", self.print_vertex(edge[0]))
            print("Vertex B:", self.print_vertex(edge[1]))
            print("-" * 40)

        if not open_edges:
            print("Açık kenar yok.")

        print()
        print("=" * 70)
        print("NON-MANIFOLD KENAR ÖRNEKLERİ")
        print("=" * 70)

        for item in non_manifold_edges[:SAMPLE_LIMIT]:
            edge = item["edge"]
            print(
                "Edge:",
                edge,
                "| Usage:",
                item["usage_count"],
                "| Faces:",
                item["faces"]
            )
            print("Vertex A:", self.print_vertex(edge[0]))
            print("Vertex B:", self.print_vertex(edge[1]))
            print("-" * 40)

        if not non_manifold_edges:
            print("Non-manifold kenar yok.")

        print()
        print("=" * 70)
        print("ANALYSIS COMPLETE")
        print("=" * 70)


def main():
    points, faces = load_stl_as_indexed_mesh(INPUT_STL)

    analyzer = AtlasMeshAnalyzer(points, faces)
    analyzer.report()


if __name__ == "__main__":
    main()