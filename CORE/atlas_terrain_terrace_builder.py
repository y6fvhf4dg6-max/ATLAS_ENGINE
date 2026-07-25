"""
ATLAS Terrain Terrace Builder v0.1

İlk aşama:
- Terrain top-point grid kotlarını taban kotuna göre sekileme
  seviyelerine indirger.
- XY grid yapısını değiştirmez.
- Aynı girdi için deterministik sonuç üretir.

Bu sürüm henüz dik seki duvarı veya kapalı STL kabuğu üretmez.
"""

import math


class AtlasTerrainTerraceBuilder:
    @staticmethod
    def quantize_z(
        z,
        base_z,
        terrace_step_mm,
    ):
        terrace_step_mm = float(
            terrace_step_mm
        )

        if (
            not math.isfinite(terrace_step_mm)
            or terrace_step_mm <= 0.0
        ):
            raise ValueError(
                "terrace_step_mm must be positive"
            )

        z = float(z)
        base_z = float(base_z)

        if not (
            math.isfinite(z)
            and math.isfinite(base_z)
        ):
            raise ValueError(
                "z and base_z must be finite"
            )

        relative_height = z - base_z

        if relative_height <= 0.0:
            return base_z

        level_index = math.floor(
            (
                relative_height
                + 1e-12
            )
            / terrace_step_mm
        )

        quantized = (
            base_z
            + level_index * terrace_step_mm
        )

        tolerance = max(
            1e-12,
            terrace_step_mm * 1e-12,
        )

        if quantized > z + tolerance:
            quantized -= terrace_step_mm

        return round(
            quantized,
            12,
        )

    @staticmethod
    def quantize_top_points(
        top_points,
        base_z,
        terrace_step_mm,
    ):
        terrace_step_mm = float(
            terrace_step_mm
        )

        if (
            not math.isfinite(terrace_step_mm)
            or terrace_step_mm <= 0.0
        ):
            raise ValueError(
                "terrace_step_mm must be positive"
            )

        if not top_points:
            return []

        quantized_rows = []

        for row in top_points:
            quantized_row = []

            for point in row:
                if (
                    not isinstance(
                        point,
                        (tuple, list),
                    )
                    or len(point) < 3
                ):
                    raise ValueError(
                        "top_points must contain XYZ points"
                    )

                x = float(point[0])
                y = float(point[1])
                z = float(point[2])

                quantized_row.append(
                    (
                        x,
                        y,
                        AtlasTerrainTerraceBuilder
                        .quantize_z(
                            z=z,
                            base_z=base_z,
                            terrace_step_mm=(
                                terrace_step_mm
                            ),
                        ),
                    )
                )

            quantized_rows.append(
                quantized_row
            )

        return quantized_rows

    @staticmethod
    def build_cell_level_grid(
        top_points,
        base_z,
        terrace_step_mm,
    ):
        """
        Her dört terrain köşesi için tek bir yatay seki kotu üretir.

        R x C nokta grid'i:
        (R - 1) x (C - 1) hücre kotu oluşturur.
        """
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

            for point in row:
                if (
                    not isinstance(point, (tuple, list))
                    or len(point) < 3
                ):
                    raise ValueError(
                        "top_points must contain XYZ points"
                    )

        cell_levels = []

        for row_index in range(
            len(top_points) - 1
        ):
            level_row = []

            upper_row = top_points[row_index]
            lower_row = top_points[row_index + 1]

            for column_index in range(
                column_count - 1
            ):
                p00 = upper_row[column_index]
                p10 = upper_row[column_index + 1]
                p01 = lower_row[column_index]
                p11 = lower_row[column_index + 1]

                average_z = (
                    float(p00[2])
                    + float(p10[2])
                    + float(p01[2])
                    + float(p11[2])
                ) / 4.0

                level_row.append(
                    AtlasTerrainTerraceBuilder.quantize_z(
                        z=average_z,
                        base_z=base_z,
                        terrace_step_mm=terrace_step_mm,
                    )
                )

            cell_levels.append(level_row)

        return cell_levels


    @staticmethod
    def build_terraced_surface_triangles(
        top_points,
        cell_levels,
    ):
        """
        Build horizontal terrace tops and internal vertical risers.

        This method does not create:
        - bottom faces
        - outer perimeter walls
        - a complete closed slab

        Those will be added by the closed terrace mesh stage.
        """
        if not top_points or len(top_points) < 2:
            raise ValueError(
                "top_points must contain at least 2 rows "
                "and 2 columns"
            )

        point_row_count = len(top_points)
        point_column_count = len(top_points[0])

        if point_column_count < 2:
            raise ValueError(
                "top_points must contain at least 2 rows "
                "and 2 columns"
            )

        for row in top_points:
            if len(row) != point_column_count:
                raise ValueError(
                    "top_points must form a rectangular grid"
                )

        expected_cell_rows = point_row_count - 1
        expected_cell_columns = point_column_count - 1

        if len(cell_levels) != expected_cell_rows:
            raise ValueError(
                "cell_levels dimensions must match "
                "the top_points cell grid"
            )

        for row in cell_levels:
            if len(row) != expected_cell_columns:
                raise ValueError(
                    "cell_levels dimensions must match "
                    "the top_points cell grid"
                )

        triangles = []

        # Horizontal terrace tops.
        for row_index in range(expected_cell_rows):
            for column_index in range(
                expected_cell_columns
            ):
                level = float(
                    cell_levels[row_index][column_index]
                )

                p00_source = (
                    top_points[row_index][column_index]
                )
                p10_source = (
                    top_points[row_index][column_index + 1]
                )
                p01_source = (
                    top_points[row_index + 1][column_index]
                )
                p11_source = (
                    top_points[row_index + 1][column_index + 1]
                )

                p00 = (
                    float(p00_source[0]),
                    float(p00_source[1]),
                    level,
                )
                p10 = (
                    float(p10_source[0]),
                    float(p10_source[1]),
                    level,
                )
                p01 = (
                    float(p01_source[0]),
                    float(p01_source[1]),
                    level,
                )
                p11 = (
                    float(p11_source[0]),
                    float(p11_source[1]),
                    level,
                )

                triangles.append(
                    (
                        p00,
                        p10,
                        p11,
                    )
                )
                triangles.append(
                    (
                        p00,
                        p11,
                        p01,
                    )
                )

        # Risers between horizontal neighbours.
        for row_index in range(expected_cell_rows):
            for column_index in range(
                expected_cell_columns - 1
            ):
                left_level = float(
                    cell_levels[row_index][column_index]
                )
                right_level = float(
                    cell_levels[row_index][column_index + 1]
                )

                if abs(left_level - right_level) <= 1e-12:
                    continue

                low_level = min(
                    left_level,
                    right_level,
                )
                high_level = max(
                    left_level,
                    right_level,
                )

                edge_start = (
                    top_points[row_index][column_index + 1]
                )
                edge_end = (
                    top_points[row_index + 1][column_index + 1]
                )

                low_start = (
                    float(edge_start[0]),
                    float(edge_start[1]),
                    low_level,
                )
                low_end = (
                    float(edge_end[0]),
                    float(edge_end[1]),
                    low_level,
                )
                high_start = (
                    float(edge_start[0]),
                    float(edge_start[1]),
                    high_level,
                )
                high_end = (
                    float(edge_end[0]),
                    float(edge_end[1]),
                    high_level,
                )

                triangles.append(
                    (
                        low_start,
                        high_end,
                        high_start,
                    )
                )
                triangles.append(
                    (
                        low_start,
                        low_end,
                        high_end,
                    )
                )

        # Risers between vertical neighbours.
        for row_index in range(
            expected_cell_rows - 1
        ):
            for column_index in range(
                expected_cell_columns
            ):
                lower_level = float(
                    cell_levels[row_index][column_index]
                )
                upper_level = float(
                    cell_levels[row_index + 1][column_index]
                )

                if abs(lower_level - upper_level) <= 1e-12:
                    continue

                low_level = min(
                    lower_level,
                    upper_level,
                )
                high_level = max(
                    lower_level,
                    upper_level,
                )

                edge_start = (
                    top_points[row_index + 1][column_index]
                )
                edge_end = (
                    top_points[row_index + 1][column_index + 1]
                )

                low_start = (
                    float(edge_start[0]),
                    float(edge_start[1]),
                    low_level,
                )
                low_end = (
                    float(edge_end[0]),
                    float(edge_end[1]),
                    low_level,
                )
                high_start = (
                    float(edge_start[0]),
                    float(edge_start[1]),
                    high_level,
                )
                high_end = (
                    float(edge_end[0]),
                    float(edge_end[1]),
                    high_level,
                )

                triangles.append(
                    (
                        low_start,
                        high_start,
                        high_end,
                    )
                )
                triangles.append(
                    (
                        low_start,
                        high_end,
                        low_end,
                    )
                )

        return triangles

    @staticmethod
    def build_closed_terraced_mesh(
        top_points,
        cell_levels,
        bottom_z,
        terrace_step_mm=None,
    ):
        """
        Build a closed terraced terrain slab.

        Every terrain cell is represented as a vertical prism. Vertical
        walls are subdivided at all terrace levels. Identical internal
        faces shared by neighbouring cells are removed deterministically.

        The resulting union contains:
        - horizontal terrace tops
        - visible internal risers
        - flat bottom faces
        - outer perimeter walls
        """
        AtlasTerrainTerraceBuilder._validate_cell_level_dimensions(
            top_points=top_points,
            cell_levels=cell_levels,
        )

        bottom_z = float(bottom_z)

        flat_levels = [
            float(level)
            for row in cell_levels
            for level in row
        ]

        minimum_level = min(flat_levels)

        if bottom_z >= minimum_level - 1e-12:
            raise ValueError(
                "bottom_z must be below every terrace level"
            )

        unique_levels = sorted(
            {
                round(level, 12)
                for level in flat_levels
            }
        )

        vertical_breaks = [
            round(bottom_z, 12),
            *unique_levels,
        ]

        triangle_map = {}

        cell_row_count = len(cell_levels)
        cell_column_count = len(cell_levels[0])

        for row_index in range(cell_row_count):
            for column_index in range(
                cell_column_count
            ):
                level = float(
                    cell_levels[row_index][column_index]
                )

                source_p00 = (
                    top_points[row_index][column_index]
                )
                source_p10 = (
                    top_points[row_index][column_index + 1]
                )
                source_p01 = (
                    top_points[row_index + 1][column_index]
                )
                source_p11 = (
                    top_points[row_index + 1][column_index + 1]
                )

                p00 = (
                    float(source_p00[0]),
                    float(source_p00[1]),
                    level,
                )
                p10 = (
                    float(source_p10[0]),
                    float(source_p10[1]),
                    level,
                )
                p01 = (
                    float(source_p01[0]),
                    float(source_p01[1]),
                    level,
                )
                p11 = (
                    float(source_p11[0]),
                    float(source_p11[1]),
                    level,
                )

                b00 = (
                    p00[0],
                    p00[1],
                    bottom_z,
                )
                b10 = (
                    p10[0],
                    p10[1],
                    bottom_z,
                )
                b01 = (
                    p01[0],
                    p01[1],
                    bottom_z,
                )
                b11 = (
                    p11[0],
                    p11[1],
                    bottom_z,
                )

                # Horizontal top.
                AtlasTerrainTerraceBuilder._toggle_triangle(
                    triangle_map,
                    (
                        p00,
                        p10,
                        p11,
                    ),
                )
                AtlasTerrainTerraceBuilder._toggle_triangle(
                    triangle_map,
                    (
                        p00,
                        p11,
                        p01,
                    ),
                )

                # Flat bottom, outward orientation.
                AtlasTerrainTerraceBuilder._toggle_triangle(
                    triangle_map,
                    (
                        b00,
                        b11,
                        b10,
                    ),
                )
                AtlasTerrainTerraceBuilder._toggle_triangle(
                    triangle_map,
                    (
                        b00,
                        b01,
                        b11,
                    ),
                )

                cell_edges = (
                    (
                        source_p00,
                        source_p10,
                    ),
                    (
                        source_p10,
                        source_p11,
                    ),
                    (
                        source_p11,
                        source_p01,
                    ),
                    (
                        source_p01,
                        source_p00,
                    ),
                )

                active_breaks = [
                    value
                    for value in vertical_breaks
                    if value <= level + 1e-12
                ]

                if active_breaks[-1] < level - 1e-12:
                    active_breaks.append(level)

                for edge_start, edge_end in cell_edges:
                    canonical_start, canonical_end = sorted(
                        (
                            (
                                float(edge_start[0]),
                                float(edge_start[1]),
                            ),
                            (
                                float(edge_end[0]),
                                float(edge_end[1]),
                            ),
                        )
                    )

                    x1, y1 = canonical_start
                    x2, y2 = canonical_end

                    for break_index in range(
                        len(active_breaks) - 1
                    ):
                        lower_z = float(
                            active_breaks[break_index]
                        )
                        upper_z = float(
                            active_breaks[break_index + 1]
                        )

                        if upper_z - lower_z <= 1e-12:
                            continue

                        lower_start = (
                            x1,
                            y1,
                            lower_z,
                        )
                        lower_end = (
                            x2,
                            y2,
                            lower_z,
                        )
                        upper_start = (
                            x1,
                            y1,
                            upper_z,
                        )
                        upper_end = (
                            x2,
                            y2,
                            upper_z,
                        )

                        AtlasTerrainTerraceBuilder._toggle_triangle(
                            triangle_map,
                            (
                                lower_start,
                                lower_end,
                                upper_end,
                            ),
                        )
                        AtlasTerrainTerraceBuilder._toggle_triangle(
                            triangle_map,
                            (
                                lower_start,
                                upper_end,
                                upper_start,
                            ),
                        )

        triangles = list(
            triangle_map.values()
        )

        metadata = {
            "closed": True,
            "terraced": True,
            "terrace_step_mm": (
                None
                if terrace_step_mm is None
                else float(terrace_step_mm)
            ),
            "bottom_z": bottom_z,
            "cell_rows": cell_row_count,
            "cell_columns": cell_column_count,
            "terrace_level_count": len(
                unique_levels
            ),
            "terrace_levels": unique_levels,
            "triangle_count": len(triangles),
        }

        return {
            "type": "terrain_terraced_closed_slab",
            "triangles": triangles,
            "metadata": metadata,
            "top_points": top_points,
            "cell_levels": [
                list(row)
                for row in cell_levels
            ],
        }

    @staticmethod
    def _validate_cell_level_dimensions(
        top_points,
        cell_levels,
    ):
        if not top_points or len(top_points) < 2:
            raise ValueError(
                "top_points must contain at least 2 rows "
                "and 2 columns"
            )

        point_column_count = len(
            top_points[0]
        )

        if point_column_count < 2:
            raise ValueError(
                "top_points must contain at least 2 rows "
                "and 2 columns"
            )

        for row in top_points:
            if len(row) != point_column_count:
                raise ValueError(
                    "top_points must form a rectangular grid"
                )

        expected_rows = len(top_points) - 1
        expected_columns = (
            point_column_count - 1
        )

        if len(cell_levels) != expected_rows:
            raise ValueError(
                "cell_levels dimensions must match "
                "the top_points cell grid"
            )

        for row in cell_levels:
            if len(row) != expected_columns:
                raise ValueError(
                    "cell_levels dimensions must match "
                    "the top_points cell grid"
                )

    @staticmethod
    def _toggle_triangle(
        triangle_map,
        triangle,
    ):
        normalized_triangle = tuple(
            tuple(
                round(float(value), 12)
                for value in point
            )
            for point in triangle
        )

        key = tuple(
            sorted(normalized_triangle)
        )

        if key in triangle_map:
            del triangle_map[key]
            return

        triangle_map[key] = normalized_triangle
