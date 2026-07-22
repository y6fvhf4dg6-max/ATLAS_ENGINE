from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np

from CORE.atlas_portrait_weak_perspective_camera import (
    AtlasPortraitWeakPerspectiveCamera,
)
from CORE.providers.portrait.atlas_portrait_flame_dynamic_landmark_evaluator import (
    AtlasPortraitFlameDynamicLandmarkEvaluation,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasPortraitFlameDynamicLandmarkPixelProjection:
    """
    Immutable pixel-coordinate projection of dynamic FLAME landmarks.
    """

    requested_yaw_degrees: float
    selected_yaw_degrees: float
    yaw_bin_index: int
    scale: float
    translation_x: float
    translation_y: float
    projected_points_2d: np.ndarray

    def __post_init__(
        self,
    ) -> None:
        requested_yaw = self._normalize_finite_float(
            self.requested_yaw_degrees,
            name="requested_yaw_degrees",
        )
        selected_yaw = self._normalize_finite_float(
            self.selected_yaw_degrees,
            name="selected_yaw_degrees",
        )
        scale = self._normalize_finite_float(
            self.scale,
            name="scale",
        )
        translation_x = self._normalize_finite_float(
            self.translation_x,
            name="translation_x",
        )
        translation_y = self._normalize_finite_float(
            self.translation_y,
            name="translation_y",
        )

        if scale <= 0.0:
            raise ValueError(
                "scale must be greater than zero."
            )

        yaw_bin_index = int(
            self.yaw_bin_index
        )

        if not 0 <= yaw_bin_index < 79:
            raise ValueError(
                "yaw_bin_index must be in the range 0..78."
            )

        projected_points = np.asarray(
            self.projected_points_2d,
            dtype=np.float64,
        ).copy()

        if (
            projected_points.ndim != 2
            or projected_points.shape[0] == 0
            or projected_points.shape[1] != 2
        ):
            raise ValueError(
                "projected_points_2d must have shape "
                "(L, 2) with L > 0."
            )

        if not np.isfinite(
            projected_points
        ).all():
            raise ValueError(
                "projected_points_2d contains non-finite values."
            )

        projected_points.setflags(
            write=False
        )

        object.__setattr__(
            self,
            "requested_yaw_degrees",
            requested_yaw,
        )
        object.__setattr__(
            self,
            "selected_yaw_degrees",
            selected_yaw,
        )
        object.__setattr__(
            self,
            "yaw_bin_index",
            yaw_bin_index,
        )
        object.__setattr__(
            self,
            "scale",
            scale,
        )
        object.__setattr__(
            self,
            "translation_x",
            translation_x,
        )
        object.__setattr__(
            self,
            "translation_y",
            translation_y,
        )
        object.__setattr__(
            self,
            "projected_points_2d",
            projected_points,
        )

    @property
    def landmark_count(
        self,
    ) -> int:
        return int(
            self.projected_points_2d.shape[0]
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "requested_yaw_degrees": (
                self.requested_yaw_degrees
            ),
            "selected_yaw_degrees": (
                self.selected_yaw_degrees
            ),
            "yaw_bin_index": self.yaw_bin_index,
            "scale": self.scale,
            "translation_x": self.translation_x,
            "translation_y": self.translation_y,
            "landmark_count": self.landmark_count,
            "projected_points_2d": (
                self.projected_points_2d.tolist()
            ),
        }

    @staticmethod
    def _normalize_finite_float(
        value: Any,
        *,
        name: str,
    ) -> float:
        try:
            normalized = float(
                value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if not math.isfinite(
            normalized
        ):
            raise ValueError(
                f"{name} must be finite."
            )

        return normalized


class AtlasPortraitFlameDynamicLandmarkPixelProjector:
    """
    Projects evaluated FLAME dynamic landmarks into pixel space.

    Projection model:

        u = scale * x + translation_x
        v = scale * y + translation_y

    Landmark depth is ignored.

    This class performs no yaw selection, mesh deformation,
    barycentric evaluation, fitting, correspondence matching,
    rendering, image writing, relief generation, or STL export.
    """

    @classmethod
    def project(
        cls,
        evaluation: AtlasPortraitFlameDynamicLandmarkEvaluation,
        *,
        camera: AtlasPortraitWeakPerspectiveCamera,
    ) -> AtlasPortraitFlameDynamicLandmarkPixelProjection:
        if not isinstance(
            evaluation,
            AtlasPortraitFlameDynamicLandmarkEvaluation,
        ):
            raise TypeError(
                "evaluation must be an "
                "AtlasPortraitFlameDynamicLandmarkEvaluation "
                "instance."
            )

        if not isinstance(
            camera,
            AtlasPortraitWeakPerspectiveCamera,
        ):
            raise TypeError(
                "camera must be an "
                "AtlasPortraitWeakPerspectiveCamera instance."
            )

        coordinate_space = camera.metadata.get(
            "coordinate_space"
        )

        if coordinate_space != "pixel":
            raise ValueError(
                "camera metadata coordinate_space "
                "must be 'pixel'."
            )

        projected_points = np.asarray(
            (
                camera.scale
                * evaluation.landmark_points[
                    :,
                    :2,
                ]
            )
            + np.array(
                [
                    camera.translation_x,
                    camera.translation_y,
                ],
                dtype=np.float64,
            ),
            dtype=np.float64,
        ).copy()

        return AtlasPortraitFlameDynamicLandmarkPixelProjection(
            requested_yaw_degrees=(
                evaluation.requested_yaw_degrees
            ),
            selected_yaw_degrees=(
                evaluation.selected_yaw_degrees
            ),
            yaw_bin_index=evaluation.yaw_bin_index,
            scale=camera.scale,
            translation_x=camera.translation_x,
            translation_y=camera.translation_y,
            projected_points_2d=projected_points,
        )
