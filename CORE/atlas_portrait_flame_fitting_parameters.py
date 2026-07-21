from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

import numpy as np


@dataclass(frozen=True)
class AtlasPortraitFlameFittingParameters:
    """
    Immutable provider-independent FLAME fitting parameters.

    The contract stores identity, expression, and pose
    parameter vectors together with deterministic metadata.

    It performs no camera solving, optimization, FLAME
    model loading, blendshape evaluation, mesh deformation,
    landmark projection, rendering, relief compression,
    or STL generation.
    """

    identity_parameters: np.ndarray
    expression_parameters: np.ndarray
    pose_parameters: np.ndarray
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        identity_parameters = self._normalize_parameter_vector(
            self.identity_parameters,
            name="identity_parameters",
        )

        expression_parameters = (
            self._normalize_parameter_vector(
                self.expression_parameters,
                name="expression_parameters",
            )
        )

        pose_parameters = self._normalize_parameter_vector(
            self.pose_parameters,
            name="pose_parameters",
        )

        metadata = self._normalize_metadata(
            self.metadata,
        )

        for vector in (
            identity_parameters,
            expression_parameters,
            pose_parameters,
        ):
            vector.setflags(
                write=False,
            )

        object.__setattr__(
            self,
            "identity_parameters",
            identity_parameters,
        )
        object.__setattr__(
            self,
            "expression_parameters",
            expression_parameters,
        )
        object.__setattr__(
            self,
            "pose_parameters",
            pose_parameters,
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
            self.identity_parameters.shape[0],
        )

    @property
    def expression_parameter_count(
        self,
    ) -> int:
        return int(
            self.expression_parameters.shape[0],
        )

    @property
    def pose_parameter_count(
        self,
    ) -> int:
        return int(
            self.pose_parameters.shape[0],
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "identity_parameter_count": (
                self.identity_parameter_count
            ),
            "expression_parameter_count": (
                self.expression_parameter_count
            ),
            "pose_parameter_count": (
                self.pose_parameter_count
            ),
            "identity_parameters": (
                self.identity_parameters.tolist()
            ),
            "expression_parameters": (
                self.expression_parameters.tolist()
            ),
            "pose_parameters": (
                self.pose_parameters.tolist()
            ),
            "metadata": {
                key: self.metadata[key]
                for key in sorted(
                    self.metadata,
                )
            },
        }

    @staticmethod
    def _normalize_parameter_vector(
        value: Any,
        *,
        name: str,
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
                f"{name} must be numeric."
            ) from exc

        if parameters.ndim != 1:
            raise ValueError(
                f"{name} must be one-dimensional."
            )

        if parameters.size < 1:
            raise ValueError(
                f"{name} must not be empty."
            )

        if not np.isfinite(
            parameters,
        ).all():
            raise ValueError(
                f"{name} contains non-finite values."
            )

        return parameters.astype(
            np.float64,
            copy=True,
        )

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
                key,
            ): item
            for key, item in value.items()
        }

        return MappingProxyType(
            {
                key: copied[key]
                for key in sorted(
                    copied,
                )
            }
        )
