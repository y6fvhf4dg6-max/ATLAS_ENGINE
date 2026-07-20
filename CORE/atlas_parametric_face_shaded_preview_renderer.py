from __future__ import annotations

import math
from typing import Any

import numpy as np

from CORE.atlas_parametric_face_shaded_preview_result import (
    AtlasParametricFaceShadedPreviewResult,
)
from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)


class AtlasParametricFaceShadedPreviewRenderer:
    """
    Renders deterministic grayscale shading from a
    regular-grid parametric face surface.

    Processing:
    - calculate row and column surface tangents
    - derive normalized front-facing surface normals
    - apply Lambertian diffuse lighting
    - combine ambient and diffuse intensity
    - produce aligned float64 and uint8 preview arrays

    The renderer performs no deformation, image writing,
    projection, triangulation, relief compression, or
    mesh generation.
    """

    DEFAULT_LIGHT_DIRECTION = (
        0.4,
        -0.5,
        0.7681145747868608,
    )

    DEFAULT_AMBIENT_STRENGTH = 0.25
    DEFAULT_DIFFUSE_STRENGTH = 0.75

    NORMAL_MAGNITUDE_EPSILON = 1e-12
    LIGHT_MAGNITUDE_EPSILON = 1e-12

    @classmethod
    def render(
        cls,
        surface: AtlasParametricFaceSurface,
        *,
        light_direction: tuple[float, float, float] = (
            DEFAULT_LIGHT_DIRECTION
        ),
        ambient_strength: float = (
            DEFAULT_AMBIENT_STRENGTH
        ),
        diffuse_strength: float = (
            DEFAULT_DIFFUSE_STRENGTH
        ),
    ) -> AtlasParametricFaceShadedPreviewResult:
        if not isinstance(
            surface,
            AtlasParametricFaceSurface,
        ):
            raise TypeError(
                "surface must be an "
                "AtlasParametricFaceSurface instance."
            )

        normalized_light_direction = (
            cls._normalize_light_direction(
                light_direction,
            )
        )

        ambient_value = cls._normalize_strength(
            ambient_strength,
            name="ambient_strength",
        )

        diffuse_value = cls._normalize_strength(
            diffuse_strength,
            name="diffuse_strength",
        )

        normals = cls._calculate_normals(
            surface,
        )

        light_vector = np.asarray(
            normalized_light_direction,
            dtype=np.float64,
        )

        diffuse_response = np.einsum(
            "ijk,k->ij",
            normals,
            light_vector,
        )

        diffuse_response = np.clip(
            diffuse_response,
            0.0,
            1.0,
        )

        shading = (
            ambient_value
            + diffuse_value
            * diffuse_response
        )

        shading = np.clip(
            shading,
            0.0,
            1.0,
        ).astype(
            np.float64,
            copy=True,
        )

        preview = np.rint(
            shading * 255.0,
        ).astype(
            np.uint8,
        )

        return AtlasParametricFaceShadedPreviewResult(
            shading=shading,
            preview=preview,
            light_direction=(
                normalized_light_direction
            ),
            ambient_strength=ambient_value,
            diffuse_strength=diffuse_value,
        )

    @classmethod
    def _calculate_normals(
        cls,
        surface: AtlasParametricFaceSurface,
    ) -> np.ndarray:
        x_coordinates = surface.x_coordinates
        y_coordinates = surface.y_coordinates
        z_coordinates = surface.z_coordinates

        column_tangent = np.stack(
            (
                np.gradient(
                    x_coordinates,
                    axis=1,
                ),
                np.gradient(
                    y_coordinates,
                    axis=1,
                ),
                np.gradient(
                    z_coordinates,
                    axis=1,
                ),
            ),
            axis=-1,
        )

        row_tangent = np.stack(
            (
                np.gradient(
                    x_coordinates,
                    axis=0,
                ),
                np.gradient(
                    y_coordinates,
                    axis=0,
                ),
                np.gradient(
                    z_coordinates,
                    axis=0,
                ),
            ),
            axis=-1,
        )

        normals = np.cross(
            column_tangent,
            row_tangent,
        )

        magnitudes = np.linalg.norm(
            normals,
            axis=-1,
        )

        invalid_mask = (
            magnitudes
            <= cls.NORMAL_MAGNITUDE_EPSILON
        )

        safe_magnitudes = np.where(
            invalid_mask,
            1.0,
            magnitudes,
        )

        normals = (
            normals
            / safe_magnitudes[
                ...,
                np.newaxis,
            ]
        )

        if np.any(
            invalid_mask,
        ):
            normals = normals.copy()
            normals[
                invalid_mask
            ] = (
                0.0,
                0.0,
                1.0,
            )

        return normals.astype(
            np.float64,
            copy=False,
        )

    @classmethod
    def _normalize_light_direction(
        cls,
        value: Any,
    ) -> tuple[float, float, float]:
        try:
            components = tuple(
                float(component)
                for component in value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "light_direction must contain "
                "three numeric components."
            ) from exc

        if len(components) != 3:
            raise ValueError(
                "light_direction must contain "
                "three components."
            )

        if not all(
            math.isfinite(component)
            for component in components
        ):
            raise ValueError(
                "light_direction must be finite."
            )

        magnitude = math.sqrt(
            sum(
                component * component
                for component in components
            )
        )

        if magnitude <= cls.LIGHT_MAGNITUDE_EPSILON:
            raise ValueError(
                "light_direction must be non-zero."
            )

        return (
            components[0] / magnitude,
            components[1] / magnitude,
            components[2] / magnitude,
        )

    @staticmethod
    def _normalize_strength(
        value: Any,
        *,
        name: str,
    ) -> float:
        try:
            strength = float(
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
            strength,
        ):
            raise ValueError(
                f"{name} must be finite."
            )

        if not (
            0.0
            <= strength
            <= 1.0
        ):
            raise ValueError(
                f"{name} must be in the "
                "0.0..1.0 range."
            )

        return strength
