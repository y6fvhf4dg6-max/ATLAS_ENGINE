from __future__ import annotations

import heapq
from collections import defaultdict
from numbers import Integral
from typing import Any

import numpy as np


class AtlasPortraitFlameJawBoundaryPathSelector:
    """
    Selects an ordered jaw path from an undirected boundary graph.

    Selection is constrained by:

    - the first and last jaw target points,
    - a mandatory chin vertex,
    - boundary-graph connectivity,
    - geometric path length,
    - distance from each candidate edge to the target jaw polyline.

    The result is an oriented, contiguous, read-only edge chain
    from the first jaw target side to the last jaw target side.

    This selector performs no triangle visibility classification,
    boundary extraction, FLAME deformation, camera projection,
    contour correspondence optimization, rendering, or STL
    generation.
    """

    _DISTANCE_WEIGHT = 0.25
    _EPSILON = 1.0e-12

    @classmethod
    def select(
        cls,
        *,
        boundary_edge_vertex_indices: Any,
        projected_vertices_2d: Any,
        jaw_target_points_2d: Any,
        chin_target_index: Any,
    ) -> np.ndarray:
        projected_vertices = cls._normalize_projected_vertices(
            projected_vertices_2d
        )

        boundary_edges = cls._normalize_boundary_edges(
            boundary_edge_vertex_indices,
            vertex_count=projected_vertices.shape[0],
        )

        target_points = cls._normalize_target_points(
            jaw_target_points_2d
        )

        normalized_chin_target_index = (
            cls._normalize_chin_target_index(
                chin_target_index,
                target_count=target_points.shape[0],
            )
        )

        adjacency = cls._build_adjacency(
            boundary_edges
        )

        boundary_vertices = np.asarray(
            sorted(
                adjacency
            ),
            dtype=np.int64,
        )

        start_vertex = cls._nearest_vertex(
            target_points[
                0
            ],
            candidate_vertex_indices=boundary_vertices,
            projected_vertices=projected_vertices,
        )

        end_vertex = cls._nearest_vertex(
            target_points[
                -1
            ],
            candidate_vertex_indices=boundary_vertices,
            projected_vertices=projected_vertices,
        )

        if start_vertex == end_vertex:
            raise ValueError(
                "boundary_edge_vertex_indices does not "
                "provide distinct jaw endpoints."
            )

        if not cls._vertices_are_connected(
            start_vertex,
            end_vertex,
            adjacency=adjacency,
        ):
            raise ValueError(
                "boundary_edge_vertex_indices does not "
                "contain a connected path between the "
                "jaw endpoints."
            )

        chin_vertex = cls._nearest_vertex(
            target_points[
                normalized_chin_target_index
            ],
            candidate_vertex_indices=np.arange(
                projected_vertices.shape[0],
                dtype=np.int64,
            ),
            projected_vertices=projected_vertices,
        )

        if chin_vertex not in adjacency:
            raise ValueError(
                "chin target does not correspond to a "
                "vertex in boundary_edge_vertex_indices."
            )

        if (
            not cls._vertices_are_connected(
                start_vertex,
                chin_vertex,
                adjacency=adjacency,
            )
            or not cls._vertices_are_connected(
                chin_vertex,
                end_vertex,
                adjacency=adjacency,
            )
        ):
            raise ValueError(
                "chin vertex is not connected to both "
                "jaw endpoints."
            )

        left_targets = target_points[
            :normalized_chin_target_index + 1
        ]
        right_targets = target_points[
            normalized_chin_target_index:
        ]

        left_path = cls._minimum_cost_path(
            start_vertex,
            chin_vertex,
            adjacency=adjacency,
            projected_vertices=projected_vertices,
            target_polyline=left_targets,
        )

        right_path = cls._minimum_cost_path(
            chin_vertex,
            end_vertex,
            adjacency=adjacency,
            projected_vertices=projected_vertices,
            target_polyline=right_targets,
        )

        if (
            left_path is None
            or right_path is None
        ):
            raise ValueError(
                "chin vertex does not provide a valid "
                "jaw boundary path."
            )

        ordered_vertices = (
            left_path
            + right_path[
                1:
            ]
        )

        if len(
            ordered_vertices
        ) < 2:
            raise ValueError(
                "boundary_edge_vertex_indices does not "
                "provide a usable jaw path."
            )

        if len(
            ordered_vertices
        ) != len(
            set(
                ordered_vertices
            )
        ):
            raise ValueError(
                "selected jaw boundary path contains "
                "a repeated vertex."
            )

        result = np.asarray(
            [
                (
                    ordered_vertices[
                        index
                    ],
                    ordered_vertices[
                        index + 1
                    ],
                )
                for index in range(
                    len(
                        ordered_vertices
                    )
                    - 1
                )
            ],
            dtype=np.int64,
        )

        result.setflags(
            write=False
        )

        return result

    @staticmethod
    def _normalize_projected_vertices(
        value: Any,
    ) -> np.ndarray:
        try:
            vertices = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "projected_vertices_2d must be numeric."
            ) from exc

        if (
            vertices.ndim != 2
            or vertices.shape[1] != 2
            or vertices.shape[0] < 2
        ):
            raise ValueError(
                "projected_vertices_2d must have "
                "shape (N, 2) with N >= 2."
            )

        if not np.isfinite(
            vertices
        ).all():
            raise ValueError(
                "projected_vertices_2d contains "
                "non-finite values."
            )

        return vertices.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _normalize_boundary_edges(
        value: Any,
        *,
        vertex_count: int,
    ) -> np.ndarray:
        try:
            numeric_edges = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "boundary_edge_vertex_indices "
                "must be numeric."
            ) from exc

        if (
            numeric_edges.ndim != 2
            or numeric_edges.shape[1] != 2
            or numeric_edges.shape[0] == 0
        ):
            raise ValueError(
                "boundary_edge_vertex_indices must "
                "have shape (E, 2) with E >= 1."
            )

        if not np.isfinite(
            numeric_edges
        ).all():
            raise ValueError(
                "boundary_edge_vertex_indices contains "
                "non-finite values."
            )

        if not np.equal(
            numeric_edges,
            np.rint(
                numeric_edges
            ),
        ).all():
            raise ValueError(
                "boundary_edge_vertex_indices must "
                "contain integer values."
            )

        edges = numeric_edges.astype(
            np.int64,
            copy=True,
        )

        if np.any(
            edges < 0
        ):
            raise ValueError(
                "boundary_edge_vertex_indices must not "
                "contain negative values."
            )

        if np.any(
            edges >= vertex_count
        ):
            raise ValueError(
                "boundary_edge_vertex_indices contains "
                "indices outside projected_vertices_2d."
            )

        if np.any(
            edges[
                :,
                0
            ]
            == edges[
                :,
                1
            ]
        ):
            raise ValueError(
                "boundary_edge_vertex_indices must not "
                "contain zero-length graph edges."
            )

        normalized_edges = np.sort(
            edges,
            axis=1,
        )

        normalized_edges = np.unique(
            normalized_edges,
            axis=0,
        )

        order = np.lexsort(
            (
                normalized_edges[
                    :,
                    1
                ],
                normalized_edges[
                    :,
                    0
                ],
            )
        )

        return normalized_edges[
            order
        ].astype(
            np.int64,
            copy=True,
        )

    @staticmethod
    def _normalize_target_points(
        value: Any,
    ) -> np.ndarray:
        try:
            points = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "jaw_target_points_2d must be numeric."
            ) from exc

        if (
            points.ndim != 2
            or points.shape[1] != 2
            or points.shape[0] < 3
        ):
            raise ValueError(
                "jaw_target_points_2d must have "
                "shape (N, 2) with N >= 3."
            )

        if not np.isfinite(
            points
        ).all():
            raise ValueError(
                "jaw_target_points_2d contains "
                "non-finite values."
            )

        return points.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _normalize_chin_target_index(
        value: Any,
        *,
        target_count: int,
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
                "chin_target_index must be an integer."
            )

        index = int(
            value
        )

        if (
            index <= 0
            or index >= target_count - 1
        ):
            raise ValueError(
                "chin_target_index must identify an "
                "interior jaw target."
            )

        return index

    @staticmethod
    def _build_adjacency(
        edges: np.ndarray,
    ) -> dict[int, tuple[int, ...]]:
        mutable_adjacency: dict[
            int,
            set[int],
        ] = defaultdict(
            set
        )

        for first, second in edges:
            first_index = int(
                first
            )
            second_index = int(
                second
            )

            mutable_adjacency[
                first_index
            ].add(
                second_index
            )
            mutable_adjacency[
                second_index
            ].add(
                first_index
            )

        return {
            vertex: tuple(
                sorted(
                    neighbours
                )
            )
            for vertex, neighbours in sorted(
                mutable_adjacency.items()
            )
        }

    @staticmethod
    def _nearest_vertex(
        point: np.ndarray,
        *,
        candidate_vertex_indices: np.ndarray,
        projected_vertices: np.ndarray,
    ) -> int:
        candidate_points = projected_vertices[
            candidate_vertex_indices
        ]

        distances = np.linalg.norm(
            candidate_points - point,
            axis=1,
        )

        minimum_distance = float(
            np.min(
                distances
            )
        )

        tied_positions = np.flatnonzero(
            np.isclose(
                distances,
                minimum_distance,
                rtol=0.0,
                atol=1.0e-12,
            )
        )

        tied_vertex_indices = (
            candidate_vertex_indices[
                tied_positions
            ]
        )

        return int(
            np.min(
                tied_vertex_indices
            )
        )

    @staticmethod
    def _vertices_are_connected(
        start: int,
        end: int,
        *,
        adjacency: dict[int, tuple[int, ...]],
    ) -> bool:
        if start == end:
            return True

        visited = {
            start,
        }
        stack = [
            start,
        ]

        while stack:
            current = stack.pop()

            for neighbour in adjacency.get(
                current,
                (),
            ):
                if neighbour == end:
                    return True

                if neighbour in visited:
                    continue

                visited.add(
                    neighbour
                )
                stack.append(
                    neighbour
                )

        return False

    @classmethod
    def _minimum_cost_path(
        cls,
        start: int,
        end: int,
        *,
        adjacency: dict[int, tuple[int, ...]],
        projected_vertices: np.ndarray,
        target_polyline: np.ndarray,
    ) -> list[int] | None:
        if start == end:
            return [
                start,
            ]

        queue: list[
            tuple[
                float,
                tuple[int, ...],
                int,
            ]
        ] = [
            (
                0.0,
                (
                    start,
                ),
                start,
            ),
        ]

        best_cost: dict[
            int,
            float,
        ] = {
            start: 0.0,
        }

        best_path: dict[
            int,
            tuple[int, ...],
        ] = {
            start: (
                start,
            ),
        }

        while queue:
            (
                current_cost,
                current_path,
                current_vertex,
            ) = heapq.heappop(
                queue
            )

            stored_cost = best_cost.get(
                current_vertex,
                float(
                    "inf"
                ),
            )

            stored_path = best_path.get(
                current_vertex
            )

            if (
                current_cost
                > stored_cost
                + cls._EPSILON
            ):
                continue

            if (
                stored_path is not None
                and abs(
                    current_cost
                    - stored_cost
                )
                <= cls._EPSILON
                and current_path
                != stored_path
            ):
                continue

            if current_vertex == end:
                return list(
                    current_path
                )

            for neighbour in adjacency.get(
                current_vertex,
                (),
            ):
                if neighbour in current_path:
                    continue

                edge_cost = cls._edge_cost(
                    current_vertex,
                    neighbour,
                    projected_vertices=(
                        projected_vertices
                    ),
                    target_polyline=target_polyline,
                )

                candidate_cost = (
                    current_cost
                    + edge_cost
                )

                candidate_path = (
                    current_path
                    + (
                        neighbour,
                    )
                )

                previous_cost = best_cost.get(
                    neighbour,
                    float(
                        "inf"
                    ),
                )

                previous_path = best_path.get(
                    neighbour
                )

                is_better = (
                    candidate_cost
                    < previous_cost
                    - cls._EPSILON
                )

                is_equal_but_deterministic = (
                    abs(
                        candidate_cost
                        - previous_cost
                    )
                    <= cls._EPSILON
                    and (
                        previous_path is None
                        or candidate_path
                        < previous_path
                    )
                )

                if not (
                    is_better
                    or is_equal_but_deterministic
                ):
                    continue

                best_cost[
                    neighbour
                ] = candidate_cost
                best_path[
                    neighbour
                ] = candidate_path

                heapq.heappush(
                    queue,
                    (
                        candidate_cost,
                        candidate_path,
                        neighbour,
                    ),
                )

        return None

    @classmethod
    def _edge_cost(
        cls,
        first_vertex: int,
        second_vertex: int,
        *,
        projected_vertices: np.ndarray,
        target_polyline: np.ndarray,
    ) -> float:
        first_point = projected_vertices[
            first_vertex
        ]
        second_point = projected_vertices[
            second_vertex
        ]

        edge_length = float(
            np.linalg.norm(
                second_point
                - first_point
            )
        )

        midpoint = (
            first_point
            + second_point
        ) * 0.5

        first_distance = cls._distance_to_polyline(
            first_point,
            target_polyline,
        )
        midpoint_distance = cls._distance_to_polyline(
            midpoint,
            target_polyline,
        )
        second_distance = cls._distance_to_polyline(
            second_point,
            target_polyline,
        )

        mean_contour_distance = (
            first_distance
            + midpoint_distance
            + second_distance
        ) / 3.0

        return (
            edge_length
            + cls._DISTANCE_WEIGHT
            * mean_contour_distance
        )

    @classmethod
    def _distance_to_polyline(
        cls,
        point: np.ndarray,
        polyline: np.ndarray,
    ) -> float:
        minimum_distance = float(
            "inf"
        )

        for index in range(
            polyline.shape[0] - 1
        ):
            distance = cls._distance_to_segment(
                point,
                polyline[
                    index
                ],
                polyline[
                    index + 1
                ],
            )

            if distance < minimum_distance:
                minimum_distance = distance

        return minimum_distance

    @staticmethod
    def _distance_to_segment(
        point: np.ndarray,
        first: np.ndarray,
        second: np.ndarray,
    ) -> float:
        direction = (
            second
            - first
        )

        squared_length = float(
            np.dot(
                direction,
                direction,
            )
        )

        if squared_length <= 1.0e-18:
            nearest = first
        else:
            parameter = float(
                np.dot(
                    point - first,
                    direction,
                )
                / squared_length
            )

            parameter = min(
                1.0,
                max(
                    0.0,
                    parameter,
                ),
            )

            nearest = (
                first
                + parameter
                * direction
            )

        return float(
            np.linalg.norm(
                point
                - nearest
            )
        )
