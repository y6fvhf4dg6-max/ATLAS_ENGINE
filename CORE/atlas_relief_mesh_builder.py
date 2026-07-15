from __future__ import annotations

from typing import Any

import numpy as np


class AtlasReliefMeshBuilder:
    """
    ATLAS Relief Mesh Builder v0.1

    Builds a closed 2.5D relief solid from a normalized
    two-dimensional height map.

    Geometry:
    - sampled relief top surface
    - flat triangulated bottom surface
    - segmented perimeter walls
    """

    @staticmethod
    def build(
        height_map: Any,
        *,
        width_mm: float,
        depth_mm: float,
        base_thickness_mm: float = 0.80,
        relief_height_mm: float = 2.00,
        origin_x: float = 0.0,
        origin_y: float = 0.0,
        origin_z: float = 0.0,
    ) -> dict:
        values = np.asarray(
            height_map,
            dtype=np.float64,
        )

        AtlasReliefMeshBuilder._validate(
            values=values,
            width_mm=width_mm,
            depth_mm=depth_mm,
            base_thickness_mm=base_thickness_mm,
            relief_height_mm=relief_height_mm,
        )

        row_count, column_count = values.shape

        x_coordinates = np.linspace(
            origin_x,
            origin_x + width_mm,
            column_count,
            dtype=np.float64,
        )

        y_coordinates = np.linspace(
            origin_y,
            origin_y + depth_mm,
            row_count,
            dtype=np.float64,
        )

        bottom_z = float(origin_z)
        relief_base_z = (
            bottom_z + float(base_thickness_mm)
        )

        bottom_grid = []
        top_grid = []

        for row_index, y in enumerate(
            y_coordinates
        ):
            bottom_row = []
            top_row = []

            for column_index, x in enumerate(
                x_coordinates
            ):
                bottom_point = (
                    float(x),
                    float(y),
                    bottom_z,
                )

                top_point = (
                    float(x),
                    float(y),
                    relief_base_z
                    + float(
                        values[
                            row_index,
                            column_index,
                        ]
                    )
                    * float(relief_height_mm),
                )

                bottom_row.append(bottom_point)
                top_row.append(top_point)

            bottom_grid.append(bottom_row)
            top_grid.append(top_row)

        triangles = []

        AtlasReliefMeshBuilder._add_top_surface(
            triangles=triangles,
            grid=top_grid,
        )

        AtlasReliefMeshBuilder._add_bottom_surface(
            triangles=triangles,
            grid=bottom_grid,
        )

        AtlasReliefMeshBuilder._add_perimeter_walls(
            triangles=triangles,
            bottom_grid=bottom_grid,
            top_grid=top_grid,
        )

        return {
            "type": "relief_mesh",
            "geometry_type": "height_map_relief",
            "triangles": triangles,
            "bottom_grid": bottom_grid,
            "top_grid": top_grid,
            "height_map": values.copy(),
            "row_count": row_count,
            "column_count": column_count,
            "width_mm": float(width_mm),
            "depth_mm": float(depth_mm),
            "base_thickness_mm": float(
                base_thickness_mm
            ),
            "relief_height_mm": float(
                relief_height_mm
            ),
            "origin": (
                float(origin_x),
                float(origin_y),
                float(origin_z),
            ),
            "minimum_z": bottom_z,
            "maximum_z": max(
                point[2]
                for row in top_grid
                for point in row
            ),
        }

    @staticmethod
    def _validate(
        *,
        values: np.ndarray,
        width_mm: float,
        depth_mm: float,
        base_thickness_mm: float,
        relief_height_mm: float,
    ) -> None:
        if values.ndim != 2:
            raise ValueError(
                "Relief height map must be "
                "two-dimensional."
            )

        if (
            values.shape[0] < 2
            or values.shape[1] < 2
        ):
            raise ValueError(
                "Relief height map must contain "
                "at least two rows and two columns."
            )

        if not np.isfinite(values).all():
            raise ValueError(
                "Relief height map contains "
                "non-finite values."
            )

        tolerance = 1e-12

        if (
            float(values.min()) < -tolerance
            or float(values.max()) > 1.0 + tolerance
        ):
            raise ValueError(
                "Relief height map values must be "
                "normalized to the 0.0..1.0 range."
            )

        parameters = {
            "width_mm": width_mm,
            "depth_mm": depth_mm,
            "base_thickness_mm": (
                base_thickness_mm
            ),
            "relief_height_mm": relief_height_mm,
        }

        for name, value in parameters.items():
            if not np.isfinite(value):
                raise ValueError(
                    f"{name} must be finite."
                )

        if width_mm <= 0.0:
            raise ValueError(
                "width_mm must be greater than zero."
            )

        if depth_mm <= 0.0:
            raise ValueError(
                "depth_mm must be greater than zero."
            )

        if base_thickness_mm <= 0.0:
            raise ValueError(
                "base_thickness_mm must be "
                "greater than zero."
            )

        if relief_height_mm < 0.0:
            raise ValueError(
                "relief_height_mm must not be "
                "negative."
            )

    @staticmethod
    def _add_top_surface(
        *,
        triangles: list,
        grid: list,
    ) -> None:
        row_count = len(grid)
        column_count = len(grid[0])

        for row in range(row_count - 1):
            for column in range(
                column_count - 1
            ):
                lower_left = grid[row][column]
                lower_right = grid[row][
                    column + 1
                ]
                upper_left = grid[row + 1][column]
                upper_right = grid[row + 1][
                    column + 1
                ]

                triangles.append(
                    (
                        lower_left,
                        lower_right,
                        upper_right,
                    )
                )
                triangles.append(
                    (
                        lower_left,
                        upper_right,
                        upper_left,
                    )
                )

    @staticmethod
    def _add_bottom_surface(
        *,
        triangles: list,
        grid: list,
    ) -> None:
        row_count = len(grid)
        column_count = len(grid[0])

        for row in range(row_count - 1):
            for column in range(
                column_count - 1
            ):
                lower_left = grid[row][column]
                lower_right = grid[row][
                    column + 1
                ]
                upper_left = grid[row + 1][column]
                upper_right = grid[row + 1][
                    column + 1
                ]

                triangles.append(
                    (
                        lower_left,
                        upper_right,
                        lower_right,
                    )
                )
                triangles.append(
                    (
                        lower_left,
                        upper_left,
                        upper_right,
                    )
                )

    @staticmethod
    def _add_perimeter_walls(
        *,
        triangles: list,
        bottom_grid: list,
        top_grid: list,
    ) -> None:
        row_count = len(top_grid)
        column_count = len(top_grid[0])

        for column in range(column_count - 1):
            AtlasReliefMeshBuilder._add_wall_quad(
                triangles,
                bottom_grid[0][column],
                bottom_grid[0][column + 1],
                top_grid[0][column + 1],
                top_grid[0][column],
            )

        for row in range(row_count - 1):
            AtlasReliefMeshBuilder._add_wall_quad(
                triangles,
                bottom_grid[row][
                    column_count - 1
                ],
                bottom_grid[row + 1][
                    column_count - 1
                ],
                top_grid[row + 1][
                    column_count - 1
                ],
                top_grid[row][
                    column_count - 1
                ],
            )

        for column in range(
            column_count - 1,
            0,
            -1,
        ):
            AtlasReliefMeshBuilder._add_wall_quad(
                triangles,
                bottom_grid[row_count - 1][column],
                bottom_grid[row_count - 1][
                    column - 1
                ],
                top_grid[row_count - 1][
                    column - 1
                ],
                top_grid[row_count - 1][column],
            )

        for row in range(
            row_count - 1,
            0,
            -1,
        ):
            AtlasReliefMeshBuilder._add_wall_quad(
                triangles,
                bottom_grid[row][0],
                bottom_grid[row - 1][0],
                top_grid[row - 1][0],
                top_grid[row][0],
            )

    @staticmethod
    def _add_wall_quad(
        triangles: list,
        bottom_a: tuple,
        bottom_b: tuple,
        top_b: tuple,
        top_a: tuple,
    ) -> None:
        triangles.append(
            (
                bottom_a,
                bottom_b,
                top_b,
            )
        )
        triangles.append(
            (
                bottom_a,
                top_b,
                top_a,
            )
        )
