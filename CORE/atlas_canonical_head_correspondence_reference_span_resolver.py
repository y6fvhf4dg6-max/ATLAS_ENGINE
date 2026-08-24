from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from CORE.atlas_canonical_head_geometry import (
    AtlasCanonicalHeadGeometry,
)
from CORE.atlas_canonical_head_residual_detail_observation import (
    AtlasCanonicalHeadResidualDetailObservation,
)
from CORE.atlas_canonical_head_surface_correspondence import (
    AtlasCanonicalHeadSurfaceCorrespondence,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadCorrespondenceReferenceSpanResult:
    image_reference_span_px: float
    canonical_reference_span: float

    def __post_init__(self) -> None:
        for field_name in (
            "image_reference_span_px",
            "canonical_reference_span",
        ):
            value = float(
                getattr(
                    self,
                    field_name,
                )
            )

            if (
                not math.isfinite(value)
                or value <= 0.0
            ):
                raise ValueError(
                    f"{field_name} must be finite and positive."
                )

            object.__setattr__(
                self,
                field_name,
                value,
            )


class AtlasCanonicalHeadCorrespondenceReferenceSpanResolver:
    @classmethod
    def resolve(
        cls,
        *,
        observation: AtlasCanonicalHeadResidualDetailObservation,
        correspondence: AtlasCanonicalHeadSurfaceCorrespondence,
        geometry: AtlasCanonicalHeadGeometry,
    ) -> AtlasCanonicalHeadCorrespondenceReferenceSpanResult:
        if not isinstance(
            observation,
            AtlasCanonicalHeadResidualDetailObservation,
        ):
            raise TypeError(
                "observation must be an "
                "AtlasCanonicalHeadResidualDetailObservation."
            )

        if not isinstance(
            correspondence,
            AtlasCanonicalHeadSurfaceCorrespondence,
        ):
            raise TypeError(
                "correspondence must be an "
                "AtlasCanonicalHeadSurfaceCorrespondence."
            )

        if not isinstance(
            geometry,
            AtlasCanonicalHeadGeometry,
        ):
            raise TypeError(
                "geometry must be an "
                "AtlasCanonicalHeadGeometry."
            )

        if (
            geometry.connectivity_signature
            != correspondence.connectivity_signature
        ):
            raise ValueError(
                "TOPOLOGY_MISMATCH"
            )

        required_indices = (
            correspondence.observed_sample_indices
        )

        observation_index_set = set(
            observation.sample_indices
        )

        missing = [
            sample_index
            for sample_index in required_indices
            if sample_index not in observation_index_set
        ]

        if missing:
            raise ValueError(
                "OBSERVATION_SAMPLE_MISMATCH"
            )

        image_points = np.asarray(
            [
                observation.pixel_coordinate(
                    sample_index
                )
                for sample_index in required_indices
            ],
            dtype=np.float64,
        )

        canonical_points = np.asarray(
            [
                cls._canonical_surface_point(
                    correspondence=correspondence,
                    geometry=geometry,
                    sample_index=sample_index,
                )
                for sample_index in required_indices
            ],
            dtype=np.float64,
        )

        image_min = np.min(
            image_points,
            axis=0,
        )
        image_max = np.max(
            image_points,
            axis=0,
        )

        canonical_min = np.min(
            canonical_points,
            axis=0,
        )
        canonical_max = np.max(
            canonical_points,
            axis=0,
        )

        image_span = float(
            np.linalg.norm(
                image_max
                - image_min
            )
        )

        canonical_span = float(
            np.linalg.norm(
                canonical_max
                - canonical_min
            )
        )

        return AtlasCanonicalHeadCorrespondenceReferenceSpanResult(
            image_reference_span_px=image_span,
            canonical_reference_span=canonical_span,
        )

    @staticmethod
    def _canonical_surface_point(
        *,
        correspondence: AtlasCanonicalHeadSurfaceCorrespondence,
        geometry: AtlasCanonicalHeadGeometry,
        sample_index: int,
    ) -> np.ndarray:
        face_index, weights = (
            correspondence.canonical_surface_location(
                sample_index
            )
        )

        vertex_indices = np.asarray(
            correspondence.topology.faces[
                face_index
            ],
            dtype=np.int64,
        )

        face_vertices = geometry.vertices[
            vertex_indices
        ]

        return (
            np.asarray(
                weights,
                dtype=np.float64,
            )
            @ face_vertices
        )
