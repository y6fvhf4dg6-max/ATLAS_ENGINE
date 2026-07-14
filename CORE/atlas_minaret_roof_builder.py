"""
ATLAS Minaret Roof Builder v0.1

tower:type=minaret ve roof:shape=pyramidal kayıtlarını
baskıya uygun sivri külah geometrisine dönüştürür.

Castle Engine'den bağımsızdır.
"""


class AtlasMinaretRoofBuilder:
    SUPPORTED_ROOF_SHAPES = {
        "pyramidal",
    }

    Z_TOLERANCE = 1e-7
    MIN_ROOF_HEIGHT_MM = 0.25
    MAX_ROOF_HEIGHT_MM = 8.00
    DEFAULT_WIDTH_HEIGHT_RATIO = 1.75

    @staticmethod
    def apply(
        mesh,
        tower_type,
        roof_shape,
        roof_height_m=None,
        coordinate_engine=None,
    ):
        if not mesh:
            return mesh

        normalized_tower_type = (
            str(tower_type).strip().lower()
            if tower_type is not None
            else None
        )

        normalized_roof_shape = (
            str(roof_shape).strip().lower()
            if roof_shape is not None
            else None
        )

        if normalized_tower_type != "minaret":
            return mesh

        if (
            normalized_roof_shape
            not in AtlasMinaretRoofBuilder
            .SUPPORTED_ROOF_SHAPES
        ):
            return mesh

        bottom_z = mesh.get("bottom_z")
        top_z = mesh.get("top_z")
        top_points = mesh.get("top", [])

        if (
            bottom_z is None
            or top_z is None
            or len(top_points) < 3
        ):
            return mesh

        base_ring = AtlasMinaretRoofBuilder._clean_ring(
            top_points
        )

        if len(base_ring) < 3:
            return mesh

        roof_height_mm = (
            AtlasMinaretRoofBuilder
            ._calculate_roof_height_mm(
                base_ring=base_ring,
                roof_height_m=roof_height_m,
                coordinate_engine=coordinate_engine,
            )
        )

        available_height_mm = (
            float(top_z) - float(bottom_z)
        )

        roof_height_mm = min(
            roof_height_mm,
            max(
                AtlasMinaretRoofBuilder.MIN_ROOF_HEIGHT_MM,
                available_height_mm,
            ),
        )

        body_top_z = max(
            float(bottom_z),
            float(top_z) - roof_height_mm,
        )

        lowered_top_ring = [
            (
                float(point[0]),
                float(point[1]),
                body_top_z,
            )
            for point in base_ring
        ]

        remaining_triangles = []
        removed_top_triangle_count = 0

        for triangle in mesh.get(
            "triangles",
            [],
        ):
            if AtlasMinaretRoofBuilder._is_top_triangle(
                triangle=triangle,
                top_z=float(top_z),
            ):
                removed_top_triangle_count += 1
                continue

            remaining_triangles.append(
                AtlasMinaretRoofBuilder
                ._lower_top_vertices(
                    triangle=triangle,
                    old_top_z=float(top_z),
                    new_top_z=body_top_z,
                )
            )

        if removed_top_triangle_count == 0:
            return mesh

        centroid_x = (
            sum(point[0] for point in lowered_top_ring)
            / len(lowered_top_ring)
        )

        centroid_y = (
            sum(point[1] for point in lowered_top_ring)
            / len(lowered_top_ring)
        )

        apex = (
            centroid_x,
            centroid_y,
            float(top_z),
        )

        roof_triangles = []

        for index, point_1 in enumerate(
            lowered_top_ring
        ):
            point_2 = lowered_top_ring[
                (index + 1)
                % len(lowered_top_ring)
            ]

            roof_triangles.append(
                (
                    point_1,
                    point_2,
                    apex,
                )
            )

        mesh["triangles"] = [
            *remaining_triangles,
            *roof_triangles,
        ]

        mesh["top"] = lowered_top_ring
        mesh["walls"] = (
            AtlasMinaretRoofBuilder
            ._lower_wall_quads(
                walls=mesh.get("walls", []),
                old_top_z=float(top_z),
                new_top_z=body_top_z,
            )
        )

        mesh["body_top_z"] = body_top_z
        mesh["roof_base_z"] = body_top_z
        mesh["roof_top_z"] = float(top_z)
        mesh["top_z"] = float(top_z)

        mesh["roof_apex"] = apex
        mesh["roof_height_mm"] = roof_height_mm
        mesh["roof_geometry"] = "minaret_pyramidal"
        mesh["roof_triangles"] = roof_triangles
        mesh["removed_top_triangle_count"] = (
            removed_top_triangle_count
        )
        mesh["minaret_roof_applied"] = True

        return mesh

    @staticmethod
    def _calculate_roof_height_mm(
        base_ring,
        roof_height_m,
        coordinate_engine,
    ):
        explicit_height_mm = None

        if (
            roof_height_m is not None
            and coordinate_engine is not None
        ):
            try:
                parsed_height_m = float(
                    str(roof_height_m)
                    .replace("m", "")
                    .strip()
                )
            except (TypeError, ValueError):
                parsed_height_m = None

            if (
                parsed_height_m is not None
                and parsed_height_m > 0.0
            ):
                explicit_height_mm = (
                    coordinate_engine
                    .height_to_stl_mm(
                        parsed_height_m
                    )
                )

        xs = [
            point[0]
            for point in base_ring
        ]

        ys = [
            point[1]
            for point in base_ring
        ]

        width_mm = max(xs) - min(xs)
        depth_mm = max(ys) - min(ys)

        positive_axes = [
            value
            for value in (
                width_mm,
                depth_mm,
            )
            if value > 0.0
        ]

        footprint_width_mm = (
            min(positive_axes)
            if positive_axes
            else 0.0
        )

        proportional_height_mm = (
            footprint_width_mm
            * AtlasMinaretRoofBuilder
            .DEFAULT_WIDTH_HEIGHT_RATIO
        )

        roof_height_mm = (
            explicit_height_mm
            if explicit_height_mm is not None
            else proportional_height_mm
        )

        return min(
            AtlasMinaretRoofBuilder.MAX_ROOF_HEIGHT_MM,
            max(
                AtlasMinaretRoofBuilder.MIN_ROOF_HEIGHT_MM,
                roof_height_mm,
            ),
        )

    @staticmethod
    def _lower_wall_quads(
        walls,
        old_top_z,
        new_top_z,
    ):
        return [
            tuple(
                AtlasMinaretRoofBuilder
                ._lower_top_vertex(
                    point=point,
                    old_top_z=old_top_z,
                    new_top_z=new_top_z,
                )
                for point in wall
            )
            for wall in walls
        ]

    @staticmethod
    def _lower_top_vertices(
        triangle,
        old_top_z,
        new_top_z,
    ):
        return tuple(
            AtlasMinaretRoofBuilder
            ._lower_top_vertex(
                point=point,
                old_top_z=old_top_z,
                new_top_z=new_top_z,
            )
            for point in triangle
        )

    @staticmethod
    def _lower_top_vertex(
        point,
        old_top_z,
        new_top_z,
    ):
        if (
            abs(
                float(point[2])
                - float(old_top_z)
            )
            <= AtlasMinaretRoofBuilder
            .Z_TOLERANCE
        ):
            return (
                float(point[0]),
                float(point[1]),
                float(new_top_z),
            )

        return (
            float(point[0]),
            float(point[1]),
            float(point[2]),
        )

    @staticmethod
    def _is_top_triangle(
        triangle,
        top_z,
    ):
        if triangle is None or len(triangle) != 3:
            return False

        return all(
            abs(
                float(point[2])
                - float(top_z)
            )
            <= AtlasMinaretRoofBuilder
            .Z_TOLERANCE
            for point in triangle
        )

    @staticmethod
    def _clean_ring(points):
        clean = []

        for point in points:
            if point is None or len(point) < 3:
                continue

            normalized = (
                float(point[0]),
                float(point[1]),
                float(point[2]),
            )

            if (
                clean
                and clean[-1] == normalized
            ):
                continue

            clean.append(normalized)

        if (
            len(clean) >= 2
            and clean[0] == clean[-1]
        ):
            clean.pop()

        return clean
