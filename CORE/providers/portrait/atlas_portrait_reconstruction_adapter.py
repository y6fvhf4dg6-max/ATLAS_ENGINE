from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

from CORE.atlas_parametric_face_geometry import (
    AtlasParametricFaceGeometry,
)


class AtlasPortraitReconstructionAdapter(ABC):
    """
    Abstract provider-specific reconstruction adapter.

    Implementations convert provider payloads into the
    provider-independent AtlasParametricFaceGeometry
    contract.

    The base class validates adapter identity, supported
    input views, and canonical output provenance. It
    performs no reconstruction inference, model loading,
    fitting, projection, relief compression, rendering,
    or STL generation.
    """

    ADAPTER_ID: str | None = None
    PROVIDER_ID: str | None = None
    MODEL_FAMILY: str | None = None
    MODEL_VERSION: str | None = None

    SUPPORTED_INPUT_VIEWS: tuple[str, ...] = (
        "single_image",
    )

    __slots__ = (
        "_adapter_id",
        "_provider_id",
        "_model_family",
        "_model_version",
        "_supported_input_views",
    )

    def __init__(self) -> None:
        object.__setattr__(
            self,
            "_adapter_id",
            self._normalize_identity(
                self.ADAPTER_ID,
                name="ADAPTER_ID",
            ),
        )

        object.__setattr__(
            self,
            "_provider_id",
            self._normalize_identity(
                self.PROVIDER_ID,
                name="PROVIDER_ID",
            ),
        )

        object.__setattr__(
            self,
            "_model_family",
            self._normalize_identity(
                self.MODEL_FAMILY,
                name="MODEL_FAMILY",
            ),
        )

        object.__setattr__(
            self,
            "_model_version",
            self._normalize_identity(
                self.MODEL_VERSION,
                name="MODEL_VERSION",
            ),
        )

        object.__setattr__(
            self,
            "_supported_input_views",
            self._normalize_supported_input_views(
                self.SUPPORTED_INPUT_VIEWS,
            ),
        )

    @property
    def adapter_id(
        self,
    ) -> str:
        return self._adapter_id

    @property
    def provider_id(
        self,
    ) -> str:
        return self._provider_id

    @property
    def model_family(
        self,
    ) -> str:
        return self._model_family

    @property
    def model_version(
        self,
    ) -> str:
        return self._model_version

    @property
    def supported_input_views(
        self,
    ) -> tuple[str, ...]:
        return self._supported_input_views

    @abstractmethod
    def adapt(
        self,
        provider_payload: Any,
        *,
        input_view: str = "single_image",
    ) -> AtlasParametricFaceGeometry:
        """
        Converts provider-specific output into canonical
        ATLAS face geometry.
        """

        raise NotImplementedError

    def validate_input_view(
        self,
        input_view: Any,
    ) -> str:
        if not isinstance(
            input_view,
            str,
        ):
            raise ValueError(
                "input_view must be a supported string."
            )

        normalized = input_view.strip()

        if (
            not normalized
            or normalized
            not in self.supported_input_views
        ):
            raise ValueError(
                "input_view must be one of: "
                + ", ".join(
                    self.supported_input_views,
                )
                + "."
            )

        return normalized

    def validate_geometry(
        self,
        geometry: Any,
    ) -> AtlasParametricFaceGeometry:
        if not isinstance(
            geometry,
            AtlasParametricFaceGeometry,
        ):
            raise TypeError(
                "Adapter output must be an "
                "AtlasParametricFaceGeometry."
            )

        expected_metadata = {
            "adapter_id": self.adapter_id,
            "provider_id": self.provider_id,
            "model_family": self.model_family,
            "model_version": self.model_version,
        }

        for key, expected_value in expected_metadata.items():
            if key not in geometry.metadata:
                raise ValueError(
                    f"Geometry metadata is missing {key}."
                )

            actual_value = geometry.metadata[
                key
            ]

            if actual_value != expected_value:
                raise ValueError(
                    f"Geometry metadata {key} does not "
                    "match the adapter identity."
                )

        return geometry

    @staticmethod
    def _normalize_identity(
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

    @classmethod
    def _normalize_supported_input_views(
        cls,
        value: Any,
    ) -> tuple[str, ...]:
        if (
            value is None
            or isinstance(
                value,
                (
                    str,
                    bytes,
                ),
            )
        ):
            raise ValueError(
                "SUPPORTED_INPUT_VIEWS must be a "
                "non-empty sequence of strings."
            )

        try:
            raw_views = tuple(
                value,
            )
        except TypeError as exc:
            raise ValueError(
                "SUPPORTED_INPUT_VIEWS must be a "
                "non-empty sequence of strings."
            ) from exc

        if not raw_views:
            raise ValueError(
                "SUPPORTED_INPUT_VIEWS must not be empty."
            )

        normalized_views: list[str] = []

        for raw_view in raw_views:
            if not isinstance(
                raw_view,
                str,
            ):
                raise ValueError(
                    "SUPPORTED_INPUT_VIEWS must contain "
                    "only non-empty strings."
                )

            normalized_view = raw_view.strip()

            if not normalized_view:
                raise ValueError(
                    "SUPPORTED_INPUT_VIEWS must contain "
                    "only non-empty strings."
                )

            normalized_views.append(
                normalized_view,
            )

        return tuple(
            sorted(
                set(
                    normalized_views,
                )
            )
        )
