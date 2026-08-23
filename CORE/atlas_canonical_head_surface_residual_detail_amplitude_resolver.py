from __future__ import annotations

import numpy as np

from CORE.atlas_canonical_head_residual_detail_amplitude_resolver import (
    AtlasCanonicalHeadResidualDetailAmplitudeResult,
)
from CORE.atlas_canonical_head_residual_detail_observation import (
    AtlasCanonicalHeadResidualDetailObservation,
)
from CORE.atlas_canonical_head_surface_correspondence import (
    AtlasCanonicalHeadSurfaceCorrespondence,
)


class AtlasCanonicalHeadSurfaceResidualDetailAmplitudeResolver:
    @classmethod
    def resolve(
        cls,
        *,
        observation: AtlasCanonicalHeadResidualDetailObservation,
        correspondence: AtlasCanonicalHeadSurfaceCorrespondence,
    ) -> AtlasCanonicalHeadResidualDetailAmplitudeResult:
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

        observation_sample_set = set(
            observation.sample_indices
        )

        correspondence_samples = (
            correspondence.observed_sample_indices
        )

        if any(
            sample_index not in observation_sample_set
            for sample_index in correspondence_samples
        ):
            raise ValueError(
                "BLOCKED_RESIDUAL_DETAIL_OBSERVATION_SAMPLE_MISMATCH"
            )

        topology = correspondence.topology
        vertex_count = topology.vertex_count

        supported_vertices = sorted(
            {
                vertex_index
                for sample_index in correspondence_samples
                for vertex_index, weight in zip(
                    topology.faces[
                        correspondence.canonical_surface_location(
                            sample_index
                        )[0]
                    ],
                    correspondence.canonical_surface_location(
                        sample_index
                    )[1],
                    strict=True,
                )
                if weight > 0.0
            }
        )

        canonical_scalar_detail = np.zeros(
            vertex_count,
            dtype=np.float64,
        )
        canonical_confidence = np.zeros(
            vertex_count,
            dtype=np.float64,
        )

        if supported_vertices:
            local_column = {
                vertex_index: column_index
                for column_index, vertex_index in enumerate(
                    supported_vertices
                )
            }

            matrix = np.zeros(
                (
                    len(correspondence_samples),
                    len(supported_vertices),
                ),
                dtype=np.float64,
            )
            detail_values = np.zeros(
                len(correspondence_samples),
                dtype=np.float64,
            )

            confidence_weighted_sum = np.zeros(
                vertex_count,
                dtype=np.float64,
            )
            confidence_weight_sum = np.zeros(
                vertex_count,
                dtype=np.float64,
            )

            for row_index, sample_index in enumerate(
                correspondence_samples
            ):
                face_index, barycentric_weights = (
                    correspondence.canonical_surface_location(
                        sample_index
                    )
                )
                face = topology.faces[
                    face_index
                ]

                detail_values[
                    row_index
                ] = observation.scalar_detail_for_sample(
                    sample_index
                )

                sample_confidence = (
                    observation.confidence_for_sample(
                        sample_index
                    )
                )

                for vertex_index, weight in zip(
                    face,
                    barycentric_weights,
                    strict=True,
                ):
                    if weight <= 0.0:
                        continue

                    matrix[
                        row_index,
                        local_column[vertex_index],
                    ] = weight

                    confidence_weighted_sum[
                        vertex_index
                    ] += (
                        weight
                        * sample_confidence
                    )
                    confidence_weight_sum[
                        vertex_index
                    ] += weight

            solved_detail, _, _, _ = np.linalg.lstsq(
                matrix,
                detail_values,
                rcond=None,
            )

            for vertex_index, column_index in (
                local_column.items()
            ):
                canonical_scalar_detail[
                    vertex_index
                ] = solved_detail[
                    column_index
                ]

                canonical_confidence[
                    vertex_index
                ] = (
                    confidence_weighted_sum[
                        vertex_index
                    ]
                    / confidence_weight_sum[
                        vertex_index
                    ]
                )

        return AtlasCanonicalHeadResidualDetailAmplitudeResult(
            canonical_scalar_detail=canonical_scalar_detail,
            canonical_confidence=canonical_confidence,
            mapped_vertex_count=len(
                supported_vertices
            ),
            connectivity_signature=(
                correspondence.connectivity_signature
            ),
        )
