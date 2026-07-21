from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np

from CORE.atlas_parametric_face_shaded_preview_renderer import (
    AtlasParametricFaceShadedPreviewRenderer,
)
from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)
from CORE.atlas_parametric_face_surface_validity_analyzer import (
    AtlasParametricFaceSurfaceValidityAnalyzer,
)
from CORE.atlas_portrait_contact_plane_compression_comparison_result import (
    AtlasPortraitContactPlaneCompressionComparisonResult,
)


class AtlasPortraitContactPlaneCompressionEvaluator:
    """
    Evaluates one contact-plane compression result against
    its source parametric face surface.

    Processing:
    - validate the compression payload
    - construct the compressed surface using preserved X/Y
    - render source and compressed shaded previews with
      identical lighting
    - analyze both surfaces for geometric validity
    - calculate height and preview error metrics
    - verify preservation of the declared contact point
    - return an immutable comparison result

    It performs no contact-plane projection, compression,
    fitting, deformation, repair, triangulation, or mesh
    generation.
    """

    EVALUATION_MODE = "surface_preview_and_validity"

    REQUIRED_COMPRESSION_FIELDS = (
        "compression_mode",
        "source_shape",
        "source_maximum_height",
        "target_maximum_height",
        "compressed_height",
    )

    @classmethod
    def evaluate(
        cls,
        source_surface: AtlasParametricFaceSurface,
        *,
        compression: Mapping[str, Any],
        contact_row: int,
        contact_column: int,
        light_direction: tuple[float, float, float] = (
            AtlasParametricFaceShadedPreviewRenderer
            .DEFAULT_LIGHT_DIRECTION
        ),
        ambient_strength: float = (
            AtlasParametricFaceShadedPreviewRenderer
            .DEFAULT_AMBIENT_STRENGTH
        ),
        diffuse_strength: float = (
            AtlasParametricFaceShadedPreviewRenderer
            .DEFAULT_DIFFUSE_STRENGTH
        ),
    ) -> AtlasPortraitContactPlaneCompressionComparisonResult:
        if not isinstance(
            source_surface,
            AtlasParametricFaceSurface,
        ):
            raise TypeError(
                "source_surface must be an "
                "AtlasParametricFaceSurface instance."
            )

        if not isinstance(
            compression,
            Mapping,
        ):
            raise TypeError(
                "compression must be a mapping."
            )

        cls._validate_required_fields(
            compression,
        )

        normalized_contact_row = cls._normalize_index(
            contact_row,
            name="contact_row",
        )
        normalized_contact_column = cls._normalize_index(
            contact_column,
            name="contact_column",
        )

        cls._validate_contact_index(
            source_surface,
            contact_row=normalized_contact_row,
            contact_column=normalized_contact_column,
        )

        source_shape = cls._normalize_source_shape(
            compression["source_shape"],
        )

        if source_shape != source_surface.shape:
            raise ValueError(
                "compression source_shape must match "
                "source_surface shape."
            )

        compressed_height = cls._normalize_height_grid(
            compression["compressed_height"],
        )

        if compressed_height.shape != source_surface.shape:
            raise ValueError(
                "compressed_height shape must match "
                "source_surface shape."
            )

        source_maximum_height = cls._normalize_nonnegative_float(
            compression["source_maximum_height"],
            name="source_maximum_height",
        )

        target_maximum_height = cls._normalize_nonnegative_float(
            compression["target_maximum_height"],
            name="target_maximum_height",
        )

        if source_maximum_height <= 0.0:
            compression_ratio = 0.0
        else:
            compression_ratio = (
                target_maximum_height
                / source_maximum_height
            )

        compressed_surface = AtlasParametricFaceSurface(
            x_coordinates=source_surface.x_coordinates,
            y_coordinates=source_surface.y_coordinates,
            z_coordinates=compressed_height,
        )

        source_preview = (
            AtlasParametricFaceShadedPreviewRenderer.render(
                source_surface,
                light_direction=light_direction,
                ambient_strength=ambient_strength,
                diffuse_strength=diffuse_strength,
            )
        )

        compressed_preview = (
            AtlasParametricFaceShadedPreviewRenderer.render(
                compressed_surface,
                light_direction=light_direction,
                ambient_strength=ambient_strength,
                diffuse_strength=diffuse_strength,
            )
        )

        source_validity = (
            AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
                source_surface,
            )
        )

        compressed_validity = (
            AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
                compressed_surface,
            )
        )

        height_error = np.abs(
            compressed_height
            - source_surface.z_coordinates
        )

        preview_error = np.abs(
            source_preview.preview.astype(
                np.float64,
            )
            - compressed_preview.preview.astype(
                np.float64,
            )
        )

        contact_point_preserved = (
            cls._is_contact_point_preserved(
                compressed_height,
                contact_row=normalized_contact_row,
                contact_column=normalized_contact_column,
                target_maximum_height=target_maximum_height,
            )
        )

        compression_mode = str(
            compression["compression_mode"],
        ).strip()

        if not compression_mode:
            raise ValueError(
                "compression_mode must not be empty."
            )

        return (
            AtlasPortraitContactPlaneCompressionComparisonResult(
                source_height=source_surface.z_coordinates,
                compressed_height=compressed_height,
                source_maximum_height=source_maximum_height,
                target_maximum_height=target_maximum_height,
                compression_ratio=compression_ratio,
                contact_row=normalized_contact_row,
                contact_column=normalized_contact_column,
                maximum_absolute_height_error=float(
                    np.max(
                        height_error,
                    )
                ),
                mean_absolute_height_error=float(
                    np.mean(
                        height_error,
                    )
                ),
                preview_mean_absolute_error=float(
                    np.mean(
                        preview_error,
                    )
                ),
                preview_maximum_absolute_error=float(
                    np.max(
                        preview_error,
                    )
                ),
                contact_point_preserved=(
                    contact_point_preserved
                ),
                source_surface_safe=source_validity.is_safe,
                compressed_surface_safe=(
                    compressed_validity.is_safe
                ),
                metadata={
                    "compression_mode": compression_mode,
                    "evaluation_mode": cls.EVALUATION_MODE,
                    "light_direction": (
                        source_preview.light_direction
                    ),
                    "ambient_strength": (
                        source_preview.ambient_strength
                    ),
                    "diffuse_strength": (
                        source_preview.diffuse_strength
                    ),
                },
            )
        )

    @classmethod
    def _validate_required_fields(
        cls,
        compression: Mapping[str, Any],
    ) -> None:
        for field_name in cls.REQUIRED_COMPRESSION_FIELDS:
            if field_name not in compression:
                raise ValueError(
                    f"compression is missing "
                    f"{field_name}."
                )

    @staticmethod
    def _normalize_height_grid(
        value: Any,
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
                "compressed_height must be numeric."
            ) from exc

        if height_grid.ndim != 2:
            raise ValueError(
                "compressed_height must be "
                "two-dimensional."
            )

        if not np.isfinite(
            height_grid,
        ).all():
            raise ValueError(
                "compressed_height contains "
                "non-finite values."
            )

        if np.any(
            height_grid < 0.0,
        ):
            raise ValueError(
                "compressed_height must not contain "
                "negative values."
            )

        return height_grid.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _normalize_source_shape(
        value: Any,
    ) -> tuple[int, int]:
        try:
            components = tuple(
                value,
            )
        except TypeError as exc:
            raise ValueError(
                "source_shape must contain two integers."
            ) from exc

        if len(
            components,
        ) != 2:
            raise ValueError(
                "source_shape must contain two integers."
            )

        normalized: list[int] = []

        for component in components:
            if (
                isinstance(
                    component,
                    bool,
                )
                or not isinstance(
                    component,
                    int,
                )
            ):
                raise ValueError(
                    "source_shape must contain two integers."
                )

            normalized.append(
                component,
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
    def _validate_contact_index(
        surface: AtlasParametricFaceSurface,
        *,
        contact_row: int,
        contact_column: int,
    ) -> None:
        if not 0 <= contact_row < surface.row_count:
            raise ValueError(
                "contact_row is outside source_surface."
            )

        if not 0 <= contact_column < surface.column_count:
            raise ValueError(
                "contact_column is outside source_surface."
            )

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
    def _is_contact_point_preserved(
        compressed_height: np.ndarray,
        *,
        contact_row: int,
        contact_column: int,
        target_maximum_height: float,
    ) -> bool:
        contact_height = float(
            compressed_height[
                contact_row,
                contact_column,
            ]
        )

        maximum_height = float(
            np.max(
                compressed_height,
            )
        )

        tolerance = max(
            1.0e-12,
            abs(
                target_maximum_height,
            )
            * 1.0e-12,
        )

        return (
            math.isclose(
                contact_height,
                target_maximum_height,
                rel_tol=0.0,
                abs_tol=tolerance,
            )
            and math.isclose(
                contact_height,
                maximum_height,
                rel_tol=0.0,
                abs_tol=tolerance,
            )
        )
