from __future__ import annotations

from typing import Any

import numpy as np

from CORE.atlas_portrait_weak_perspective_camera import (
    AtlasPortraitWeakPerspectiveCamera,
)


class AtlasPortraitFlamePixelCameraAdapter:
    """
    Converts a normalized weak-perspective portrait camera
    into pixel-coordinate space.

    The conversion uses the same isotropic image extent as
    the portrait fitting chain:

        pixel_scale = max(
            image_width - 1,
            image_height - 1,
        )

    Camera scale, translation, projected points, and weighted
    reprojection error are multiplied by this value.

    It performs no camera fitting, FLAME deformation,
    projection, rasterization, rendering, image writing,
    relief generation, or STL export.
    """

    @classmethod
    def adapt(
        cls,
        camera: AtlasPortraitWeakPerspectiveCamera,
        *,
        image_width: Any,
        image_height: Any,
    ) -> AtlasPortraitWeakPerspectiveCamera:
        if not isinstance(
            camera,
            AtlasPortraitWeakPerspectiveCamera,
        ):
            raise TypeError(
                "camera must be an "
                "AtlasPortraitWeakPerspectiveCamera instance."
            )

        normalized_width = cls._normalize_image_dimension(
            image_width,
            name="image_width",
        )
        normalized_height = cls._normalize_image_dimension(
            image_height,
            name="image_height",
        )

        pixel_scale = float(
            max(
                normalized_width - 1,
                normalized_height - 1,
            )
        )

        source_coordinate_space = str(
            camera.metadata.get(
                "coordinate_space",
                "normalized",
            )
        )

        metadata = dict(
            camera.metadata,
        )
        metadata.update(
            {
                "coordinate_space": "pixel",
                "image_height": normalized_height,
                "image_width": normalized_width,
                "pixel_scale": pixel_scale,
                "source_coordinate_space": (
                    source_coordinate_space
                ),
            }
        )

        return AtlasPortraitWeakPerspectiveCamera(
            scale=camera.scale * pixel_scale,
            translation_x=(
                camera.translation_x
                * pixel_scale
            ),
            translation_y=(
                camera.translation_y
                * pixel_scale
            ),
            projected_points_2d=(
                np.asarray(
                    camera.projected_points_2d,
                    dtype=np.float64,
                )
                * pixel_scale
            ),
            weighted_root_mean_square_error=(
                camera.weighted_root_mean_square_error
                * pixel_scale
            ),
            metadata=metadata,
        )

    @staticmethod
    def _normalize_image_dimension(
        value: Any,
        *,
        name: str,
    ) -> int:
        if isinstance(
            value,
            (
                bool,
                np.bool_,
            ),
        ):
            raise TypeError(
                f"{name} must be an integer."
            )

        if not isinstance(
            value,
            (
                int,
                np.integer,
            ),
        ):
            raise TypeError(
                f"{name} must be an integer."
            )

        normalized = int(
            value,
        )

        if normalized < 2:
            raise ValueError(
                f"{name} must be at least 2."
            )

        return normalized
