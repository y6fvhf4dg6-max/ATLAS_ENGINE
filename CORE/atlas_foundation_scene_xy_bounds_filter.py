class AtlasFoundationSceneXYBoundsFilter:
    @staticmethod
    def keep_fully_inside(
        meshes,
        min_x,
        max_x,
        min_y,
        max_y,
        tolerance=0.0,
    ):
        filtered = []

        min_x = float(min_x)
        max_x = float(max_x)
        min_y = float(min_y)
        max_y = float(max_y)
        tolerance = float(tolerance)

        for mesh in meshes:
            points = []

            points.extend(mesh.get("bottom", ()))
            points.extend(mesh.get("top", ()))

            for triangle in mesh.get("triangles", ()):
                points.extend(triangle)

            if not points:
                continue

            xs = [float(point[0]) for point in points]
            ys = [float(point[1]) for point in points]

            fully_inside = (
                min(xs) >= min_x - tolerance
                and max(xs) <= max_x + tolerance
                and min(ys) >= min_y - tolerance
                and max(ys) <= max_y + tolerance
            )

            if fully_inside:
                filtered.append(mesh)

        return filtered
