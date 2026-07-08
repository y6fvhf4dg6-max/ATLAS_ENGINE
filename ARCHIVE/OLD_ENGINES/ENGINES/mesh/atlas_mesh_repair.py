"""
ATLAS Engine 2.0

Module : Mesh Repair
Version: 0.1
Status : Development

Purpose:
Repair mesh integrity problems before STL export.
First target:
- detect open edges
- prepare automatic repair pipeline
"""

from collections import defaultdict


class AtlasMeshRepair:
    def __init__(self, points, faces):
        self.points = points
        self.faces = faces

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

    def report(self):
        open_edges = self.get_open_edges()

        print("=" * 60)
        print("ATLAS MESH REPAIR REPORT")
        print("=" * 60)
        print("Points     :", len(self.points))
        print("Faces      :", len(self.faces))
        print("Open edges :", len(open_edges))
        print("=" * 60)

        return {
            "points": len(self.points),
            "faces": len(self.faces),
            "open_edges": len(open_edges),
        }

    def repair(self):
        """
        Placeholder for future automatic repair.
        For now, only returns original mesh safely.
        """
        print("Mesh repair v0.1: automatic repair not active yet.")
        return self.points, self.faces