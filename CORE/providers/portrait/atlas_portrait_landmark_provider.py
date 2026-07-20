from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from CORE.atlas_portrait_landmark_result import (
    AtlasPortraitLandmarkResult,
)


class AtlasPortraitLandmarkProvider(ABC):
    """
    Base interface for portrait landmark providers.

    Concrete providers may use MediaPipe, another
    local model, a remote service, or a deterministic
    fixture implementation.

    The provider interface does not own portrait input
    loading or model-specific inference details.
    """

    PROVIDER_ID: str | None = None

    def __init__(self) -> None:
        provider_id = self.PROVIDER_ID

        if not isinstance(
            provider_id,
            str,
        ):
            raise ValueError("PROVIDER_ID must be a string.")

        normalized_provider_id = provider_id.strip()

        if not normalized_provider_id:
            raise ValueError("PROVIDER_ID must not be blank.")

        self._provider_id = normalized_provider_id

    @property
    def provider_id(self) -> str:
        return self._provider_id

    @abstractmethod
    def detect(
        self,
        portrait_input: Any,
    ) -> AtlasPortraitLandmarkResult:
        """
        Detects facial landmarks for a portrait input.

        Concrete providers must return an
        AtlasPortraitLandmarkResult whose provider_id
        matches this provider instance.
        """
        raise NotImplementedError

    def validate_result(
        self,
        result: Any,
    ) -> AtlasPortraitLandmarkResult:
        if not isinstance(
            result,
            AtlasPortraitLandmarkResult,
        ):
            raise TypeError(
                "provider result must be an " "AtlasPortraitLandmarkResult."
            )

        if result.provider_id != self.provider_id:
            raise ValueError("result provider_id must match " "the provider instance.")

        return result
