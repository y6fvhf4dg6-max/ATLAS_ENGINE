from __future__ import annotations

from CORE.atlas_canonical_head_residual_detail_amplitude_policy import (
    AtlasCanonicalHeadResidualDetailAmplitudePolicy,
)
from CORE.atlas_canonical_head_residual_detail_observation import (
    AtlasCanonicalHeadResidualDetailObservation,
)
from CORE.atlas_canonical_head_surface_correspondence import (
    AtlasCanonicalHeadSurfaceCorrespondence,
)
from CORE.atlas_canonical_head_surface_residual_detail_amplitude_resolver import (
    AtlasCanonicalHeadSurfaceResidualDetailAmplitudeResolver,
)
from CORE.atlas_canonical_head_view_residual_detail_bridge import (
    AtlasCanonicalHeadViewResidualDetailBridgeResult,
)


class AtlasCanonicalHeadSurfaceViewResidualDetailBridge:
    @classmethod
    def resolve(
        cls,
        *,
        observation: AtlasCanonicalHeadResidualDetailObservation,
        correspondence: AtlasCanonicalHeadSurfaceCorrespondence,
        maximum_absolute_amplitude: float,
    ) -> AtlasCanonicalHeadViewResidualDetailBridgeResult:
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

        amplitude_result = (
            AtlasCanonicalHeadSurfaceResidualDetailAmplitudeResolver
            .resolve(
                observation=observation,
                correspondence=correspondence,
            )
        )

        policy_result = (
            AtlasCanonicalHeadResidualDetailAmplitudePolicy
            .apply(
                amplitude_result=amplitude_result,
                maximum_absolute_amplitude=(
                    maximum_absolute_amplitude
                ),
            )
        )

        return AtlasCanonicalHeadViewResidualDetailBridgeResult(
            observation_id=observation.observation_id,
            source_view_id=observation.source_view_id,
            canonical_scalar_detail=(
                amplitude_result.canonical_scalar_detail
            ),
            canonical_confidence=(
                amplitude_result.canonical_confidence
            ),
            weighted_amplitude=(
                policy_result.weighted_amplitude
            ),
            bounded_amplitude=(
                policy_result.bounded_amplitude
            ),
            maximum_absolute_amplitude=(
                policy_result.maximum_absolute_amplitude
            ),
            mapped_vertex_count=(
                policy_result.mapped_vertex_count
            ),
            connectivity_signature=(
                policy_result.connectivity_signature
            ),
        )
