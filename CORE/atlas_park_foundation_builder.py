from CORE.atlas_polygon_triangulator import AtlasPolygonTriangulator
from CORE.atlas_foundation_sampler import AtlasFoundationSampler


class AtlasParkFoundationBuilder:
    """
    ATLAS Park Foundation Builder v0.3

    Park ve yeşil alan poligonlarını terrain üzerine oturan,
    kapalı ve ince 3D foundation meshleri olarak üretir.
    """

    PARK_HEIGHT_MM = 0.30

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

        if len(geometry) < 3:
            return None

        points = list(
            coordinate_engine.geometry_to_stl_mm(geometry)
        )

        if len(points) >= 2 and points[0] == points[-1]:
            points = points[:-1]

        if len(points) < 3:
            return None

        metadata = terrain_mesh.get("metadata", {})

        size_x_mm = float(
            metadata.get(
                "size_x_mm",
                metadata.get("size_mm", 200.0),
            )
        )
        size_y_mm = float(
            metadata.get(
                "size_y_mm",
                metadata.get("size_mm", 200.0),
            )
        )

        clipped_polygons = (
            AtlasParkFoundationBuilder._clip_polygon_to_bounds(
                points=points,
                min_x=0.0,
                max_x=size_x_mm,
                min_y=0.0,
                max_y=size_y_mm,
            )
        )

        if not clipped_polygons:
            return None

        points = clipped_polygons[0]

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

            bottom.append((x, y, terrain_z))
            top.append(
                (
                    x,
                    y,
                    terrain_z
                    + AtlasParkFoundationBuilder.PARK_HEIGHT_MM,
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
                        terrain_z
                        + AtlasParkFoundationBuilder.PARK_HEIGHT_MM,
                    )
                )
                bottom_triangle.append((x, y, terrain_z))

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

            walls.append((b1, b2, t2, t1))
            triangles.extend(
                [
                    (b1, b2, t2),
                    (b1, t2, t1),
                ]
            )

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
    def _clip_polygon_to_bounds(
        points,
        min_x,
        max_x,
        min_y,
        max_y,
    ):
        polygon = list(points)

        if len(polygon) >= 2 and polygon[0] == polygon[-1]:
            polygon = polygon[:-1]

        if len(polygon) < 3:
            return []

        def clip_edge(vertices, inside, intersection):
            if not vertices:
                return []

            result = []
            previous = vertices[-1]
            previous_inside = inside(previous)

            for current in vertices:
                current_inside = inside(current)

                if current_inside:
                    if not previous_inside:
                        result.append(
                            intersection(previous, current)
                        )
                    result.append(current)
                elif previous_inside:
                    result.append(
                        intersection(previous, current)
                    )

                previous = current
                previous_inside = current_inside

            return result

        def vertical_intersection(start, end, x_value):
            x1, y1 = start
            x2, y2 = end

            if x2 == x1:
                return (float(x_value), float(y1))

            ratio = (x_value - x1) / (x2 - x1)
            return (
                float(x_value),
                float(y1 + ratio * (y2 - y1)),
            )

        def horizontal_intersection(start, end, y_value):
            x1, y1 = start
            x2, y2 = end

            if y2 == y1:
                return (float(x1), float(y_value))

            ratio = (y_value - y1) / (y2 - y1)
            return (
                float(x1 + ratio * (x2 - x1)),
                float(y_value),
            )

        polygon = clip_edge(
            polygon,
            lambda point: point[0] >= min_x,
            lambda start, end: vertical_intersection(
                start,
                end,
                min_x,
            ),
        )
        polygon = clip_edge(
            polygon,
            lambda point: point[0] <= max_x,
            lambda start, end: vertical_intersection(
                start,
                end,
                max_x,
            ),
        )
        polygon = clip_edge(
            polygon,
            lambda point: point[1] >= min_y,
            lambda start, end: horizontal_intersection(
                start,
                end,
                min_y,
            ),
        )
        polygon = clip_edge(
            polygon,
            lambda point: point[1] <= max_y,
            lambda start, end: horizontal_intersection(
                start,
                end,
                max_y,
            ),
        )

        cleaned = []

        for point in polygon:
            normalized = (
                float(point[0]),
                float(point[1]),
            )

            if not cleaned or normalized != cleaned[-1]:
                cleaned.append(normalized)

        if len(cleaned) >= 2 and cleaned[0] == cleaned[-1]:
            cleaned.pop()

        if len(cleaned) < 3:
            return []

        start_index = min(
            range(len(cleaned)),
            key=lambda index: (
                cleaned[index][1],
                cleaned[index][0],
            ),
        )
        cleaned = (
            cleaned[start_index:]
            + cleaned[:start_index]
        )

        return [cleaned]

    @staticmethod
    def _clip_points_to_bounds(
        points,
        min_x,
        max_x,
        min_y,
        max_y,
    ):
        polygons = AtlasParkFoundationBuilder._clip_polygon_to_bounds(
            points=points,
            min_x=min_x,
            max_x=max_x,
            min_y=min_y,
            max_y=max_y,
        )

        if not polygons:
            return []

        return polygons[0]
