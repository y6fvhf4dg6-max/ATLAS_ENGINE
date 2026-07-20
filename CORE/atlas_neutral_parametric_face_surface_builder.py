from __future__ import annotations

import math
from typing import Any

import numpy as np

from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)


class AtlasNeutralParametricFaceSurfaceBuilder:
    """
    Builds a deterministic neutral frontal face surface.

    The generated surface is a regular normalized X/Y grid
    with a continuous symmetric Z field. It provides only
    a broad neutral facial form suitable for later
    parameter deformation.

    It performs no landmark fitting, identity modeling,
    depth projection, relief compression, triangulation,
    or mesh generation.
    """

    @classmethod
    def build(
        cls,
        *,
        row_count: int,
        column_count: int,
    ) -> AtlasParametricFaceSurface:
        row_count_value = cls._validate_grid_dimension(
            row_count,
            name="row_count",
        )
        column_count_value = cls._validate_grid_dimension(
            column_count,
            name="column_count",
        )

        x_axis = np.linspace(
            -1.0,
            1.0,
            column_count_value,
            dtype=np.float64,
        )
        y_axis = np.linspace(
            -1.0,
            1.0,
            row_count_value,
            dtype=np.float64,
        )

        x_coordinates, y_coordinates = np.meshgrid(
            x_axis,
            y_axis,
        )

        z_coordinates = cls._build_depth_field(
            x_coordinates=x_coordinates,
            y_coordinates=y_coordinates,
        )

        return AtlasParametricFaceSurface(
            x_coordinates=x_coordinates,
            y_coordinates=y_coordinates,
            z_coordinates=z_coordinates,
        )

    @classmethod
    def _build_depth_field(
        cls,
        *,
        x_coordinates: np.ndarray,
        y_coordinates: np.ndarray,
    ) -> np.ndarray:
        face_envelope = np.clip(
            1.0
            - (
                x_coordinates / 1.0
            )
            ** 2
            - (
                y_coordinates / 1.15
            )
            ** 2,
            0.0,
            None,
        )

        broad_cranium = (
            0.34
            * np.power(
                face_envelope,
                0.72,
                dtype=np.float64,
            )
        )

        cheek_pair = (
            0.10
            * np.exp(
                -(
                    (
                        (
                            np.abs(
                                x_coordinates,
                            )
                            - 0.40
                        )
                        / 0.25
                    )
                    ** 2
                    + (
                        (
                            y_coordinates
                            + 0.05
                        )
                        / 0.34
                    )
                    ** 2
                )
            )
        )

        forehead = (
            0.07
            * np.exp(
                -(
                    (
                        x_coordinates
                        / 0.58
                    )
                    ** 2
                    + (
                        (
                            y_coordinates
                            - 0.58
                        )
                        / 0.30
                    )
                    ** 2
                )
            )
        )

        chin = (
            0.08
            * np.exp(
                -(
                    (
                        x_coordinates
                        / 0.32
                    )
                    ** 2
                    + (
                        (
                            y_coordinates
                            + 0.73
                        )
                        / 0.22
                    )
                    ** 2
                )
            )
        )

        nose_bridge = (
            0.26
            * np.exp(
                -(
                    (
                        x_coordinates
                        / 0.17
                    )
                    ** 2
                    + (
                        (
                            y_coordinates
                            - 0.08
                        )
                        / 0.46
                    )
                    ** 2
                )
            )
        )

        nose_tip = (
            0.30
            * np.exp(
                -(
                    (
                        x_coordinates
                        / 0.15
                    )
                    ** 2
                    + (
                        (
                            y_coordinates
                            + 0.12
                        )
                        / 0.16
                    )
                    ** 2
                )
            )
        )

        z_coordinates = (
            broad_cranium
            + cheek_pair
            + forehead
            + chin
            + nose_bridge
            + nose_tip
        )

        z_coordinates *= np.sqrt(
            face_envelope,
            dtype=np.float64,
        )

        minimum = float(
            z_coordinates.min(),
        )

        if minimum < 0.0:
            z_coordinates = (
                z_coordinates - minimum
            )

        return z_coordinates.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _validate_grid_dimension(
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

        if value < 2:
            raise ValueError(
                f"{name} must be at least 2."
            )

        if not math.isfinite(
            float(value),
        ):
            raise ValueError(
                f"{name} must be finite."
            )

        return value
