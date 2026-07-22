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

    Two shading modes are supported:

    - flat shading:
      triangle_faces is omitted and each covered pixel uses
      the corresponding face normal.

    - smooth shading:
      triangle_faces is supplied and each covered pixel uses
      barycentrically interpolated vertex normals.

    Background pixels receive a separate constant intensity.

    The renderer performs no fitting, rasterization, image writing,
    relief compression, or STL generation.
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
    _NORMAL_MAGNITUDE_EPSILON = 1.0e-12

    @classmethod
    def render(
        cls,
        rasterization: (
            AtlasPortraitFlameTriangleRasterization
        ),
        *,
        normal_field: AtlasPortraitFlameNormalField,
        triangle_faces: Any = None,
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

        normalized_triangle_faces = None

        if triangle_faces is not None:
            normalized_triangle_faces = (
                cls._normalize_triangle_faces(
                    triangle_faces,
                    normal_field=normal_field,
                )
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
            if normalized_triangle_faces is None:
                covered_normals = (
                    normal_field.face_normals[
                        covered_indices
                    ]
                )
            else:
                covered_normals = (
                    cls._interpolate_vertex_normals(
                        rasterization,
                        normal_field=normal_field,
                        triangle_faces=(
                            normalized_triangle_faces
                        ),
                        covered_triangle_indices=(
                            covered_indices
                        ),
                    )
                )

            light_vector = np.asarray(
                normalized_light_direction,
                dtype=np.float64,
            )

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
    def _normalize_triangle_faces(
        cls,
        value: Any,
        *,
        normal_field: AtlasPortraitFlameNormalField,
    ) -> np.ndarray:
        try:
            numeric_faces = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "triangle_faces must be numeric."
            ) from exc

        if (
            numeric_faces.ndim != 2
            or numeric_faces.shape[1] != 3
        ):
            raise ValueError(
                "triangle_faces must have shape (F, 3)."
            )

        if not np.isfinite(
            numeric_faces,
        ).all():
            raise ValueError(
                "triangle_faces contains non-finite values."
            )

        if not np.equal(
            numeric_faces,
            np.rint(
                numeric_faces,
            ),
        ).all():
            raise ValueError(
                "triangle_faces must contain integer indices."
            )

        faces = numeric_faces.astype(
            np.int64,
            copy=True,
        )

        if faces.shape[0] != normal_field.face_count:
            raise ValueError(
                "triangle_faces face count must match "
                "normal_field face_count."
            )

        if faces.size:
            if np.any(
                faces < 0,
            ):
                raise ValueError(
                    "triangle_faces contains negative indices."
                )

            if np.any(
                faces
                >= normal_field.vertex_count
            ):
                raise ValueError(
                    "triangle_faces contains indices outside "
                    "normal_field vertex normals."
                )

        return faces

    @classmethod
    def _interpolate_vertex_normals(
        cls,
        rasterization: (
            AtlasPortraitFlameTriangleRasterization
        ),
        *,
        normal_field: AtlasPortraitFlameNormalField,
        triangle_faces: np.ndarray,
        covered_triangle_indices: np.ndarray,
    ) -> np.ndarray:
        covered_faces = triangle_faces[
            covered_triangle_indices
        ]

        corner_normals = normal_field.vertex_normals[
            covered_faces
        ]

        covered_weights = (
            rasterization.barycentric_coordinates[
                rasterization.coverage_mask
            ]
        )

        interpolated_normals = np.einsum(
            "ij,ijk->ik",
            covered_weights,
            corner_normals,
        )

        magnitudes = np.linalg.norm(
            interpolated_normals,
            axis=1,
        )

        if np.any(
            magnitudes
            <= cls._NORMAL_MAGNITUDE_EPSILON
        ):
            raise ValueError(
                "Interpolated vertex normal magnitude "
                "must be non-zero."
            )

        return (
            interpolated_normals
            / magnitudes[
                :,
                None,
            ]
        ).astype(
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
