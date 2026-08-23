from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from CORE.atlas_canonical_head_dense_correspondence import (
    AtlasCanonicalHeadDenseCorrespondence,
)
from CORE.atlas_canonical_head_residual_detail_correspondence_gate import (
    AtlasCanonicalHeadResidualDetailCorrespondenceGate,
)
from CORE.atlas_canonical_head_residual_detail_observation import (
    AtlasCanonicalHeadResidualDetailObservation,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadResidualDetailAmplitudeResult:
    canonical_scalar_detail: np.ndarray
    canonical_confidence: np.ndarray
    mapped_vertex_count: int
    connectivity_signature: str

    def __post_init__(self) -> None:
        scalar_detail = np.asarray(
            self.canonical_scalar_detail,
            dtype=np.float64,
        )
        confidence = np.asarray(
            self.canonical_confidence,
            dtype=np.float64,
        )

        if scalar_detail.ndim != 1:
            raise ValueError(
                "canonical_scalar_detail must be one-dimensional."
            )

        if confidence.shape != scalar_detail.shape:
            raise ValueError(
                "canonical_confidence shape must match "
                "canonical_scalar_detail."
            )

        if not np.isfinite(
            scalar_detail
        ).all():
            raise ValueError(
                "canonical_scalar_detail must contain "
                "only finite values."
            )

        if not np.isfinite(
            confidence
        ).all():
            raise ValueError(
                "canonical_confidence must contain "
                "only finite values."
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
                "canonical_confidence values must be "
                "in the 0.0..1.0 range."
            )

        if (
            isinstance(
                self.mapped_vertex_count,
                bool,
            )
            or not isinstance(
                self.mapped_vertex_count,
                int,
            )
        ):
            raise TypeError(
                "mapped_vertex_count must be an integer."
            )

        if (
            self.mapped_vertex_count < 0
            or self.mapped_vertex_count > scalar_detail.shape[0]
        ):
            raise ValueError(
                "mapped_vertex_count must be inside "
                "the canonical vertex range."
            )

        if not isinstance(
            self.connectivity_signature,
            str,
        ):
            raise TypeError(
                "connectivity_signature must be a string."
            )

        connectivity_signature = (
            self.connectivity_signature.strip()
        )

        if not connectivity_signature:
            raise ValueError(
                "connectivity_signature must not be blank."
            )

        scalar_detail = scalar_detail.copy()
        confidence = confidence.copy()

        scalar_detail.setflags(
            write=False
        )
        confidence.setflags(
            write=False
        )

        object.__setattr__(
            self,
            "canonical_scalar_detail",
            scalar_detail,
        )
        object.__setattr__(
            self,
            "canonical_confidence",
            confidence,
        )
        object.__setattr__(
            self,
            "connectivity_signature",
            connectivity_signature,
        )


class AtlasCanonicalHeadResidualDetailAmplitudeResolver:
    @classmethod
    def resolve(
        cls,
        *,
        observation: AtlasCanonicalHeadResidualDetailObservation,
        correspondence: AtlasCanonicalHeadDenseCorrespondence,
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
            AtlasCanonicalHeadDenseCorrespondence,
        ):
            raise TypeError(
                "correspondence must be an "
                "AtlasCanonicalHeadDenseCorrespondence."
            )

        compatibility = (
            AtlasCanonicalHeadResidualDetailCorrespondenceGate
            .evaluate(
                observation=observation,
                correspondence=correspondence,
            )
        )

        if not compatibility.compatible:
            raise ValueError(
                compatibility.blocked_reasons[0]
            )

        vertex_count = (
            correspondence.topology.vertex_count
        )

        canonical_scalar_detail = np.zeros(
            vertex_count,
            dtype=np.float64,
        )
        canonical_confidence = np.zeros(
            vertex_count,
            dtype=np.float64,
        )

        for (
            sample_index,
            canonical_vertex_index,
        ) in zip(
            compatibility.observed_sample_indices,
            compatibility.canonical_vertex_indices,
            strict=True,
        ):
            canonical_scalar_detail[
                canonical_vertex_index
            ] = (
                observation.scalar_detail_for_sample(
                    sample_index
                )
            )

            canonical_confidence[
                canonical_vertex_index
            ] = (
                observation.confidence_for_sample(
                    sample_index
                )
            )

        return AtlasCanonicalHeadResidualDetailAmplitudeResult(
            canonical_scalar_detail=canonical_scalar_detail,
            canonical_confidence=canonical_confidence,
            mapped_vertex_count=(
                compatibility.matched_sample_count
            ),
            connectivity_signature=(
                correspondence.connectivity_signature
            ),
        )
