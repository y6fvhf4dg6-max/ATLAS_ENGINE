from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from CORE.atlas_parametric_face_parameters import (
    AtlasParametricFaceParameters,
)
from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)


@dataclass(frozen=True)
class AtlasParametricFaceSurfaceComparisonResult:
    """
    Immutable neutral/adapted parametric face surface
    comparison result.

    The result stores both surfaces, the parameters used
    for adaptation, read-only coordinate delta arrays,
    and maximum absolute coordinate differences.

    It performs no measurement, parameter initialization,
    deformation, rendering, projection, triangulation,
    or mesh generation.
    """

    neutral_surface: AtlasParametricFaceSurface
    adapted_surface: AtlasParametricFaceSurface
    parameters: AtlasParametricFaceParameters

    x_deltas: np.ndarray = field(
        init=False,
        repr=False,
    )
    y_deltas: np.ndarray = field(
        init=False,
        repr=False,
    )
    z_deltas: np.ndarray = field(
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.neutral_surface,
            AtlasParametricFaceSurface,
        ):
            raise TypeError(
                "neutral_surface must be an "
                "AtlasParametricFaceSurface instance."
            )

        if not isinstance(
            self.adapted_surface,
            AtlasParametricFaceSurface,
        ):
            raise TypeError(
                "adapted_surface must be an "
                "AtlasParametricFaceSurface instance."
            )

        if not isinstance(
            self.parameters,
            AtlasParametricFaceParameters,
        ):
            raise TypeError(
                "parameters must be an "
                "AtlasParametricFaceParameters instance."
            )

        if (
            self.neutral_surface.shape
            != self.adapted_surface.shape
        ):
            raise ValueError(
                "neutral_surface and adapted_surface "
                "must have the same shape."
            )

        object.__setattr__(
            self,
            "x_deltas",
            self._build_delta_array(
                self.adapted_surface.x_coordinates,
                self.neutral_surface.x_coordinates,
            ),
        )
        object.__setattr__(
            self,
            "y_deltas",
            self._build_delta_array(
                self.adapted_surface.y_coordinates,
                self.neutral_surface.y_coordinates,
            ),
        )
        object.__setattr__(
            self,
            "z_deltas",
            self._build_delta_array(
                self.adapted_surface.z_coordinates,
                self.neutral_surface.z_coordinates,
            ),
        )

    @property
    def maximum_absolute_x_delta(self) -> float:
        return float(
            np.max(
                np.abs(
                    self.x_deltas,
                )
            )
        )

    @property
    def maximum_absolute_y_delta(self) -> float:
        return float(
            np.max(
                np.abs(
                    self.y_deltas,
                )
            )
        )

    @property
    def maximum_absolute_z_delta(self) -> float:
        return float(
            np.max(
                np.abs(
                    self.z_deltas,
                )
            )
        )

    @property
    def has_coordinate_change(self) -> bool:
        return any(
            value > 0.0
            for value in (
                self.maximum_absolute_x_delta,
                self.maximum_absolute_y_delta,
                self.maximum_absolute_z_delta,
            )
        )

    @staticmethod
    def _build_delta_array(
        adapted_values: np.ndarray,
        neutral_values: np.ndarray,
    ) -> np.ndarray:
        deltas = np.asarray(
            adapted_values - neutral_values,
            dtype=np.float64,
        ).copy()

        deltas.setflags(
            write=False,
        )

        return deltas
