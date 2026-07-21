from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

import numpy as np


@dataclass(frozen=True)
class AtlasPortraitWeakPerspectiveFittingInput:
    """
    Immutable provider-independent weak-perspective
    portrait fitting input.

    The contract stores ordered canonical 3D landmarks,
    ordered normalized portrait 2D landmarks, landmark
    weights, image dimensions, and deterministic metadata.

    It performs no camera estimation, optimization,
    FLAME deformation, projection, rendering, relief
    compression, or STL generation.
    """

    landmark_names: tuple[str, ...]
    source_points_3d: np.ndarray
    target_points_2d: np.ndarray
    landmark_weights: np.ndarray
    image_width: int
    image_height: int
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        landmark_names = self._normalize_landmark_names(
            self.landmark_names,
        )

        landmark_count = len(
            landmark_names,
        )

        source_points_3d = self._normalize_points(
            self.source_points_3d,
            name="source_points_3d",
            landmark_count=landmark_count,
            coordinate_count=3,
        )

        target_points_2d = self._normalize_points(
            self.target_points_2d,
            name="target_points_2d",
            landmark_count=landmark_count,
            coordinate_count=2,
        )

        if (
            np.any(
                target_points_2d < 0.0,
            )
            or np.any(
                target_points_2d > 1.0,
            )
        ):
            raise ValueError(
                "target_points_2d coordinates must be "
                "in the 0.0..1.0 range."
            )

        landmark_weights = self._normalize_weights(
            self.landmark_weights,
            landmark_count=landmark_count,
        )

        image_width = self._normalize_dimension(
            self.image_width,
            name="image_width",
        )

        image_height = self._normalize_dimension(
            self.image_height,
            name="image_height",
        )

        metadata = self._normalize_metadata(
            self.metadata,
        )

        for array in (
            source_points_3d,
            target_points_2d,
            landmark_weights,
        ):
            array.setflags(
                write=False,
            )

        object.__setattr__(
            self,
            "landmark_names",
            landmark_names,
        )
        object.__setattr__(
            self,
            "source_points_3d",
            source_points_3d,
        )
        object.__setattr__(
            self,
            "target_points_2d",
            target_points_2d,
        )
        object.__setattr__(
            self,
            "landmark_weights",
            landmark_weights,
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
            "metadata",
            metadata,
        )

    @property
    def landmark_count(
        self,
    ) -> int:
        return len(
            self.landmark_names,
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "landmark_count": self.landmark_count,
            "landmark_names": list(
                self.landmark_names,
            ),
            "source_points_3d": (
                self.source_points_3d.tolist()
            ),
            "target_points_2d": (
                self.target_points_2d.tolist()
            ),
            "landmark_weights": (
                self.landmark_weights.tolist()
            ),
            "image_width": self.image_width,
            "image_height": self.image_height,
            "metadata": {
                key: self.metadata[key]
                for key in sorted(
                    self.metadata,
                )
            },
        }

    @staticmethod
    def _normalize_landmark_names(
        value: Any,
    ) -> tuple[str, ...]:
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
                "landmark_names must be a non-empty "
                "sequence of strings."
            )

        try:
            raw_names = tuple(
                value,
            )
        except TypeError as exc:
            raise TypeError(
                "landmark_names must be a non-empty "
                "sequence of strings."
            ) from exc

        if not raw_names:
            raise ValueError(
                "landmark_names must not be empty."
            )

        normalized_names: list[str] = []

        for raw_name in raw_names:
            if not isinstance(
                raw_name,
                str,
            ):
                raise TypeError(
                    "landmark_names must contain only "
                    "strings."
                )

            normalized_name = raw_name.strip()

            if not normalized_name:
                raise ValueError(
                    "landmark_names must not contain "
                    "blank values."
                )

            normalized_names.append(
                normalized_name,
            )

        if len(
            normalized_names,
        ) != len(
            set(
                normalized_names,
            )
        ):
            raise ValueError(
                "landmark_names must be unique."
            )

        return tuple(
            normalized_names,
        )

    @staticmethod
    def _normalize_points(
        value: Any,
        *,
        name: str,
        landmark_count: int,
        coordinate_count: int,
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
                f"{name} must be numeric."
            ) from exc

        if points.shape != (
            landmark_count,
            coordinate_count,
        ):
            raise ValueError(
                f"{name} must have shape "
                f"({landmark_count}, {coordinate_count})."
            )

        if not np.isfinite(
            points,
        ).all():
            raise ValueError(
                f"{name} contains non-finite values."
            )

        return points.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _normalize_weights(
        value: Any,
        *,
        landmark_count: int,
    ) -> np.ndarray:
        try:
            weights = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "landmark_weights must be numeric."
            ) from exc

        if weights.shape != (
            landmark_count,
        ):
            raise ValueError(
                "landmark_weights must have shape "
                f"({landmark_count},)."
            )

        if not np.isfinite(
            weights,
        ).all():
            raise ValueError(
                "landmark_weights contains non-finite "
                "values."
            )

        if np.any(
            weights <= 0.0,
        ):
            raise ValueError(
                "landmark_weights must contain only "
                "positive values."
            )

        return weights.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _normalize_dimension(
        value: Any,
        *,
        name: str,
    ) -> int:
        try:
            numeric_value = float(
                value,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if not math.isfinite(
            numeric_value,
        ):
            raise ValueError(
                f"{name} must be finite."
            )

        if not numeric_value.is_integer():
            raise ValueError(
                f"{name} must be an integer."
            )

        integer_value = int(
            numeric_value,
        )

        if integer_value <= 0:
            raise ValueError(
                f"{name} must be greater than zero."
            )

        return integer_value

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
                key,
            ): item
            for key, item in value.items()
        }

        return MappingProxyType(
            {
                key: copied[key]
                for key in sorted(
                    copied,
                )
            }
        )
