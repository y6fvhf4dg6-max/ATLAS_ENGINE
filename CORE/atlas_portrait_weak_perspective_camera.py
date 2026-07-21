from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

import numpy as np


@dataclass(frozen=True)
class AtlasPortraitWeakPerspectiveCamera:
    """
    Immutable weak-perspective portrait camera result.

    The contract stores scale, image-plane translation,
    projected 2D landmark points, weighted reprojection
    error, and deterministic metadata.

    It performs no camera initialization, optimization,
    FLAME deformation, coordinate normalization,
    rendering, relief compression, or STL generation.
    """

    scale: float
    translation_x: float
    translation_y: float
    projected_points_2d: np.ndarray
    weighted_root_mean_square_error: float
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        scale = self._normalize_float(
            self.scale,
            name="scale",
        )

        if scale <= 0.0:
            raise ValueError(
                "scale must be greater than zero."
            )

        translation_x = self._normalize_float(
            self.translation_x,
            name="translation_x",
        )

        translation_y = self._normalize_float(
            self.translation_y,
            name="translation_y",
        )

        projected_points_2d = (
            self._normalize_projected_points(
                self.projected_points_2d,
            )
        )

        weighted_error = self._normalize_float(
            self.weighted_root_mean_square_error,
            name="weighted_root_mean_square_error",
        )

        if weighted_error < 0.0:
            raise ValueError(
                "weighted_root_mean_square_error must "
                "not be negative."
            )

        metadata = self._normalize_metadata(
            self.metadata,
        )

        projected_points_2d.setflags(
            write=False,
        )

        object.__setattr__(
            self,
            "scale",
            scale,
        )
        object.__setattr__(
            self,
            "translation_x",
            translation_x,
        )
        object.__setattr__(
            self,
            "translation_y",
            translation_y,
        )
        object.__setattr__(
            self,
            "projected_points_2d",
            projected_points_2d,
        )
        object.__setattr__(
            self,
            "weighted_root_mean_square_error",
            weighted_error,
        )
        object.__setattr__(
            self,
            "metadata",
            metadata,
        )

    @property
    def projected_point_count(
        self,
    ) -> int:
        return int(
            self.projected_points_2d.shape[0],
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "scale": self.scale,
            "translation_x": self.translation_x,
            "translation_y": self.translation_y,
            "projected_point_count": (
                self.projected_point_count
            ),
            "projected_points_2d": (
                self.projected_points_2d.tolist()
            ),
            "weighted_root_mean_square_error": (
                self.weighted_root_mean_square_error
            ),
            "metadata": {
                key: self.metadata[key]
                for key in sorted(
                    self.metadata,
                )
            },
        }

    @staticmethod
    def _normalize_projected_points(
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
                "projected_points_2d must be numeric."
            ) from exc

        if (
            points.ndim != 2
            or points.shape[1] != 2
            or points.shape[0] < 1
        ):
            raise ValueError(
                "projected_points_2d must have shape "
                "(N, 2) and contain at least one point."
            )

        if not np.isfinite(
            points,
        ).all():
            raise ValueError(
                "projected_points_2d contains non-finite "
                "values."
            )

        return points.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _normalize_float(
        value: Any,
        *,
        name: str,
    ) -> float:
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

        return numeric_value

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
