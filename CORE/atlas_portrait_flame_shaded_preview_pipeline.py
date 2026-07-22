from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)
from CORE.atlas_portrait_flame_deformed_mesh_evaluator import (
    AtlasPortraitFlameDeformedMesh,
    AtlasPortraitFlameDeformedMeshEvaluator,
)
from CORE.atlas_portrait_flame_shaded_preview_renderer import (
    AtlasPortraitFlameShadedPreviewRenderer,
)
from CORE.atlas_portrait_flame_shaded_preview_result import (
    AtlasPortraitFlameShadedPreviewResult,
)
from CORE.atlas_portrait_flame_triangle_rasterizer import (
    AtlasPortraitFlameTriangleRasterization,
    AtlasPortraitFlameTriangleRasterizer,
)
from CORE.atlas_portrait_flame_triangle_visibility_evaluator import (
    AtlasPortraitFlameTriangleVisibility,
    AtlasPortraitFlameTriangleVisibilityEvaluator,
)
from CORE.atlas_portrait_flame_vertex_normal_evaluator import (
    AtlasPortraitFlameNormalField,
    AtlasPortraitFlameVertexNormalEvaluator,
)
from CORE.atlas_portrait_flame_weak_perspective_projection_evaluator import (
    AtlasPortraitFlameWeakPerspectiveProjection,
    AtlasPortraitFlameWeakPerspectiveProjectionEvaluator,
)
from CORE.atlas_portrait_weak_perspective_camera import (
    AtlasPortraitWeakPerspectiveCamera,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasPortraitFlameShadedPreviewPipelineResult:
    """
    Immutable aggregate result for the FLAME shaded-preview pipeline.

    The contract exposes every deterministic intermediate result:

    - deformed mesh
    - face and vertex normals
    - weak-perspective projection
    - projected-triangle visibility
    - depth-aware triangle rasterization
    - grayscale shaded preview

    It performs no fitting, parameter optimization, image writing,
    relief conversion, mesh export, or STL generation.
    """

    mesh: AtlasPortraitFlameDeformedMesh
    normal_field: AtlasPortraitFlameNormalField
    projection: AtlasPortraitFlameWeakPerspectiveProjection
    visibility: AtlasPortraitFlameTriangleVisibility
    rasterization: AtlasPortraitFlameTriangleRasterization
    preview: AtlasPortraitFlameShadedPreviewResult

    def __post_init__(
        self,
    ) -> None:
        expected_types = (
            (
                "mesh",
                self.mesh,
                AtlasPortraitFlameDeformedMesh,
            ),
            (
                "normal_field",
                self.normal_field,
                AtlasPortraitFlameNormalField,
            ),
            (
                "projection",
                self.projection,
                AtlasPortraitFlameWeakPerspectiveProjection,
            ),
            (
                "visibility",
                self.visibility,
                AtlasPortraitFlameTriangleVisibility,
            ),
            (
                "rasterization",
                self.rasterization,
                AtlasPortraitFlameTriangleRasterization,
            ),
            (
                "preview",
                self.preview,
                AtlasPortraitFlameShadedPreviewResult,
            ),
        )

        for (
            name,
            value,
            expected_type,
        ) in expected_types:
            if not isinstance(
                value,
                expected_type,
            ):
                raise TypeError(
                    f"{name} must be an "
                    f"{expected_type.__name__} instance."
                )

        if self.normal_field.vertex_count != self.mesh.vertex_count:
            raise ValueError(
                "normal_field vertex_count must match mesh "
                "vertex_count."
            )

        if self.normal_field.face_count != self.mesh.face_count:
            raise ValueError(
                "normal_field face_count must match mesh face_count."
            )

        if self.projection.vertex_count != self.mesh.vertex_count:
            raise ValueError(
                "projection vertex_count must match mesh "
                "vertex_count."
            )

        if self.projection.face_count != self.mesh.face_count:
            raise ValueError(
                "projection face_count must match mesh face_count."
            )

        if not np.array_equal(
            self.projection.triangle_faces,
            self.mesh.triangle_faces,
        ):
            raise ValueError(
                "projection triangle_faces must match mesh "
                "triangle_faces."
            )

        if self.visibility.triangle_count != self.mesh.face_count:
            raise ValueError(
                "visibility triangle_count must match mesh "
                "face_count."
            )

        if (
            self.rasterization.image_width
            != self.preview.image_width
            or self.rasterization.image_height
            != self.preview.image_height
        ):
            raise ValueError(
                "rasterization and preview image dimensions "
                "must match."
            )

        if not np.array_equal(
            self.rasterization.coverage_mask,
            self.preview.coverage_mask,
        ):
            raise ValueError(
                "rasterization and preview coverage_mask "
                "must match."
            )

    @property
    def vertex_count(
        self,
    ) -> int:
        return self.mesh.vertex_count

    @property
    def face_count(
        self,
    ) -> int:
        return self.mesh.face_count

    @property
    def visible_triangle_count(
        self,
    ) -> int:
        return self.visibility.visible_triangle_count

    @property
    def image_width(
        self,
    ) -> int:
        return self.rasterization.image_width

    @property
    def image_height(
        self,
    ) -> int:
        return self.rasterization.image_height

    @property
    def covered_pixel_count(
        self,
    ) -> int:
        return self.rasterization.covered_pixel_count

    @property
    def background_pixel_count(
        self,
    ) -> int:
        return self.rasterization.background_pixel_count

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "vertex_count": self.vertex_count,
            "face_count": self.face_count,
            "visible_triangle_count": (
                self.visible_triangle_count
            ),
            "image_width": self.image_width,
            "image_height": self.image_height,
            "covered_pixel_count": (
                self.covered_pixel_count
            ),
            "background_pixel_count": (
                self.background_pixel_count
            ),
            "mesh": self._to_plain_value(
                self.mesh.to_dict(),
            ),
            "normal_field": self._to_plain_value(
                self.normal_field.to_dict(),
            ),
            "projection": self._to_plain_value(
                self.projection.to_dict(),
            ),
            "visibility": self._to_plain_value(
                self.visibility.to_dict(),
            ),
            "rasterization": self._to_plain_value(
                self.rasterization.to_dict(),
            ),
            "preview": self._to_plain_value(
                self.preview.to_dict(),
            ),
        }

    @classmethod
    def _to_plain_value(
        cls,
        value: Any,
    ) -> Any:
        if isinstance(
            value,
            np.ndarray,
        ):
            return value.tolist()

        if isinstance(
            value,
            np.generic,
        ):
            return value.item()

        if isinstance(
            value,
            dict,
        ):
            return {
                key: cls._to_plain_value(
                    item,
                )
                for key, item in value.items()
            }

        if isinstance(
            value,
            tuple,
        ):
            return [
                cls._to_plain_value(
                    item,
                )
                for item in value
            ]

        if isinstance(
            value,
            list,
        ):
            return [
                cls._to_plain_value(
                    item,
                )
                for item in value
            ]

        return value


