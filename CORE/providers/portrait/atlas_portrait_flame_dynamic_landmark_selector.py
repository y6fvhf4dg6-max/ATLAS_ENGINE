from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Real
from typing import Any

import numpy as np

from CORE.providers.portrait.atlas_portrait_flame_dynamic_landmark_embedding_loader import (
    AtlasPortraitFlameDynamicLandmarkEmbedding,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasPortraitFlameDynamicLandmarkSelection:
    """
    Immutable selection of one pose-dependent FLAME contour row.

    The selected face indices and barycentric coordinates belong
    to one discrete yaw entry from the official 79-row FLAME
    dynamic landmark embedding.
    """

    requested_yaw_degrees: float
    selected_yaw_degrees: float
    yaw_bin_index: int
    landmark_face_indices: np.ndarray
    landmark_barycentric_coordinates: np.ndarray

    def __post_init__(
        self,
    ) -> None:
        requested_yaw = float(
            self.requested_yaw_degrees
        )
        selected_yaw = float(
            self.selected_yaw_degrees
        )
        yaw_bin_index = int(
            self.yaw_bin_index
        )

        face_indices = np.asarray(
            self.landmark_face_indices,
            dtype=np.int64,
        ).copy()

        barycentric_coordinates = np.asarray(
            self.landmark_barycentric_coordinates,
            dtype=np.float64,
        ).copy()

        if not math.isfinite(
            requested_yaw
        ):
            raise ValueError(
                "requested_yaw_degrees must be finite."
            )

        if not math.isfinite(
            selected_yaw
        ):
            raise ValueError(
                "selected_yaw_degrees must be finite."
            )

        if not 0 <= yaw_bin_index < 79:
            raise ValueError(
                "yaw_bin_index must be in the range 0..78."
            )

        if (
            face_indices.ndim != 1
            or face_indices.shape[0] == 0
        ):
            raise ValueError(
                "landmark_face_indices must have "
                "shape (L,) with L > 0."
            )

        expected_barycentric_shape = (
            face_indices.shape[0],
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
            "requested_yaw_degrees",
            requested_yaw,
        )
        object.__setattr__(
            self,
            "selected_yaw_degrees",
            selected_yaw,
        )
        object.__setattr__(
            self,
            "yaw_bin_index",
            yaw_bin_index,
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
    def landmark_count(
        self,
    ) -> int:
        return int(
            self.landmark_face_indices.shape[0]
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "requested_yaw_degrees": (
                self.requested_yaw_degrees
            ),
            "selected_yaw_degrees": (
                self.selected_yaw_degrees
            ),
            "yaw_bin_index": self.yaw_bin_index,
            "landmark_count": self.landmark_count,
            "landmark_face_indices": (
                self.landmark_face_indices.tolist()
            ),
            "landmark_barycentric_coordinates": (
                self
                .landmark_barycentric_coordinates
                .tolist()
            ),
        }


class AtlasPortraitFlameDynamicLandmarkSelector:
    """
    Selects one row from the official FLAME dynamic embedding.

    Official 79-row layout:

    - row 0: zero yaw,
    - rows 1..39: positive yaw from +1 through +39 degrees,
    - rows 40..78: negative yaw from -1 through -39 degrees.

    Yaw is rounded to the nearest integral degree using the same
    ties-to-even behaviour as the official PyTorch implementation.
    Values outside -39..+39 degrees are clamped to the appropriate
    terminal row.

    This class performs no root-pose extraction, FLAME deformation,
    barycentric evaluation, fitting, rendering, or STL generation.
    """

    _EXPECTED_YAW_BIN_COUNT = 79
    _MAXIMUM_ABSOLUTE_YAW_DEGREES = 39

    @classmethod
    def select(
        cls,
        embedding: AtlasPortraitFlameDynamicLandmarkEmbedding,
        *,
        yaw_degrees: Any,
    ) -> AtlasPortraitFlameDynamicLandmarkSelection:
        if not isinstance(
            embedding,
            AtlasPortraitFlameDynamicLandmarkEmbedding,
        ):
            raise TypeError(
                "embedding must be an "
                "AtlasPortraitFlameDynamicLandmarkEmbedding "
                "instance."
            )

        if (
            embedding.yaw_bin_count
            != cls._EXPECTED_YAW_BIN_COUNT
        ):
            raise ValueError(
                "embedding yaw_bin_count must be exactly 79 "
                "for the official FLAME dynamic landmark layout."
            )

        requested_yaw = cls._normalize_yaw_degrees(
            yaw_degrees
        )

        rounded_yaw = int(
            np.rint(
                requested_yaw
            )
        )

        clamped_yaw = max(
            -cls._MAXIMUM_ABSOLUTE_YAW_DEGREES,
            min(
                cls._MAXIMUM_ABSOLUTE_YAW_DEGREES,
                rounded_yaw,
            ),
        )

        yaw_bin_index = cls._yaw_to_bin_index(
            clamped_yaw
        )

        return AtlasPortraitFlameDynamicLandmarkSelection(
            requested_yaw_degrees=requested_yaw,
            selected_yaw_degrees=float(
                clamped_yaw
            ),
            yaw_bin_index=yaw_bin_index,
            landmark_face_indices=(
                embedding.landmark_face_indices[
                    yaw_bin_index
                ]
            ),
            landmark_barycentric_coordinates=(
                embedding
                .landmark_barycentric_coordinates[
                    yaw_bin_index
                ]
            ),
        )

    @staticmethod
    def _normalize_yaw_degrees(
        value: Any,
    ) -> float:
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
                Real,
            )
        ):
            raise TypeError(
                "yaw_degrees must be a finite real number."
            )

        yaw_degrees = float(
            value
        )

        if not math.isfinite(
            yaw_degrees
        ):
            raise ValueError(
                "yaw_degrees must be finite."
            )

        return yaw_degrees

    @staticmethod
    def _yaw_to_bin_index(
        rounded_yaw_degrees: int,
    ) -> int:
        if rounded_yaw_degrees >= 0:
            return rounded_yaw_degrees

        return 39 - rounded_yaw_degrees
