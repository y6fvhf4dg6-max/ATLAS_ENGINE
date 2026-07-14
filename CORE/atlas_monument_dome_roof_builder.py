"""
ATLAS Monument Dome Roof Builder v0.1

Normal bina ve building:part kayıtlarındaki roof:shape=dome
etiketini baskıya uygun, kapalı bir kubbe geometrisine dönüştürür.

Temel ilkeler:
- Castle Engine'den bağımsızdır.
- Mevcut bina gövdesinin üst sınır segmentasyonunu korur.
- Düz üst kapağı kaldırır.
- Kademeli küçülen halkalar ve tepe noktası üretir.
- Sonuç açık veya non-manifold kenar oluşturmamalıdır.
"""


from math import sin, pi


class AtlasMonumentDomeRoofBuilder:
    """
    Genel anıtsal kubbe üreticisi.
    """

    SUPPORTED_ROOF_SHAPES = {
        "dome",
    }

    POINT_PRECISION = 9
    Z_TOLERANCE = 1e-7

    DEFAULT_RING_LEVEL_COUNT = 5

    MIN_ROOF_HEIGHT_MM = 0.25
    MAX_ROOF_HEIGHT_MM = 8.00

    DEFAULT_WIDTH_HEIGHT_RATIO = 0.30

    @staticmethod
    def apply(
        mesh,
        roof_shape,
        roof_height_m=None,
        coordinate_engine=None,
        total_height_m=None,
        min_height_m=None,
    ):
        if not mesh:
            return mesh

        normalized_roof_shape = (
            str(roof_shape).strip().lower()
            if roof_shape is not None
            else None
        )

        if (
            normalized_roof_shape
            not in AtlasMonumentDomeRoofBuilder
            .SUPPORTED_ROOF_SHAPES
        ):
            return mesh

        top_z = mesh.get("top_z")
        bottom_z = mesh.get("bottom_z")
        top_points = mesh.get("top", [])

        if (
            top_z is None
            or bottom_z is None
            or len(top_points) < 3
        ):
            return mesh

        semantic_interval = (
            AtlasMonumentDomeRoofBuilder
            ._resolve_height_interval(
                bottom_z=float(bottom_z),
                top_z=float(top_z),
                total_height_m=total_height_m,
                min_height_m=min_height_m,
                coordinate_engine=coordinate_engine,
            )
        )

        roof_base_z = semantic_interval["roof_base_z"]
        roof_target_top_z = semantic_interval["roof_top_z"]
        semantic_mode = semantic_interval["mode"]

        if semantic_mode == "height_interval":
            top_points = [
                (
                    float(point[0]),
                    float(point[1]),
                    roof_base_z,
                )
                for point in top_points
            ]

        base_ring = (
            AtlasMonumentDomeRoofBuilder
            ._clean_ring(top_points)
        )

        if len(base_ring) < 3:
            return mesh

        remaining_triangles = []
        removed_top_triangle_count = 0
        removed_wall_triangle_count = 0

        for triangle in mesh.get(
            "triangles",
            [],
        ):
            if (
                AtlasMonumentDomeRoofBuilder
                ._is_top_triangle(
                    triangle=triangle,
                    top_z=float(top_z),
                )
            ):
                removed_top_triangle_count += 1
                continue

            if semantic_mode == "height_interval":
                if (
                    AtlasMonumentDomeRoofBuilder
                    ._is_bottom_triangle(
                        triangle=triangle,
                        bottom_z=float(bottom_z),
                    )
                ):
                    remaining_triangles.append(triangle)
                else:
                    removed_wall_triangle_count += 1

                continue

            remaining_triangles.append(triangle)

        if removed_top_triangle_count == 0:
            return mesh

        centroid_x = (
            sum(point[0] for point in base_ring)
            / len(base_ring)
        )

        centroid_y = (
            sum(point[1] for point in base_ring)
            / len(base_ring)
        )

        if semantic_mode == "height_interval":
            roof_height_mm = max(
                roof_target_top_z - roof_base_z,
                AtlasMonumentDomeRoofBuilder.MIN_ROOF_HEIGHT_MM,
            )
        else:
            roof_height_mm = (
                AtlasMonumentDomeRoofBuilder
                ._calculate_roof_height_mm(
                    base_ring=base_ring,
                    roof_height_m=roof_height_m,
                    coordinate_engine=coordinate_engine,
                )
            )

        ring_levels = [
            base_ring,
        ]

        level_count = (
            AtlasMonumentDomeRoofBuilder
            .DEFAULT_RING_LEVEL_COUNT
        )

        for level_index in range(
            1,
            level_count,
        ):
            progress = level_index / level_count

            angle = progress * (pi / 2.0)

            radius_scale = max(
                0.0,
                sin(
                    (pi / 2.0) - angle
                ),
            )

            z_offset = (
                roof_height_mm
                * sin(angle)
            )

            ring = []

            for point in base_ring:
                x = (
                    centroid_x
                    + (point[0] - centroid_x)
                    * radius_scale
                )

                y = (
                    centroid_y
                    + (point[1] - centroid_y)
                    * radius_scale
                )

                ring.append(
                    (
                        x,
                        y,
                        roof_base_z + z_offset,
                    )
                )

            ring_levels.append(ring)

        roof_triangles = []

        for lower_ring, upper_ring in zip(
            ring_levels,
            ring_levels[1:],
        ):
            point_count = len(lower_ring)

            for index in range(point_count):
                next_index = (
                    index + 1
                ) % point_count

                lower_1 = lower_ring[index]
                lower_2 = lower_ring[next_index]

                upper_1 = upper_ring[index]
                upper_2 = upper_ring[next_index]

                roof_triangles.extend(
                    [
                        (
                            lower_1,
                            lower_2,
                            upper_2,
                        ),
                        (
                            lower_1,
                            upper_2,
                            upper_1,
                        ),
                    ]
                )

        final_ring = ring_levels[-1]

        apex = (
            centroid_x,
            centroid_y,
            (
                roof_target_top_z
                if semantic_mode == "height_interval"
                else roof_base_z + roof_height_mm
            ),
        )

        for index, point_1 in enumerate(
            final_ring
        ):
            point_2 = final_ring[
                (index + 1) % len(final_ring)
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

        if semantic_mode == "height_interval":
            mesh["top"] = base_ring
            mesh["walls"] = (
                AtlasMonumentDomeRoofBuilder
                ._build_base_ring_walls(
                    lower_ring=base_ring,
                    upper_ring=ring_levels[1],
                )
            )

        mesh["body_top_z"] = roof_base_z
        mesh["roof_base_z"] = roof_base_z
        mesh["roof_top_z"] = apex[2]
        mesh["top_z"] = apex[2]

        mesh["roof_apex"] = apex
        mesh["roof_height_mm"] = roof_height_mm
        mesh["roof_semantic_mode"] = semantic_mode
        mesh["roof_geometry"] = "dome"
        mesh["roof_triangles"] = roof_triangles
        mesh["roof_ring_levels"] = ring_levels
        mesh["roof_ring_point_count"] = len(
            base_ring
        )
        mesh["roof_level_count"] = len(
            ring_levels
        )
        mesh["removed_top_triangle_count"] = (
            removed_top_triangle_count
        )
        mesh["removed_wall_triangle_count"] = (
            removed_wall_triangle_count
        )
        mesh["monument_dome_applied"] = True

        return mesh

    @staticmethod
    def _build_base_ring_walls(
        lower_ring,
        upper_ring,
    ):
        if (
            len(lower_ring) < 3
            or len(lower_ring) != len(upper_ring)
        ):
            return []

        walls = []

        for index in range(len(lower_ring)):
            next_index = (
                index + 1
            ) % len(lower_ring)

            walls.append(
                (
                    lower_ring[index],
                    lower_ring[next_index],
                    upper_ring[next_index],
                    upper_ring[index],
                )
            )

        return walls

    @staticmethod
    def _lower_top_vertices(
        triangle,
        old_top_z,
        new_top_z,
    ):
        return tuple(
            AtlasMonumentDomeRoofBuilder
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
            <= AtlasMonumentDomeRoofBuilder.Z_TOLERANCE
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
    def _resolve_height_interval(
        bottom_z,
        top_z,
        total_height_m,
        min_height_m,
        coordinate_engine,
    ):
        result = {
            "mode": "additive_roof",
            "roof_base_z": float(top_z),
            "roof_top_z": float(top_z),
        }

        try:
            total_height = float(
                str(total_height_m)
                .replace("m", "")
                .strip()
            )
            min_height = float(
                str(min_height_m)
                .replace("m", "")
                .strip()
            )
        except (TypeError, ValueError):
            return result

        if (
            total_height <= 0.0
            or min_height < 0.0
            or min_height >= total_height
        ):
            return result

        # Foundation extruder min_height değerini zaten bottom_z
        # konumuna uygular ve top_z değerini toplam height olarak kurar.
        # Bu nedenle mevcut mesh aralığı doğrudan kubbe aralığıdır.
        roof_base_z = float(bottom_z)
        roof_top_z = float(top_z)

        if roof_top_z <= roof_base_z:
            return result

        return {
            "mode": "height_interval",
            "roof_base_z": roof_base_z,
            "roof_top_z": roof_top_z,
        }

    @staticmethod
    def _calculate_roof_height_mm(
        base_ring,
        roof_height_m,
        coordinate_engine,
    ):
        explicit_height_mm = None

        if roof_height_m is not None:
            try:
                parsed_roof_height_m = float(
                    str(roof_height_m)
                    .replace("m", "")
                    .strip()
                )
            except (TypeError, ValueError):
                parsed_roof_height_m = None

            if (
                parsed_roof_height_m is not None
                and parsed_roof_height_m > 0.0
                and coordinate_engine is not None
            ):
                explicit_height_mm = (
                    coordinate_engine
                    .height_to_stl_mm(
                        parsed_roof_height_m
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
            axis
            for axis in (
                width_mm,
                depth_mm,
            )
            if axis > 0.0
        ]

        if not positive_axes:
            footprint_width_mm = 0.0
        else:
            footprint_width_mm = min(
                positive_axes
            )

        proportional_height_mm = (
            footprint_width_mm
            * AtlasMonumentDomeRoofBuilder
            .DEFAULT_WIDTH_HEIGHT_RATIO
        )

        roof_height_mm = (
            explicit_height_mm
            if explicit_height_mm is not None
            else proportional_height_mm
        )

        roof_height_mm = max(
            roof_height_mm,
            AtlasMonumentDomeRoofBuilder
            .MIN_ROOF_HEIGHT_MM,
        )

        roof_height_mm = min(
            roof_height_mm,
            AtlasMonumentDomeRoofBuilder
            .MAX_ROOF_HEIGHT_MM,
        )

        return roof_height_mm

    @staticmethod
    def _clean_ring(points):
        clean = []

        for point in points:
            if point is None or len(point) < 3:
                continue

            normalized_point = (
                float(point[0]),
                float(point[1]),
                float(point[2]),
            )

            if (
                clean
                and AtlasMonumentDomeRoofBuilder
                ._same_point(
                    clean[-1],
                    normalized_point,
                )
            ):
                continue

            clean.append(normalized_point)

        if (
            len(clean) >= 2
            and AtlasMonumentDomeRoofBuilder
            ._same_point(
                clean[0],
                clean[-1],
            )
        ):
            clean.pop()

        return clean

    @staticmethod
    def _same_point(
        first,
        second,
    ):
        return all(
            round(
                float(first[index]),
                AtlasMonumentDomeRoofBuilder
                .POINT_PRECISION,
            )
            == round(
                float(second[index]),
                AtlasMonumentDomeRoofBuilder
                .POINT_PRECISION,
            )
            for index in range(3)
        )

    @staticmethod
    def _is_bottom_triangle(
        triangle,
        bottom_z,
    ):
        if triangle is None or len(triangle) != 3:
            return False

        return all(
            abs(
                float(point[2])
                - float(bottom_z)
            )
            <= AtlasMonumentDomeRoofBuilder
            .Z_TOLERANCE
            for point in triangle
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
            <= AtlasMonumentDomeRoofBuilder
            .Z_TOLERANCE
            for point in triangle
        )
