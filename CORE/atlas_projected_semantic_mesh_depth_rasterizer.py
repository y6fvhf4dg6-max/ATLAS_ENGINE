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

        raw_vertex_normals = mesh.get("vertex_normals")
        raw_face_vertex_indices = mesh.get("face_vertex_indices")

        vertex_normals = None
        face_vertex_indices = None

        if (
            raw_vertex_normals is not None
            or raw_face_vertex_indices is not None
        ):
            if (
                raw_vertex_normals is None
                or raw_face_vertex_indices is None
            ):
                raise ValueError(
                    "vertex_normals and face_vertex_indices "
                    "must be provided together"
                )

            vertex_normals = np.asarray(
                raw_vertex_normals,
                dtype=np.float64,
            )
            face_vertex_indices = np.asarray(
                raw_face_vertex_indices,
                dtype=np.int64,
            )

            if (
                vertex_normals.ndim != 2
                or vertex_normals.shape[1] != 3
                or not np.isfinite(vertex_normals).all()
            ):
                raise ValueError(
                    "vertex_normals must have shape "
                    "(vertex_count, 3) and be finite"
                )

            if face_vertex_indices.shape != (
                len(triangles),
                3,
            ):
                raise ValueError(
                    "face_vertex_indices must have shape "
                    "(triangle_count, 3)"
                )

            if (
                np.any(face_vertex_indices < 0)
                or np.any(
                    face_vertex_indices
                    >= len(vertex_normals)
                )
            ):
                raise ValueError(
                    "face_vertex_indices reference "
                    "invalid vertex normals"
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

        face_index_map = np.full(
            (
                row_count,
                column_count,
            ),
            -1,
            dtype=np.int64,
        )

        barycentric_map = np.zeros(
            (
                row_count,
                column_count,
                3,
            ),
            dtype=np.float64,
        )

        normal_map = np.zeros(
            (
                row_count,
                column_count,
                3,
            ),
            dtype=np.float64,
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

        for face_index, triangle in enumerate(triangles):
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
                        face_index_map[
                            row,
                            column,
                        ] = face_index
                        barycentric_map[
                            row,
                            column,
                        ] = (
                            w0,
                            w1,
                            w2,
                        )

                        if vertex_normals is not None:
                            indices = face_vertex_indices[
                                face_index
                            ]
                            interpolated_normal = (
                                w0 * vertex_normals[indices[0]]
                                + w1 * vertex_normals[indices[1]]
                                + w2 * vertex_normals[indices[2]]
                            )
                            normal_length = float(
                                np.linalg.norm(
                                    interpolated_normal
                                )
                            )
                            if normal_length <= 1e-12:
                                raise ValueError(
                                    "interpolated visible normal "
                                    "must be non-degenerate"
                                )
                            normal_map[
                                row,
                                column,
                            ] = (
                                interpolated_normal
                                / normal_length
                            )

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
            "face_index_map": (
                face_index_map
            ),
            "barycentric_map": (
                barycentric_map
            ),
            "normal_map": (
                normal_map
            ),
            "coordinate_space": (
                "local_uv_depth"
                if target is None
                else (
                    "target_local_uv_signed_depth"
                )
            ),
        }
