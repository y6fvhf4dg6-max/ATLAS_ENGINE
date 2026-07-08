# CORE/atlas_scene_preparation_pipeline.py

from CORE.atlas_scene_fitter import AtlasSceneFitter
from CORE.atlas_scene_normalizer import AtlasSceneNormalizer


class AtlasScenePreparationPipeline:
    """
    ATLAS Scene Preparation Pipeline v1.0

    Scene meshlerini normalize eder, fit eder,
    city Z offset ve XY sahne offset uygular.
    """

    @staticmethod
    def prepare_scene_meshes(
        meshes,
        road_groove_meshes,
        city_z_offset_mm,
        scene_origin_x,
        scene_origin_y,
        target_size_mm,
    ):
        normalize_transform = AtlasSceneNormalizer.calculate_transform(meshes)

        meshes = AtlasSceneNormalizer.apply_transform(
            meshes,
            normalize_transform,
        )

        road_groove_meshes = AtlasSceneNormalizer.apply_transform(
            road_groove_meshes,
            normalize_transform,
        )

        fit_transform = AtlasSceneFitter.calculate_transform(
            meshes,
            bed_width=target_size_mm,
            bed_depth=target_size_mm,
            margin=0,
        )

        meshes = AtlasSceneFitter.apply_transform(
            meshes,
            fit_transform,
        )

        road_groove_meshes = AtlasSceneFitter.apply_transform(
            road_groove_meshes,
            fit_transform,
        )

        meshes = AtlasScenePreparationPipeline._offset_meshes_z(
            meshes,
            city_z_offset_mm,
        )

        road_groove_meshes = AtlasScenePreparationPipeline._offset_meshes_z(
            road_groove_meshes,
            city_z_offset_mm,
        )

        xy_offset = {
            "min_x": 0.0,
            "min_y": 0.0,
            "min_z": 0.0,
            "scale": 1.0,
            "offset_x": scene_origin_x,
            "offset_y": scene_origin_y,
        }

        meshes = AtlasSceneFitter.apply_transform(
            meshes,
            xy_offset,
        )

        road_groove_meshes = AtlasSceneFitter.apply_transform(
            road_groove_meshes,
            xy_offset,
        )

        return meshes, road_groove_meshes

    @staticmethod
    def offset_mesh_xy(
        mesh,
        scene_origin_x,
        scene_origin_y,
    ):
        return AtlasSceneFitter.apply_transform(
            [mesh],
            {
                "min_x": 0.0,
                "min_y": 0.0,
                "min_z": 0.0,
                "scale": 1.0,
                "offset_x": scene_origin_x,
                "offset_y": scene_origin_y,
            },
        )[0]

    @staticmethod
    def _offset_meshes_z(meshes, offset_z):
        return [
            AtlasScenePreparationPipeline._offset_mesh_z(mesh, offset_z)
            for mesh in meshes
        ]

    @staticmethod
    def _offset_mesh_z(mesh, offset_z):
        if not mesh:
            return mesh

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
                AtlasScenePreparationPipeline._offset_point_z(point, offset_z)
            )

        for point in mesh.get("top", []):
            new_mesh["top"].append(
                AtlasScenePreparationPipeline._offset_point_z(point, offset_z)
            )

        for wall in mesh.get("walls", []):
            new_wall = []
            for point in wall:
                new_wall.append(
                    AtlasScenePreparationPipeline._offset_point_z(point, offset_z)
                )
            new_mesh["walls"].append(tuple(new_wall))

        for triangle in mesh.get("triangles", []):
            new_triangle = []
            for point in triangle:
                new_triangle.append(
                    AtlasScenePreparationPipeline._offset_point_z(point, offset_z)
                )
            new_mesh["triangles"].append(tuple(new_triangle))

        return new_mesh

    @staticmethod
    def _offset_point_z(point, offset_z):
        x, y, z = point
        return (x, y, z + offset_z)
