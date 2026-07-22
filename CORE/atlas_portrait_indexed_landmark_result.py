from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from numbers import Integral
from types import MappingProxyType
from typing import Any

import numpy as np


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasPortraitIndexedLandmarkResult:
    """
    Immutable provider-independent indexed landmark result.

    The result preserves ordered integer landmark IDs and
    normalized three-dimensional landmark coordinates.

    X and Y coordinates use the inclusive normalized
    0.0..1.0 image range. Z coordinates are provider-defined
    and must only be finite.

    The contract performs no provider loading, landmark
    correspondence, camera fitting, FLAME deformation,
    rendering, relief compression, or STL generation.
    """

    image_width: int
    image_height: int
    landmark_ids: tuple[int, ...]
    landmarks_3d: np.ndarray
    confidence: float
    provider_id: str
    metadata: Mapping[str, Any]

    def __post_init__(
        self,
    ) -> None:
        image_width = self._normalize_dimension(
            self.image_width,
            name="image_width",
        )
        image_height = self._normalize_dimension(
            self.image_height,
            name="image_height",
        )

        landmark_ids = self._normalize_landmark_ids(
            self.landmark_ids,
        )

        landmarks_3d = self._normalize_landmarks_3d(
            self.landmarks_3d,
            landmark_count=len(
                landmark_ids
            ),
        )

        confidence = self._normalize_confidence(
            self.confidence,
        )
        provider_id = self._normalize_provider_id(
            self.provider_id,
        )
        metadata = self._normalize_metadata(
            self.metadata,
        )

        landmarks_3d.setflags(
            write=False
        )

        object.__setattr__(
            self,
            "image_width",
            image_width,
        )
        object.__setattr__(
            self,
            "image_height",
            image_height,
        )
        object.__setattr__(
            self,
            "landmark_ids",
            landmark_ids,
        )
        object.__setattr__(
            self,
            "landmarks_3d",
            landmarks_3d,
        )
        object.__setattr__(
            self,
            "confidence",
            confidence,
        )
        object.__setattr__(
            self,
            "provider_id",
            provider_id,
        )
        object.__setattr__(
            self,
            "metadata",
            metadata,
        )

    @property
    def landmark_count(
        self,
    ) -> int:
        return len(
            self.landmark_ids
        )

    @property
    def points_2d(
        self,
    ) -> np.ndarray:
        points = self.landmarks_3d[
            :,
            :2,
        ].copy()

        points.setflags(
            write=False
        )

        return points

    @property
    def index_by_id(
        self,
    ) -> Mapping[int, int]:
        return MappingProxyType(
            {
                landmark_id: index
                for index, landmark_id in enumerate(
                    self.landmark_ids
                )
            }
        )

    def landmark_3d(
        self,
        landmark_id: int,
    ) -> np.ndarray:
        index = self.index_by_id[
            landmark_id
        ]

        point = self.landmarks_3d[
            index
        ].copy()

        point.setflags(
            write=False
        )

        return point

    def landmark_2d(
        self,
        landmark_id: int,
    ) -> np.ndarray:
        index = self.index_by_id[
            landmark_id
        ]

        point = self.landmarks_3d[
            index,
            :2,
        ].copy()

        point.setflags(
            write=False
        )

        return point

    def pixel_landmark(
        self,
        landmark_id: int,
    ) -> tuple[float, float]:
        normalized_x, normalized_y = self.landmark_2d(
            landmark_id
        )

        return (
            float(
                normalized_x
                * (
                    self.image_width
                    - 1
                )
            ),
            float(
                normalized_y
                * (
                    self.image_height
                    - 1
                )
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "image_width": self.image_width,
            "image_height": self.image_height,
            "landmark_count": self.landmark_count,
            "landmark_ids": list(
                self.landmark_ids
            ),
            "landmarks_3d": (
                self.landmarks_3d.tolist()
            ),
            "confidence": self.confidence,
            "provider_id": self.provider_id,
            "metadata": {
                key: self.metadata[
                    key
                ]
                for key in sorted(
                    self.metadata
                )
            },
        }

    @staticmethod
    def _normalize_dimension(
        value: Any,
        *,
        name: str,
    ) -> int:
        try:
            numeric_value = float(
                value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if not math.isfinite(
            numeric_value
        ):
            raise ValueError(
                f"{name} must be finite."
            )

        if not numeric_value.is_integer():
            raise ValueError(
                f"{name} must be an integer."
            )

        integer_value = int(
            numeric_value
        )

        if integer_value <= 0:
            raise ValueError(
                f"{name} must be greater than zero."
            )

        return integer_value

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
            raw_ids = tuple(
                value
            )
        except TypeError as exc:
            raise TypeError(
                "landmark_ids must be a non-empty "
                "sequence of integers."
            ) from exc

        if not raw_ids:
            raise ValueError(
                "landmark_ids must not be empty."
            )

        normalized_ids: list[int] = []

        for raw_id in raw_ids:
            if (
                isinstance(
                    raw_id,
                    bool,
                )
                or not isinstance(
                    raw_id,
                    Integral,
                )
            ):
                raise TypeError(
                    "landmark_ids must contain integer values."
                )

            landmark_id = int(
                raw_id
            )

            if landmark_id < 0:
                raise ValueError(
                    "landmark_ids must not contain "
                    "negative values."
                )

            normalized_ids.append(
                landmark_id
            )

        if len(
            normalized_ids
        ) != len(
            set(
                normalized_ids
            )
        ):
            raise ValueError(
                "landmark_ids must contain unique values."
            )

        return tuple(
            normalized_ids
        )

    @staticmethod
    def _normalize_landmarks_3d(
        value: Any,
        *,
        landmark_count: int,
    ) -> np.ndarray:
        try:
            landmarks = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "landmarks_3d must be numeric."
            ) from exc

        expected_shape = (
            landmark_count,
            3,
        )

        if landmarks.shape != expected_shape:
            raise ValueError(
                "landmarks_3d must have shape "
                f"{expected_shape}."
            )

        if not np.isfinite(
            landmarks
        ).all():
            raise ValueError(
                "landmarks_3d must contain only finite values."
            )

        points_2d = landmarks[
            :,
            :2,
        ]

        if (
            np.any(
                points_2d < 0.0
            )
            or np.any(
                points_2d > 1.0
            )
        ):
            raise ValueError(
                "landmarks_3d x/y coordinates must be "
                "in the 0.0..1.0 range."
            )

        return landmarks.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _normalize_confidence(
        value: Any,
    ) -> float:
        try:
            confidence = float(
                value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "confidence must be numeric."
            ) from exc

        if not math.isfinite(
            confidence
        ):
            raise ValueError(
                "confidence must be finite."
            )

        if not (
            0.0
            <= confidence
            <= 1.0
        ):
            raise ValueError(
                "confidence must be in the "
                "0.0..1.0 range."
            )

        return confidence

    @staticmethod
    def _normalize_provider_id(
        value: Any,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "provider_id must be a string."
            )

        provider_id = value.strip()

        if not provider_id:
            raise ValueError(
                "provider_id must not be blank."
            )

        return provider_id

    @staticmethod
    def _normalize_metadata(
        value: Any,
    ) -> Mapping[str, Any]:
        if not isinstance(
            value,
            Mapping,
        ):
            raise TypeError(
                "metadata must be a mapping."
            )

        copied = {
            str(
                key
            ): item
            for key, item in value.items()
        }

        return MappingProxyType(
            {
                key: copied[
                    key
                ]
                for key in sorted(
                    copied
                )
            }
        )