class AtlasPortraitFlameShadedPreviewPipeline:
    """
    Runs the complete deterministic FLAME shaded-preview chain.

    Processing sequence:

        canonical topology + skinned vertices
        -> deformed mesh
        -> face and vertex normals
        -> weak-perspective projection
        -> projected-triangle visibility
        -> depth-aware rasterization
        -> grayscale Lambertian preview

    The pipeline assumes that skinned FLAME vertices and a fitted or
    initialized weak-perspective camera already exist.

    It performs no FLAME parameter evaluation, skinning, fitting,
    optimization, image writing, relief generation, or STL export.
    """

    @classmethod
    def run(
        cls,
        model: AtlasPortraitFlameCanonicalModel,
        *,
        skinned_vertices: Any,
        camera: AtlasPortraitWeakPerspectiveCamera,
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
    ) -> AtlasPortraitFlameShadedPreviewPipelineResult:
        if not isinstance(
            model,
            AtlasPortraitFlameCanonicalModel,
        ):
            raise TypeError(
                "model must be an "
                "AtlasPortraitFlameCanonicalModel instance."
            )

        if not isinstance(
            camera,
            AtlasPortraitWeakPerspectiveCamera,
        ):
            raise TypeError(
                "camera must be an "
                "AtlasPortraitWeakPerspectiveCamera instance."
            )

        mesh = AtlasPortraitFlameDeformedMeshEvaluator.evaluate(
            model,
            skinned_vertices=skinned_vertices,
        )

        normal_field = (
            AtlasPortraitFlameVertexNormalEvaluator.evaluate(
                mesh,
            )
        )

        projection = (
            AtlasPortraitFlameWeakPerspectiveProjectionEvaluator
            .evaluate(
                mesh,
                camera=camera,
            )
        )

        visibility = (
            AtlasPortraitFlameTriangleVisibilityEvaluator
            .evaluate(
                mesh,
                projection=projection,
            )
        )

        rasterization = (
            AtlasPortraitFlameTriangleRasterizer.rasterize(
                projection,
                visibility=visibility,
                image_width=image_width,
                image_height=image_height,
            )
        )

        preview = (
            AtlasPortraitFlameShadedPreviewRenderer.render(
                rasterization,
                normal_field=normal_field,
                light_direction=light_direction,
                ambient_strength=ambient_strength,
                diffuse_strength=diffuse_strength,
                background_intensity=background_intensity,
            )
        )

        return AtlasPortraitFlameShadedPreviewPipelineResult(
            mesh=mesh,
            normal_field=normal_field,
            projection=projection,
            visibility=visibility,
            rasterization=rasterization,
            preview=preview,
        )
