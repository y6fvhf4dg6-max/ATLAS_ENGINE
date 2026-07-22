from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

import numpy as np

from CORE.atlas_portrait_weak_perspective_camera import (
    AtlasPortraitWeakPerspectiveCamera,
)


@dataclass(frozen=True)
class AtlasPortraitFlameRootPoseFitResult:
    """
    Immutable result of FLAME root-pose fitting.

    The contract stores the fitted three-component root
    axis-angle vector, the resulting weak-perspective
    camera, initial and final weighted reprojection errors,
    optimizer diagnostics, and deterministic metadata.

    It performs no optimization, FLAME deformation,
    landmark evaluation, projection, rendering, relief
    compression, or STL generation.
    """

    root_pose_parameters: np.ndarray
    camera: AtlasPortraitWeakPerspectiveCamera
    initial_weighted_root_mean_square_error: float
    final_weighted_root_mean_square_error: float
    function_evaluation_count: int
    optimizer_success: bool
    optimizer_status: int
    optimizer_message: str
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        root_pose_parameters = (
            self._normalize_root_pose_parameters(
                self.root_pose_parameters
            )
        )

        if not isinstance(
            self.camera,
            AtlasPortraitWeakPerspectiveCamera,
        ):
            raise TypeError(
                "camera must be an "
                "AtlasPortraitWeakPerspectiveCamera instance."
            )

        initial_error = self._normalize_non_negative_float(
            self.initial_weighted_root_mean_square_error,
            name=(
                "initial_weighted_root_mean_square_error"
            ),
        )

        final_error = self._normalize_non_negative_float(
            self.final_weighted_root_mean_square_error,
            name=(
                "final_weighted_root_mean_square_error"
            ),
        )

        if final_error > initial_error:
            raise ValueError(
                "final_weighted_root_mean_square_error "
                "must not exceed "
                "initial_weighted_root_mean_square_error."
            )

        function_evaluation_count = (
            self._normalize_positive_integer(
                self.function_evaluation_count,
                name="function_evaluation_count",
            )
        )

        optimizer_success = self._normalize_boolean(
            self.optimizer_success,
            name="optimizer_success",
        )

        optimizer_status = self._normalize_integer(
            self.optimizer_status,
            name="optimizer_status",
        )

        optimizer_message = self._normalize_message(
            self.optimizer_message
        )

        metadata = self._normalize_metadata(
            self.metadata
        )

        root_pose_parameters.setflags(
            write=False
        )

        object.__setattr__(
            self,
            "root_pose_parameters",
            root_pose_parameters,
        )
        object.__setattr__(
            self,
            "initial_weighted_root_mean_square_error",
            initial_error,
        )
        object.__setattr__(
            self,
            "final_weighted_root_mean_square_error",
            final_error,
        )
        object.__setattr__(
            self,
            "function_evaluation_count",
            function_evaluation_count,
        )
        object.__setattr__(
            self,
            "optimizer_success",
            optimizer_success,
        )
        object.__setattr__(
            self,
            "optimizer_status",
            optimizer_status,
        )
        object.__setattr__(
            self,
            "optimizer_message",
            optimizer_message,
        )
        object.__setattr__(
            self,
            "metadata",
            metadata,
        )

    @property
    def root_pose_parameter_count(
        self,
    ) -> int:
        return int(
            self.root_pose_parameters.shape[0]
        )

    @property
    def error_improvement(
        self,
    ) -> float:
        return (
            self.initial_weighted_root_mean_square_error
            - self.final_weighted_root_mean_square_error
        )

    @property
    def relative_error_improvement(
        self,
    ) -> float:
        initial_error = (
            self.initial_weighted_root_mean_square_error
        )

        if initial_error == 0.0:
            return 0.0

        return (
            self.error_improvement
            / initial_error
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "root_pose_parameter_count": (
                self.root_pose_parameter_count
            ),
            "root_pose_parameters": (
                self.root_pose_parameters.tolist()
            ),
            "camera": self.camera.to_dict(),
            "initial_weighted_root_mean_square_error": (
                self.initial_weighted_root_mean_square_error
            ),
            "final_weighted_root_mean_square_error": (
                self.final_weighted_root_mean_square_error
            ),
            "error_improvement": self.error_improvement,
            "relative_error_improvement": (
                self.relative_error_improvement
            ),
            "function_evaluation_count": (
                self.function_evaluation_count
            ),
            "optimizer_success": self.optimizer_success,
            "optimizer_status": self.optimizer_status,
            "optimizer_message": self.optimizer_message,
            "metadata": {
                key: self.metadata[key]
                for key in sorted(
                    self.metadata
                )
            },
        }

    @staticmethod
    def _normalize_root_pose_parameters(
        value: Any,
    ) -> np.ndarray:
        try:
            parameters = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "root_pose_parameters must be numeric."
            ) from exc

        if parameters.shape != (
            3,
        ):
            raise ValueError(
                "root_pose_parameters must have shape (3,)."
            )

        if not np.isfinite(
            parameters
        ).all():
            raise ValueError(
                "root_pose_parameters contains non-finite "
                "values."
            )

        return parameters.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _normalize_non_negative_float(
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

        if normalized < 0.0:
            raise ValueError(
                f"{name} must not be negative."
            )

        return normalized

    @staticmethod
    def _normalize_positive_integer(
        value: Any,
        *,
        name: str,
    ) -> int:
        normalized = (
            AtlasPortraitFlameRootPoseFitResult
            ._normalize_integer(
                value,
                name=name,
            )
        )

        if normalized <= 0:
            raise ValueError(
                f"{name} must be greater than zero."
            )

        return normalized

    @staticmethod
    def _normalize_integer(
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
            raise ValueError(
                f"{name} must be an integer."
            )

        try:
            numeric_value = float(
                value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be an integer."
            ) from exc

        if (
            not math.isfinite(
                numeric_value
            )
            or not numeric_value.is_integer()
        ):
            raise ValueError(
                f"{name} must be an integer."
            )

        return int(
            numeric_value
        )

    @staticmethod
    def _normalize_boolean(
        value: Any,
        *,
        name: str,
    ) -> bool:
        if not isinstance(
            value,
            (
                bool,
                np.bool_,
            ),
        ):
            raise TypeError(
                f"{name} must be a boolean."
            )

        return bool(
            value
        )

    @staticmethod
    def _normalize_message(
        value: Any,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "optimizer_message must be a string."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "optimizer_message must not be blank."
            )

        return normalized

    @staticmethod
    def _normalize_metadata(
        value: Any,
    ) -> Mapping[str, Any]:
        if not isinstance(
            value,
            Mapping,
        ):
            raise TypeError(
                "metadata must be a mapping."
            )

        copied = {
            str(
                key
            ): item
            for key, item in value.items()
        }

        return MappingProxyType(
            {
                key: copied[key]
                for key in sorted(
                    copied
                )
            }
        )
