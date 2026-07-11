from CORE.atlas_polygon_triangulator import AtlasPolygonTriangulator
from CORE.atlas_foundation_sampler import AtlasFoundationSampler


class AtlasParkFoundationBuilder:
    """
    ATLAS Park Foundation Builder v0.2

    Park / yeşil alan poligonlarını terrain üzerine oturan
    kapalı ve ince 3D foundation meshleri olarak üretir.
    """

    PARK_HEIGHT_MM = 0.18

    @staticmethod
    def build_parks(
        parks,
        coordinate_engine,
        terrain_mesh,
        debug=True,
    ):
        meshes = []
        accepted = 0
        skipped = 0

        for park in parks:
            mesh = AtlasParkFoundationBuilder._build_park_mesh(
                park=park,
                coordinate_engine=coordinate_engine,
                terrain_mesh=terrain_mesh,
            )

            if mesh:
                meshes.append(mesh)
                accepted += 1
            else:
                skipped += 1

        if debug:
            print("")
            print("=" * 60)
            print("ATLAS PARK FOUNDATION BUILDER REPORT")
            print("=" * 60)
            print(f"Input parks      : {len(parks)}")
            print(f"Accepted parks   : {accepted}")
            print(f"Skipped parks    : {skipped}")
            print(f"Park meshes      : {len(meshes)}")
            print("=" * 60)
            print("")

        return meshes

    @staticmethod
    def _build_park_mesh(
        park,
        coordinate_engine,
        terrain_mesh,
    ):
        geometry = park.get("geometry", [])

        if len(geometry) < 4:
            return None

        points = coordinate_engine.geometry_to_stl_mm(geometry)

        points = AtlasParkFoundationBuilder._clip_points_to_bounds(
            points=points,
            min_x=0.0,
            max_x=200.0,
            min_y=0.0,
            max_y=200.0,
        )

        if len(points) >= 2 and points[0] == points[-1]:
            points = points[:-1]

        if len(points) < 3:
            return None

        flat_triangles = AtlasPolygonTriangulator.triangulate(points)

        if not flat_triangles:
            return None

        bottom = []
        top = []
        walls = []
        triangles = []

        for x, y in points:
            terrain_z = AtlasFoundationSampler.terrain_z_at_xy(
                terrain_mesh=terrain_mesh,
                x=x,
                y=y,
            )

            bottom.append(
                (
                    x,
                    y,
                    terrain_z,
                )
            )

            top.append(
                (
                    x,
                    y,
                    terrain_z + AtlasParkFoundationBuilder.PARK_HEIGHT_MM,
                )
            )

        for triangle in flat_triangles:
            top_triangle = []
            bottom_triangle = []

            for x, y in triangle:
                terrain_z = AtlasFoundationSampler.terrain_z_at_xy(
                    terrain_mesh=terrain_mesh,
                    x=x,
                    y=y,
                )

                top_triangle.append(
                    (
                        x,
                        y,
                        terrain_z + AtlasParkFoundationBuilder.PARK_HEIGHT_MM,
                    )
                )

                bottom_triangle.append(
                    (
                        x,
                        y,
                        terrain_z,
                    )
                )

            triangles.append(tuple(top_triangle))

            triangles.append(
                (
                    bottom_triangle[2],
                    bottom_triangle[1],
                    bottom_triangle[0],
                )
            )

        point_count = len(points)

        for index in range(point_count):
            next_index = (index + 1) % point_count

            b1 = bottom[index]
            b2 = bottom[next_index]
            t1 = top[index]
            t2 = top[next_index]

            wall = (b1, b2, t2, t1)

            wall_triangles = [
                (b1, b2, t2),
                (b1, t2, t1),
            ]

            walls.append(wall)
            triangles.extend(wall_triangles)

        return {
            "type": "park_foundation",
            "park_type": park.get(
                "park_type",
                "green_area",
            ),
            "bottom": bottom,
            "top": top,
            "walls": walls,
            "triangles": triangles,
            "placement_mode": "foundation_first",
        }

    @staticmethod
    def _clip_points_to_bounds(
        points,
        min_x,
        max_x,
        min_y,
        max_y,
    ):
        clipped = []

        for x, y in points:
            if min_x <= x <= max_x and min_y <= y <= max_y:
                clipped.append((x, y))

        return clipped
