import copy
import math

from CORE.atlas_terrain_mesh_generator import (
    AtlasTerrainMeshGenerator,
)


class AtlasTerrainPresentationSurfaceRegularizer:
    """
    Product-facing terrain surface regularization.

    Canonical terrain truth in mesh["grid"] is preserved.
    Only visible top-point Z values may be regularized.
    """

    @staticmethod
    def _validate_passes(value):
        try:
            parsed = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "passes must be a non-negative integer"
            ) from exc

        if parsed < 0:
            raise ValueError(
                "passes must be a non-negative integer"
            )

        return parsed

    @staticmethod
    def _validate_strength(value):
        try:
            parsed = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "strength must be between 0 and 1"
            ) from exc

        if (
            not math.isfinite(parsed)
            or parsed < 0.0
            or parsed > 1.0
        ):
            raise ValueError(
                "strength must be between 0 and 1"
            )

        return parsed

    @classmethod
    def regularize(
        cls,
        *,
        mesh,
        passes=1,
        strength=0.50,
    ):
        passes = cls._validate_passes(passes)
        strength = cls._validate_strength(strength)

        result = copy.deepcopy(mesh)

        top_points = result.get("top_points")

        if not top_points:
            raise ValueError(
                "mesh requires top_points"
            )

        row_count = len(top_points)
        column_count = len(top_points[0])

        if (
            row_count < 2
            or column_count < 2
            or any(
                len(row) != column_count
                for row in top_points
            )
        ):
            raise ValueError(
                "top_points must form a rectangular grid"
            )

        current = [
            [
                (
                    float(point[0]),
                    float(point[1]),
                    float(point[2]),
                )
                for point in row
            ]
            for row in top_points
        ]

        for _ in range(passes):
            next_points = [
                list(row)
                for row in current
            ]

            for row_index in range(
                1,
                row_count - 1,
            ):
                for column_index in range(
                    1,
                    column_count - 1,
                ):
                    point = current[
                        row_index
                    ][column_index]

                    neighbor_z = [
                        current[
                            neighbor_row
                        ][neighbor_column][2]
                        for neighbor_row in range(
                            row_index - 1,
                            row_index + 2,
                        )
                        for neighbor_column in range(
                            column_index - 1,
                            column_index + 2,
                        )
                        if not (
                            neighbor_row == row_index
                            and neighbor_column == column_index
                        )
                    ]

                    mean_z = (
                        sum(neighbor_z)
                        / len(neighbor_z)
                    )

                    resolved_z = (
                        point[2]
                        + (
                            mean_z
                            - point[2]
                        )
                        * strength
                    )

                    next_points[
                        row_index
                    ][column_index] = (
                        point[0],
                        point[1],
                        float(resolved_z),
                    )

            current = [
                tuple(row)
                for row in next_points
            ]

        presentation_top_points = [
            list(row)
            for row in current
        ]

        result["presentation_top_points"] = (
            presentation_top_points
        )

        bottom_points = result.get(
            "bottom_points"
        )

        if bottom_points:
            grid_size = int(
                result.get(
                    "metadata",
                    {},
                ).get(
                    "grid_size",
                    row_count,
                )
            )

            result["triangles"] = [
                *AtlasTerrainMeshGenerator.build_surface_triangles(
                    points=presentation_top_points,
                    grid_size=grid_size,
                ),
                *AtlasTerrainMeshGenerator.build_bottom_triangles(
                    bottom_points=bottom_points,
                    grid_size=grid_size,
                ),
                *AtlasTerrainMeshGenerator.build_side_wall_triangles(
                    top_points=result["top_points"],
                    bottom_points=bottom_points,
                    grid_size=grid_size,
                ),
            ]

        metadata = dict(
            result.get("metadata", {})
        )

        metadata["presentation_regularized"] = True
        metadata["presentation_regularization_passes"] = passes
        metadata["presentation_regularization_strength"] = strength

        result["metadata"] = metadata

        return result
