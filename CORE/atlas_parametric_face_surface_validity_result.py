from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AtlasParametricFaceSurfaceValidityResult:
    """
    Immutable parametric face surface validity report.

    The result stores grid dimensions, foldover and
    degeneracy counts, inverted-normal counts, minimum
    signed cell area, minimum normal Z, minimum local
    edge lengths, and the tolerances used to classify
    the surface.

    It performs no surface analysis, deformation,
    rendering, triangulation, or mesh generation.
    """

    row_count: int
    column_count: int
    cell_count: int
    folded_cell_count: int
    degenerate_cell_count: int
    inverted_normal_count: int

    minimum_signed_cell_area: float
    minimum_normal_z: float
    minimum_horizontal_edge_length: float
    minimum_vertical_edge_length: float

    area_tolerance: float
    normal_z_tolerance: float
    edge_length_tolerance: float

    def __post_init__(self) -> None:
        integer_values = {
            "row_count": self.row_count,
            "column_count": self.column_count,
            "cell_count": self.cell_count,
            "folded_cell_count": self.folded_cell_count,
            "degenerate_cell_count": self.degenerate_cell_count,
            "inverted_normal_count": self.inverted_normal_count,
        }

        normalized_integers: dict[str, int] = {}

        for name, value in integer_values.items():
            normalized_integers[name] = self._normalize_integer(
                value,
                name=name,
            )

        if normalized_integers["row_count"] < 2:
            raise ValueError(
                "row_count must be at least 2."
            )

        if normalized_integers["column_count"] < 2:
            raise ValueError(
                "column_count must be at least 2."
            )

        for name in (
            "cell_count",
            "folded_cell_count",
            "degenerate_cell_count",
            "inverted_normal_count",
        ):
            if normalized_integers[name] < 0:
                raise ValueError(
                    f"{name} must not be negative."
                )

        expected_cell_count = (
            normalized_integers["row_count"] - 1
        ) * (
            normalized_integers["column_count"] - 1
        )

        if (
            normalized_integers["cell_count"]
            != expected_cell_count
        ):
            raise ValueError(
                "cell_count must equal "
                "(row_count - 1) * "
                "(column_count - 1)."
            )

        if (
            normalized_integers["folded_cell_count"]
            > normalized_integers["cell_count"]
        ):
            raise ValueError(
                "folded_cell_count must not exceed "
                "cell_count."
            )

        if (
            normalized_integers["degenerate_cell_count"]
            > normalized_integers["cell_count"]
        ):
            raise ValueError(
                "degenerate_cell_count must not exceed "
                "cell_count."
            )

        point_count = (
            normalized_integers["row_count"]
            * normalized_integers["column_count"]
        )

        if (
            normalized_integers["inverted_normal_count"]
            > point_count
        ):
            raise ValueError(
                "inverted_normal_count must not exceed "
                "point_count."
            )

        numeric_values = {
            "minimum_signed_cell_area": (
                self.minimum_signed_cell_area
            ),
            "minimum_normal_z": self.minimum_normal_z,
            "minimum_horizontal_edge_length": (
                self.minimum_horizontal_edge_length
            ),
            "minimum_vertical_edge_length": (
                self.minimum_vertical_edge_length
            ),
            "area_tolerance": self.area_tolerance,
            "normal_z_tolerance": (
                self.normal_z_tolerance
            ),
            "edge_length_tolerance": (
                self.edge_length_tolerance
            ),
        }

        normalized_numeric: dict[str, float] = {}

        for name, value in numeric_values.items():
            normalized_numeric[name] = self._normalize_float(
                value,
                name=name,
            )

        for name in (
            "minimum_horizontal_edge_length",
            "minimum_vertical_edge_length",
            "area_tolerance",
            "edge_length_tolerance",
        ):
            if normalized_numeric[name] < 0.0:
                raise ValueError(
                    f"{name} must not be negative."
                )

        for name, value in normalized_integers.items():
            object.__setattr__(
                self,
                name,
                value,
            )

        for name, value in normalized_numeric.items():
            object.__setattr__(
                self,
                name,
                value,
            )

    @property
    def point_count(
        self,
    ) -> int:
        return (
            self.row_count
            * self.column_count
        )

    @property
    def folded_cell_ratio(
        self,
    ) -> float:
        return (
            self.folded_cell_count
            / self.cell_count
        )

    @property
    def degenerate_cell_ratio(
        self,
    ) -> float:
        return (
            self.degenerate_cell_count
            / self.cell_count
        )

    @property
    def inverted_normal_ratio(
        self,
    ) -> float:
        return (
            self.inverted_normal_count
            / self.point_count
        )

    @property
    def has_foldover(
        self,
    ) -> bool:
        return (
            self.folded_cell_count > 0
            or self.minimum_signed_cell_area
            < -self.area_tolerance
        )

    @property
    def has_degenerate_cells(
        self,
    ) -> bool:
        return (
            self.degenerate_cell_count > 0
            or abs(
                self.minimum_signed_cell_area
            )
            <= self.area_tolerance
        )

    @property
    def has_inverted_normals(
        self,
    ) -> bool:
        return (
            self.inverted_normal_count > 0
            or self.minimum_normal_z
            < self.normal_z_tolerance
        )

    @property
    def is_safe(
        self,
    ) -> bool:
        return not (
            self.has_foldover
            or self.has_degenerate_cells
            or self.has_inverted_normals
        )

    @staticmethod
    def _normalize_integer(
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
