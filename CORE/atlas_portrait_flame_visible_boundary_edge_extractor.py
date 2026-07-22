from __future__ import annotations

from collections import Counter
from numbers import Integral
from typing import Any

import numpy as np


class AtlasPortraitFlameVisibleBoundaryEdgeExtractor:
    """
    Extracts deterministic boundary edges from visible triangles.

    An undirected edge is considered a visible boundary edge
    when it occurs exactly once among visible triangles.

    The extractor performs no camera projection, triangle
    visibility classification, connected-component selection,
    anatomical filtering, jaw-path ordering, correspondence
    matching, optimization, rendering, or STL generation.
    """

    @classmethod
    def extract(
        cls,
        *,
        triangle_faces: Any,
        visible_triangle_mask: Any,
        vertex_count: Any,
    ) -> np.ndarray:
        normalized_vertex_count = cls._normalize_vertex_count(
            vertex_count
        )

        faces = cls._normalize_triangle_faces(
            triangle_faces,
            vertex_count=normalized_vertex_count,
        )

        visible_mask = cls._normalize_visible_triangle_mask(
            visible_triangle_mask,
            triangle_count=faces.shape[0],
        )

        visible_faces = faces[
            visible_mask
        ]

        if visible_faces.shape[0] == 0:
            result = np.empty(
                (
                    0,
                    2,
                ),
                dtype=np.int64,
            )
            result.setflags(
                write=False
            )
            return result

        edge_counts: Counter[
            tuple[int, int]
        ] = Counter()

        for first, second, third in visible_faces:
            for raw_first, raw_second in (
                (
                    first,
                    second,
                ),
                (
                    second,
                    third,
                ),
                (
                    third,
                    first,
                ),
            ):
                edge = cls._normalize_edge(
                    int(
                        raw_first
                    ),
                    int(
                        raw_second
                    ),
                )
                edge_counts[
                    edge
                ] += 1

        boundary_edges = sorted(
            edge
            for edge, count in edge_counts.items()
            if count == 1
        )

        result = np.asarray(
            boundary_edges,
            dtype=np.int64,
        )

        if result.size == 0:
            result = np.empty(
                (
                    0,
                    2,
                ),
                dtype=np.int64,
            )
        else:
            result = result.reshape(
                -1,
                2,
            )

        result.setflags(
            write=False
        )

        return result

    @staticmethod
    def _normalize_vertex_count(
        value: Any,
    ) -> int:
        if (
            isinstance(
                value,
                (
                    bool,
                    np.bool_,
                ),
            )
            or not isinstance(
                value,
                Integral,
            )
        ):
            raise TypeError(
                "vertex_count must be a positive integer."
            )

        vertex_count = int(
            value
        )

        if vertex_count <= 0:
            raise ValueError(
                "vertex_count must be greater than zero."
            )

        return vertex_count

    @staticmethod
    def _normalize_triangle_faces(
        value: Any,
        *,
        vertex_count: int,
    ) -> np.ndarray:
        try:
            numeric_faces = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "triangle_faces must be numeric."
            ) from exc

        if (
            numeric_faces.ndim != 2
            or numeric_faces.shape[1] != 3
        ):
            raise ValueError(
                "triangle_faces must have shape (F, 3)."
            )

        if not np.isfinite(
            numeric_faces
        ).all():
            raise ValueError(
                "triangle_faces contains non-finite values."
            )

        if not np.equal(
            numeric_faces,
            np.rint(
                numeric_faces
            ),
        ).all():
            raise ValueError(
                "triangle_faces must contain integer indices."
            )

        faces = numeric_faces.astype(
            np.int64,
            copy=True,
        )

        if np.any(
            faces < 0
        ):
            raise ValueError(
                "triangle_faces contains negative indices."
            )

        if np.any(
            faces >= vertex_count
        ):
            raise ValueError(
                "triangle_faces contains indices outside "
                "vertex_count."
            )

        if faces.shape[0] > 0:
            repeated_vertices = (
                (
                    faces[
                        :,
                        0
                    ]
                    == faces[
                        :,
                        1
                    ]
                )
                | (
                    faces[
                        :,
                        1
                    ]
                    == faces[
                        :,
                        2
                    ]
                )
                | (
                    faces[
                        :,
                        2
                    ]
                    == faces[
                        :,
                        0
                    ]
                )
            )

            if np.any(
                repeated_vertices
            ):
                raise ValueError(
                    "triangle_faces contains a degenerate "
                    "triangle."
                )

        return faces

    @staticmethod
    def _normalize_visible_triangle_mask(
        value: Any,
        *,
        triangle_count: int,
    ) -> np.ndarray:
        mask = np.asarray(
            value
        )

        expected_shape = (
            triangle_count,
        )

        if mask.shape != expected_shape:
            raise ValueError(
                "visible_triangle_mask must have shape "
                f"{expected_shape}."
            )

        if mask.dtype.kind != "b":
            raise ValueError(
                "visible_triangle_mask must contain "
                "boolean values."
            )

        return mask.astype(
            np.bool_,
            copy=True,
        )

    @staticmethod
    def _normalize_edge(
        first: int,
        second: int,
    ) -> tuple[int, int]:
        return (
            min(
                first,
                second,
            ),
            max(
                first,
                second,
            ),
        )
