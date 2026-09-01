from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Any

import numpy as np


@dataclass(frozen=True)
class AtlasPortraitFlameIdentityGeometry:
    """
    Neutral subject-specific FLAME geometry.

    This result contains geometry only. Camera, rigid head pose,
    expression, jaw articulation and physical-product conversion are
    deliberately outside this object.
    """

    vertices: np.ndarray
    faces: np.ndarray
    identity_vector: np.ndarray

    def __post_init__(self) -> None:
        vertices = np.asarray(self.vertices, dtype=np.float64)
        faces = np.asarray(self.faces, dtype=np.int64)
        identity = np.asarray(self.identity_vector, dtype=np.float64)

        if vertices.ndim != 2 or vertices.shape[1] != 3:
            raise ValueError("vertices must have shape (N, 3).")

        if faces.ndim != 2 or faces.shape[1] != 3:
            raise ValueError("faces must have shape (F, 3).")

        if identity.ndim != 1:
            raise ValueError("identity_vector must be one-dimensional.")

        if vertices.shape[0] == 0:
            raise ValueError("vertices must not be empty.")

        if faces.shape[0] == 0:
            raise ValueError("faces must not be empty.")

        if not np.all(np.isfinite(vertices)):
            raise ValueError("vertices must contain only finite values.")

        if not np.all(np.isfinite(identity)):
            raise ValueError(
                "identity_vector must contain only finite values."
            )

        if np.any(faces < 0) or np.any(faces >= vertices.shape[0]):
            raise ValueError("faces contain invalid vertex indices.")

        vertices = vertices.copy()
        faces = faces.copy()
        identity = identity.copy()

        vertices.setflags(write=False)
        faces.setflags(write=False)
        identity.setflags(write=False)

        object.__setattr__(self, "vertices", vertices)
        object.__setattr__(self, "faces", faces)
        object.__setattr__(self, "identity_vector", identity)

    @property
    def vertex_count(self) -> int:
        return int(self.vertices.shape[0])

    @property
    def face_count(self) -> int:
        return int(self.faces.shape[0])


@dataclass(frozen=True)
class AtlasPortraitFlameIdentityGeometryEvaluator:
    """
    ATLAS-owned neutral FLAME identity-shape evaluator.

    FLAME-compatible model schema:
        v_template: (N, 3)
        f:          (F, 3)
        shapedirs:  (N, 3, K)

    Only the configured identity channels are consumed.

    No external FLAME source code, pretrained neural network, or
    third-party fitting implementation is embedded here.
    """

    template_vertices: np.ndarray
    faces: np.ndarray
    identity_directions: np.ndarray

    def __post_init__(self) -> None:
        template = np.asarray(
            self.template_vertices,
            dtype=np.float64,
        )
        faces = np.asarray(
            self.faces,
            dtype=np.int64,
        )
        directions = np.asarray(
            self.identity_directions,
            dtype=np.float64,
        )

        if template.ndim != 2 or template.shape[1] != 3:
            raise ValueError(
                "template_vertices must have shape (N, 3)."
            )

        if template.shape[0] == 0:
            raise ValueError(
                "template_vertices must not be empty."
            )

        if faces.ndim != 2 or faces.shape[1] != 3:
            raise ValueError(
                "faces must have shape (F, 3)."
            )

        if faces.shape[0] == 0:
            raise ValueError("faces must not be empty.")

        if directions.ndim != 3:
            raise ValueError(
                "identity_directions must have shape (N, 3, K)."
            )

        if directions.shape[:2] != template.shape:
            raise ValueError(
                "identity_directions vertex dimensions must match "
                "template_vertices."
            )

        if directions.shape[2] <= 0:
            raise ValueError(
                "identity_directions must contain at least one channel."
            )

        if not np.all(np.isfinite(template)):
            raise ValueError(
                "template_vertices must contain only finite values."
            )

        if not np.all(np.isfinite(directions)):
            raise ValueError(
                "identity_directions must contain only finite values."
            )

        if np.any(faces < 0) or np.any(faces >= template.shape[0]):
            raise ValueError(
                "faces contain invalid vertex indices."
            )

        template = template.copy()
        faces = faces.copy()
        directions = directions.copy()

        template.setflags(write=False)
        faces.setflags(write=False)
        directions.setflags(write=False)

        object.__setattr__(self, "template_vertices", template)
        object.__setattr__(self, "faces", faces)
        object.__setattr__(self, "identity_directions", directions)

    @classmethod
    def from_flame_mapping(
        cls,
        *,
        flame: Mapping[str, Any],
        identity_parameter_count: int = 300,
    ) -> "AtlasPortraitFlameIdentityGeometryEvaluator":
        """
        Build from the documented FLAME-style tensor mapping.

        Asset licensing is deliberately not inferred here. Possession of
        a model file does not imply commercial-use clearance.
        """

        if not isinstance(identity_parameter_count, int):
            raise TypeError(
                "identity_parameter_count must be an integer."
            )

        if identity_parameter_count <= 0:
            raise ValueError(
                "identity_parameter_count must be positive."
            )

        required = (
            "v_template",
            "f",
            "shapedirs",
        )

        missing = [
            name
            for name in required
            if name not in flame
        ]

        if missing:
            raise ValueError(
                "FLAME mapping missing required fields: "
                + ", ".join(missing)
            )

        shapedirs = np.asarray(
            flame["shapedirs"],
            dtype=np.float64,
        )

        if shapedirs.ndim != 3:
            raise ValueError(
                "FLAME shapedirs must have shape (N, 3, K)."
            )

        if shapedirs.shape[2] < identity_parameter_count:
            raise ValueError(
                "FLAME shapedirs do not contain the requested "
                "identity parameter count."
            )

        return cls(
            template_vertices=np.asarray(
                flame["v_template"],
                dtype=np.float64,
            ),
            faces=np.asarray(
                flame["f"],
                dtype=np.int64,
            ),
            identity_directions=shapedirs[
                :,
                :,
                :identity_parameter_count,
            ],
        )

    @property
    def identity_parameter_count(self) -> int:
        return int(self.identity_directions.shape[2])

    @property
    def vertex_count(self) -> int:
        return int(self.template_vertices.shape[0])

    @property
    def face_count(self) -> int:
        return int(self.faces.shape[0])

    def evaluate(
        self,
        *,
        identity_vector: np.ndarray,
    ) -> AtlasPortraitFlameIdentityGeometry:
        identity = np.asarray(
            identity_vector,
            dtype=np.float64,
        )

        if identity.shape != (
            self.identity_parameter_count,
        ):
            raise ValueError(
                "identity_vector dimension does not match "
                "identity_parameter_count."
            )

        if not np.all(np.isfinite(identity)):
            raise ValueError(
                "identity_vector must contain only finite values."
            )

        displacement = np.tensordot(
            self.identity_directions,
            identity,
            axes=([2], [0]),
        )

        vertices = (
            self.template_vertices
            + displacement
        )

        return AtlasPortraitFlameIdentityGeometry(
            vertices=vertices,
            faces=self.faces,
            identity_vector=identity,
        )
