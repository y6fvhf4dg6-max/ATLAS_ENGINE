from __future__ import annotations

import math
from dataclasses import dataclass
from dataclasses import field
from types import MappingProxyType
from typing import Any
from typing import Mapping

import numpy as np


@dataclass(frozen=True)
class AtlasPortraitContactPlaneCompressionComparisonResult:
    """
    Immutable contact-plane compression comparison result.

    The contract stores source and compressed relief-height
    grids, compression metrics, shaded-preview error metrics,
    contact-point preservation, surface-safety flags, and
    deterministic metadata.

    It performs no contact-plane projection, compression,
    surface construction, rendering, validity analysis,
    triangulation, or mesh generation.
    """

    source_height: np.ndarray
    compressed_height: np.ndarray

    source_maximum_height: float
    target_maximum_height: float
    compression_ratio: float

    contact_row: int
    contact_column: int

    maximum_absolute_height_error: float
    mean_absolute_height_error: float

    preview_mean_absolute_error: float
    preview_maximum_absolute_error: float

    contact_point_preserved: bool
    source_surface_safe: bool
    compressed_surface_safe: bool

    metadata: Mapping[str, Any]

    height_deltas: np.ndarray = field(
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        source_height = self._normalize_height_grid(
            self.source_height,
            name="source_height",
        )

        compressed_height = self._normalize_height_grid(
            self.compressed_height,
            name="compressed_height",
        )

        if source_height.shape != compressed_height.shape:
            raise ValueError(
                "source_height and compressed_height "
                "must have identical shapes."
            )

        row_count, column_count = source_height.shape

        contact_row = self._normalize_index(
            self.contact_row,
            name="contact_row",
        )

        contact_column = self._normalize_index(
            self.contact_column,
            name="contact_column",
        )

        if not 0 <= contact_row < row_count:
            raise ValueError(
                "contact_row is outside the height grid."
            )

        if not 0 <= contact_column < column_count:
            raise ValueError(
                "contact_column is outside the height grid."
            )

        numeric_values = {
            "source_maximum_height": (
                self.source_maximum_height
            ),
            "target_maximum_height": (
                self.target_maximum_height
            ),
            "compression_ratio": self.compression_ratio,
            "maximum_absolute_height_error": (
                self.maximum_absolute_height_error
            ),
            "mean_absolute_height_error": (
                self.mean_absolute_height_error
            ),
            "preview_mean_absolute_error": (
                self.preview_mean_absolute_error
            ),
            "preview_maximum_absolute_error": (
                self.preview_maximum_absolute_error
            ),
        }

        normalized_numeric: dict[str, float] = {}

        for name, value in numeric_values.items():
            normalized_numeric[name] = (
                self._normalize_nonnegative_float(
                    value,
                    name=name,
                )
            )

        boolean_values = {
            "contact_point_preserved": (
                self.contact_point_preserved
            ),
            "source_surface_safe": (
                self.source_surface_safe
            ),
            "compressed_surface_safe": (
                self.compressed_surface_safe
            ),
        }

        normalized_booleans: dict[str, bool] = {}

        for name, value in boolean_values.items():
            normalized_booleans[name] = (
                self._normalize_boolean(
                    value,
                    name=name,
                )
            )

        metadata = self._normalize_metadata(
            self.metadata,
        )

        height_deltas = (
            compressed_height
            - source_height
        ).astype(
            np.float64,
            copy=True,
        )

        source_height.setflags(
            write=False,
        )
        compressed_height.setflags(
            write=False,
        )
        height_deltas.setflags(
            write=False,
        )

        object.__setattr__(
            self,
            "source_height",
            source_height,
        )
        object.__setattr__(
            self,
            "compressed_height",
            compressed_height,
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

        for name, value in normalized_numeric.items():
            object.__setattr__(
                self,
                name,
                value,
            )

        for name, value in normalized_booleans.items():
            object.__setattr__(
                self,
                name,
                value,
            )

        object.__setattr__(
            self,
            "metadata",
            metadata,
        )
        object.__setattr__(
            self,
            "height_deltas",
            height_deltas,
        )

    @property
    def shape(
        self,
    ) -> tuple[int, int]:
        return self.source_height.shape

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

    @staticmethod
    def _normalize_height_grid(
        value: Any,
        *,
        name: str,
    ) -> np.ndarray:
        try:
            height_grid = np.asarray(
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

        if height_grid.ndim != 2:
            raise ValueError(
                f"{name} must be two-dimensional."
            )

        row_count, column_count = height_grid.shape

        if row_count < 2 or column_count < 2:
            raise ValueError(
                f"{name} must contain at least two rows "
                "and two columns."
            )

        if not np.isfinite(
            height_grid,
        ).all():
            raise ValueError(
                f"{name} contains non-finite values."
            )

        if np.any(
            height_grid < 0.0,
        ):
            raise ValueError(
                f"{name} must not contain negative values."
            )

        return height_grid.astype(
            np.float64,
            copy=True,
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
    def _normalize_nonnegative_float(
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

        if numeric_value < 0.0:
            raise ValueError(
                f"{name} must not be negative."
            )

        return numeric_value

    @staticmethod
    def _normalize_boolean(
        value: Any,
        *,
        name: str,
    ) -> bool:
        if not isinstance(
            value,
            bool,
        ):
            raise TypeError(
                f"{name} must be a boolean."
            )

        return value

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

        return MappingProxyType(
            dict(
                value,
            )
        )
