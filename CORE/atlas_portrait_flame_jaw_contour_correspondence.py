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
class AtlasPortraitFlameJawContourCorrespondence:
    """
    Immutable dynamic jaw-contour correspondence result.

    The contract stores:

    - ordered MediaPipe jaw landmark IDs,
    - target image points,
    - matched FLAME contour points,
    - matched FLAME boundary-edge vertex indices,
    - per-landmark visibility,
    - per-landmark pixel residuals,
    - deterministic metadata.

    It performs no contour extraction, edge filtering,
    correspondence search, visibility evaluation, FLAME
    deformation, camera projection, optimization, rendering,
    relief conversion, or STL generation.
    """

    landmark_ids: tuple[int, ...]
    target_points_2d: np.ndarray
    matched_points_2d: np.ndarray
    matched_edge_vertex_indices: np.ndarray
    visible_landmark_mask: np.ndarray
    residuals: np.ndarray
    metadata: Mapping[str, Any]

    def __post_init__(
        self,
    ) -> None:
        landmark_ids = self._normalize_landmark_ids(
            self.landmark_ids
        )

        landmark_count = len(
            landmark_ids
        )

        target_points = self._normalize_points(
            self.target_points_2d,
            name="target_points_2d",
            landmark_count=landmark_count,
        )

        matched_points = self._normalize_points(
            self.matched_points_2d,
            name="matched_points_2d",
            landmark_count=landmark_count,
        )

        matched_edge_indices = (
            self._normalize_edge_vertex_indices(
                self.matched_edge_vertex_indices,
                landmark_count=landmark_count,
            )
        )

        visible_mask = self._normalize_visibility_mask(
            self.visible_landmark_mask,
            landmark_count=landmark_count,
        )

        residuals = self._normalize_residuals(
            self.residuals,
            landmark_count=landmark_count,
        )

        metadata = self._normalize_metadata(
            self.metadata
        )

        for array in (
            target_points,
            matched_points,
            matched_edge_indices,
            visible_mask,
            residuals,
        ):
            array.setflags(
                write=False
            )

        object.__setattr__(
            self,
            "landmark_ids",
            landmark_ids,
        )
        object.__setattr__(
            self,
            "target_points_2d",
            target_points,
        )
        object.__setattr__(
            self,
            "matched_points_2d",
            matched_points,
        )
        object.__setattr__(
            self,
            "matched_edge_vertex_indices",
            matched_edge_indices,
        )
        object.__setattr__(
            self,
            "visible_landmark_mask",
            visible_mask,
        )
        object.__setattr__(
            self,
            "residuals",
            residuals,
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
    def visible_landmark_count(
        self,
    ) -> int:
        return int(
            np.count_nonzero(
                self.visible_landmark_mask
            )
        )

    @property
    def visible_residuals(
        self,
    ) -> np.ndarray:
        result = self.residuals[
            self.visible_landmark_mask
        ].copy()

        result.setflags(
            write=False
        )

        return result

    @property
    def mean_residual(
        self,
    ) -> float:
        values = self.visible_residuals

        if values.size == 0:
            return 0.0

        return float(
            np.mean(
                values
            )
        )

    @property
    def median_residual(
        self,
    ) -> float:
        values = self.visible_residuals

        if values.size == 0:
            return 0.0

        return float(
            np.median(
                values
            )
        )

    @property
    def maximum_residual(
        self,
    ) -> float:
        values = self.visible_residuals

        if values.size == 0:
            return 0.0

        return float(
            np.max(
                values
            )
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "landmark_ids": list(
                self.landmark_ids
            ),
            "landmark_count": self.landmark_count,
            "target_points_2d": (
                self.target_points_2d.tolist()
            ),
            "matched_points_2d": (
                self.matched_points_2d.tolist()
            ),
            "matched_edge_vertex_indices": (
                self
                .matched_edge_vertex_indices
                .tolist()
            ),
            "visible_landmark_mask": (
                self.visible_landmark_mask.tolist()
            ),
            "visible_landmark_count": (
                self.visible_landmark_count
            ),
            "residuals": self.residuals.tolist(),
            "mean_residual": self.mean_residual,
            "median_residual": self.median_residual,
            "maximum_residual": self.maximum_residual,
            "metadata": {
                key: self._to_plain_value(
                    self.metadata[
                        key
                    ]
                )
                for key in sorted(
                    self.metadata
                )
            },
        }

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
                    (
                        bool,
                        np.bool_,
                    ),
                )
                or not isinstance(
                    raw_id,
                    Integral,
                )
            ):
                raise TypeError(
                    "landmark_ids must contain "
                    "integer values."
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
    def _normalize_points(
        value: Any,
        *,
        name: str,
        landmark_count: int,
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

        expected_shape = (
            landmark_count,
            2,
        )

        if points.shape != expected_shape:
            raise ValueError(
                f"{name} must have shape "
                f"{expected_shape}."
            )

        if not np.isfinite(
            points
        ).all():
            raise ValueError(
                f"{name} contains non-finite values."
            )

        return points.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _normalize_edge_vertex_indices(
        value: Any,
        *,
        landmark_count: int,
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
                "matched_edge_vertex_indices "
                "must be numeric."
            ) from exc

        expected_shape = (
            landmark_count,
            2,
        )

        if numeric.shape != expected_shape:
            raise ValueError(
                "matched_edge_vertex_indices must "
                f"have shape {expected_shape}."
            )

        if not np.isfinite(
            numeric
        ).all():
            raise ValueError(
                "matched_edge_vertex_indices contains "
                "non-finite values."
            )

        if not np.equal(
            numeric,
            np.rint(
                numeric
            ),
        ).all():
            raise ValueError(
                "matched_edge_vertex_indices must "
                "contain integer values."
            )

        indices = numeric.astype(
            np.int64,
            copy=True,
        )

        if np.any(
            indices < 0
        ):
            raise ValueError(
                "matched_edge_vertex_indices must not "
                "contain negative values."
            )

        return indices

    @staticmethod
    def _normalize_visibility_mask(
        value: Any,
        *,
        landmark_count: int,
    ) -> np.ndarray:
        array = np.asarray(
            value
        )

        expected_shape = (
            landmark_count,
        )

        if array.shape != expected_shape:
            raise ValueError(
                "visible_landmark_mask must have "
                f"shape {expected_shape}."
            )

        if array.dtype.kind != "b":
            raise ValueError(
                "visible_landmark_mask must contain "
                "boolean values."
            )

        return array.astype(
            np.bool_,
            copy=True,
        )

    @staticmethod
    def _normalize_residuals(
        value: Any,
        *,
        landmark_count: int,
    ) -> np.ndarray:
        try:
            residuals = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "residuals must be numeric."
            ) from exc

        expected_shape = (
            landmark_count,
        )

        if residuals.shape != expected_shape:
            raise ValueError(
                "residuals must have shape "
                f"{expected_shape}."
            )

        if not np.isfinite(
            residuals
        ).all():
            raise ValueError(
                "residuals contains non-finite values."
            )

        if np.any(
            residuals < 0.0
        ):
            raise ValueError(
                "residuals must not contain "
                "negative values."
            )

        return residuals.astype(
            np.float64,
            copy=True,
        )

    @classmethod
    def _normalize_metadata(
        cls,
        value: Any,
    ) -> Mapping[str, Any]:
        if not isinstance(
            value,
            Mapping,
        ):
            raise TypeError(
                "metadata must be a mapping."
            )

        normalized: dict[str, Any] = {}

        for raw_key in sorted(
            value,
            key=lambda item: str(
                item
            ),
        ):
            key = str(
                raw_key
            )

            normalized[
                key
            ] = cls._snapshot_plain_value(
                value[
                    raw_key
                ]
            )

        return MappingProxyType(
            normalized
        )

    @classmethod
    def _snapshot_plain_value(
        cls,
        value: Any,
    ) -> Any:
        if isinstance(
            value,
            np.ndarray,
        ):
            copied = value.copy()
            copied.setflags(
                write=False
            )
            return copied

        if isinstance(
            value,
            np.generic,
        ):
            return value.item()

        if isinstance(
            value,
            Mapping,
        ):
            return MappingProxyType(
                {
                    str(
                        key
                    ): cls._snapshot_plain_value(
                        item
                    )
                    for key, item in sorted(
                        value.items(),
                        key=lambda pair: str(
                            pair[
                                0
                            ]
                        ),
                    )
                }
            )

        if isinstance(
            value,
            (
                list,
                tuple,
            ),
        ):
            return tuple(
                cls._snapshot_plain_value(
                    item
                )
                for item in value
            )

        if isinstance(
            value,
            float,
        ) and not math.isfinite(
            value
        ):
            raise ValueError(
                "metadata must not contain "
                "non-finite float values."
            )

        return value

    @classmethod
    def _to_plain_value(
        cls,
        value: Any,
    ) -> Any:
        if isinstance(
            value,
            np.ndarray,
        ):
            return value.tolist()

        if isinstance(
            value,
            np.generic,
        ):
            return value.item()

        if isinstance(
            value,
            Mapping,
        ):
            return {
                key: cls._to_plain_value(
                    item
                )
                for key, item in sorted(
                    value.items()
                )
            }

        if isinstance(
            value,
            (
                tuple,
                list,
            ),
        ):
            return [
                cls._to_plain_value(
                    item
                )
                for item in value
            ]

        return value
