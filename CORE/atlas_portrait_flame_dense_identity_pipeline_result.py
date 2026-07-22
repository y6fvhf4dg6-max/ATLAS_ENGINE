from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

import numpy as np

from CORE.atlas_portrait_flame_identity_fit_result import (
    AtlasPortraitFlameIdentityFitResult,
)
from CORE.atlas_portrait_flame_root_pose_fit_result import (
    AtlasPortraitFlameRootPoseFitResult,
)
from CORE.atlas_portrait_weak_perspective_camera import (
    AtlasPortraitWeakPerspectiveCamera,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasPortraitFlameDenseIdentityPipelineResult:
    """
    Immutable result of the staged FLAME dense-identity
    portrait fitting pipeline.

    Root-pose and dense-identity errors remain separate
    because the two fitting stages can use different
    landmark sets.
    """

    root_pose_result: AtlasPortraitFlameRootPoseFitResult
    identity_fit_result: AtlasPortraitFlameIdentityFitResult
    metadata: Mapping[str, Any]

    def __post_init__(
        self,
    ) -> None:
        root_pose_result = self._snapshot_root_pose_result(
            self.root_pose_result
        )
        identity_fit_result = (
            self._snapshot_identity_fit_result(
                self.identity_fit_result
            )
        )
        metadata = self._normalize_metadata(
            self.metadata
        )

        object.__setattr__(
            self,
            "root_pose_result",
            root_pose_result,
        )
        object.__setattr__(
            self,
            "identity_fit_result",
            identity_fit_result,
        )
        object.__setattr__(
            self,
            "metadata",
            metadata,
        )

    @property
    def final_root_pose_parameters(
        self,
    ) -> np.ndarray:
        result = (
            self.root_pose_result
            .root_pose_parameters
            .copy()
        )
        result.setflags(
            write=False
        )
        return result

    @property
    def final_identity_parameters(
        self,
    ) -> np.ndarray:
        result = (
            self.identity_fit_result
            .identity_parameters
            .copy()
        )
        result.setflags(
            write=False
        )
        return result

    @property
    def final_camera(
        self,
    ) -> AtlasPortraitWeakPerspectiveCamera:
        return self._snapshot_camera(
            self.identity_fit_result.camera
        )

    @property
    def root_pose_error_improvement(
        self,
    ) -> float:
        return float(
            self.root_pose_result.error_improvement
        )

    @property
    def root_pose_relative_error_improvement(
        self,
    ) -> float:
        return float(
            self.root_pose_result
            .relative_error_improvement
        )

    @property
    def identity_error_improvement(
        self,
    ) -> float:
        return float(
            self.identity_fit_result.error_improvement
        )

    @property
    def identity_relative_error_improvement(
        self,
    ) -> float:
        return float(
            self.identity_fit_result
            .relative_error_improvement
        )

    @property
    def total_function_evaluation_count(
        self,
    ) -> int:
        return int(
            self.root_pose_result
            .function_evaluation_count
            + self.identity_fit_result
            .function_evaluation_count
        )

    @property
    def optimizer_success(
        self,
    ) -> bool:
        return bool(
            self.root_pose_result.optimizer_success
            and self.identity_fit_result.optimizer_success
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "root_pose_result": (
                self.root_pose_result.to_dict()
            ),
            "identity_fit_result": (
                self.identity_fit_result.to_dict()
            ),
            "final_root_pose_parameters": (
                self.final_root_pose_parameters.tolist()
            ),
            "final_identity_parameters": (
                self.final_identity_parameters.tolist()
            ),
            "final_camera": (
                self.final_camera.to_dict()
            ),
            "root_pose_error_improvement": (
                self.root_pose_error_improvement
            ),
            "root_pose_relative_error_improvement": (
                self.root_pose_relative_error_improvement
            ),
            "identity_error_improvement": (
                self.identity_error_improvement
            ),
            "identity_relative_error_improvement": (
                self.identity_relative_error_improvement
            ),
            "total_function_evaluation_count": (
                self.total_function_evaluation_count
            ),
            "optimizer_success": self.optimizer_success,
            "metadata": {
                key: self._to_plain_value(
                    self.metadata[key]
                )
                for key in sorted(
                    self.metadata
                )
            },
        }

    @classmethod
    def _snapshot_root_pose_result(
        cls,
        value: Any,
    ) -> AtlasPortraitFlameRootPoseFitResult:
        if not isinstance(
            value,
            AtlasPortraitFlameRootPoseFitResult,
        ):
            raise TypeError(
                "root_pose_result must be an "
                "AtlasPortraitFlameRootPoseFitResult instance."
            )

        return AtlasPortraitFlameRootPoseFitResult(
            root_pose_parameters=(
                value.root_pose_parameters.copy()
            ),
            camera=cls._snapshot_camera(
                value.camera
            ),
            initial_weighted_root_mean_square_error=(
                value
                .initial_weighted_root_mean_square_error
            ),
            final_weighted_root_mean_square_error=(
                value
                .final_weighted_root_mean_square_error
            ),
            function_evaluation_count=(
                value.function_evaluation_count
            ),
            optimizer_success=value.optimizer_success,
            optimizer_status=value.optimizer_status,
            optimizer_message=value.optimizer_message,
            metadata=cls._to_plain_value(
                value.metadata
            ),
        )

    @classmethod
    def _snapshot_identity_fit_result(
        cls,
        value: Any,
    ) -> AtlasPortraitFlameIdentityFitResult:
        if not isinstance(
            value,
            AtlasPortraitFlameIdentityFitResult,
        ):
            raise TypeError(
                "identity_fit_result must be an "
                "AtlasPortraitFlameIdentityFitResult instance."
            )

        return AtlasPortraitFlameIdentityFitResult(
            identity_parameters=(
                value.identity_parameters.copy()
            ),
            camera=cls._snapshot_camera(
                value.camera
            ),
            initial_weighted_root_mean_square_error=(
                value
                .initial_weighted_root_mean_square_error
            ),
            final_weighted_root_mean_square_error=(
                value
                .final_weighted_root_mean_square_error
            ),
            regularization_weight=(
                value.regularization_weight
            ),
            function_evaluation_count=(
                value.function_evaluation_count
            ),
            optimizer_success=value.optimizer_success,
            optimizer_status=value.optimizer_status,
            optimizer_message=value.optimizer_message,
            metadata=cls._to_plain_value(
                value.metadata
            ),
        )

    @staticmethod
    def _snapshot_camera(
        value: Any,
    ) -> AtlasPortraitWeakPerspectiveCamera:
        if not isinstance(
            value,
            AtlasPortraitWeakPerspectiveCamera,
        ):
            raise TypeError(
                "camera must be an "
                "AtlasPortraitWeakPerspectiveCamera instance."
            )

        return AtlasPortraitWeakPerspectiveCamera(
            scale=value.scale,
            translation_x=value.translation_x,
            translation_y=value.translation_y,
            projected_points_2d=(
                value.projected_points_2d.copy()
            ),
            weighted_root_mean_square_error=(
                value.weighted_root_mean_square_error
            ),
            metadata=dict(
                value.metadata
            ),
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

            normalized[key] = cls._snapshot_plain_value(
                value[key]
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
                    key: cls._snapshot_plain_value(
                        item
                    )
                    for key, item in sorted(
                        value.items()
                    )
                }
            )

        if isinstance(
            value,
            list,
        ):
            return tuple(
                cls._snapshot_plain_value(
                    item
                )
                for item in value
            )

        if isinstance(
            value,
            tuple,
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
