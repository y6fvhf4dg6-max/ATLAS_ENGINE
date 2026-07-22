from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

import numpy as np

from CORE.atlas_portrait_flame_deformed_mesh_evaluator import (
    AtlasPortraitFlameDeformedMesh,
)
from CORE.atlas_portrait_flame_dense_identity_pipeline_result import (
    AtlasPortraitFlameDenseIdentityPipelineResult,
)
from CORE.atlas_portrait_flame_shaded_preview_pipeline import (
    AtlasPortraitFlameShadedPreviewPipelineResult,
)
from CORE.atlas_portrait_weak_perspective_camera import (
    AtlasPortraitWeakPerspectiveCamera,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasPortraitFlameFittedShadedPreviewPipelineResult:
    """
    Immutable aggregate result for a fitted FLAME shaded
    portrait preview.

    The contract combines:

    - staged dense-identity fitting result
    - fitted image-coordinate FLAME mesh
    - pixel-coordinate weak-perspective camera
    - complete shaded-preview pipeline result
    - deterministic metadata

    The fitted mesh must be exactly the mesh consumed by
    the shaded-preview pipeline. This prevents accidental
    reuse of canonical triangle winding after conversion to
    image coordinates.

    It performs no fitting, mesh deformation, camera
    conversion, projection, rasterization, rendering, image
    writing, relief generation, or STL export.
    """

    fitting_result: AtlasPortraitFlameDenseIdentityPipelineResult
    fitted_mesh: AtlasPortraitFlameDeformedMesh
    pixel_camera: AtlasPortraitWeakPerspectiveCamera
    shaded_preview_result: (
        AtlasPortraitFlameShadedPreviewPipelineResult
    )
    metadata: Mapping[str, Any]

    def __post_init__(
        self,
    ) -> None:
        self._validate_type(
            self.fitting_result,
            name="fitting_result",
            expected_type=(
                AtlasPortraitFlameDenseIdentityPipelineResult
            ),
        )
        self._validate_type(
            self.fitted_mesh,
            name="fitted_mesh",
            expected_type=AtlasPortraitFlameDeformedMesh,
        )
        self._validate_type(
            self.pixel_camera,
            name="pixel_camera",
            expected_type=AtlasPortraitWeakPerspectiveCamera,
        )
        self._validate_type(
            self.shaded_preview_result,
            name="shaded_preview_result",
            expected_type=(
                AtlasPortraitFlameShadedPreviewPipelineResult
            ),
        )

        coordinate_space = self.pixel_camera.metadata.get(
            "coordinate_space"
        )

        if coordinate_space != "pixel":
            raise ValueError(
                "pixel_camera metadata coordinate_space "
                "must be 'pixel'."
            )

        preview_mesh = self.shaded_preview_result.mesh

        if not np.array_equal(
            self.fitted_mesh.vertices,
            preview_mesh.vertices,
        ):
            raise ValueError(
                "fitted_mesh vertices must match the "
                "shaded-preview mesh vertices."
            )

        if not np.array_equal(
            self.fitted_mesh.triangle_faces,
            preview_mesh.triangle_faces,
        ):
            raise ValueError(
                "fitted_mesh triangle_faces must match the "
                "shaded-preview mesh triangle_faces."
            )

        metadata = self._normalize_metadata(
            self.metadata
        )

        object.__setattr__(
            self,
            "metadata",
            metadata,
        )

    @property
    def vertex_count(
        self,
    ) -> int:
        return self.fitted_mesh.vertex_count

    @property
    def face_count(
        self,
    ) -> int:
        return self.fitted_mesh.face_count

    @property
    def visible_triangle_count(
        self,
    ) -> int:
        return (
            self.shaded_preview_result
            .visible_triangle_count
        )

    @property
    def image_width(
        self,
    ) -> int:
        return self.shaded_preview_result.image_width

    @property
    def image_height(
        self,
    ) -> int:
        return self.shaded_preview_result.image_height

    @property
    def covered_pixel_count(
        self,
    ) -> int:
        return (
            self.shaded_preview_result
            .covered_pixel_count
        )

    @property
    def background_pixel_count(
        self,
    ) -> int:
        return (
            self.shaded_preview_result
            .background_pixel_count
        )

    @property
    def optimizer_success(
        self,
    ) -> bool:
        return bool(
            self.fitting_result.optimizer_success
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "background_pixel_count": (
                self.background_pixel_count
            ),
            "covered_pixel_count": (
                self.covered_pixel_count
            ),
            "face_count": self.face_count,
            "fitted_mesh": self._to_plain_value(
                self.fitted_mesh.to_dict()
            ),
            "fitting_result": self._to_plain_value(
                self.fitting_result.to_dict()
            ),
            "image_height": self.image_height,
            "image_width": self.image_width,
            "metadata": self._to_plain_value(
                self.metadata
            ),
            "optimizer_success": self.optimizer_success,
            "pixel_camera": self._to_plain_value(
                self.pixel_camera.to_dict()
            ),
            "shaded_preview_result": (
                self._to_plain_value(
                    self.shaded_preview_result.to_dict()
                )
            ),
            "vertex_count": self.vertex_count,
            "visible_triangle_count": (
                self.visible_triangle_count
            ),
        }

    @staticmethod
    def _validate_type(
        value: Any,
        *,
        name: str,
        expected_type: type,
    ) -> None:
        if not isinstance(
            value,
            expected_type,
        ):
            raise TypeError(
                f"{name} must be an "
                f"{expected_type.__name__} instance."
            )

    @classmethod
    def _normalize_metadata(
        cls,
        value: Any,
    ) -> Mapping[str, Any]:
        if not isinstance(
            value,
            Mapping,
        ):
            raise TypeError(
                "metadata must be a mapping."
            )

        normalized: dict[str, Any] = {}

        for key in sorted(
            value
        ):
            if not isinstance(
                key,
                str,
            ):
                raise TypeError(
                    "metadata keys must be strings."
                )

            normalized[
                key
            ] = cls._snapshot_plain_value(
                value[
                    key
                ]
            )

        return MappingProxyType(
            normalized
        )

    @classmethod
    def _snapshot_plain_value(
        cls,
        value: Any,
    ) -> Any:
        if isinstance(
            value,
            np.ndarray,
        ):
            copied = value.copy()
            copied.setflags(
                write=False
            )
            return copied

        if isinstance(
            value,
            np.generic,
        ):
            return value.item()

        if isinstance(
            value,
            Mapping,
        ):
            return MappingProxyType(
                {
                    str(
                        key
                    ): cls._snapshot_plain_value(
                        item
                    )
                    for key, item in sorted(
                        value.items(),
                        key=lambda pair: str(
                            pair[
                                0
                            ]
                        ),
                    )
                }
            )

        if isinstance(
            value,
            (
                tuple,
                list,
            ),
        ):
            return tuple(
                cls._snapshot_plain_value(
                    item
                )
                for item in value
            )

        return value

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
            Mapping,
        ):
            return {
                key: cls._to_plain_value(
                    item
                )
                for key, item in sorted(
                    value.items()
                )
            }

        if isinstance(
            value,
            (
                tuple,
                list,
            ),
        ):
            return [
                cls._to_plain_value(
                    item
                )
                for item in value
            ]

        return value
