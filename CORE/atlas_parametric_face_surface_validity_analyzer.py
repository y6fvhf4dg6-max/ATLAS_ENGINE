from __future__ import annotations

import math
from typing import Any

import numpy as np

from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)
from CORE.atlas_parametric_face_surface_validity_result import (
    AtlasParametricFaceSurfaceValidityResult,
)


class AtlasParametricFaceSurfaceValidityAnalyzer:
    """
    Analyzes regular-grid parametric face surface validity.

    The analyzer measures:

    - signed XY orientation of both triangles in every cell
    - folded and degenerate grid cells
    - normalized point-normal Z components
    - inverted or insufficiently front-facing normals
    - minimum horizontal and vertical 3D edge lengths

    It performs no deformation, repair, rendering,
    triangulation, relief compression, or mesh generation.
    """

    DEFAULT_AREA_TOLERANCE = 1e-12
    DEFAULT_NORMAL_Z_TOLERANCE = 0.0
    DEFAULT_EDGE_LENGTH_TOLERANCE = 1e-12

    NORMAL_MAGNITUDE_EPSILON = 1e-12

    @classmethod
    def analyze(
        cls,
        surface: AtlasParametricFaceSurface,
        *,
        area_tolerance: float = DEFAULT_AREA_TOLERANCE,
        normal_z_tolerance: float = (
            DEFAULT_NORMAL_Z_TOLERANCE
        ),
        edge_length_tolerance: float = (
            DEFAULT_EDGE_LENGTH_TOLERANCE
        ),
    ) -> AtlasParametricFaceSurfaceValidityResult:
        if not isinstance(
            surface,
            AtlasParametricFaceSurface,
        ):
            raise TypeError(
                "surface must be an "
                "AtlasParametricFaceSurface instance."
            )

        normalized_area_tolerance = (
            cls._normalize_tolerance(
                area_tolerance,
                name="area_tolerance",
                require_nonnegative=True,
            )
        )

        normalized_normal_z_tolerance = (
            cls._normalize_tolerance(
                normal_z_tolerance,
                name="normal_z_tolerance",
                require_nonnegative=False,
            )
        )

        normalized_edge_length_tolerance = (
            cls._normalize_tolerance(
                edge_length_tolerance,
                name="edge_length_tolerance",
                require_nonnegative=True,
            )
        )

        (
            minimum_signed_cell_area,
            folded_cell_count,
            degenerate_cell_count,
        ) = cls._analyze_cells(
            surface,
            area_tolerance=(
                normalized_area_tolerance
            ),
        )

        (
            minimum_normal_z,
            inverted_normal_count,
        ) = cls._analyze_normals(
            surface,
            normal_z_tolerance=(
                normalized_normal_z_tolerance
            ),
        )

        (
            minimum_horizontal_edge_length,
            minimum_vertical_edge_length,
        ) = cls._analyze_edge_lengths(
            surface,
        )

        return AtlasParametricFaceSurfaceValidityResult(
            row_count=surface.row_count,
            column_count=surface.column_count,
            cell_count=(
                (surface.row_count - 1)
                * (surface.column_count - 1)
            ),
            folded_cell_count=folded_cell_count,
            degenerate_cell_count=(
                degenerate_cell_count
            ),
            inverted_normal_count=(
                inverted_normal_count
            ),
            minimum_signed_cell_area=(
                minimum_signed_cell_area
            ),
            minimum_normal_z=minimum_normal_z,
            minimum_horizontal_edge_length=(
                minimum_horizontal_edge_length
            ),
            minimum_vertical_edge_length=(
                minimum_vertical_edge_length
            ),
            area_tolerance=(
                normalized_area_tolerance
            ),
            normal_z_tolerance=(
                normalized_normal_z_tolerance
            ),
            edge_length_tolerance=(
                normalized_edge_length_tolerance
            ),
        )

    @staticmethod
    def _analyze_cells(
        surface: AtlasParametricFaceSurface,
        *,
        area_tolerance: float,
    ) -> tuple[float, int, int]:
        x_coordinates = surface.x_coordinates
        y_coordinates = surface.y_coordinates

        top_left_x = x_coordinates[:-1, :-1]
        top_left_y = y_coordinates[:-1, :-1]

        top_right_x = x_coordinates[:-1, 1:]
        top_right_y = y_coordinates[:-1, 1:]

        bottom_right_x = x_coordinates[1:, 1:]
        bottom_right_y = y_coordinates[1:, 1:]

        bottom_left_x = x_coordinates[1:, :-1]
        bottom_left_y = y_coordinates[1:, :-1]

        first_triangle_area = (
            (
                top_right_x
                - top_left_x
            )
            * (
                bottom_right_y
                - top_left_y
            )
            - (
                top_right_y
                - top_left_y
            )
            * (
                bottom_right_x
                - top_left_x
            )
        )

        second_triangle_area = (
            (
                bottom_right_x
                - top_left_x
            )
            * (
                bottom_left_y
                - top_left_y
            )
            - (
                bottom_right_y
                - top_left_y
            )
            * (
                bottom_left_x
                - top_left_x
            )
        )

        cell_minimum_area = np.minimum(
            first_triangle_area,
            second_triangle_area,
        )

        folded_mask = (
            (first_triangle_area < -area_tolerance)
            | (
                second_triangle_area
                < -area_tolerance
            )
        )

        degenerate_mask = (
            ~folded_mask
            & (
                (
                    np.abs(
                        first_triangle_area,
                    )
                    <= area_tolerance
                )
                | (
                    np.abs(
                        second_triangle_area,
                    )
                    <= area_tolerance
                )
            )
        )

        return (
            float(
                np.min(
                    cell_minimum_area,
                )
            ),
            int(
                np.count_nonzero(
                    folded_mask,
                )
            ),
            int(
                np.count_nonzero(
                    degenerate_mask,
                )
            ),
        )

    @classmethod
    def _analyze_normals(
        cls,
        surface: AtlasParametricFaceSurface,
        *,
        normal_z_tolerance: float,
    ) -> tuple[float, int]:
        x_coordinates = surface.x_coordinates
        y_coordinates = surface.y_coordinates
        z_coordinates = surface.z_coordinates

        column_tangent = np.stack(
            (
                np.gradient(
                    x_coordinates,
                    axis=1,
                ),
                np.gradient(
                    y_coordinates,
                    axis=1,
                ),
                np.gradient(
                    z_coordinates,
                    axis=1,
                ),
            ),
            axis=-1,
        )

        row_tangent = np.stack(
            (
                np.gradient(
                    x_coordinates,
                    axis=0,
                ),
                np.gradient(
                    y_coordinates,
                    axis=0,
                ),
                np.gradient(
                    z_coordinates,
                    axis=0,
                ),
            ),
            axis=-1,
        )

        normals = np.cross(
            column_tangent,
            row_tangent,
        )

        normal_magnitudes = np.linalg.norm(
            normals,
            axis=-1,
        )

        valid_normal_mask = (
            normal_magnitudes
            > cls.NORMAL_MAGNITUDE_EPSILON
        )

        normal_z = np.zeros(
            surface.shape,
            dtype=np.float64,
        )

        normal_z[
            valid_normal_mask
        ] = (
            normals[
                valid_normal_mask,
                2,
            ]
            / normal_magnitudes[
                valid_normal_mask
            ]
        )

        inverted_mask = (
            normal_z
            < normal_z_tolerance
        )

        return (
            float(
                np.min(
                    normal_z,
                )
            ),
            int(
                np.count_nonzero(
                    inverted_mask,
                )
            ),
        )

    @staticmethod
    def _analyze_edge_lengths(
        surface: AtlasParametricFaceSurface,
    ) -> tuple[float, float]:
        points = np.stack(
            (
                surface.x_coordinates,
                surface.y_coordinates,
                surface.z_coordinates,
            ),
            axis=-1,
        )

        horizontal_edges = (
            points[:, 1:, :]
            - points[:, :-1, :]
        )

        vertical_edges = (
            points[1:, :, :]
            - points[:-1, :, :]
        )

        horizontal_lengths = np.linalg.norm(
            horizontal_edges,
            axis=-1,
        )

        vertical_lengths = np.linalg.norm(
            vertical_edges,
            axis=-1,
        )

        return (
            float(
                np.min(
                    horizontal_lengths,
                )
            ),
            float(
                np.min(
                    vertical_lengths,
                )
            ),
        )

    @staticmethod
    def _normalize_tolerance(
        value: Any,
        *,
        name: str,
        require_nonnegative: bool,
    ) -> float:
        try:
            tolerance = float(
                value,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if not math.isfinite(
            tolerance,
        ):
            raise ValueError(
                f"{name} must be finite."
            )

        if (
            require_nonnegative
            and tolerance < 0.0
        ):
            raise ValueError(
                f"{name} must not be negative."
            )

        return tolerance
