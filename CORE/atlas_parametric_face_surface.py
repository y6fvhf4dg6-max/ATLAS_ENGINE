from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class AtlasParametricFaceSurface:
    """
    Immutable regular-grid parametric face surface.

    The contract stores aligned X, Y, and Z coordinate
    grids representing a deterministic three-dimensional
    frontal face surface.

    It performs no parameter fitting, deformation,
    triangulation, projection, depth rendering,
    relief compression, or mesh generation.
    """

    x_coordinates: np.ndarray
    y_coordinates: np.ndarray
    z_coordinates: np.ndarray

    def __post_init__(self) -> None:
        x_coordinates = self._normalize_coordinate_grid(
            self.x_coordinates,
            name="x_coordinates",
        )
        y_coordinates = self._normalize_coordinate_grid(
            self.y_coordinates,
            name="y_coordinates",
        )
        z_coordinates = self._normalize_coordinate_grid(
            self.z_coordinates,
            name="z_coordinates",
        )

        if not (
            x_coordinates.shape
            == y_coordinates.shape
            == z_coordinates.shape
        ):
            raise ValueError(
                "Coordinate grids must have identical shapes."
            )

        row_count, column_count = x_coordinates.shape

        if row_count < 2 or column_count < 2:
            raise ValueError(
                "Coordinate grids must contain at least "
                "two rows and two columns."
            )

        x_coordinates.setflags(
            write=False,
        )
        y_coordinates.setflags(
            write=False,
        )
        z_coordinates.setflags(
            write=False,
        )

        object.__setattr__(
            self,
            "x_coordinates",
            x_coordinates,
        )
        object.__setattr__(
            self,
            "y_coordinates",
            y_coordinates,
        )
        object.__setattr__(
            self,
            "z_coordinates",
            z_coordinates,
        )

    @property
    def shape(
        self,
    ) -> tuple[int, int]:
        return self.x_coordinates.shape

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
    def minimum_z(
        self,
    ) -> float:
        return float(
            self.z_coordinates.min(),
        )

    @property
    def maximum_z(
        self,
    ) -> float:
        return float(
            self.z_coordinates.max(),
        )

    @staticmethod
    def _normalize_coordinate_grid(
        value: Any,
        *,
        name: str,
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
                f"{name} must be numeric."
            ) from exc

        if coordinates.ndim != 2:
            raise ValueError(
                f"{name} must be two-dimensional."
            )

        if not np.isfinite(
            coordinates,
        ).all():
            raise ValueError(
                f"{name} contains non-finite values."
            )

        return coordinates.astype(
            np.float64,
            copy=True,
        )
