class AtlasFoundationSceneXYMeshClipper:
    @staticmethod
    def _interpolate_point(start, end, ratio):
        return (
            start[0] + (end[0] - start[0]) * ratio,
            start[1] + (end[1] - start[1]) * ratio,
            start[2] + (end[2] - start[2]) * ratio,
        )

    @classmethod
    def _clip_polygon_against_boundary(
        cls,
        polygon,
        inside,
        intersection,
    ):
        if not polygon:
            return []

        output = []
        previous = polygon[-1]
        previous_inside = inside(previous)

        for current in polygon:
            current_inside = inside(current)

            if current_inside:
                if not previous_inside:
                    output.append(
                        intersection(previous, current)
                    )

                output.append(current)

            elif previous_inside:
                output.append(
                    intersection(previous, current)
                )

            previous = current
            previous_inside = current_inside

        return output

    @staticmethod
    def _intersection_at_x(start, end, boundary_x):
        delta_x = end[0] - start[0]

        if abs(delta_x) <= 1e-12:
            return (
                float(boundary_x),
                float(start[1]),
                float(start[2]),
            )

        ratio = (
            float(boundary_x) - start[0]
        ) / delta_x

        return AtlasFoundationSceneXYMeshClipper._interpolate_point(
            start,
            end,
            ratio,
        )

    @staticmethod
    def _intersection_at_y(start, end, boundary_y):
        delta_y = end[1] - start[1]

        if abs(delta_y) <= 1e-12:
            return (
                float(start[0]),
                float(boundary_y),
                float(start[2]),
            )

        ratio = (
            float(boundary_y) - start[1]
        ) / delta_y

        return AtlasFoundationSceneXYMeshClipper._interpolate_point(
            start,
            end,
            ratio,
        )

    @classmethod
    def _clip_triangle(
        cls,
        triangle,
        min_x,
        max_x,
        min_y,
        max_y,
    ):
        polygon = [
            (
                float(point[0]),
                float(point[1]),
                float(point[2]),
            )
            for point in triangle
        ]

        polygon = cls._clip_polygon_against_boundary(
            polygon=polygon,
            inside=lambda point: point[0] >= min_x,
            intersection=lambda start, end: cls._intersection_at_x(
                start,
                end,
                min_x,
            ),
        )

        polygon = cls._clip_polygon_against_boundary(
            polygon=polygon,
            inside=lambda point: point[0] <= max_x,
            intersection=lambda start, end: cls._intersection_at_x(
                start,
                end,
                max_x,
            ),
        )

        polygon = cls._clip_polygon_against_boundary(
            polygon=polygon,
            inside=lambda point: point[1] >= min_y,
            intersection=lambda start, end: cls._intersection_at_y(
                start,
                end,
                min_y,
            ),
        )

        polygon = cls._clip_polygon_against_boundary(
            polygon=polygon,
            inside=lambda point: point[1] <= max_y,
            intersection=lambda start, end: cls._intersection_at_y(
                start,
                end,
                max_y,
            ),
        )

        if len(polygon) < 3:
            return []

        triangles = []
        anchor = polygon[0]

        for index in range(1, len(polygon) - 1):
            triangles.append(
                (
                    anchor,
                    polygon[index],
                    polygon[index + 1],
                )
            )

        return triangles

    @classmethod
    def clip_mesh(
        cls,
        mesh,
        min_x,
        max_x,
        min_y,
        max_y,
    ):
        min_x = float(min_x)
        max_x = float(max_x)
        min_y = float(min_y)
        max_y = float(max_y)

        if max_x <= min_x or max_y <= min_y:
            raise ValueError(
                "Clip bounds must have positive area"
            )

        clipped_triangles = []

        for triangle in mesh.get("triangles", ()):
            clipped_triangles.extend(
                cls._clip_triangle(
                    triangle=triangle,
                    min_x=min_x,
                    max_x=max_x,
                    min_y=min_y,
                    max_y=max_y,
                )
            )

        if not clipped_triangles:
            return None

        clipped_mesh = dict(mesh)
        clipped_mesh["triangles"] = clipped_triangles

        return clipped_mesh

    @classmethod
    def clip_meshes(
        cls,
        meshes,
        min_x,
        max_x,
        min_y,
        max_y,
    ):
        clipped = []

        for mesh in meshes:
            clipped_mesh = cls.clip_mesh(
                mesh=mesh,
                min_x=min_x,
                max_x=max_x,
                min_y=min_y,
                max_y=max_y,
            )

            if clipped_mesh is not None:
                clipped.append(clipped_mesh)

        return clipped
