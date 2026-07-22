from __future__ import annotations

from dataclasses import dataclass
import math
from numbers import Integral, Real
from types import MappingProxyType
from typing import Any, Mapping

import numpy as np

from CORE.atlas_portrait_weak_perspective_camera import (
    AtlasPortraitWeakPerspectiveCamera,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasPortraitFlameIdentityFitResult:
    """
    Immutable result of dense FLAME identity fitting.

    The contract stores:

    - fitted identity parameters,
    - the final weak-perspective camera,
    - initial and final landmark errors,
    - regularization and optimizer diagnostics,
    - deterministic metadata.

    It performs no fitting, optimization, mesh evaluation,
    rendering, persistence, or preview generation.
    """

    identity_parameters: np.ndarray
    camera: AtlasPortraitWeakPerspectiveCamera
    initial_weighted_root_mean_square_error: float
    final_weighted_root_mean_square_error: float
    regularization_weight: float
    function_evaluation_count: int
    optimizer_success: bool
    optimizer_status: int
    optimizer_message: str
    metadata: Mapping[str, Any]

    def __post_init__(
        self,
    ) -> None:
        identity_parameters = self._normalize_identity_parameters(
            self.identity_parameters
        )

        camera = self._snapshot_camera(
            self.camera
        )

        initial_error = self._normalize_nonnegative_float(
            self.initial_weighted_root_mean_square_error,
            name=(
                "initial_weighted_root_mean_square_error"
            ),
        )

        final_error = self._normalize_nonnegative_float(
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

        regularization_weight = (
            self._normalize_nonnegative_float(
                self.regularization_weight,
                name="regularization_weight",
            )
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

        object.__setattr__(
            self,
            "identity_parameters",
            identity_parameters,
        )
        object.__setattr__(
            self,
            "camera",
            camera,
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
            "regularization_weight",
            regularization_weight,
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
    def identity_parameter_count(
        self,
    ) -> int:
        return int(
            self.identity_parameters.shape[0]
        )

    @property
    def identity_parameter_l2_norm(
        self,
    ) -> float:
        return float(
            np.linalg.norm(
                self.identity_parameters
            )
        )

    @property
    def maximum_absolute_identity_parameter(
        self,
    ) -> float:
        return float(
            np.max(
                np.abs(
                    self.identity_parameters
                )
            )
        )

    @property
    def error_improvement(
        self,
    ) -> float:
        return float(
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

        return float(
            self.error_improvement
            / initial_error
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "identity_parameter_count": (
                self.identity_parameter_count
            ),
            "identity_parameters": (
                self.identity_parameters.tolist()
            ),
            "identity_parameter_l2_norm": (
                self.identity_parameter_l2_norm
            ),
            "maximum_absolute_identity_parameter": (
                self.maximum_absolute_identity_parameter
            ),
            "camera": self._to_plain_value(
                self.camera.to_dict()
            ),
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
            "regularization_weight": (
                self.regularization_weight
            ),
            "function_evaluation_count": (
                self.function_evaluation_count
            ),
            "optimizer_success": self.optimizer_success,
            "optimizer_status": self.optimizer_status,
            "optimizer_message": self.optimizer_message,
            "metadata": {
                key: self._to_plain_value(
                    self.metadata[key]
                )
                for key in sorted(
                    self.metadata
                )
            },
        }

    @staticmethod
    def _normalize_identity_parameters(
        value: Any,
    ) -> np.ndarray:
        try:
            parameters = np.asarray(
                value,
                dtype=np.float64,
            ).copy()
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "identity_parameters must be numeric."
            ) from exc

        if (
            parameters.ndim != 1
            or parameters.shape[0] == 0
        ):
            raise ValueError(
                "identity_parameters must have shape "
                "(N,) with N greater than zero."
            )

        if not np.isfinite(
            parameters
        ).all():
            raise ValueError(
                "identity_parameters must contain "
                "only finite values."
            )

        parameters.setflags(
            write=False
        )

        return parameters

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

    @staticmethod
    def _normalize_nonnegative_float(
        value: Any,
        *,
        name: str,
    ) -> float:
        if isinstance(
            value,
            (
                bool,
                np.bool_,
            ),
        ):
            raise ValueError(
                f"{name} must be a finite "
                "nonnegative number."
            )

        if not isinstance(
            value,
            Real,
        ):
            raise ValueError(
                f"{name} must be a finite "
                "nonnegative number."
            )

        normalized = float(
            value
        )

        if (
            not math.isfinite(
                normalized
            )
            or normalized < 0.0
        ):
            raise ValueError(
                f"{name} must be a finite "
                "nonnegative number."
            )

        return normalized

    @staticmethod
    def _normalize_positive_integer(
        value: Any,
        *,
        name: str,
    ) -> int:
        normalized = (
            AtlasPortraitFlameIdentityFitResult
            ._normalize_integer(
                value,
                name=name,
            )
        )

        if normalized <= 0:
            raise ValueError(
                f"{name} must be a positive integer."
            )

        return normalized

    @staticmethod
    def _normalize_integer(
        value: Any,
        *,
        name: str,
    ) -> int:
        if (
            isinstance(
                value,
                (
                    bool,
                    np.bool_,
                ),
            )
            or not isinstance(
                value,
                Integral,
            )
        ):
            raise ValueError(
                f"{name} must be an integer."
            )

        return int(
            value
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
            raise ValueError(
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
            raise ValueError(
                "optimizer_message must be a "
                "nonempty string."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "optimizer_message must be a "
                "nonempty string."
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

            normalized[key] = (
                AtlasPortraitFlameIdentityFitResult
                ._snapshot_plain_value(
                    value[key]
                )
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
            array = value.copy()
            array.setflags(
                write=False
            )
            return array

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
            tuple,
        ):
            return [
                cls._to_plain_value(
                    item
                )
                for item in value
            ]

        if isinstance(
            value,
            list,
        ):
            return [
                cls._to_plain_value(
                    item
                )
                for item in value
            ]

        return value
