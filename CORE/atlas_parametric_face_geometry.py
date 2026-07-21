from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

import numpy as np


@dataclass(frozen=True)
class AtlasParametricFaceGeometry:
    """
    Immutable provider-independent canonical face geometry.

    The contract stores a connected triangular face mesh,
    normalized vertex normals, UV coordinates, semantic
    vertex regions, landmark-to-vertex correspondence,
    separated identity/expression/pose parameter vectors,
    per-vertex confidence and visibility, and deterministic
    metadata.

    It performs no reconstruction, fitting, camera
    normalization, projection, relief compression,
    rendering, triangulation, or STL generation.
    """

    vertices: np.ndarray
    triangle_faces: np.ndarray
    surface_normals: np.ndarray
    uv_coordinates: np.ndarray

    semantic_vertex_regions: Mapping[
        str,
        tuple[int, ...],
    ]
    landmark_vertex_map: Mapping[str, int]

    identity_parameters: np.ndarray
    expression_parameters: np.ndarray
    pose_parameters: np.ndarray

    confidence: np.ndarray
    visibility: np.ndarray

    metadata: Mapping[str, Any]

    REQUIRED_SEMANTIC_REGIONS = (
        "forehead",
        "left_brow",
        "right_brow",
        "left_eye_socket",
        "right_eye_socket",
        "nose_bridge",
        "nose_tip",
        "left_ala",
        "right_ala",
        "columella",
        "philtrum",
        "upper_lip",
        "lower_lip",
        "chin",
        "left_cheek",
        "right_cheek",
        "jaw",
    )

    NORMAL_LENGTH_TOLERANCE = 1e-12

    def __post_init__(self) -> None:
        vertices = self._normalize_vertices(
            self.vertices,
        )

        vertex_count = int(
            vertices.shape[0],
        )

        triangle_faces = self._normalize_triangle_faces(
            self.triangle_faces,
            vertex_count=vertex_count,
        )

        surface_normals = self._normalize_surface_normals(
            self.surface_normals,
            vertex_count=vertex_count,
        )

        uv_coordinates = self._normalize_uv_coordinates(
            self.uv_coordinates,
            vertex_count=vertex_count,
        )

        semantic_vertex_regions = (
            self._normalize_semantic_vertex_regions(
                self.semantic_vertex_regions,
                vertex_count=vertex_count,
            )
        )

        landmark_vertex_map = (
            self._normalize_landmark_vertex_map(
                self.landmark_vertex_map,
                vertex_count=vertex_count,
            )
        )

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

        confidence = self._normalize_confidence(
            self.confidence,
            vertex_count=vertex_count,
        )

        visibility = self._normalize_visibility(
            self.visibility,
            vertex_count=vertex_count,
        )

        metadata = self._normalize_metadata(
            self.metadata,
        )

        for array in (
            vertices,
            triangle_faces,
            surface_normals,
            uv_coordinates,
            identity_parameters,
            expression_parameters,
            pose_parameters,
            confidence,
            visibility,
        ):
            array.setflags(
                write=False,
            )

        object.__setattr__(
            self,
            "vertices",
            vertices,
        )
        object.__setattr__(
            self,
            "triangle_faces",
            triangle_faces,
        )
        object.__setattr__(
            self,
            "surface_normals",
            surface_normals,
        )
        object.__setattr__(
            self,
            "uv_coordinates",
            uv_coordinates,
        )
        object.__setattr__(
            self,
            "semantic_vertex_regions",
            semantic_vertex_regions,
        )
        object.__setattr__(
            self,
            "landmark_vertex_map",
            landmark_vertex_map,
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
            "confidence",
            confidence,
        )
        object.__setattr__(
            self,
            "visibility",
            visibility,
        )
        object.__setattr__(
            self,
            "metadata",
            metadata,
        )

    @property
    def vertex_count(
        self,
    ) -> int:
        return int(
            self.vertices.shape[0],
        )

    @property
    def triangle_count(
        self,
    ) -> int:
        return int(
            self.triangle_faces.shape[0],
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
            "vertex_count": self.vertex_count,
            "triangle_count": self.triangle_count,
            "vertices": self.vertices.tolist(),
            "triangle_faces": (
                self.triangle_faces.tolist()
            ),
            "surface_normals": (
                self.surface_normals.tolist()
            ),
            "uv_coordinates": (
                self.uv_coordinates.tolist()
            ),
            "semantic_vertex_regions": {
                name: list(
                    self.semantic_vertex_regions[name],
                )
                for name in sorted(
                    self.semantic_vertex_regions,
                )
            },
            "landmark_vertex_map": {
                name: self.landmark_vertex_map[name]
                for name in sorted(
                    self.landmark_vertex_map,
                )
            },
            "identity_parameters": (
                self.identity_parameters.tolist()
            ),
            "expression_parameters": (
                self.expression_parameters.tolist()
            ),
            "pose_parameters": (
                self.pose_parameters.tolist()
            ),
            "confidence": self.confidence.tolist(),
            "visibility": [
                bool(value)
                for value in self.visibility.tolist()
            ],
            "metadata": {
                key: self.metadata[key]
                for key in sorted(
                    self.metadata,
                )
            },
        }

    @staticmethod
    def _normalize_vertices(
        value: Any,
    ) -> np.ndarray:
        vertices = (
            AtlasParametricFaceGeometry._normalize_float_array(
                value,
                name="vertices",
            )
        )

        if (
            vertices.ndim != 2
            or vertices.shape[1] != 3
        ):
            raise ValueError(
                "vertices must have shape (N, 3)."
            )

        if vertices.shape[0] < 3:
            raise ValueError(
                "vertices must contain at least three "
                "vertices."
            )

        return vertices

    @staticmethod
    def _normalize_triangle_faces(
        value: Any,
        *,
        vertex_count: int,
    ) -> np.ndarray:
        try:
            numeric_faces = np.asarray(
                value,
                dtype=np.float64,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "triangle_faces must be numeric."
            ) from exc

        if (
            numeric_faces.ndim != 2
            or numeric_faces.shape[1] != 3
        ):
            raise ValueError(
                "triangle_faces must have shape (M, 3)."
            )

        if numeric_faces.shape[0] < 1:
            raise ValueError(
                "triangle_faces must not be empty."
            )

        if not np.isfinite(
            numeric_faces,
        ).all():
            raise ValueError(
                "triangle_faces contains non-finite "
                "values."
            )

        if not np.equal(
            numeric_faces,
            np.rint(
                numeric_faces,
            ),
        ).all():
            raise ValueError(
                "triangle_faces must contain integer "
                "indices."
            )

        triangle_faces = numeric_faces.astype(
            np.int64,
            copy=True,
        )

        if (
            np.any(
                triangle_faces < 0,
            )
            or np.any(
                triangle_faces >= vertex_count,
            )
        ):
            raise ValueError(
                "triangle indices are outside the vertex "
                "range."
            )

        sorted_faces = np.sort(
            triangle_faces,
            axis=1,
        )

        if np.any(
            sorted_faces[:, 0]
            == sorted_faces[:, 1]
        ) or np.any(
            sorted_faces[:, 1]
            == sorted_faces[:, 2]
        ):
            raise ValueError(
                "triangle_faces contains a degenerate "
                "triangle."
            )

        return triangle_faces

    @classmethod
    def _normalize_surface_normals(
        cls,
        value: Any,
        *,
        vertex_count: int,
    ) -> np.ndarray:
        normals = cls._normalize_float_array(
            value,
            name="surface_normals",
        )

        if normals.shape != (
            vertex_count,
            3,
        ):
            raise ValueError(
                "surface_normals must have shape "
                "(vertex_count, 3)."
            )

        lengths = np.linalg.norm(
            normals,
            axis=1,
        )

        if np.any(
            lengths <= cls.NORMAL_LENGTH_TOLERANCE,
        ):
            raise ValueError(
                "surface_normals must not contain zero "
                "vectors."
            )

        return (
            normals
            / lengths[
                :,
                np.newaxis,
            ]
        ).astype(
            np.float64,
            copy=True,
        )

    @classmethod
    def _normalize_uv_coordinates(
        cls,
        value: Any,
        *,
        vertex_count: int,
    ) -> np.ndarray:
        uv_coordinates = cls._normalize_float_array(
            value,
            name="uv_coordinates",
        )

        if uv_coordinates.shape != (
            vertex_count,
            2,
        ):
            raise ValueError(
                "uv_coordinates must have shape "
                "(vertex_count, 2)."
            )

        if (
            np.any(
                uv_coordinates < 0.0,
            )
            or np.any(
                uv_coordinates > 1.0,
            )
        ):
            raise ValueError(
                "uv_coordinates must be in the "
                "0.0..1.0 range."
            )

        return uv_coordinates

    @classmethod
    def _normalize_semantic_vertex_regions(
        cls,
        value: Any,
        *,
        vertex_count: int,
    ) -> Mapping[str, tuple[int, ...]]:
        if not isinstance(
            value,
            Mapping,
        ):
            raise TypeError(
                "semantic_vertex_regions must be a "
                "mapping."
            )

        normalized: dict[str, tuple[int, ...]] = {}

        for raw_name, raw_indices in value.items():
            name = cls._normalize_name(
                raw_name,
                subject="semantic region",
            )

            if name in normalized:
                raise ValueError(
                    "semantic region names must be unique "
                    "after normalization."
                )

            indices = cls._normalize_index_sequence(
                raw_indices,
                name=name,
                vertex_count=vertex_count,
            )

            normalized[name] = indices

        missing_regions = [
            name
            for name in cls.REQUIRED_SEMANTIC_REGIONS
            if name not in normalized
        ]

        if missing_regions:
            raise ValueError(
                "Missing required semantic regions: "
                + ", ".join(
                    missing_regions,
                )
                + "."
            )

        return MappingProxyType(
            {
                name: normalized[name]
                for name in sorted(
                    normalized,
                )
            }
        )

    @classmethod
    def _normalize_landmark_vertex_map(
        cls,
        value: Any,
        *,
        vertex_count: int,
    ) -> Mapping[str, int]:
        if not isinstance(
            value,
            Mapping,
        ):
            raise TypeError(
                "landmark_vertex_map must be a mapping."
            )

        if not value:
            raise ValueError(
                "landmark_vertex_map must not be empty."
            )

        normalized: dict[str, int] = {}

        for raw_name, raw_index in value.items():
            name = cls._normalize_name(
                raw_name,
                subject="landmark",
            )

            if name in normalized:
                raise ValueError(
                    "landmark names must be unique after "
                    "normalization."
                )

            index = cls._normalize_index(
                raw_index,
                name=f"landmark {name}",
            )

            if not (
                0
                <= index
                < vertex_count
            ):
                raise ValueError(
                    f"landmark {name} index is outside "
                    "the vertex range."
                )

            normalized[name] = index

        return MappingProxyType(
            {
                name: normalized[name]
                for name in sorted(
                    normalized,
                )
            }
        )

    @classmethod
    def _normalize_parameter_vector(
        cls,
        value: Any,
        *,
        name: str,
    ) -> np.ndarray:
        parameters = cls._normalize_float_array(
            value,
            name=name,
        )

        if parameters.ndim != 1:
            raise ValueError(
                f"{name} must be one-dimensional."
            )

        if parameters.size < 1:
            raise ValueError(
                f"{name} must not be empty."
            )

        return parameters

    @classmethod
    def _normalize_confidence(
        cls,
        value: Any,
        *,
        vertex_count: int,
    ) -> np.ndarray:
        confidence = cls._normalize_float_array(
            value,
            name="confidence",
        )

        if confidence.shape != (
            vertex_count,
        ):
            raise ValueError(
                "confidence must have shape "
                "(vertex_count,)."
            )

        if (
            np.any(
                confidence < 0.0,
            )
            or np.any(
                confidence > 1.0,
            )
        ):
            raise ValueError(
                "confidence must be in the "
                "0.0..1.0 range."
            )

        return confidence

    @staticmethod
    def _normalize_visibility(
        value: Any,
        *,
        vertex_count: int,
    ) -> np.ndarray:
        visibility = np.asarray(
            value,
        )

        if visibility.shape != (
            vertex_count,
        ):
            raise ValueError(
                "visibility must have shape "
                "(vertex_count,)."
            )

        if visibility.dtype.kind != "b":
            raise TypeError(
                "visibility must contain boolean values."
            )

        return visibility.astype(
            np.bool_,
            copy=True,
        )

    @staticmethod
    def _normalize_float_array(
        value: Any,
        *,
        name: str,
    ) -> np.ndarray:
        try:
            array = np.asarray(
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

        if not np.isfinite(
            array,
        ).all():
            raise ValueError(
                f"{name} contains non-finite values."
            )

        return array.astype(
            np.float64,
            copy=True,
        )

    @staticmethod
    def _normalize_name(
        value: Any,
        *,
        subject: str,
    ) -> str:
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{subject} names must be strings."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{subject} names must not be blank."
            )

        return normalized

    @classmethod
    def _normalize_index_sequence(
        cls,
        value: Any,
        *,
        name: str,
        vertex_count: int,
    ) -> tuple[int, ...]:
        if isinstance(
            value,
            (
                str,
                bytes,
            ),
        ):
            raise TypeError(
                f"{name} indices must be a sequence."
            )

        try:
            raw_indices = tuple(
                value,
            )
        except TypeError as exc:
            raise TypeError(
                f"{name} indices must be a sequence."
            ) from exc

        if not raw_indices:
            raise ValueError(
                f"{name} semantic region must not be "
                "empty."
            )

        indices = tuple(
            sorted(
                {
                    cls._normalize_index(
                        raw_index,
                        name=f"{name} semantic index",
                    )
                    for raw_index in raw_indices
                }
            )
        )

        if any(
            index < 0
            or index >= vertex_count
            for index in indices
        ):
            raise ValueError(
                f"{name} semantic index is outside the "
                "vertex range."
            )

        return indices

    @staticmethod
    def _normalize_index(
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
                (
                    int,
                    np.integer,
                ),
            )
        ):
            raise TypeError(
                f"{name} must be an integer."
            )

        return int(
            value,
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
