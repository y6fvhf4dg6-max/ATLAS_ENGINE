"""
============================================================
ATLAS MESH CLEANER
Version : 1.2
Purpose : Normalize vertices and remove invalid mesh faces
============================================================
"""


class AtlasMeshCleaner:

    def __init__(self, points, faces, precision=5):
        self.points = points
        self.faces = faces
        self.precision = precision

    def normalize_vertices(self):
        new_points = []
        point_map = {}
        old_to_new = {}

        for old_index, point in enumerate(self.points):
            key = (
                round(float(point[0]), self.precision),
                round(float(point[1]), self.precision),
                round(float(point[2]), self.precision),
            )

            if key not in point_map:
                point_map[key] = len(new_points)
                new_points.append(key)

            old_to_new[old_index] = point_map[key]

        new_faces = []

        for face in self.faces:
            a, b, c = face
            new_faces.append(
                (
                    old_to_new[a],
                    old_to_new[b],
                    old_to_new[c],
                )
            )

        print("Original vertices       :", len(self.points))
        print("Normalized vertices     :", len(new_points))
        print("Merged duplicate verts  :", len(self.points) - len(new_points))

        return new_points, new_faces

    def remove_degenerate_faces(self, faces):
        cleaned_faces = []
        removed = 0

        for face in faces:
            a, b, c = face

            if a == b or b == c or a == c:
                removed += 1
                continue

            cleaned_faces.append(face)

        print("Degenerate faces removed:", removed)

        return cleaned_faces

    def remove_duplicate_faces(self, faces):
        cleaned_faces = []
        seen = set()
        removed = 0

        for face in faces:
            normalized = tuple(sorted(face))

            if normalized in seen:
                removed += 1
                continue

            seen.add(normalized)
            cleaned_faces.append(face)

        print("Duplicate faces removed :", removed)

        return cleaned_faces

    def clean_unused_vertices(self, points, faces):
        used_indices = set()

        for face in faces:
            used_indices.update(face)

        index_map = {}
        new_points = []

        for old_index, point in enumerate(points):
            if old_index in used_indices:
                index_map[old_index] = len(new_points)
                new_points.append(point)

        new_faces = []

        for face in faces:
            a, b, c = face
            new_faces.append(
                (
                    index_map[a],
                    index_map[b],
                    index_map[c],
                )
            )

        print("Unused vertices removed :", len(points) - len(new_points))

        return new_points, new_faces

    def clean(self):
        print()
        print("=" * 60)
        print("ATLAS MESH CLEANER v1.2")
        print("=" * 60)

        points, faces = self.normalize_vertices()
        faces = self.remove_degenerate_faces(faces)
        faces = self.remove_duplicate_faces(faces)
        points, faces = self.clean_unused_vertices(points, faces)

        print()
        print("Original points :", len(self.points))
        print("Clean points    :", len(points))
        print("Original faces  :", len(self.faces))
        print("Clean faces     :", len(faces))

        print("=" * 60)

        return points, faces


def main():
    print()
    print("=" * 60)
    print("ATLAS MESH CLEANER TEST")
    print("=" * 60)

    points = [
        (0, 0, 0),
        (1, 0, 0),
        (0, 1, 0),
        (0, 1, 0),  # duplicate vertex
    ]

    faces = [
        (0, 1, 2),
        (0, 1, 3),  # duplicate same geometry after vertex merge
        (0, 0, 2),  # degenerate
    ]

    cleaner = AtlasMeshCleaner(points, faces)
    cleaner.clean()


if __name__ == "__main__":
    main()