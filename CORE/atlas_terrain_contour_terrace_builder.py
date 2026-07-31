"""
ATLAS Terrain Contour Terrace Builder v0.1

Bu ilk sürüm yalnız contour segmentleri çıkarır.

Görevler:
- Tek terrain üçgenini belirli bir Z düzleminde kesmek
- Düzenli terrain grid'inin tüm üst üçgenlerinden segment üretmek
- Düz yüzeylerde yapay contour oluşturmamak
- Aynı girdide deterministik sonuç vermek
"""


class AtlasTerrainContourTerraceBuilder:
    TOLERANCE = 1e-12

    @staticmethod
    def extract_triangle_contour_segment(
        triangle,
        contour_z,
    ):
        if (
            not isinstance(triangle, (tuple, list))
            or len(triangle) != 3
        ):
            raise ValueError(
                "triangle must contain exactly 3 XYZ points"
            )

        points = []

        for point in triangle:
            if (
                not isinstance(point, (tuple, list))
                or len(point) < 3
            ):
                raise ValueError(
                    "triangle must contain XYZ points"
                )

            points.append(
                (
                    float(point[0]),
                    float(point[1]),
                    float(point[2]),
                )
            )

        contour_z = float(contour_z)
        tolerance = (
            AtlasTerrainContourTerraceBuilder
            .TOLERANCE
        )

        z_values = [
            point[2]
            for point in points
        ]

        minimum_z = min(z_values)
        maximum_z = max(z_values)

        # Tamamen düz bir üçgende, contour düzlemi üçgenin tamamıyla
        # çakışsa bile çizgi üretmeyiz. Düz alan düzdür.
        if maximum_z - minimum_z <= tolerance:
            return None

        if contour_z < minimum_z - tolerance:
            return None

        if contour_z > maximum_z + tolerance:
            return None

        intersections = []

        edges = (
            (points[0], points[1]),
            (points[1], points[2]),
            (points[2], points[0]),
        )

        for point_a, point_b in edges:
            intersection = (
                AtlasTerrainContourTerraceBuilder
                ._intersect_edge_with_contour(
                    point_a=point_a,
                    point_b=point_b,
                    contour_z=contour_z,
                )
            )

            if intersection is None:
                continue

            AtlasTerrainContourTerraceBuilder._append_unique_point(
                intersections,
                intersection,
            )

        if len(intersections) != 2:
            return None

        intersections.sort(
            key=lambda point: (
                round(point[0], 12),
                round(point[1], 12),
                round(point[2], 12),
            )
        )

        return tuple(intersections)

    @staticmethod
    def extract_grid_contour_segments(
        top_points,
        contour_z,
    ):
        if not top_points or len(top_points) < 2:
            raise ValueError(
                "top_points must contain at least 2 rows "
                "and 2 columns"
            )

        column_count = len(top_points[0])

        if column_count < 2:
            raise ValueError(
                "top_points must contain at least 2 rows "
                "and 2 columns"
            )

        for row in top_points:
            if len(row) != column_count:
                raise ValueError(
                    "top_points must form a rectangular grid"
                )

        segments = []

        for row_index in range(
            len(top_points) - 1
        ):
            for column_index in range(
                column_count - 1
            ):
                p00 = (
                    top_points[row_index][column_index]
                )
                p10 = (
                    top_points[row_index][column_index + 1]
                )
                p01 = (
                    top_points[row_index + 1][column_index]
                )
                p11 = (
                    top_points[row_index + 1][column_index + 1]
                )

                terrain_triangles = (
                    (
                        p00,
                        p10,
                        p11,
                    ),
                    (
                        p00,
                        p11,
                        p01,
                    ),
                )

                for triangle in terrain_triangles:
                    segment = (
                        AtlasTerrainContourTerraceBuilder
                        .extract_triangle_contour_segment(
                            triangle=triangle,
                            contour_z=contour_z,
                        )
                    )

                    if segment is not None:
                        segments.append(segment)

        return segments

    @staticmethod
    def _intersect_edge_with_contour(
        point_a,
        point_b,
        contour_z,
    ):
        tolerance = (
            AtlasTerrainContourTerraceBuilder
            .TOLERANCE
        )

        ax, ay, az = point_a
        bx, by, bz = point_b

        a_on = abs(az - contour_z) <= tolerance
        b_on = abs(bz - contour_z) <= tolerance

        # Kenarın tamamı contour düzlemindeyse onu contour segmenti
        # olarak kabul etmeyiz. Bu, düz alanlarda yapay çizgileri önler.
        if a_on and b_on:
            return None

        if a_on:
            return (
                round(ax, 12),
                round(ay, 12),
                round(contour_z, 12),
            )

        if b_on:
            return (
                round(bx, 12),
                round(by, 12),
                round(contour_z, 12),
            )

        crosses = (
            (az < contour_z < bz)
            or (bz < contour_z < az)
        )

        if not crosses:
            return None

        factor = (
            (contour_z - az)
            / (bz - az)
        )

        x = ax + factor * (bx - ax)
        y = ay + factor * (by - ay)

        return (
            round(x, 12),
            round(y, 12),
            round(contour_z, 12),
        )

    @staticmethod
    def _append_unique_point(
        points,
        candidate,
    ):
        tolerance = (
            AtlasTerrainContourTerraceBuilder
            .TOLERANCE
        )

        for existing in points:
            if (
                abs(existing[0] - candidate[0])
                <= tolerance
                and abs(existing[1] - candidate[1])
                <= tolerance
                and abs(existing[2] - candidate[2])
                <= tolerance
            ):
                return

        points.append(candidate)

    @staticmethod
    def connect_contour_segments(
        segments,
    ):
        if not segments:
            return []

        normalized_segments = {}

        for segment in segments:
            if (
                not isinstance(segment, (tuple, list))
                or len(segment) != 2
            ):
                raise ValueError(
                    "segments must contain point pairs"
                )

            point_a = (
                AtlasTerrainContourTerraceBuilder
                ._normalize_contour_point(
                    segment[0]
                )
            )
            point_b = (
                AtlasTerrainContourTerraceBuilder
                ._normalize_contour_point(
                    segment[1]
                )
            )

            if point_a == point_b:
                continue

            key = tuple(
                sorted((
                    point_a,
                    point_b,
                ))
            )

            normalized_segments[key] = key

        if not normalized_segments:
            return []

        adjacency = {}

        for point_a, point_b in normalized_segments.values():
            adjacency.setdefault(
                point_a,
                set(),
            ).add(point_b)

            adjacency.setdefault(
                point_b,
                set(),
            ).add(point_a)

        unused_edges = set(
            normalized_segments.keys()
        )

        lines = []

        while unused_edges:
            component_edges = (
                AtlasTerrainContourTerraceBuilder
                ._collect_edge_component(
                    start_edge=min(unused_edges),
                    unused_edges=unused_edges,
                    adjacency=adjacency,
                )
            )

            component_points = {
                point
                for edge in component_edges
                for point in edge
            }

            component_adjacency = {
                point: sorted(
                    neighbor
                    for neighbor in adjacency[point]
                    if tuple(sorted((point, neighbor)))
                    in component_edges
                )
                for point in component_points
            }

            endpoints = sorted(
                point
                for point, neighbors
                in component_adjacency.items()
                if len(neighbors) == 1
            )

            if endpoints:
                start_point = endpoints[0]
                closed = False
            else:
                start_point = min(
                    component_points
                )
                closed = True

            ordered_points = (
                AtlasTerrainContourTerraceBuilder
                ._walk_contour_component(
                    start_point=start_point,
                    component_edges=component_edges,
                    component_adjacency=(
                        component_adjacency
                    ),
                    closed=closed,
                )
            )

            lines.append(
                {
                    "closed": closed,
                    "points": ordered_points,
                }
            )

        lines.sort(
            key=lambda line: (
                line["points"][0],
                len(line["points"]),
                line["closed"],
            )
        )

        return lines

    @staticmethod
    def _normalize_contour_point(
        point,
    ):
        if (
            not isinstance(point, (tuple, list))
            or len(point) < 3
        ):
            raise ValueError(
                "contour points must be XYZ points"
            )

        return tuple(
            round(float(value), 12)
            for value in point[:3]
        )

    @staticmethod
    def _collect_edge_component(
        start_edge,
        unused_edges,
        adjacency,
    ):
        component_edges = set()
        pending_points = list(
            start_edge
        )
        visited_points = set()

        while pending_points:
            point = pending_points.pop()

            if point in visited_points:
                continue

            visited_points.add(point)

            for neighbor in adjacency.get(
                point,
                (),
            ):
                edge = tuple(
                    sorted((
                        point,
                        neighbor,
                    ))
                )

                if edge not in unused_edges:
                    continue

                unused_edges.remove(edge)
                component_edges.add(edge)
                pending_points.append(neighbor)

        return component_edges

    @staticmethod
    def _walk_contour_component(
        start_point,
        component_edges,
        component_adjacency,
        closed,
    ):
        points = [
            start_point
        ]

        used_edges = set()
        previous_point = None
        current_point = start_point

        while True:
            candidates = []

            for neighbor in component_adjacency.get(
                current_point,
                (),
            ):
                edge = tuple(
                    sorted((
                        current_point,
                        neighbor,
                    ))
                )

                if edge in used_edges:
                    continue

                candidates.append(
                    neighbor
                )

            if not candidates:
                break

            if (
                previous_point is not None
                and len(candidates) > 1
            ):
                non_previous = [
                    candidate
                    for candidate in candidates
                    if candidate != previous_point
                ]

                if non_previous:
                    candidates = non_previous

            next_point = min(
                candidates
            )

            edge = tuple(
                sorted((
                    current_point,
                    next_point,
                ))
            )

            used_edges.add(edge)
            previous_point = current_point
            current_point = next_point
            points.append(current_point)

            if (
                closed
                and current_point == start_point
            ):
                break

        if (
            closed
            and points[-1] != points[0]
        ):
            points.append(
                points[0]
            )

        return points

    @staticmethod
    def build_contour_levels(
        top_points,
        base_z,
        contour_step_mm,
    ):
        """
        Build contour levels strictly inside the terrain Z range.

        Minimum and maximum terrain elevations are excluded:
        - the minimum boundary does not represent a visible contour
        - the maximum point alone cannot form a useful contour line
        """
        contour_step_mm = float(
            contour_step_mm
        )

        if contour_step_mm <= 0.0:
            raise ValueError(
                "contour_step_mm must be positive"
            )

        if not top_points or len(top_points) < 2:
            raise ValueError(
                "top_points must contain at least 2 rows "
                "and 2 columns"
            )

        column_count = len(
            top_points[0]
        )

        if column_count < 2:
            raise ValueError(
                "top_points must contain at least 2 rows "
                "and 2 columns"
            )

        z_values = []

        for row in top_points:
            if len(row) != column_count:
                raise ValueError(
                    "top_points must form a rectangular grid"
                )

            for point in row:
                if (
                    not isinstance(point, (tuple, list))
                    or len(point) < 3
                ):
                    raise ValueError(
                        "top_points must contain XYZ points"
                    )

                z_values.append(
                    float(point[2])
                )

        minimum_z = min(z_values)
        maximum_z = max(z_values)

        tolerance = (
            AtlasTerrainContourTerraceBuilder
            .TOLERANCE
        )

        # Düz alan düzdür; contour seviyesi oluşturulmaz.
        if maximum_z - minimum_z <= tolerance:
            return []

        base_z = float(base_z)

        first_level_index = int(
            (minimum_z - base_z)
            // contour_step_mm
        ) + 1

        levels = []
        level_index = max(
            1,
            first_level_index,
        )

        while True:
            contour_z = (
                base_z
                + level_index * contour_step_mm
            )

            # Maksimum terrain kotuyla çakışan seviye dahil edilmez.
            if contour_z >= maximum_z - tolerance:
                break

            if contour_z > minimum_z + tolerance:
                levels.append(
                    round(
                        contour_z,
                        12,
                    )
                )

            level_index += 1

        return levels

    @staticmethod
    def extract_contours(
        top_points,
        base_z,
        contour_step_mm,
    ):
        """
        Extract connected contour lines for every internal contour level.

        Returned structure:
        [
            {
                "contour_z": float,
                "lines": [
                    {
                        "closed": bool,
                        "points": [...]
                    }
                ]
            }
        ]
        """
        levels = (
            AtlasTerrainContourTerraceBuilder
            .build_contour_levels(
                top_points=top_points,
                base_z=base_z,
                contour_step_mm=contour_step_mm,
            )
        )

        contours = []

        for contour_z in levels:
            segments = (
                AtlasTerrainContourTerraceBuilder
                .extract_grid_contour_segments(
                    top_points=top_points,
                    contour_z=contour_z,
                )
            )

            if not segments:
                continue

            lines = (
                AtlasTerrainContourTerraceBuilder
                .connect_contour_segments(
                    segments=segments,
                )
            )

            if not lines:
                continue

            contours.append(
                {
                    "contour_z": round(
                        float(contour_z),
                        12,
                    ),
                    "lines": lines,
                }
            )

        contours.sort(
            key=lambda contour: (
                contour["contour_z"]
            )
        )

        return contours
