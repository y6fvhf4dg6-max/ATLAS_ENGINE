from __future__ import annotations

from typing import Any

import numpy as np

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)
from CORE.atlas_portrait_flame_dense_identity_pipeline_result import (
    AtlasPortraitFlameDenseIdentityPipelineResult,
)
from CORE.atlas_portrait_flame_fitted_mesh_builder import (
    AtlasPortraitFlameFittedMeshBuilder,
)
from CORE.atlas_portrait_flame_fitted_shaded_preview_pipeline_result import (
    AtlasPortraitFlameFittedShadedPreviewPipelineResult,
)
from CORE.atlas_portrait_flame_pixel_camera_adapter import (
    AtlasPortraitFlamePixelCameraAdapter,
)
from CORE.atlas_portrait_flame_shaded_preview_pipeline import (
    AtlasPortraitFlameShadedPreviewPipeline,
)
from CORE.atlas_portrait_flame_shaded_preview_renderer import (
    AtlasPortraitFlameShadedPreviewRenderer,
)


class AtlasPortraitFlameFittedShadedPreviewPipeline:
    """
    Builds and renders a fitted FLAME shaded portrait preview.

    Processing sequence:

        dense-identity fitting result
        -> fitted image-coordinate FLAME mesh
        -> normalized-to-pixel camera conversion
        -> fitted-topology preview model
        -> shaded-preview pipeline
        -> immutable aggregate result

    The preview model uses the fitted mesh triangle winding,
    rather than the canonical FLAME winding. This is required
    because image-coordinate normalization reflects the Y axis
    and reverses triangle orientation.

    It performs no landmark loading, fitting, optimization,
    image writing, relief generation, mesh export, or STL
    generation.
    """

    @classmethod
    def run(
        cls,
        model: AtlasPortraitFlameCanonicalModel,
        *,
        fitting_result: (
            AtlasPortraitFlameDenseIdentityPipelineResult
        ),
        image_width: Any,
        image_height: Any,
        light_direction: tuple[float, float, float] = (
            AtlasPortraitFlameShadedPreviewRenderer
            .DEFAULT_LIGHT_DIRECTION
        ),
        ambient_strength: float = (
            AtlasPortraitFlameShadedPreviewRenderer
            .DEFAULT_AMBIENT_STRENGTH
        ),
        diffuse_strength: float = (
            AtlasPortraitFlameShadedPreviewRenderer
            .DEFAULT_DIFFUSE_STRENGTH
        ),
        background_intensity: float = (
            AtlasPortraitFlameShadedPreviewRenderer
            .DEFAULT_BACKGROUND_INTENSITY
        ),
    ) -> AtlasPortraitFlameFittedShadedPreviewPipelineResult:
        if not isinstance(
            model,
            AtlasPortraitFlameCanonicalModel,
        ):
            raise TypeError(
                "model must be an "
                "AtlasPortraitFlameCanonicalModel instance."
            )

        if not isinstance(
            fitting_result,
            AtlasPortraitFlameDenseIdentityPipelineResult,
        ):
            raise TypeError(
                "fitting_result must be an "
                "AtlasPortraitFlameDenseIdentityPipelineResult "
                "instance."
            )

        normalized_width = cls._normalize_image_dimension(
            image_width,
            name="image_width",
        )
        normalized_height = cls._normalize_image_dimension(
            image_height,
            name="image_height",
        )

        fitted_mesh = AtlasPortraitFlameFittedMeshBuilder.build(
            model,
            pipeline_result=fitting_result,
        )

        pixel_camera = AtlasPortraitFlamePixelCameraAdapter.adapt(
            fitting_result.final_camera,
            image_width=normalized_width,
            image_height=normalized_height,
        )

        preview_model = cls._build_preview_model(
            model,
            fitted_triangle_faces=(
                fitted_mesh.triangle_faces
            ),
        )

        shaded_preview_result = (
            AtlasPortraitFlameShadedPreviewPipeline.run(
                preview_model,
                skinned_vertices=fitted_mesh.vertices,
                camera=pixel_camera,
                image_width=normalized_width,
                image_height=normalized_height,
                light_direction=light_direction,
                ambient_strength=ambient_strength,
                diffuse_strength=diffuse_strength,
                background_intensity=background_intensity,
            )
        )

        return (
            AtlasPortraitFlameFittedShadedPreviewPipelineResult(
                fitting_result=fitting_result,
                fitted_mesh=fitted_mesh,
                pixel_camera=pixel_camera,
                shaded_preview_result=(
                    shaded_preview_result
                ),
                metadata={
                    "coordinate_space": "pixel",
                    "image_height": normalized_height,
                    "image_width": normalized_width,
                    "model_family": "flame",
                    "model_version": model.metadata.get(
                        "model_version"
                    ),
                    "pipeline": (
                        "flame_fitted_shaded_preview"
                    ),
                    "synthetic": model.metadata.get(
                        "synthetic"
                    ),
                },
            )
        )

    @staticmethod
    def _build_preview_model(
        model: AtlasPortraitFlameCanonicalModel,
        *,
        fitted_triangle_faces: Any,
    ) -> AtlasPortraitFlameCanonicalModel:
        return AtlasPortraitFlameCanonicalModel(
            template_vertices=model.template_vertices,
            triangle_faces=np.asarray(
                fitted_triangle_faces,
                dtype=np.int64,
            ).copy(),
            identity_shape_directions=(
                model.identity_shape_directions
            ),
            expression_shape_directions=(
                model.expression_shape_directions
            ),
            pose_directions=model.pose_directions,
            pose_parameter_count=model.pose_parameter_count,
            joint_regressor=model.joint_regressor,
            skinning_weights=model.skinning_weights,
            kinematic_tree=model.kinematic_tree,
            metadata={
                **dict(
                    model.metadata
                ),
                "coordinate_space": "image",
                "preview_topology": "fitted_mesh",
            },
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
            value
        )

        if normalized < 2:
            raise ValueError(
                f"{name} must be at least 2."
            )

        return normalized
