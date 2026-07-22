from __future__ import annotations

import math
from typing import Any

import numpy as np

from CORE.atlas_portrait_flame_shaded_preview_result import (
    AtlasPortraitFlameShadedPreviewResult,
)
from CORE.atlas_portrait_flame_triangle_rasterizer import (
    AtlasPortraitFlameTriangleRasterization,
)
from CORE.atlas_portrait_flame_vertex_normal_evaluator import (
    AtlasPortraitFlameNormalField,
)


class AtlasPortraitFlameShadedPreviewRenderer:
    """
    Renders deterministic grayscale FLAME mesh shading.

    Covered pixels use the face normal referenced by the
    rasterization triangle-index buffer. Lighting is
    Lambertian with ambient and diffuse strengths.

    Background pixels receive a separate constant intensity.

    The renderer performs no fitting, rasterization,
    image writing, relief compression, or STL generation.
    """

    DEFAULT_LIGHT_DIRECTION = (
        0.4,
        -0.5,
        0.7681145747868608,
    )
    DEFAULT_AMBIENT_STRENGTH = 0.25
    DEFAULT_DIFFUSE_STRENGTH = 0.75
    DEFAULT_BACKGROUND_INTENSITY = 0.0

    _LIGHT_MAGNITUDE_EPSILON = 1.0e-12

    @classmethod
    def render(
        cls,
        rasterization: (
            AtlasPortraitFlameTriangleRasterization
        ),
        *,
        normal_field: AtlasPortraitFlameNormalField,
        light_direction: tuple[float, float, float] = (
            DEFAULT_LIGHT_DIRECTION
        ),
        ambient_strength: float = (
            DEFAULT_AMBIENT_STRENGTH
        ),
        diffuse_strength: float = (
            DEFAULT_DIFFUSE_STRENGTH
        ),
        background_intensity: float = (
            DEFAULT_BACKGROUND_INTENSITY
        ),
    ) -> AtlasPortraitFlameShadedPreviewResult:
        if not isinstance(
            rasterization,
            AtlasPortraitFlameTriangleRasterization,
        ):
            raise TypeError(
                "rasterization must be an "
                "AtlasPortraitFlameTriangleRasterization "
                "instance."
            )

        if not isinstance(
            normal_field,
            AtlasPortraitFlameNormalField,
        ):
            raise TypeError(
                "normal_field must be an "
                "AtlasPortraitFlameNormalField instance."
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
        background_value = cls._normalize_strength(
            background_intensity,
            name="background_intensity",
        )

        covered_indices = (
            rasterization.triangle_index_buffer[
                rasterization.coverage_mask
            ]
        )

        if covered_indices.size:
            maximum_triangle_index = int(
                np.max(
                    covered_indices,
                )
            )

            if (
                maximum_triangle_index
                >= normal_field.face_count
            ):
                raise ValueError(
                    "triangle_index_buffer contains an "
                    "index outside normal_field face normals."
                )

        shading = np.full(
            (
                rasterization.image_height,
                rasterization.image_width,
            ),
            background_value,
            dtype=np.float64,
        )

        if covered_indices.size:
            light_vector = np.asarray(
                normalized_light_direction,
                dtype=np.float64,
            )

            covered_normals = normal_field.face_normals[
                covered_indices
            ]

            diffuse_response = np.einsum(
                "ij,j->i",
                covered_normals,
                light_vector,
            )

            diffuse_response = np.clip(
                diffuse_response,
                0.0,
                1.0,
            )

            covered_shading = (
                ambient_value
                + diffuse_value
                * diffuse_response
            )

            shading[
                rasterization.coverage_mask
            ] = np.clip(
                covered_shading,
                0.0,
                1.0,
            )

        preview = np.rint(
            shading
            * 255.0
        ).astype(
            np.uint8,
        )

        return AtlasPortraitFlameShadedPreviewResult(
            shading=shading,
            preview=preview,
            coverage_mask=rasterization.coverage_mask,
            light_direction=normalized_light_direction,
            ambient_strength=ambient_value,
            diffuse_strength=diffuse_value,
            background_intensity=background_value,
        )

    @classmethod
    def _normalize_light_direction(
        cls,
        value: Any,
    ) -> tuple[float, float, float]:
        try:
            components = tuple(
                float(
                    component,
                )
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

        if len(
            components,
        ) != 3:
            raise ValueError(
                "light_direction must contain "
                "three components."
            )

        if not all(
            math.isfinite(
                component,
            )
            for component in components
        ):
            raise ValueError(
                "light_direction must be finite."
            )

        magnitude = math.sqrt(
            sum(
                component
                * component
                for component in components
            )
        )

        if magnitude <= cls._LIGHT_MAGNITUDE_EPSILON:
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
