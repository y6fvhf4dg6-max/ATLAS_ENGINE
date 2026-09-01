from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasPortraitDenseImageSurfaceEvidence:
    evidence_id: str
    source_view_id: str
    image_width: int
    image_height: int
    canonical_vertex_indices: np.ndarray
    projected_xy: np.ndarray
    observed_rgb: np.ndarray
    rendered_rgb: np.ndarray
    confidence: np.ndarray

    EVIDENCE_CLASS = (
        "IMAGE_CONDITIONED_DENSE_SURFACE_EVIDENCE"
    )

    def __post_init__(self) -> None:
        evidence_id = self._normalize_identifier(
            self.evidence_id,
            name="evidence_id",
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

        vertex_indices = self._readonly_int_vector(
            self.canonical_vertex_indices,
            name="canonical_vertex_indices",
        )

        if np.any(vertex_indices < 0):
            raise ValueError(
                "canonical_vertex_indices must be nonnegative."
            )

        if (
            np.unique(vertex_indices).size
            != vertex_indices.size
        ):
            raise ValueError(
                "canonical_vertex_indices must be unique."
            )

        projected_xy = self._readonly_float_matrix(
            self.projected_xy,
            name="projected_xy",
            column_count=2,
        )

        observed_rgb = self._readonly_rgb(
            self.observed_rgb,
            name="observed_rgb",
        )

        rendered_rgb = self._readonly_rgb(
            self.rendered_rgb,
            name="rendered_rgb",
        )

        confidence = self._readonly_float_vector(
            self.confidence,
            name="confidence",
        )

        sample_count = vertex_indices.size

        observed_counts = {
            sample_count,
            projected_xy.shape[0],
            observed_rgb.shape[0],
            rendered_rgb.shape[0],
            confidence.size,
        }

        if len(observed_counts) != 1:
            raise ValueError(
                "all dense surface arrays must have the same "
                "sample count."
            )

        if np.any(confidence < 0.0) or np.any(
            confidence > 1.0
        ):
            raise ValueError(
                "confidence must be inside the 0.0..1.0 range."
            )

        object.__setattr__(
            self,
            "evidence_id",
            evidence_id,
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
            "canonical_vertex_indices",
            vertex_indices,
        )
        object.__setattr__(
            self,
            "projected_xy",
            projected_xy,
        )
        object.__setattr__(
            self,
            "observed_rgb",
            observed_rgb,
        )
        object.__setattr__(
            self,
            "rendered_rgb",
            rendered_rgb,
        )
        object.__setattr__(
            self,
            "confidence",
            confidence,
        )

    @property
    def sample_count(self) -> int:
        return int(
            self.canonical_vertex_indices.size
        )

    @property
    def evidence_class(self) -> str:
        return self.EVIDENCE_CLASS

    @property
    def anatomical_homology_claim(self) -> bool:
        return False

    @property
    def canonical_identity_owner(self) -> bool:
        return False

    @property
    def mutates_canonical_identity(self) -> bool:
        return False

    @staticmethod
    def _normalize_identifier(
        value: object,
        *,
        name: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{name} must be a string."
            )

        normalized = value.strip()

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
            isinstance(value, bool)
            or not isinstance(
                value,
                (int, np.integer),
            )
        ):
            raise TypeError(
                f"{name} must be an integer."
            )

        normalized = int(value)

        if normalized <= 0:
            raise ValueError(
                f"{name} must be positive."
            )

        return normalized

    @staticmethod
    def _readonly_int_vector(
        value: object,
        *,
        name: str,
    ) -> np.ndarray:
        array = np.array(
            value,
            dtype=np.int64,
            copy=True,
        )

        if array.ndim != 1:
            raise ValueError(
                f"{name} must be a 1D array."
            )

        if array.size == 0:
            raise ValueError(
                f"{name} must not be empty."
            )

        array.setflags(write=False)
        return array

    @staticmethod
    def _readonly_float_vector(
        value: object,
        *,
        name: str,
    ) -> np.ndarray:
        array = np.array(
            value,
            dtype=np.float64,
            copy=True,
        )

        if array.ndim != 1:
            raise ValueError(
                f"{name} must be a 1D array."
            )

        if array.size == 0:
            raise ValueError(
                f"{name} must not be empty."
            )

        if not np.all(np.isfinite(array)):
            raise ValueError(
                f"{name} must contain only finite values."
            )

        array.setflags(write=False)
        return array

    @staticmethod
    def _readonly_float_matrix(
        value: object,
        *,
        name: str,
        column_count: int,
    ) -> np.ndarray:
        array = np.array(
            value,
            dtype=np.float64,
            copy=True,
        )

        if (
            array.ndim != 2
            or array.shape[1] != column_count
        ):
            raise ValueError(
                f"{name} must have shape (N, {column_count})."
            )

        if array.shape[0] == 0:
            raise ValueError(
                f"{name} must not be empty."
            )

        if not np.all(np.isfinite(array)):
            raise ValueError(
                f"{name} must contain only finite values."
            )

        array.setflags(write=False)
        return array

    @classmethod
    def _readonly_rgb(
        cls,
        value: object,
        *,
        name: str,
    ) -> np.ndarray:
        array = cls._readonly_float_matrix(
            value,
            name=name,
            column_count=3,
        )

        if np.any(array < 0.0) or np.any(
            array > 1.0
        ):
            raise ValueError(
                f"{name} rgb values must be inside "
                "the 0.0..1.0 range."
            )

        return array
