from __future__ import annotations

from numbers import Integral
from typing import Any

import numpy as np


class AtlasFlameBarycentricLandmarkEvaluator:
    """
    Evaluates FLAME MediaPipe barycentric landmarks
    on a triangular canonical face mesh.
    """

    BARYCENTRIC_SUM_TOLERANCE = 1e-10

    @classmethod
    def evaluate(
        cls,
        *,
        vertices: Any,
        triangle_faces: Any,
        landmark_indices: Any,
        landmark_face_indices: Any,
        landmark_barycentric_coordinates: Any,
        requested_mediapipe_ids: Any,
    ) -> np.ndarray:
        vertices_array = cls._vertices(
            vertices,
        )

        faces_array = cls._faces(
            triangle_faces,
            vertex_count=vertices_array.shape[0],
        )

        landmark_ids = cls._integer_vector(
            landmark_indices,
            name="landmark_indices",
        )

        if len(
            set(
                landmark_ids.tolist(),
            )
        ) != landmark_ids.size:
            raise ValueError(
                "landmark_indices must contain unique values."
            )

        face_indices = cls._integer_vector(
            landmark_face_indices,
            name="landmark_face_indices",
        )

        barycentric = cls._barycentric(
            landmark_barycentric_coordinates,
        )

        embedding_count = landmark_ids.shape[0]

        if (
            face_indices.shape[0] != embedding_count
            or barycentric.shape[0] != embedding_count
        ):
            raise ValueError(
                "FLAME embedding arrays must have matching lengths."
            )

        if (
            np.any(
                face_indices < 0,
            )
            or np.any(
                face_indices >= faces_array.shape[0],
            )
        ):
            raise ValueError(
                "landmark face index is outside the face range."
            )

        requested_ids = cls._requested_ids(
            requested_mediapipe_ids,
        )

        position_by_id = {
            int(
                media_pipe_id,
            ): position
            for position, media_pipe_id in enumerate(
                landmark_ids,
            )
        }

        missing_ids = tuple(
            media_pipe_id
            for media_pipe_id in requested_ids
            if media_pipe_id not in position_by_id
        )

        if missing_ids:
            raise ValueError(
                "Embedding is missing requested MediaPipe IDs: "
                + ", ".join(
                    str(
                        value,
                    )
                    for value in missing_ids
                )
                + "."
            )

        result = np.empty(
            (
                len(
                    requested_ids,
                ),
                3,
            ),
            dtype=np.float64,
        )

        for output_index, media_pipe_id in enumerate(
            requested_ids,
        ):
            embedding_position = position_by_id[
                media_pipe_id
            ]

            face_index = int(
                face_indices[
                    embedding_position
                ]
            )

            triangle = faces_array[
                face_index
            ]

            triangle_vertices = vertices_array[
                triangle
            ]

            weights = barycentric[
                embedding_position
            ]

            result[
                output_index
            ] = np.sum(
                triangle_vertices
                * weights[
                    :,
                    np.newaxis,
                ],
                axis=0,
            )

        result.setflags(
            write=False,
        )

        return result

    @staticmethod
    def _vertices(
        value: Any,
    ) -> np.ndarray:
        try:
            result = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "vertices must be numeric."
            ) from exc

        if (
            result.ndim != 2
            or result.shape[1] != 3
            or result.shape[0] < 3
        ):
            raise ValueError(
                "vertices must have shape (N, 3)."
            )

        if not np.isfinite(
            result,
        ).all():
            raise ValueError(
                "vertices contains non-finite values."
            )

        return result.astype(
            np.float64,
            copy=True,
        )

    @classmethod
    def _faces(
        cls,
        value: Any,
        *,
        vertex_count: int,
    ) -> np.ndarray:
        result = cls._integer_array(
            value,
            name="triangle_faces",
        )

        if (
            result.ndim != 2
            or result.shape[1] != 3
            or result.shape[0] < 1
        ):
            raise ValueError(
                "triangle_faces must have shape (N, 3)."
            )

        if (
            np.any(
                result < 0,
            )
            or np.any(
                result >= vertex_count,
            )
        ):
            raise ValueError(
                "triangle vertex index is outside the vertex range."
            )

        return result

    @classmethod
    def _integer_vector(
        cls,
        value: Any,
        *,
        name: str,
    ) -> np.ndarray:
        result = cls._integer_array(
            value,
            name=name,
        )

        if result.ndim != 1:
            raise ValueError(
                f"{name} must be one-dimensional."
            )

        return result

    @staticmethod
    def _integer_array(
        value: Any,
        *,
        name: str,
    ) -> np.ndarray:
        try:
            numeric = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if not np.isfinite(
            numeric,
        ).all():
            raise ValueError(
                f"{name} contains non-finite values."
            )

        if not np.equal(
            numeric,
            np.rint(
                numeric,
            ),
        ).all():
            raise ValueError(
                f"{name} must contain integer values."
            )

        return numeric.astype(
            np.int64,
            copy=True,
        )

    @classmethod
    def _barycentric(
        cls,
        value: Any,
    ) -> np.ndarray:
        try:
            result = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "landmark barycentric coordinates must be numeric."
            ) from exc

        if (
            result.ndim != 2
            or result.shape[1] != 3
        ):
            raise ValueError(
                "landmark barycentric coordinates must "
                "have shape (N, 3)."
            )

        if not np.isfinite(
            result,
        ).all():
            raise ValueError(
                "landmark barycentric coordinates contain "
                "non-finite values."
            )

        sums = result.sum(
            axis=1,
        )

        if not np.allclose(
            sums,
            1.0,
            rtol=0.0,
            atol=cls.BARYCENTRIC_SUM_TOLERANCE,
        ):
            raise ValueError(
                "Each barycentric coordinate triplet must sum to 1.0."
            )

        return result.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _requested_ids(
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
                "requested_mediapipe_ids must be an iterable."
            )

        try:
            raw_values = tuple(
                value,
            )
        except TypeError as exc:
            raise TypeError(
                "requested_mediapipe_ids must be an iterable."
            ) from exc

        if not raw_values:
            raise ValueError(
                "requested_mediapipe_ids must not be empty."
            )

        normalized: list[int] = []

        for raw_value in raw_values:
            if (
                isinstance(
                    raw_value,
                    bool,
                )
                or not isinstance(
                    raw_value,
                    Integral,
                )
            ):
                raise TypeError(
                    "requested_mediapipe_ids must contain integers."
                )

            normalized.append(
                int(
                    raw_value,
                )
            )

        if len(
            normalized,
        ) != len(
            set(
                normalized,
            )
        ):
            raise ValueError(
                "requested_mediapipe_ids must be unique."
            )

        return tuple(
            normalized,
        )
