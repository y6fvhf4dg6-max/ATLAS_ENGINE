from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from numbers import Integral
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasPortraitFlameDynamicLandmarkEmbedding:
    """
    Immutable pose-dependent FLAME contour embedding.

    The first array axis represents discrete yaw bins.
    The second axis represents ordered contour landmarks.
    """

    landmark_face_indices: np.ndarray
    landmark_barycentric_coordinates: np.ndarray

    def __post_init__(
        self,
    ) -> None:
        face_indices = np.asarray(
            self.landmark_face_indices,
            dtype=np.int64,
        ).copy()

        barycentric_coordinates = np.asarray(
            self.landmark_barycentric_coordinates,
            dtype=np.float64,
        ).copy()

        if (
            face_indices.ndim != 2
            or face_indices.shape[0] == 0
            or face_indices.shape[1] == 0
        ):
            raise ValueError(
                "landmark_face_indices must have "
                "shape (Y, L) with Y > 0 and L > 0."
            )

        expected_barycentric_shape = (
            face_indices.shape[0],
            face_indices.shape[1],
            3,
        )

        if (
            barycentric_coordinates.shape
            != expected_barycentric_shape
        ):
            raise ValueError(
                "landmark_barycentric_coordinates must "
                f"have shape {expected_barycentric_shape}."
            )

        if np.any(
            face_indices < 0
        ):
            raise ValueError(
                "landmark_face_indices must not contain "
                "negative values."
            )

        if not np.isfinite(
            barycentric_coordinates
        ).all():
            raise ValueError(
                "landmark_barycentric_coordinates contains "
                "non-finite values."
            )

        face_indices.setflags(
            write=False
        )
        barycentric_coordinates.setflags(
            write=False
        )

        object.__setattr__(
            self,
            "landmark_face_indices",
            face_indices,
        )
        object.__setattr__(
            self,
            "landmark_barycentric_coordinates",
            barycentric_coordinates,
        )

    @property
    def yaw_bin_count(
        self,
    ) -> int:
        return int(
            self.landmark_face_indices.shape[0]
        )

    @property
    def contour_landmark_count(
        self,
    ) -> int:
        return int(
            self.landmark_face_indices.shape[1]
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "yaw_bin_count": self.yaw_bin_count,
            "contour_landmark_count": (
                self.contour_landmark_count
            ),
            "landmark_face_indices": (
                self.landmark_face_indices.tolist()
            ),
            "landmark_barycentric_coordinates": (
                self
                .landmark_barycentric_coordinates
                .tolist()
            ),
        }


