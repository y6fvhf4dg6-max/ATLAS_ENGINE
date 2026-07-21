from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any


@dataclass(frozen=True)
class AtlasPortraitFlameModelParameterSpecification:
    """
    Immutable FLAME model parameter-dimension contract.

    The specification stores model identity and the
    expected identity, expression, and pose parameter
    counts together with deterministic metadata.

    It performs no FLAME model loading, parameter
    initialization, fitting, optimization, blendshape
    evaluation, mesh deformation, projection, rendering,
    relief compression, or STL generation.
    """

    model_family: str
    model_version: str

    identity_parameter_count: int
    expression_parameter_count: int
    pose_parameter_count: int

    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        model_family = self._normalize_required_text(
            self.model_family,
            name="model_family",
        )

        model_version = self._normalize_required_text(
            self.model_version,
            name="model_version",
        )

        identity_parameter_count = (
            self._normalize_positive_integer(
                self.identity_parameter_count,
                name="identity_parameter_count",
            )
        )

        expression_parameter_count = (
            self._normalize_positive_integer(
                self.expression_parameter_count,
                name="expression_parameter_count",
            )
        )

        pose_parameter_count = (
            self._normalize_positive_integer(
                self.pose_parameter_count,
                name="pose_parameter_count",
            )
        )

        metadata = self._normalize_metadata(
            self.metadata,
        )

        object.__setattr__(
            self,
            "model_family",
            model_family,
        )
        object.__setattr__(
            self,
            "model_version",
            model_version,
        )
        object.__setattr__(
            self,
            "identity_parameter_count",
            identity_parameter_count,
        )
        object.__setattr__(
            self,
            "expression_parameter_count",
            expression_parameter_count,
        )
        object.__setattr__(
            self,
            "pose_parameter_count",
            pose_parameter_count,
        )
        object.__setattr__(
            self,
            "metadata",
            metadata,
        )

    @property
    def total_parameter_count(
        self,
    ) -> int:
        return (
            self.identity_parameter_count
            + self.expression_parameter_count
            + self.pose_parameter_count
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "model_family": self.model_family,
            "model_version": self.model_version,
            "identity_parameter_count": (
                self.identity_parameter_count
            ),
            "expression_parameter_count": (
                self.expression_parameter_count
            ),
            "pose_parameter_count": (
                self.pose_parameter_count
            ),
            "total_parameter_count": (
                self.total_parameter_count
            ),
            "metadata": {
                key: self.metadata[key]
                for key in sorted(
                    self.metadata,
                )
            },
        }

    @staticmethod
    def _normalize_required_text(
        value: Any,
        *,
        name: str,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                f"{name} must be a non-empty string."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{name} must be a non-empty string."
            )

        return normalized

    @staticmethod
    def _normalize_positive_integer(
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

        if value <= 0:
            raise ValueError(
                f"{name} must be greater than zero."
            )

        return value

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
