# CORE/atlas_scene_fitter.py

"""
ATLAS Engine

Atlas Scene Fitter v1.2

Fits meshes into the printer bed.

New in v1.2:
- calculate_transform()
- apply_transform()
- fit() now uses the same reusable transform system

Purpose:
The same fit transform can be applied to additional layers
such as recessed roads, water, terrain, and future surface meshes.
"""


class AtlasSceneFitter:

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
    def calculate_transform(meshes, bed_width=256, bed_depth=256, margin=15):
        points = AtlasSceneFitter._collect_points(meshes)

        if not points:
            return {
                "min_x": 0.0,
                "min_y": 0.0,
                "min_z": 0.0,
                "scale": 1.0,
                "offset_x": 0.0,
                "offset_y": 0.0,
            }

        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)

        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)

        min_z = min(p[2] for p in points)

        width = max_x - min_x
        depth = max_y - min_y

        usable_width = bed_width - (margin * 2)
        usable_depth = bed_depth - (margin * 2)

        scale_x = usable_width / width if width else 1.0
        scale_y = usable_depth / depth if depth else 1.0

        fit_scale = min(scale_x, scale_y, 1.0)

        fitted_width = width * fit_scale
        fitted_depth = depth * fit_scale

        offset_x = (bed_width - fitted_width) / 2
        offset_y = (bed_depth - fitted_depth) / 2

        return {
            "min_x": min_x,
            "min_y": min_y,
            "min_z": min_z,
            "scale": fit_scale,
            "offset_x": offset_x,
            "offset_y": offset_y,
        }

    @staticmethod
    def _fit_point(point, transform):
        x, y, z = point

        return (
            ((x - transform["min_x"]) * transform["scale"]) + transform["offset_x"],
            ((y - transform["min_y"]) * transform["scale"]) + transform["offset_y"],
            z - transform["min_z"],
        )

    @staticmethod
    def apply_transform(meshes, transform):
        fitted_meshes = []

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
                new_mesh["bottom"].append(AtlasSceneFitter._fit_point(point, transform))

            for point in mesh.get("top", []):
                new_mesh["top"].append(AtlasSceneFitter._fit_point(point, transform))

            for wall in mesh.get("walls", []):
                new_wall = []

                for point in wall:
                    new_wall.append(AtlasSceneFitter._fit_point(point, transform))

                new_mesh["walls"].append(tuple(new_wall))

            for triangle in mesh.get("triangles", []):
                new_triangle = []

                for point in triangle:
                    new_triangle.append(AtlasSceneFitter._fit_point(point, transform))

                new_mesh["triangles"].append(tuple(new_triangle))

            fitted_meshes.append(new_mesh)

        return fitted_meshes

    @staticmethod
    def fit(meshes, bed_width=256, bed_depth=256, margin=15):
        transform = AtlasSceneFitter.calculate_transform(
            meshes,
            bed_width=bed_width,
            bed_depth=bed_depth,
            margin=margin,
        )

        return AtlasSceneFitter.apply_transform(meshes, transform)
