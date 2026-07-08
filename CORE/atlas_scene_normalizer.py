# CORE/atlas_scene_normalizer.py

"""
ATLAS Engine

Atlas Scene Normalizer v1.2

Moves meshes so the full scene starts at X=0, Y=0, Z=0.

New in v1.2:
- calculate_transform()
- apply_transform()
- normalize() now uses the same reusable transform system

Purpose:
The same normalization transform can be applied to additional layers
such as recessed roads, water, terrain, and future surface meshes.
"""


class AtlasSceneNormalizer:
    @staticmethod
    def _collect_points(meshes):
        points = []

        for mesh in meshes:
            points.extend(mesh.get("bottom", []))
            points.extend(mesh.get("top", []))

            for wall in mesh.get("walls", []):
                points.extend(wall)

            for triangle in mesh.get("triangles", []):
                points.extend(triangle)

        return points

    @staticmethod
    def calculate_transform(meshes):
        points = AtlasSceneNormalizer._collect_points(meshes)

        if not points:
            return {
                "min_x": 0.0,
                "min_y": 0.0,
                "min_z": 0.0,
            }

        return {
            "min_x": min(p[0] for p in points),
            "min_y": min(p[1] for p in points),
            "min_z": min(p[2] for p in points),
        }

    @staticmethod
    def _move_point(point, transform):
        x, y, z = point

        return (
            x - transform["min_x"],
            y - transform["min_y"],
            z - transform["min_z"],
        )

    @staticmethod
    def apply_transform(meshes, transform):
        transformed = []

        for mesh in meshes:
            new_mesh = {
                "bottom": [],
                "top": [],
                "walls": [],
                "triangles": [],
            }

            for key, value in mesh.items():
                if key not in new_mesh:
                    new_mesh[key] = value

            for point in mesh.get("bottom", []):
                new_mesh["bottom"].append(
                    AtlasSceneNormalizer._move_point(point, transform)
                )

            for point in mesh.get("top", []):
                new_mesh["top"].append(
                    AtlasSceneNormalizer._move_point(point, transform)
                )

            for wall in mesh.get("walls", []):
                new_wall = []

                for point in wall:
                    new_wall.append(AtlasSceneNormalizer._move_point(point, transform))

                new_mesh["walls"].append(tuple(new_wall))

            for triangle in mesh.get("triangles", []):
                new_triangle = []

                for point in triangle:
                    new_triangle.append(
                        AtlasSceneNormalizer._move_point(point, transform)
                    )

                new_mesh["triangles"].append(tuple(new_triangle))

            transformed.append(new_mesh)

        return transformed

    @staticmethod
    def normalize(meshes):
        transform = AtlasSceneNormalizer.calculate_transform(meshes)
        return AtlasSceneNormalizer.apply_transform(meshes, transform)
