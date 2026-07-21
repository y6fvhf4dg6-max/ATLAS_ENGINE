from __future__ import annotations

import math
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any
from typing import Mapping

import numpy as np


@dataclass(frozen=True)
class AtlasPortraitContactPlaneProjectionResult:
    """
    Immutable contact-plane projection result.

    The contract stores the nonnegative distance of every
    regular-grid face point from a frontal contact plane,
    the contact-plane Z position, the grid contact index,
    the maximum measured distance, the source grid shape,
    and deterministic projection metadata.

    It performs no face reconstruction, plane selection,
    distance calculation, relief compression, rendering,
    triangulation, or mesh generation.
    """

    distance_to_plane: np.ndarray
    contact_plane_z: float
    contact_row: int
    contact_column: int
    maximum_distance: float
    source_shape: tuple[int, int]
    metadata: Mapping[str, Any]

    DISTANCE_TOLERANCE = 1e-12

    def __post_init__(self) -> None:
        distance_to_plane = self._normalize_distance_grid(
            self.distance_to_plane,
        )

        row_count, column_count = distance_to_plane.shape

        source_shape = self._normalize_source_shape(
            self.source_shape,
        )

        if source_shape != distance_to_plane.shape:
            raise ValueError(
                "source_shape must match "
                "distance_to_plane shape."
            )

        contact_row = self._normalize_index(
            self.contact_row,
            name="contact_row",
        )
        contact_column = self._normalize_index(
            self.contact_column,
            name="contact_column",
        )

        if not (
            0
            <= contact_row
            < row_count
        ):
            raise ValueError(
                "contact_row is outside the source grid."
            )

        if not (
            0
            <= contact_column
            < column_count
        ):
            raise ValueError(
                "contact_column is outside the source grid."
            )

        contact_plane_z = self._normalize_float(
            self.contact_plane_z,
            name="contact_plane_z",
        )

        maximum_distance = self._normalize_float(
            self.maximum_distance,
            name="maximum_distance",
        )

        if maximum_distance < 0.0:
            raise ValueError(
                "maximum_distance must not be negative."
            )

        contact_distance = float(
            distance_to_plane[
                contact_row,
                contact_column,
            ]
        )

        if not math.isclose(
            contact_distance,
            0.0,
            abs_tol=self.DISTANCE_TOLERANCE,
            rel_tol=0.0,
        ):
            raise ValueError(
                "distance at the contact point must be zero."
            )

        measured_maximum_distance = float(
            np.max(
                distance_to_plane,
            )
        )

        if not math.isclose(
            maximum_distance,
            measured_maximum_distance,
            abs_tol=self.DISTANCE_TOLERANCE,
            rel_tol=self.DISTANCE_TOLERANCE,
        ):
            raise ValueError(
                "maximum_distance must match the maximum "
                "value in distance_to_plane."
            )

        metadata = self._normalize_metadata(
            self.metadata,
        )

        distance_to_plane.setflags(
            write=False,
        )

        object.__setattr__(
            self,
            "distance_to_plane",
            distance_to_plane,
        )
        object.__setattr__(
            self,
            "contact_plane_z",
            contact_plane_z,
        )
        object.__setattr__(
            self,
            "contact_row",
            contact_row,
        )
        object.__setattr__(
            self,
            "contact_column",
            contact_column,
        )
        object.__setattr__(
            self,
            "maximum_distance",
            maximum_distance,
        )
        object.__setattr__(
            self,
            "source_shape",
            source_shape,
        )
        object.__setattr__(
            self,
            "metadata",
            metadata,
        )

    @property
    def shape(
        self,
    ) -> tuple[int, int]:
        return self.distance_to_plane.shape

    @property
    def row_count(
        self,
    ) -> int:
        return int(
            self.shape[0],
        )

    @property
    def column_count(
        self,
    ) -> int:
        return int(
            self.shape[1],
        )

    @property
    def contact_index(
        self,
    ) -> tuple[int, int]:
        return (
            self.contact_row,
            self.contact_column,
        )

    @property
    def minimum_distance(
        self,
    ) -> float:
        return float(
            np.min(
                self.distance_to_plane,
            )
        )

    @staticmethod
    def _normalize_distance_grid(
        value: Any,
    ) -> np.ndarray:
        try:
            distance_to_plane = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "distance_to_plane must be numeric."
            ) from exc

        if distance_to_plane.ndim != 2:
            raise ValueError(
                "distance_to_plane must be "
                "two-dimensional."
            )

        row_count, column_count = (
            distance_to_plane.shape
        )

        if row_count < 2 or column_count < 2:
            raise ValueError(
                "distance_to_plane must contain at least "
                "two rows and two columns."
            )

        if not np.isfinite(
            distance_to_plane,
        ).all():
            raise ValueError(
                "distance_to_plane contains "
                "non-finite values."
            )

        if np.any(
            distance_to_plane < 0.0,
        ):
            raise ValueError(
                "distance_to_plane must not contain "
                "negative values."
            )

        return distance_to_plane.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _normalize_source_shape(
        value: Any,
    ) -> tuple[int, int]:
        if not isinstance(
            value,
            tuple,
        ):
            raise TypeError(
                "source_shape must be a tuple."
            )

        if len(value) != 2:
            raise ValueError(
                "source_shape must contain two values."
            )

        normalized: list[int] = []

        for dimension in value:
            if (
                isinstance(
                    dimension,
                    bool,
                )
                or not isinstance(
                    dimension,
                    int,
                )
            ):
                raise TypeError(
                    "source_shape values must be integers."
                )

            if dimension < 2:
                raise ValueError(
                    "source_shape values must be "
                    "at least 2."
                )

            normalized.append(
                dimension,
            )

        return (
            normalized[0],
            normalized[1],
        )

    @staticmethod
    def _normalize_index(
        value: Any,
        *,
        name: str,
    ) -> int:
        if (
            isinstance(
                value,
                bool,
            )
            or not isinstance(
                value,
                int,
            )
        ):
            raise TypeError(
                f"{name} must be an integer."
            )

        return value

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

        copied = dict(
            value,
        )

        return MappingProxyType(
            copied,
        )
