from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Integral

import numpy as np


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadResidualDetailObservation:
    observation_id: str
    source_view_id: str
    image_width: int
    image_height: int
    sample_indices: tuple[int, ...]
    sample_coordinates_normalized: np.ndarray
    scalar_detail: np.ndarray
    confidence: np.ndarray

    def __post_init__(self) -> None:
        observation_id = self._normalize_identifier(
            self.observation_id,
            name="observation_id",
        )
        source_view_id = self._normalize_identifier(
            self.source_view_id,
            name="source_view_id",
        )
        image_width = self._normalize_dimension(
            self.image_width,
            name="image_width",
        )
        image_height = self._normalize_dimension(
            self.image_height,
            name="image_height",
        )
        sample_indices = self._normalize_sample_indices(
            self.sample_indices,
        )

        sample_count = len(
            sample_indices
        )

        coordinates = self._normalize_coordinates(
            self.sample_coordinates_normalized,
            sample_count=sample_count,
        )
        scalar_detail = self._normalize_vector(
            self.scalar_detail,
            sample_count=sample_count,
            name="scalar_detail",
        )
        confidence = self._normalize_confidence(
            self.confidence,
            sample_count=sample_count,
        )

        coordinates.setflags(
            write=False
        )
        scalar_detail.setflags(
            write=False
        )
        confidence.setflags(
            write=False
        )

        object.__setattr__(
            self,
            "observation_id",
            observation_id,
        )
        object.__setattr__(
            self,
            "source_view_id",
            source_view_id,
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
            "sample_indices",
            sample_indices,
        )
        object.__setattr__(
            self,
            "sample_coordinates_normalized",
            coordinates,
        )
        object.__setattr__(
            self,
            "scalar_detail",
            scalar_detail,
        )
        object.__setattr__(
            self,
            "confidence",
            confidence,
        )

    @property
    def sample_count(
        self,
    ) -> int:
        return len(
            self.sample_indices
        )

    def pixel_coordinate(
        self,
        sample_index: int,
    ) -> tuple[float, float]:
        position = self._position_for_sample(
            sample_index
        )

        normalized_x, normalized_y = (
            self.sample_coordinates_normalized[
                position
            ]
        )

        return (
            float(
                normalized_x
                * (
                    self.image_width
                    - 1
                )
            ),
            float(
                normalized_y
                * (
                    self.image_height
                    - 1
                )
            ),
        )

    def scalar_detail_for_sample(
        self,
        sample_index: int,
    ) -> float:
        position = self._position_for_sample(
            sample_index
        )

        return float(
            self.scalar_detail[
                position
            ]
        )

    def confidence_for_sample(
        self,
        sample_index: int,
    ) -> float:
        position = self._position_for_sample(
            sample_index
        )

        return float(
            self.confidence[
                position
            ]
        )

    def _position_for_sample(
        self,
        sample_index: int,
    ) -> int:
        try:
            return self.sample_indices.index(
                sample_index
            )
        except ValueError as exc:
            raise KeyError(
                sample_index
            ) from exc

    @staticmethod
    def _normalize_identifier(
        value: object,
        *,
        name: str,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{name} must be a string."
            )

        normalized = "_".join(
            value.strip().lower().split()
        )

        if not normalized:
            raise ValueError(
                f"{name} must not be blank."
            )

        return normalized

    @staticmethod
    def _normalize_dimension(
        value: object,
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
                Integral,
            )
        ):
            raise TypeError(
                f"{name} must be an integer."
            )

        normalized = int(
            value
        )

        if normalized <= 0:
            raise ValueError(
                f"{name} must be greater than zero."
            )

        return normalized

    @staticmethod
    def _normalize_sample_indices(
        value: object,
    ) -> tuple[int, ...]:
        if isinstance(
            value,
            (
                str,
                bytes,
            ),
        ):
            raise TypeError(
                "sample_indices must be a non-empty "
                "sequence of integers."
            )

        try:
            raw_values = tuple(
                value
            )
        except TypeError as exc:
            raise TypeError(
                "sample_indices must be a non-empty "
                "sequence of integers."
            ) from exc

        if not raw_values:
            raise ValueError(
                "sample_indices must not be empty."
            )

        normalized = []

        for raw_value in raw_values:
            if (
                isinstance(
                    raw_value,
                    bool,
                )
                or not isinstance(
                    raw_value,
                    Integral,
                )
            ):
                raise TypeError(
                    "sample_indices must contain integers."
                )

            sample_index = int(
                raw_value
            )

            if sample_index < 0:
                raise ValueError(
                    "sample_indices must not contain "
                    "negative values."
                )

            normalized.append(
                sample_index
            )

        if len(
            normalized
        ) != len(
            set(
                normalized
            )
        ):
            raise ValueError(
                "sample_indices must contain unique values."
            )

        return tuple(
            normalized
        )

    @staticmethod
    def _normalize_coordinates(
        value: object,
        *,
        sample_count: int,
    ) -> np.ndarray:
        try:
            coordinates = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "sample_coordinates_normalized must be numeric."
            ) from exc

        expected_shape = (
            sample_count,
            2,
        )

        if coordinates.shape != expected_shape:
            raise ValueError(
                "sample_coordinates_normalized must have shape "
                f"{expected_shape}."
            )

        if not np.isfinite(
            coordinates
        ).all():
            raise ValueError(
                "sample_coordinates_normalized must contain "
                "only finite values."
            )

        if (
            np.any(
                coordinates < 0.0
            )
            or np.any(
                coordinates > 1.0
            )
        ):
            raise ValueError(
                "sample_coordinates_normalized values must be "
                "in the 0.0..1.0 range."
            )

        return coordinates.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _normalize_vector(
        value: object,
        *,
        sample_count: int,
        name: str,
    ) -> np.ndarray:
        try:
            vector = np.asarray(
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

        expected_shape = (
            sample_count,
        )

        if vector.shape != expected_shape:
            raise ValueError(
                f"{name} must have shape "
                f"{expected_shape}."
            )

        if not np.isfinite(
            vector
        ).all():
            raise ValueError(
                f"{name} must contain only finite values."
            )

        return vector.astype(
            np.float64,
            copy=True,
        )

    @classmethod
    def _normalize_confidence(
        cls,
        value: object,
        *,
        sample_count: int,
    ) -> np.ndarray:
        confidence = cls._normalize_vector(
            value,
            sample_count=sample_count,
            name="confidence",
        )

        if (
            np.any(
                confidence < 0.0
            )
            or np.any(
                confidence > 1.0
            )
        ):
            raise ValueError(
                "confidence values must be in the "
                "0.0..1.0 range."
            )

        return confidence
