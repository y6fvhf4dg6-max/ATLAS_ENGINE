# CORE/atlas_placement_pipeline.py

from CORE.atlas_foundation_engine import AtlasFoundationEngine


class AtlasPlacementPipeline:
    """
    ATLAS Placement Pipeline v1.0

    Amaç:
    - Meshlerin terrain üzerine yerleştirilmesini yönetmek.
    - AtlasEngine içindeki placement sorumluluğunu azaltmak.
    - Foundation hesaplamasını pipeline seviyesine taşımak.

    Bu sınıf terrain üretmez.
    Mesh üretmez.
    STL yazmaz.
    Sadece mevcut meshleri terrain yüksekliğine göre Z yönünde yerleştirir.
    """

    @staticmethod
    def place_meshes_on_terrain(
        meshes,
        terrain_mesh,
        scene_origin_x,
        scene_origin_y,
        embed_depth_mm=0.30,
        sample_grid=5,
        debug=True,
    ):
        placed_meshes = []

        if debug:
            print("")
            print("=" * 70)
            print("ATLAS PLACEMENT PIPELINE DEBUG REPORT")
            print("=" * 70)

        for index, mesh in enumerate(meshes):
            before_min_z = AtlasPlacementPipeline._mesh_min_z(mesh)

            foundation_z = AtlasFoundationEngine.calculate_foundation_z(
                mesh=mesh,
                terrain_mesh=terrain_mesh,
                scene_origin_x=scene_origin_x,
                scene_origin_y=scene_origin_y,
                embed_depth_mm=embed_depth_mm,
                sample_grid=sample_grid,
            )

            placed_mesh = AtlasPlacementPipeline._offset_mesh_z(
                mesh,
                foundation_z - before_min_z,
            )

            after_min_z = AtlasPlacementPipeline._mesh_min_z(placed_mesh)

            if debug and index < 50:
                mesh_type = mesh.get("type", "unknown")

                print(
                    f"{index:03d} | {mesh_type:20s} | "
                    f"before_min_z={before_min_z:7.3f} | "
                    f"foundation_z={foundation_z:7.3f} | "
                    f"after_min_z={after_min_z:7.3f}"
                )

            placed_meshes.append(placed_mesh)

        if debug:
            print("=" * 70)
            print("")

        return placed_meshes

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
                AtlasPlacementPipeline._offset_point_z(point, offset_z)
            )

        for point in mesh.get("top", []):
            new_mesh["top"].append(
                AtlasPlacementPipeline._offset_point_z(point, offset_z)
            )

        for wall in mesh.get("walls", []):
            new_wall = []
            for point in wall:
                new_wall.append(AtlasPlacementPipeline._offset_point_z(point, offset_z))
            new_mesh["walls"].append(tuple(new_wall))

        for triangle in mesh.get("triangles", []):
            new_triangle = []
            for point in triangle:
                new_triangle.append(
                    AtlasPlacementPipeline._offset_point_z(point, offset_z)
                )
            new_mesh["triangles"].append(tuple(new_triangle))

        return new_mesh

    @staticmethod
    def _mesh_min_z(mesh):
        points = []

        points.extend(mesh.get("bottom", []))
        points.extend(mesh.get("top", []))

        for triangle in mesh.get("triangles", []):
            points.extend(triangle)

        if not points:
            return 0.0

        return min(point[2] for point in points)

    @staticmethod
    def _offset_point_z(point, offset_z):
        x, y, z = point
        return (x, y, z + offset_z)
