from __future__ import annotations

from typing import Any

import numpy as np


class AtlasProjectedSemanticMeshDepthRasterizer:
    @staticmethod
    def _positive_float(
        value: Any,
        *,
        name: str,
    ) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{name} must be numeric"
            ) from exc

        if (
            not np.isfinite(numeric)
            or numeric <= 0.0
        ):
            raise ValueError(
                f"{name} must be finite and greater than zero"
            )

        return numeric

    @staticmethod
    def _positive_int(
        value: Any,
        *,
        name: str,
    ) -> int:
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or value <= 0
        ):
            raise ValueError(
                f"{name} must be a positive integer"
            )

        return value

    @staticmethod
    def _triangles(mesh: Any):
        if not isinstance(
            mesh,
            dict,
        ):
            raise TypeError(
                "mesh must be a dictionary"
            )

        triangles = mesh.get(
            "triangles"
        )

        if not isinstance(
            triangles,
            (list, tuple),
        ):
            raise ValueError(
                "mesh must contain triangles"
            )

        return tuple(
            triangles
        )

    @classmethod
    def rasterize(
        cls,
        *,
        mesh: dict[str, Any],
        width_mm: float,
        depth_mm: float,
        rows: int,
        columns: int,
        target=None,
    ) -> dict[str, Any]:
        physical_width = cls._positive_float(
            width_mm,
            name="width_mm",
        )
        physical_depth = cls._positive_float(
            depth_mm,
            name="depth_mm",
        )

        row_count = cls._positive_int(
            rows,
            name="rows",
        )
        column_count = cls._positive_int(
            columns,
            name="columns",
        )

        triangles = cls._triangles(
            mesh
        )

        depth_map = np.zeros(
            (
                row_count,
                column_count,
            ),
            dtype=np.float64,
        )

        coverage_map = np.zeros(
            (
                row_count,
                column_count,
            ),
            dtype=bool,
        )

        pixel_x = np.linspace(
            0.0,
            physical_width,
            column_count,
            dtype=np.float64,
        )

        pixel_y = np.linspace(
            0.0,
            physical_depth,
            row_count,
            dtype=np.float64,
        )

        epsilon = 1e-12

        for triangle in triangles:
            if (
                not isinstance(
                    triangle,
                    (list, tuple),
                )
                or len(triangle) != 3
            ):
                continue

            try:
                points = np.asarray(
                    triangle,
                    dtype=np.float64,
                )
            except (
                TypeError,
                ValueError,
            ):
                continue

            if (
                points.shape != (3, 3)
                or not np.isfinite(
                    points
                ).all()
            ):
                continue

            if target is None:
                local_points = points
                coordinate_space = (
                    "local_uv_depth"
                )
            else:
                from CORE.atlas_surface_target import (
                    AtlasSurfaceTarget,
                )

                if not isinstance(
                    target,
                    AtlasSurfaceTarget,
                ):
                    raise TypeError(
                        "target must be an AtlasSurfaceTarget"
                    )

                origin = np.asarray(
                    target.origin,
                    dtype=np.float64,
                )
                u_axis = np.asarray(
                    target.u_axis,
                    dtype=np.float64,
                )
                v_axis = np.asarray(
                    target.v_axis,
                    dtype=np.float64,
                )
                normal = np.asarray(
                    target.outward_normal,
                    dtype=np.float64,
                )

                relative = (
                    points - origin
                )

                local_points = np.column_stack(
                    (
                        relative @ u_axis,
                        relative @ v_axis,
                        relative @ normal,
                    )
                )

                coordinate_space = (
                    "target_local_uv_signed_depth"
                )

            x0, y0, z0 = local_points[0]
            x1, y1, z1 = local_points[1]
            x2, y2, z2 = local_points[2]

            denominator = (
                (y1 - y2)
                * (x0 - x2)
                + (x2 - x1)
                * (y0 - y2)
            )

            if abs(
                denominator
            ) <= epsilon:
                continue

            min_x = max(
                0.0,
                min(
                    x0,
                    x1,
                    x2,
                ),
            )
            max_x = min(
                physical_width,
                max(
                    x0,
                    x1,
                    x2,
                ),
            )

            min_y = max(
                0.0,
                min(
                    y0,
                    y1,
                    y2,
                ),
            )
            max_y = min(
                physical_depth,
                max(
                    y0,
                    y1,
                    y2,
                ),
            )

            if (
                min_x > max_x
                or min_y > max_y
            ):
                continue

            column_indices = np.flatnonzero(
                (
                    pixel_x
                    >= min_x - epsilon
                )
                & (
                    pixel_x
                    <= max_x + epsilon
                )
            )

            row_indices = np.flatnonzero(
                (
                    pixel_y
                    >= min_y - epsilon
                )
                & (
                    pixel_y
                    <= max_y + epsilon
                )
            )

            for row in row_indices:
                y = pixel_y[
                    row
                ]

                for column in column_indices:
                    x = pixel_x[
                        column
                    ]

                    w0 = (
                        (
                            (y1 - y2)
                            * (x - x2)
                            + (x2 - x1)
                            * (y - y2)
                        )
                        / denominator
                    )

                    w1 = (
                        (
                            (y2 - y0)
                            * (x - x2)
                            + (x0 - x2)
                            * (y - y2)
                        )
                        / denominator
                    )

                    w2 = (
                        1.0
                        - w0
                        - w1
                    )

                    if (
                        w0 < -epsilon
                        or w1 < -epsilon
                        or w2 < -epsilon
                    ):
                        continue

                    depth = (
                        w0 * z0
                        + w1 * z1
                        + w2 * z2
                    )

                    if not coverage_map[
                        row,
                        column,
                    ]:
                        should_replace = True
                    elif (
                        target is not None
                        and target.relief_polarity == "inward"
                    ):
                        should_replace = (
                            depth
                            < depth_map[
                                row,
                                column,
                            ]
                        )
                    else:
                        should_replace = (
                            depth
                            > depth_map[
                                row,
                                column,
                            ]
                        )

                    if should_replace:
                        depth_map[
                            row,
                            column,
                        ] = depth

                    coverage_map[
                        row,
                        column,
                    ] = True

        return {
            "type": (
                "projected_semantic_mesh_depth_rasterization"
            ),
            "shape": (
                row_count,
                column_count,
            ),
            "width_mm": (
                physical_width
            ),
            "depth_mm": (
                physical_depth
            ),
            "depth_map": (
                depth_map
            ),
            "coverage_map": (
                coverage_map
            ),
            "coordinate_space": (
                "local_uv_depth"
                if target is None
                else (
                    "target_local_uv_signed_depth"
                )
            ),
        }
