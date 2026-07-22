from __future__ import annotations

from collections.abc import Mapping
from numbers import Integral
from typing import Any

import numpy as np

from CORE.atlas_portrait_flame_jaw_contour_correspondence import (
    AtlasPortraitFlameJawContourCorrespondence,
)


class AtlasPortraitFlameJawContourMatcher:
    """
    Matches ordered 2D jaw targets to an ordered FLAME jaw edge chain.

    The caller must supply a jaw-only edge chain that has already
    excluded ears, skull, neck, bust, and unrelated mesh boundaries.

    Matching rules:

    - the edge chain must be contiguous and consistently oriented,
    - the chin landmark must be an interior target,
    - the chin target is anchored to the nearest interior chain vertex,
    - targets before and after the chin are matched separately,
    - edge assignments remain monotonic within each side,
    - matches use point-to-segment distance.

    This class performs no FLAME deformation, camera projection,
    boundary extraction, anatomical edge filtering, optimization,
    visibility analysis, rendering, or STL generation.
    """

    _SEGMENT_EPSILON = 1.0e-18

    @classmethod
    def match(
        cls,
        *,
        landmark_ids: Any,
        target_points_2d: Any,
        projected_vertices_2d: Any,
        ordered_jaw_edge_vertex_indices: Any,
        chin_landmark_id: Any,
        metadata: Mapping[str, Any],
    ) -> AtlasPortraitFlameJawContourCorrespondence:
        normalized_landmark_ids = (
            cls._normalize_landmark_ids(
                landmark_ids
            )
        )

        target_points = cls._normalize_target_points(
            target_points_2d,
            expected_count=len(
                normalized_landmark_ids
            ),
        )

        projected_vertices = (
            cls._normalize_projected_vertices(
                projected_vertices_2d
            )
        )

        ordered_edges = cls._normalize_ordered_edges(
            ordered_jaw_edge_vertex_indices,
            vertex_count=projected_vertices.shape[0],
        )

        normalized_chin_id = cls._normalize_chin_landmark_id(
            chin_landmark_id,
            landmark_ids=normalized_landmark_ids,
        )

        normalized_metadata = cls._normalize_metadata(
            metadata
        )

        chain_vertex_indices = cls._build_chain_vertex_indices(
            ordered_edges
        )

        chin_target_index = normalized_landmark_ids.index(
            normalized_chin_id
        )

        chin_chain_position = cls._select_chin_chain_position(
            target_points[
                chin_target_index
            ],
            chain_vertex_indices=chain_vertex_indices,
            projected_vertices=projected_vertices,
        )

        matched_points = np.empty_like(
            target_points,
            dtype=np.float64,
        )
        matched_edges = np.empty(
            (
                len(
                    normalized_landmark_ids
                ),
                2,
            ),
            dtype=np.int64,
        )

        cls._match_left_side(
            targets=target_points[
                :chin_target_index
            ],
            ordered_edges=ordered_edges,
            maximum_edge_index=chin_chain_position - 1,
            projected_vertices=projected_vertices,
            output_points=matched_points[
                :chin_target_index
            ],
            output_edges=matched_edges[
                :chin_target_index
            ],
        )

        cls._assign_chin_anchor(
            chin_target_index=chin_target_index,
            chin_chain_position=chin_chain_position,
            chain_vertex_indices=chain_vertex_indices,
            ordered_edges=ordered_edges,
            projected_vertices=projected_vertices,
            output_points=matched_points,
            output_edges=matched_edges,
        )

        cls._match_right_side(
            targets=target_points[
                chin_target_index + 1:
            ],
            ordered_edges=ordered_edges,
            minimum_edge_index=chin_chain_position,
            projected_vertices=projected_vertices,
            output_points=matched_points[
                chin_target_index + 1:
            ],
            output_edges=matched_edges[
                chin_target_index + 1:
            ],
        )

        residuals = np.linalg.norm(
            matched_points - target_points,
            axis=1,
        )

        result_metadata = dict(
            normalized_metadata
        )
        result_metadata.update(
            {
                "chin_landmark_id": normalized_chin_id,
                "correspondence_type": (
                    "ordered_dynamic_jaw_contour"
                ),
                "jaw_edge_count": int(
                    ordered_edges.shape[0]
                ),
                "landmark_count": len(
                    normalized_landmark_ids
                ),
                "matching_method": (
                    "split_monotonic_point_to_segment"
                ),
            }
        )

        return AtlasPortraitFlameJawContourCorrespondence(
            landmark_ids=normalized_landmark_ids,
            target_points_2d=target_points,
            matched_points_2d=matched_points,
            matched_edge_vertex_indices=matched_edges,
            visible_landmark_mask=np.ones(
                len(
                    normalized_landmark_ids
                ),
                dtype=np.bool_,
            ),
            residuals=residuals,
            metadata=result_metadata,
        )

    @staticmethod
    def _normalize_landmark_ids(
        value: Any,
    ) -> tuple[int, ...]:
        if (
            value is None
            or isinstance(
                value,
                (
                    str,
                    bytes,
                ),
            )
        ):
            raise TypeError(
                "landmark_ids must be a non-empty "
                "sequence of integers."
            )

        try:
            raw_values = tuple(
                value
            )
        except TypeError as exc:
            raise TypeError(
                "landmark_ids must be a non-empty "
                "sequence of integers."
            ) from exc

        if not raw_values:
            raise ValueError(
                "landmark_ids must not be empty."
            )

        normalized: list[int] = []

        for raw_value in raw_values:
            if (
                isinstance(
                    raw_value,
                    (
                        bool,
                        np.bool_,
                    ),
                )
                or not isinstance(
                    raw_value,
                    Integral,
                )
            ):
                raise TypeError(
                    "landmark_ids must contain "
                    "integer values."
                )

            landmark_id = int(
                raw_value
            )

            if landmark_id < 0:
                raise ValueError(
                    "landmark_ids must not contain "
                    "negative values."
                )

            normalized.append(
                landmark_id
            )

        if len(
            normalized
        ) != len(
            set(
                normalized
            )
        ):
            raise ValueError(
                "landmark_ids must contain unique values."
            )

        return tuple(
            normalized
        )

    @staticmethod
    def _normalize_target_points(
        value: Any,
        *,
        expected_count: int,
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
                "target_points_2d must be numeric."
            ) from exc

        expected_shape = (
            expected_count,
            2,
        )

        if points.shape != expected_shape:
            raise ValueError(
                "target_points_2d must have shape "
                f"{expected_shape}."
            )

        if not np.isfinite(
            points
        ).all():
            raise ValueError(
                "target_points_2d contains "
                "non-finite values."
            )

        return points.astype(
            np.float64,
            copy=True,
        )

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
            or vertices.shape[0] < 3
        ):
            raise ValueError(
                "projected_vertices_2d must have "
                "shape (N, 2) with N >= 3."
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
    def _normalize_ordered_edges(
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
                "ordered_jaw_edge_vertex_indices "
                "must be numeric."
            ) from exc

        if (
            numeric_edges.ndim != 2
            or numeric_edges.shape[1] != 2
            or numeric_edges.shape[0] < 2
        ):
            raise ValueError(
                "ordered_jaw_edge_vertex_indices must "
                "have shape (E, 2) with E >= 2."
            )

        if not np.isfinite(
            numeric_edges
        ).all():
            raise ValueError(
                "ordered_jaw_edge_vertex_indices "
                "contains non-finite values."
            )

        if not np.equal(
            numeric_edges,
            np.rint(
                numeric_edges
            ),
        ).all():
            raise ValueError(
                "ordered_jaw_edge_vertex_indices must "
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
                "ordered_jaw_edge_vertex_indices must "
                "not contain negative values."
            )

        if np.any(
            edges >= vertex_count
        ):
            raise ValueError(
                "ordered_jaw_edge_vertex_indices "
                "contains indices outside "
                "projected_vertices_2d."
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
                "ordered_jaw_edge_vertex_indices must "
                "not contain zero-length edges."
            )

        for edge_index in range(
            1,
            edges.shape[0],
        ):
            previous_edge = edges[
                edge_index - 1
            ]
            current_edge = edges[
                edge_index
            ]

            if (
                int(
                    previous_edge[
                        1
                    ]
                )
                != int(
                    current_edge[
                        0
                    ]
                )
            ):
                raise ValueError(
                    "ordered_jaw_edge_vertex_indices must "
                    "form one contiguous, consistently "
                    "oriented edge chain."
                )

        chain_vertices = np.concatenate(
            (
                edges[
                    :1,
                    0
                ],
                edges[
                    :,
                    1
                ],
            )
        )

        if len(
            set(
                chain_vertices.tolist()
            )
        ) != chain_vertices.shape[0]:
            raise ValueError(
                "ordered_jaw_edge_vertex_indices must "
                "not repeat or reverse chain vertices."
            )

        return edges

    @staticmethod
    def _normalize_chin_landmark_id(
        value: Any,
        *,
        landmark_ids: tuple[int, ...],
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
                "chin_landmark_id must be an integer."
            )

        chin_landmark_id = int(
            value
        )

        if chin_landmark_id not in landmark_ids:
            raise ValueError(
                "chin_landmark_id must exist in "
                "landmark_ids."
            )

        chin_index = landmark_ids.index(
            chin_landmark_id
        )

        if (
            chin_index == 0
            or chin_index
            == len(
                landmark_ids
            )
            - 1
        ):
            raise ValueError(
                "chin_landmark_id must identify an "
                "interior landmark."
            )

        return chin_landmark_id

    @staticmethod
    def _normalize_metadata(
        value: Any,
    ) -> dict[str, Any]:
        if not isinstance(
            value,
            Mapping,
        ):
            raise TypeError(
                "metadata must be a mapping."
            )

        return {
            str(
                key
            ): item
            for key, item in sorted(
                value.items(),
                key=lambda pair: str(
                    pair[
                        0
                    ]
                ),
            )
        }

    @staticmethod
    def _build_chain_vertex_indices(
        ordered_edges: np.ndarray,
    ) -> np.ndarray:
        return np.concatenate(
            (
                ordered_edges[
                    :1,
                    0
                ],
                ordered_edges[
                    :,
                    1
                ],
            )
        ).astype(
            np.int64,
            copy=False,
        )

    @staticmethod
    def _select_chin_chain_position(
        chin_target: np.ndarray,
        *,
        chain_vertex_indices: np.ndarray,
        projected_vertices: np.ndarray,
    ) -> int:
        interior_positions = np.arange(
            1,
            chain_vertex_indices.shape[0] - 1,
            dtype=np.int64,
        )

        interior_points = projected_vertices[
            chain_vertex_indices[
                interior_positions
            ]
        ]

        distances = np.linalg.norm(
            interior_points - chin_target,
            axis=1,
        )

        return int(
            interior_positions[
                int(
                    np.argmin(
                        distances
                    )
                )
            ]
        )

    @classmethod
    def _match_left_side(
        cls,
        *,
        targets: np.ndarray,
        ordered_edges: np.ndarray,
        maximum_edge_index: int,
        projected_vertices: np.ndarray,
        output_points: np.ndarray,
        output_edges: np.ndarray,
    ) -> None:
        if targets.shape[0] == 0:
            return

        candidate_edges = ordered_edges[
            :maximum_edge_index + 1
        ]

        cls._match_monotonic(
            targets=targets,
            candidate_edges=candidate_edges,
            candidate_edge_offset=0,
            projected_vertices=projected_vertices,
            output_points=output_points,
            output_edges=output_edges,
        )

    @classmethod
    def _match_right_side(
        cls,
        *,
        targets: np.ndarray,
        ordered_edges: np.ndarray,
        minimum_edge_index: int,
        projected_vertices: np.ndarray,
        output_points: np.ndarray,
        output_edges: np.ndarray,
    ) -> None:
        if targets.shape[0] == 0:
            return

        candidate_edges = ordered_edges[
            minimum_edge_index:
        ]

        cls._match_monotonic(
            targets=targets,
            candidate_edges=candidate_edges,
            candidate_edge_offset=minimum_edge_index,
            projected_vertices=projected_vertices,
            output_points=output_points,
            output_edges=output_edges,
        )

    @classmethod
    def _match_monotonic(
        cls,
        *,
        targets: np.ndarray,
        candidate_edges: np.ndarray,
        candidate_edge_offset: int,
        projected_vertices: np.ndarray,
        output_points: np.ndarray,
        output_edges: np.ndarray,
    ) -> None:
        target_count = targets.shape[0]
        edge_count = candidate_edges.shape[0]

        if edge_count == 0:
            raise ValueError(
                "ordered_jaw_edge_vertex_indices does "
                "not provide an edge for every side "
                "of the chin."
            )

        candidate_points = np.empty(
            (
                target_count,
                edge_count,
                2,
            ),
            dtype=np.float64,
        )
        candidate_costs = np.empty(
            (
                target_count,
                edge_count,
            ),
            dtype=np.float64,
        )

        for target_index, target in enumerate(
            targets
        ):
            for edge_index, edge in enumerate(
                candidate_edges
            ):
                point, distance = (
                    cls._nearest_point_on_segment(
                        target,
                        projected_vertices[
                            int(
                                edge[
                                    0
                                ]
                            )
                        ],
                        projected_vertices[
                            int(
                                edge[
                                    1
                                ]
                            )
                        ],
                    )
                )

                candidate_points[
                    target_index,
                    edge_index,
                ] = point
                candidate_costs[
                    target_index,
                    edge_index,
                ] = distance

        cumulative_costs = np.full(
            (
                target_count,
                edge_count,
            ),
            np.inf,
            dtype=np.float64,
        )
        predecessors = np.full(
            (
                target_count,
                edge_count,
            ),
            -1,
            dtype=np.int64,
        )

        cumulative_costs[
            0
        ] = candidate_costs[
            0
        ]

        for target_index in range(
            1,
            target_count,
        ):
            best_previous_cost = np.inf
            best_previous_index = -1

            for edge_index in range(
                edge_count
            ):
                previous_cost = cumulative_costs[
                    target_index - 1,
                    edge_index,
                ]

                if previous_cost < best_previous_cost:
                    best_previous_cost = previous_cost
                    best_previous_index = edge_index

                cumulative_costs[
                    target_index,
                    edge_index,
                ] = (
                    best_previous_cost
                    + candidate_costs[
                        target_index,
                        edge_index,
                    ]
                )
                predecessors[
                    target_index,
                    edge_index,
                ] = best_previous_index

        selected_edge_indices = np.empty(
            target_count,
            dtype=np.int64,
        )

        selected_edge_indices[
            -1
        ] = int(
            np.argmin(
                cumulative_costs[
                    -1
                ]
            )
        )

        for target_index in range(
            target_count - 1,
            0,
            -1,
        ):
            selected_edge_indices[
                target_index - 1
            ] = predecessors[
                target_index,
                selected_edge_indices[
                    target_index
                ],
            ]

        for target_index, local_edge_index in enumerate(
            selected_edge_indices
        ):
            output_points[
                target_index
            ] = candidate_points[
                target_index,
                local_edge_index,
            ]

            output_edges[
                target_index
            ] = candidate_edges[
                local_edge_index
            ]

        _ = candidate_edge_offset

    @staticmethod
    def _assign_chin_anchor(
        *,
        chin_target_index: int,
        chin_chain_position: int,
        chain_vertex_indices: np.ndarray,
        ordered_edges: np.ndarray,
        projected_vertices: np.ndarray,
        output_points: np.ndarray,
        output_edges: np.ndarray,
    ) -> None:
        chin_vertex_index = int(
            chain_vertex_indices[
                chin_chain_position
            ]
        )

        output_points[
            chin_target_index
        ] = projected_vertices[
            chin_vertex_index
        ]

        output_edges[
            chin_target_index
        ] = ordered_edges[
            chin_chain_position - 1
        ]

    @classmethod
    def _nearest_point_on_segment(
        cls,
        point: np.ndarray,
        first: np.ndarray,
        second: np.ndarray,
    ) -> tuple[np.ndarray, float]:
        direction = second - first

        squared_length = float(
            np.dot(
                direction,
                direction,
            )
        )

        if squared_length <= cls._SEGMENT_EPSILON:
            nearest = first.copy()
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
                + parameter * direction
            )

        distance = float(
            np.linalg.norm(
                point - nearest
            )
        )

        return nearest, distance
