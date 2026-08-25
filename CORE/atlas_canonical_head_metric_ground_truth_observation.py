from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadMetricGroundTruthObservation:
    observation_id: str
    subject_id: str
    source_id: str
    units: str

    ground_truth_vertices: np.ndarray
    ground_truth_faces: tuple[tuple[int, int, int], ...]

    reconstruction_vertices: np.ndarray
    reconstruction_faces: tuple[tuple[int, int, int], ...]

    source_provenance_state: str
    evaluation_license_state: str
    evaluation_use_only: bool

    def __post_init__(self) -> None:
        for field_name in (
            "observation_id",
            "subject_id",
            "source_id",
        ):
            value = str(
                getattr(self, field_name)
            ).strip()

            if not value:
                raise ValueError(
                    f"{field_name} must be non-blank."
                )

            object.__setattr__(
                self,
                field_name,
                value,
            )

        units = str(self.units).strip().lower()

        if units != "mm":
            raise ValueError(
                "units must be 'mm'."
            )

        object.__setattr__(
            self,
            "units",
            units,
        )

        source_provenance_state = str(
            self.source_provenance_state
        ).strip().upper()

        if source_provenance_state not in (
            "VERIFIED",
            "UNRESOLVED",
        ):
            raise ValueError(
                "source_provenance_state must be one of "
                "('VERIFIED', 'UNRESOLVED')."
            )

        object.__setattr__(
            self,
            "source_provenance_state",
            source_provenance_state,
        )

        evaluation_license_state = str(
            self.evaluation_license_state
        ).strip().upper()

        if evaluation_license_state not in (
            "ACCEPTABLE",
            "BLOCKED",
            "UNRESOLVED",
        ):
            raise ValueError(
                "evaluation_license_state must be one of "
                "('ACCEPTABLE', 'BLOCKED', 'UNRESOLVED')."
            )

        object.__setattr__(
            self,
            "evaluation_license_state",
            evaluation_license_state,
        )

        if not isinstance(
            self.evaluation_use_only,
            bool,
        ):
            raise TypeError(
                "evaluation_use_only must be boolean."
            )

        ground_truth_vertices = self._normalize_vertices(
            self.ground_truth_vertices,
            name="ground_truth_vertices",
        )
        reconstruction_vertices = self._normalize_vertices(
            self.reconstruction_vertices,
            name="reconstruction_vertices",
        )

        ground_truth_faces = self._normalize_faces(
            self.ground_truth_faces,
            vertex_count=ground_truth_vertices.shape[0],
            name="ground_truth_faces",
        )
        reconstruction_faces = self._normalize_faces(
            self.reconstruction_faces,
            vertex_count=reconstruction_vertices.shape[0],
            name="reconstruction_faces",
        )

        object.__setattr__(
            self,
            "ground_truth_vertices",
            ground_truth_vertices,
        )
        object.__setattr__(
            self,
            "ground_truth_faces",
            ground_truth_faces,
        )
        object.__setattr__(
            self,
            "reconstruction_vertices",
            reconstruction_vertices,
        )
        object.__setattr__(
            self,
            "reconstruction_faces",
            reconstruction_faces,
        )

    @staticmethod
    def _normalize_vertices(
        value: object,
        *,
        name: str,
    ) -> np.ndarray:
        vertices = np.asarray(
            value,
            dtype=np.float64,
        )

        if (
            vertices.ndim != 2
            or vertices.shape[1] != 3
            or vertices.shape[0] == 0
        ):
            raise ValueError(
                f"{name} must have shape (N, 3)."
            )

        if not np.all(
            np.isfinite(vertices)
        ):
            raise ValueError(
                f"{name} must contain only finite values."
            )

        vertices = vertices.copy()
        vertices.setflags(write=False)

        return vertices

    @staticmethod
    def _normalize_faces(
        value: object,
        *,
        vertex_count: int,
        name: str,
    ) -> tuple[tuple[int, int, int], ...]:
        try:
            raw_faces = tuple(value)
        except TypeError as exc:
            raise TypeError(
                f"{name} must be an iterable of triangles."
            ) from exc

        if not raw_faces:
            raise ValueError(
                f"{name} must not be empty."
            )

        normalized = []

        for raw_face in raw_faces:
            try:
                face = tuple(raw_face)
            except TypeError as exc:
                raise TypeError(
                    f"{name} must contain triangles."
                ) from exc

            if len(face) != 3:
                raise ValueError(
                    f"{name} must contain triangular faces."
                )

            if any(
                isinstance(index, bool)
                or not isinstance(
                    index,
                    (int, np.integer),
                )
                for index in face
            ):
                raise TypeError(
                    f"{name} indices must be integers."
                )

            triangle = tuple(
                int(index)
                for index in face
            )

            if any(
                index < 0
                or index >= vertex_count
                for index in triangle
            ):
                raise ValueError(
                    f"{name} indices must be inside vertex bounds."
                )

            normalized.append(
                triangle
            )

        return tuple(normalized)
