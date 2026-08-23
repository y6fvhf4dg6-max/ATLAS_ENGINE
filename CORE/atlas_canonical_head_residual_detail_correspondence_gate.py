from __future__ import annotations

from dataclasses import dataclass

from CORE.atlas_canonical_head_dense_correspondence import (
    AtlasCanonicalHeadDenseCorrespondence,
)
from CORE.atlas_canonical_head_residual_detail_observation import (
    AtlasCanonicalHeadResidualDetailObservation,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadResidualDetailCorrespondenceResult:
    compatible: bool
    status: str
    blocked_reasons: tuple[str, ...]
    matched_sample_count: int
    observed_sample_indices: tuple[int, ...]
    canonical_vertex_indices: tuple[int, ...]
    connectivity_signature: str | None


class AtlasCanonicalHeadResidualDetailCorrespondenceGate:
    @classmethod
    def evaluate(
        cls,
        *,
        observation: AtlasCanonicalHeadResidualDetailObservation,
        correspondence: AtlasCanonicalHeadDenseCorrespondence,
    ) -> AtlasCanonicalHeadResidualDetailCorrespondenceResult:
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
            AtlasCanonicalHeadDenseCorrespondence,
        ):
            raise TypeError(
                "correspondence must be an "
                "AtlasCanonicalHeadDenseCorrespondence."
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
            return (
                AtlasCanonicalHeadResidualDetailCorrespondenceResult(
                    compatible=False,
                    status="BLOCKED",
                    blocked_reasons=(
                        "BLOCKED_RESIDUAL_DETAIL_OBSERVATION_SAMPLE_MISMATCH",
                    ),
                    matched_sample_count=0,
                    observed_sample_indices=(),
                    canonical_vertex_indices=(),
                    connectivity_signature=None,
                )
            )

        canonical_vertex_indices = tuple(
            correspondence.canonical_vertex_index(
                sample_index
            )
            for sample_index in correspondence_samples
        )

        return (
            AtlasCanonicalHeadResidualDetailCorrespondenceResult(
                compatible=True,
                status="ACCEPTED",
                blocked_reasons=(),
                matched_sample_count=len(
                    correspondence_samples
                ),
                observed_sample_indices=tuple(
                    correspondence_samples
                ),
                canonical_vertex_indices=canonical_vertex_indices,
                connectivity_signature=(
                    correspondence.connectivity_signature
                ),
            )
        )
