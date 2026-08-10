"""
ATLAS WorldCover Surface Aggregator v0.1

WorldCover hücre merkezlerini deterministik biçimde birleşik
dikdörtgen yüzey kayıtlarına dönüştürür.

Davranış:
- forest ve grass sınıfları desteklenir.
- Aynı satırdaki bitişik hücreler yatay run olarak birleşir.
- Aynı sütun aralığına sahip ardışık run'lar düşey birleşir.
- Yinelenen hücreler kaldırılır.
- Sonuç giriş sırasından bağımsızdır.
"""

import math

from shapely.geometry import Point, box
from shapely.ops import unary_union


class AtlasWorldCoverSurfaceAggregator:
    SUPPORTED_SURFACE_TYPES = {
        "forest",
        "grass",
    }

    DEFAULT_GRID_STEP_DEGREES = 1.0 / 12000.0

    @staticmethod
    def aggregate(
        cells,
        surface_type,
        grid_step_degrees=None,
    ):
        if surface_type not in (
            AtlasWorldCoverSurfaceAggregator
            .SUPPORTED_SURFACE_TYPES
        ):
            raise ValueError(
                "surface_type must be one of: "
                f"{sorted(AtlasWorldCoverSurfaceAggregator.SUPPORTED_SURFACE_TYPES)}"
            )

        if not cells:
            return []

        step = (
            AtlasWorldCoverSurfaceAggregator
            ._resolve_grid_step(
                cells=cells,
                explicit_step=grid_step_degrees,
            )
        )

        indexed_cells = (
            AtlasWorldCoverSurfaceAggregator
            ._index_cells(
                cells=cells,
                step=step,
            )
        )

        if not indexed_cells:
            return []

        row_runs = (
            AtlasWorldCoverSurfaceAggregator
            ._build_row_runs(indexed_cells)
        )

        rectangles = (
            AtlasWorldCoverSurfaceAggregator
            ._merge_vertical_runs(row_runs)
        )

        origin_lat = min(
            item["lat"]
            for item in indexed_cells.values()
        )
        origin_lon = min(
            item["lon"]
            for item in indexed_cells.values()
        )

        surfaces = []

        for index, rectangle in enumerate(rectangles):
            row_start = rectangle["row_start"]
            row_end = rectangle["row_end"]
            col_start = rectangle["col_start"]
            col_end = rectangle["col_end"]

            south = (
                origin_lat
                + row_start * step
                - step / 2.0
            )
            north = (
                origin_lat
                + row_end * step
                + step / 2.0
            )
            west = (
                origin_lon
                + col_start * step
                - step / 2.0
            )
            east = (
                origin_lon
                + col_end * step
                + step / 2.0
            )

            cell_count = (
                (row_end - row_start + 1)
                * (col_end - col_start + 1)
            )

            surfaces.append(
                {
                    "id": (
                        "worldcover_"
                        f"{surface_type}_"
                        f"{index}"
                    ),
                    "surface_type": surface_type,
                    "source": "worldcover",
                    "cell_count": cell_count,
                    "resolution_m": 10,
                    "geometry": [
                        (south, west),
                        (south, east),
                        (north, east),
                        (north, west),
                    ],
                    "tags": {
                        "source": "worldcover",
                        "surface_type": surface_type,
                        "cell_count": cell_count,
                    },
                }
            )

        return surfaces

    @staticmethod
    def dissolve(
        cells,
        surface_type,
        min_cell_count=1,
        grid_step_degrees=None,
        reject_holes=True,
    ):
        if surface_type not in (
            AtlasWorldCoverSurfaceAggregator
            .SUPPORTED_SURFACE_TYPES
        ):
            raise ValueError(
                "surface_type must be one of: "
                f"{sorted(AtlasWorldCoverSurfaceAggregator.SUPPORTED_SURFACE_TYPES)}"
            )

        if min_cell_count < 1:
            raise ValueError(
                "min_cell_count must be at least 1"
            )

        if not cells:
            return []

        step = (
            AtlasWorldCoverSurfaceAggregator
            ._resolve_grid_step(
                cells=cells,
                explicit_step=grid_step_degrees,
            )
        )

        indexed_cells = (
            AtlasWorldCoverSurfaceAggregator
            ._index_cells(
                cells=cells,
                step=step,
            )
        )

        if not indexed_cells:
            return []

        origin_lat = min(
            cell["lat"]
            for cell in indexed_cells.values()
        )
        origin_lon = min(
            cell["lon"]
            for cell in indexed_cells.values()
        )

        cell_boxes = [
            box(
                column - 0.5,
                row - 0.5,
                column + 0.5,
                row + 0.5,
            )
            for row, column in sorted(indexed_cells)
        ]

        dissolved = unary_union(cell_boxes)

        if dissolved.is_empty:
            return []

        if dissolved.geom_type == "Polygon":
            polygons = [dissolved]
        elif dissolved.geom_type == "MultiPolygon":
            polygons = list(dissolved.geoms)
        else:
            polygons = [
                geometry
                for geometry in dissolved.geoms
                if geometry.geom_type == "Polygon"
            ]

        class_id = (
            10
            if surface_type == "forest"
            else 30
        )

        candidates = []

        for polygon in polygons:
            cell_count = int(
                round(polygon.area)
            )

            if cell_count < min_cell_count:
                continue

            if reject_holes and polygon.interiors:
                component_cells = [
                    indexed_cells[(row, column)]
                    for row, column in sorted(
                        indexed_cells
                    )
                    if polygon.covers(
                        Point(
                            column,
                            row,
                        )
                    )
                ]

                decomposed_surfaces = (
                    AtlasWorldCoverSurfaceAggregator
                    .aggregate(
                        cells=component_cells,
                        surface_type=surface_type,
                        grid_step_degrees=step,
                    )
                )

                for surface in decomposed_surfaces:
                    geometry = list(
                        surface["geometry"]
                    )

                    if len(geometry) < 3:
                        continue

                    latitudes = [
                        point[0]
                        for point in geometry
                    ]
                    longitudes = [
                        point[1]
                        for point in geometry
                    ]

                    decomposed_cell_count = int(
                        surface["cell_count"]
                    )

                    candidates.append(
                        {
                            "surface_type": surface_type,
                            "source": "worldcover",
                            "cell_count": (
                                decomposed_cell_count
                            ),
                            "resolution_m": 10,
                            "park_type": (
                                f"worldcover:{surface_type}"
                            ),
                            "geometry": geometry,
                            "tags": {
                                "source": "worldcover",
                                "class_id": class_id,
                                "surface_type": (
                                    surface_type
                                ),
                                "cell_count": (
                                    decomposed_cell_count
                                ),
                            },
                            "_sort_key": (
                                round(
                                    min(latitudes),
                                    12,
                                ),
                                round(
                                    min(longitudes),
                                    12,
                                ),
                                round(
                                    max(latitudes),
                                    12,
                                ),
                                round(
                                    max(longitudes),
                                    12,
                                ),
                                decomposed_cell_count,
                            ),
                        }
                    )

                continue

            coordinates = list(
                polygon.exterior.coords
            )

            if (
                len(coordinates) >= 2
                and coordinates[0] == coordinates[-1]
            ):
                coordinates = coordinates[:-1]

            coordinates = (
                AtlasWorldCoverSurfaceAggregator
                ._remove_collinear_points(
                    coordinates
                )
            )

            geometry = [
                (
                    float(
                        origin_lat
                        + latitude * step
                    ),
                    float(
                        origin_lon
                        + longitude * step
                    ),
                )
                for longitude, latitude in coordinates
            ]

            if len(geometry) < 3:
                continue

            (
                min_column,
                min_row,
                max_column,
                max_row,
            ) = polygon.bounds

            min_lat = origin_lat + min_row * step
            min_lon = origin_lon + min_column * step
            max_lat = origin_lat + max_row * step
            max_lon = origin_lon + max_column * step

            candidates.append(
                {
                    "surface_type": surface_type,
                    "source": "worldcover",
                    "cell_count": cell_count,
                    "resolution_m": 10,
                    "park_type": (
                        f"worldcover:{surface_type}"
                    ),
                    "geometry": geometry,
                    "tags": {
                        "source": "worldcover",
                        "class_id": class_id,
                        "surface_type": surface_type,
                        "cell_count": cell_count,
                    },
                    "_sort_key": (
                        round(min_lat, 12),
                        round(min_lon, 12),
                        round(max_lat, 12),
                        round(max_lon, 12),
                        cell_count,
                    ),
                }
            )

        candidates.sort(
            key=lambda item: item["_sort_key"]
        )

        surfaces = []

        for index, item in enumerate(candidates):
            item = dict(item)
            item.pop("_sort_key")

            item["id"] = (
                "worldcover_"
                f"{surface_type}_surface_"
                f"{index}"
            )

            surfaces.append(item)

        return surfaces

    @staticmethod
    def _remove_collinear_points(points):
        if len(points) <= 3:
            return list(points)

        cleaned = []
        point_count = len(points)

        for index in range(point_count):
            previous_point = points[
                (index - 1) % point_count
            ]
            current_point = points[index]
            next_point = points[
                (index + 1) % point_count
            ]

            previous_x, previous_y = previous_point
            current_x, current_y = current_point
            next_x, next_y = next_point

            cross_product = (
                (current_x - previous_x)
                * (next_y - current_y)
                - (
                    current_y - previous_y
                )
                * (next_x - current_x)
            )

            if abs(cross_product) <= 1e-12:
                continue

            cleaned.append(current_point)

        return cleaned

    @staticmethod
    def _resolve_grid_step(
        cells,
        explicit_step,
    ):
        if explicit_step is not None:
            step = float(explicit_step)

            if not math.isfinite(step) or step <= 0.0:
                raise ValueError(
                    "grid_step_degrees must be positive"
                )

            return step

        candidate_steps = []

        for key in ("lat", "lon"):
            values = sorted({
                round(float(cell[key]), 12)
                for cell in cells
                if key in cell
            })

            for index in range(len(values) - 1):
                delta = values[index + 1] - values[index]

                if delta > 0.0:
                    candidate_steps.append(delta)

        if candidate_steps:
            return min(candidate_steps)

        return (
            AtlasWorldCoverSurfaceAggregator
            .DEFAULT_GRID_STEP_DEGREES
        )

    @staticmethod
    def _index_cells(
        cells,
        step,
    ):
        valid_cells = []

        for cell in cells:
            try:
                lat = float(cell["lat"])
                lon = float(cell["lon"])
            except (KeyError, TypeError, ValueError):
                continue

            if not (
                math.isfinite(lat)
                and math.isfinite(lon)
            ):
                continue

            valid_cells.append(
                {
                    "lat": lat,
                    "lon": lon,
                }
            )

        if not valid_cells:
            return {}

        origin_lat = min(
            item["lat"]
            for item in valid_cells
        )
        origin_lon = min(
            item["lon"]
            for item in valid_cells
        )

        indexed = {}

        for item in valid_cells:
            row = round(
                (item["lat"] - origin_lat)
                / step
            )
            column = round(
                (item["lon"] - origin_lon)
                / step
            )

            indexed[(row, column)] = item

        return indexed

    @staticmethod
    def _build_row_runs(indexed_cells):
        columns_by_row = {}

        for row, column in indexed_cells:
            columns_by_row.setdefault(
                row,
                [],
            ).append(column)

        row_runs = []

        for row in sorted(columns_by_row):
            columns = sorted(
                set(columns_by_row[row])
            )

            start = columns[0]
            previous = columns[0]

            for column in columns[1:]:
                if column == previous + 1:
                    previous = column
                    continue

                row_runs.append(
                    {
                        "row": row,
                        "col_start": start,
                        "col_end": previous,
                    }
                )

                start = column
                previous = column

            row_runs.append(
                {
                    "row": row,
                    "col_start": start,
                    "col_end": previous,
                }
            )

        return row_runs

    @staticmethod
    def _merge_vertical_runs(row_runs):
        grouped = {}

        for run in row_runs:
            key = (
                run["col_start"],
                run["col_end"],
            )

            grouped.setdefault(
                key,
                [],
            ).append(run["row"])

        rectangles = []

        for (
            col_start,
            col_end,
        ), rows in sorted(grouped.items()):
            rows = sorted(set(rows))

            row_start = rows[0]
            previous_row = rows[0]

            for row in rows[1:]:
                if row == previous_row + 1:
                    previous_row = row
                    continue

                rectangles.append(
                    {
                        "row_start": row_start,
                        "row_end": previous_row,
                        "col_start": col_start,
                        "col_end": col_end,
                    }
                )

                row_start = row
                previous_row = row

            rectangles.append(
                {
                    "row_start": row_start,
                    "row_end": previous_row,
                    "col_start": col_start,
                    "col_end": col_end,
                }
            )

        rectangles.sort(
            key=lambda item: (
                item["row_start"],
                item["col_start"],
                item["row_end"],
                item["col_end"],
            )
        )

        return rectangles
