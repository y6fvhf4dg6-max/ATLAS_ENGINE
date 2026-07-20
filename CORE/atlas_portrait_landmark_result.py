from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any


@dataclass(frozen=True)
class AtlasPortraitLandmarkResult:
    """
    Immutable normalized portrait-landmark result.

    The result stores image dimensions, normalized
    two-dimensional facial landmarks, provider
    confidence, provider identity, and metadata.

    Landmark coordinates use the inclusive normalized
    0.0..1.0 range. Pixel coordinates are derived
    deterministically from image dimensions.
    """

    image_width: int
    image_height: int
    landmarks: Mapping[str, tuple[float, float]]
    confidence: float
    provider_id: str
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        image_width = self._normalize_dimension(
            self.image_width,
            name="image_width",
        )
        image_height = self._normalize_dimension(
            self.image_height,
            name="image_height",
        )

        landmarks = self._normalize_landmarks(
            self.landmarks,
        )
        confidence = self._normalize_confidence(
            self.confidence,
        )
        provider_id = self._normalize_provider_id(
            self.provider_id,
        )
        metadata = self._normalize_metadata(
            self.metadata,
        )

        object.__setattr__(
            self,
            "image_width",
            image_width,
        )
        object.__setattr__(
            self,
            "image_height",
            image_height,
        )
        object.__setattr__(
            self,
            "landmarks",
            landmarks,
        )
        object.__setattr__(
            self,
            "confidence",
            confidence,
        )
        object.__setattr__(
            self,
            "provider_id",
            provider_id,
        )
        object.__setattr__(
            self,
            "metadata",
            metadata,
        )

    def pixel_landmark(
        self,
        name: str,
    ) -> tuple[float, float]:
        normalized_x, normalized_y = self.landmarks[name]

        return (
            normalized_x * (self.image_width - 1),
            normalized_y * (self.image_height - 1),
        )

    @staticmethod
    def _normalize_dimension(
        value: Any,
        *,
        name: str,
    ) -> int:
        try:
            numeric_value = float(value)
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(f"{name} must be numeric.") from exc

        if not math.isfinite(numeric_value):
            raise ValueError(f"{name} must be finite.")

        if not numeric_value.is_integer():
            raise ValueError(f"{name} must be an integer.")

        integer_value = int(numeric_value)

        if integer_value <= 0:
            raise ValueError(f"{name} must be greater than zero.")

        return integer_value

    @classmethod
    def _normalize_landmarks(
        cls,
        landmarks: Any,
    ) -> Mapping[str, tuple[float, float]]:
        if not isinstance(
            landmarks,
            Mapping,
        ):
            raise ValueError("landmarks must be a mapping.")

        if not landmarks:
            raise ValueError("landmarks must not be empty.")

        normalized: dict[
            str,
            tuple[float, float],
        ] = {}

        for raw_name, raw_coordinates in landmarks.items():
            if not isinstance(raw_name, str):
                raise ValueError("landmark names must be strings.")

            name = raw_name.strip()

            if not name:
                raise ValueError("landmark names must not be blank.")

            if name in normalized:
                raise ValueError(
                    "landmark names must be unique " "after normalization."
                )

            coordinates = cls._normalize_coordinates(
                raw_coordinates,
                name=name,
            )

            normalized[name] = coordinates

        return MappingProxyType(
            normalized,
        )

    @staticmethod
    def _normalize_coordinates(
        coordinates: Any,
        *,
        name: str,
    ) -> tuple[float, float]:
        if isinstance(
            coordinates,
            (str, bytes),
        ):
            raise ValueError(
                f"{name} coordinates must contain " "exactly two numeric values."
            )

        try:
            coordinate_values = tuple(coordinates)
        except TypeError as exc:
            raise ValueError(
                f"{name} coordinates must contain " "exactly two numeric values."
            ) from exc

        if len(coordinate_values) != 2:
            raise ValueError(
                f"{name} coordinates must contain " "exactly two numeric values."
            )

        normalized_coordinates = []

        for axis, value in zip(
            ("x", "y"),
            coordinate_values,
            strict=True,
        ):
            try:
                numeric_value = float(value)
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise ValueError(
                    f"{name} {axis} coordinate must " "be numeric."
                ) from exc

            if not math.isfinite(numeric_value):
                raise ValueError(f"{name} {axis} coordinate must " "be finite.")

            if not (0.0 <= numeric_value <= 1.0):
                raise ValueError(
                    f"{name} {axis} coordinate must " "be in the 0.0..1.0 range."
                )

            normalized_coordinates.append(numeric_value)

        return (
            normalized_coordinates[0],
            normalized_coordinates[1],
        )

    @staticmethod
    def _normalize_confidence(
        confidence: Any,
    ) -> float:
        try:
            numeric_confidence = float(confidence)
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError("confidence must be numeric.") from exc

        if not math.isfinite(numeric_confidence):
            raise ValueError("confidence must be finite.")

        if not (0.0 <= numeric_confidence <= 1.0):
            raise ValueError("confidence must be in the " "0.0..1.0 range.")

        return numeric_confidence

    @staticmethod
    def _normalize_provider_id(
        provider_id: Any,
    ) -> str:
        if not isinstance(
            provider_id,
            str,
        ):
            raise ValueError("provider_id must be a string.")

        normalized_provider_id = provider_id.strip()

        if not normalized_provider_id:
            raise ValueError("provider_id must not be blank.")

        return normalized_provider_id

    @staticmethod
    def _normalize_metadata(
        metadata: Any,
    ) -> Mapping[str, Any]:
        if not isinstance(
            metadata,
            Mapping,
        ):
            raise ValueError("metadata must be a mapping.")

        return MappingProxyType(dict(metadata))