class AtlasPortraitFlameDynamicLandmarkEmbeddingLoader:
    """
    Loads and validates RingNet-style FLAME dynamic landmarks.

    Expected payload keys:

    - lmk_face_idx: shape (Y, L)
    - lmk_b_coords: shape (Y, L, 3)

    This loader performs no yaw-bin selection, pose estimation,
    barycentric evaluation, fitting, rendering, or STL generation.
    """

    _BARYCENTRIC_NEGATIVE_TOLERANCE = 1.0e-12
    _BARYCENTRIC_SUM_TOLERANCE = 1.0e-9

    @classmethod
    def load(
        cls,
        path: str | Path,
        *,
        triangle_count: Any,
    ) -> AtlasPortraitFlameDynamicLandmarkEmbedding:
        normalized_triangle_count = (
            cls._normalize_triangle_count(
                triangle_count
            )
        )

        embedding_path = Path(
            path
        )

        if not embedding_path.is_file():
            raise FileNotFoundError(
                "FLAME dynamic landmark embedding "
                f"was not found: {embedding_path}"
            )

        raw_payload = np.load(
            embedding_path,
            allow_pickle=True,
            encoding="latin1",
        )

        try:
            payload = cls._unwrap_payload(
                raw_payload
            )
        finally:
            if isinstance(
                raw_payload,
                np.lib.npyio.NpzFile,
            ):
                raw_payload.close()

        if not isinstance(
            payload,
            Mapping,
        ):
            raise TypeError(
                "FLAME dynamic landmark embedding "
                "payload must be a mapping."
            )

        if "lmk_face_idx" not in payload:
            raise KeyError(
                "lmk_face_idx is required in the "
                "dynamic landmark embedding."
            )

        if "lmk_b_coords" not in payload:
            raise KeyError(
                "lmk_b_coords is required in the "
                "dynamic landmark embedding."
            )

        face_indices = cls._normalize_face_indices(
            payload[
                "lmk_face_idx"
            ],
            triangle_count=normalized_triangle_count,
        )

        barycentric_coordinates = (
            cls._normalize_barycentric_coordinates(
                payload[
                    "lmk_b_coords"
                ],
                expected_shape=(
                    face_indices.shape[0],
                    face_indices.shape[1],
                    3,
                ),
            )
        )

        return AtlasPortraitFlameDynamicLandmarkEmbedding(
            landmark_face_indices=face_indices,
            landmark_barycentric_coordinates=(
                barycentric_coordinates
            ),
        )

    @staticmethod
    def _unwrap_payload(
        value: Any,
    ) -> Any:
        if isinstance(
            value,
            np.lib.npyio.NpzFile,
        ):
            return {
                key: value[
                    key
                ]
                for key in value.files
            }

        if (
            isinstance(
                value,
                np.ndarray,
            )
            and value.shape == ()
            and value.dtype == object
        ):
            return value.item()

        return value

    @staticmethod
    def _normalize_triangle_count(
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
                "triangle_count must be a positive integer."
            )

        triangle_count = int(
            value
        )

        if triangle_count <= 0:
            raise ValueError(
                "triangle_count must be greater than zero."
            )

        return triangle_count

    @staticmethod
    def _normalize_face_indices(
        value: Any,
        *,
        triangle_count: int,
    ) -> np.ndarray:
        try:
            numeric_indices = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "lmk_face_idx must be numeric."
            ) from exc

        if (
            numeric_indices.ndim != 2
            or numeric_indices.shape[0] == 0
            or numeric_indices.shape[1] == 0
        ):
            raise ValueError(
                "lmk_face_idx must have shape "
                "(Y, L) with Y > 0 and L > 0."
            )

        if not np.isfinite(
            numeric_indices
        ).all():
            raise ValueError(
                "lmk_face_idx contains non-finite values."
            )

        if not np.equal(
            numeric_indices,
            np.rint(
                numeric_indices
            ),
        ).all():
            raise ValueError(
                "lmk_face_idx must contain integer values."
            )

        face_indices = numeric_indices.astype(
            np.int64,
            copy=True,
        )

        if np.any(
            face_indices < 0
        ):
            raise ValueError(
                "lmk_face_idx must not contain "
                "negative values."
            )

        if np.any(
            face_indices >= triangle_count
        ):
            raise ValueError(
                "lmk_face_idx contains an index outside "
                "triangle_count."
            )

        return face_indices

    @classmethod
    def _normalize_barycentric_coordinates(
        cls,
        value: Any,
        *,
        expected_shape: tuple[int, int, int],
    ) -> np.ndarray:
        try:
            coordinates = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "lmk_b_coords must be numeric."
            ) from exc

        if coordinates.shape != expected_shape:
            raise ValueError(
                "lmk_b_coords must have shape "
                f"{expected_shape}."
            )

        if not np.isfinite(
            coordinates
        ).all():
            raise ValueError(
                "lmk_b_coords contains non-finite values."
            )

        if np.any(
            coordinates
            < -cls._BARYCENTRIC_NEGATIVE_TOLERANCE
        ):
            raise ValueError(
                "lmk_b_coords contains materially "
                "negative values."
            )

        normalized = coordinates.astype(
            np.float64,
            copy=True,
        )

        normalized[
            (
                normalized < 0.0
            )
            & (
                normalized
                >= -cls._BARYCENTRIC_NEGATIVE_TOLERANCE
            )
        ] = 0.0

        sums = np.sum(
            normalized,
            axis=-1,
            dtype=np.float64,
        )

        if not np.allclose(
            sums,
            1.0,
            rtol=0.0,
            atol=cls._BARYCENTRIC_SUM_TOLERANCE,
        ):
            raise ValueError(
                "lmk_b_coords barycentric values must "
                "sum to 1."
            )

        normalized /= sums[
            :,
            :,
            np.newaxis,
        ]

        return normalized
