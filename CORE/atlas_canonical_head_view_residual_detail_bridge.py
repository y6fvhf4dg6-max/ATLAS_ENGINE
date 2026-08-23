from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from CORE.atlas_canonical_head_dense_correspondence import (
    AtlasCanonicalHeadDenseCorrespondence,
)
from CORE.atlas_canonical_head_residual_detail_amplitude_policy import (
    AtlasCanonicalHeadResidualDetailAmplitudePolicy,
)
from CORE.atlas_canonical_head_residual_detail_amplitude_resolver import (
    AtlasCanonicalHeadResidualDetailAmplitudeResolver,
)
from CORE.atlas_canonical_head_residual_detail_observation import (
    AtlasCanonicalHeadResidualDetailObservation,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadViewResidualDetailBridgeResult:
    observation_id: str
    source_view_id: str
    canonical_scalar_detail: np.ndarray
    canonical_confidence: np.ndarray
    weighted_amplitude: np.ndarray
    bounded_amplitude: np.ndarray
    maximum_absolute_amplitude: float
    mapped_vertex_count: int
    connectivity_signature: str

    def __post_init__(self) -> None:
        for field_name in (
            "observation_id",
            "source_view_id",
            "connectivity_signature",
        ):
            value = getattr(
                self,
                field_name,
            )

            if not isinstance(
                value,
                str,
            ):
                raise TypeError(
                    f"{field_name} must be a string."
                )

            normalized = value.strip()

            if not normalized:
                raise ValueError(
                    f"{field_name} must not be blank."
                )

            object.__setattr__(
                self,
                field_name,
                normalized,
            )

        arrays = {}

        for field_name in (
            "canonical_scalar_detail",
            "canonical_confidence",
            "weighted_amplitude",
            "bounded_amplitude",
        ):
            array = np.asarray(
                getattr(
                    self,
                    field_name,
                ),
                dtype=np.float64,
            )

            if array.ndim != 1:
                raise ValueError(
                    f"{field_name} must be one-dimensional."
                )

            if not np.isfinite(
                array
            ).all():
                raise ValueError(
                    f"{field_name} must contain only finite values."
                )

            arrays[
                field_name
            ] = array

        canonical_shape = (
            arrays[
                "canonical_scalar_detail"
            ].shape
        )

        for field_name in (
            "canonical_confidence",
            "weighted_amplitude",
            "bounded_amplitude",
        ):
            if (
                arrays[
                    field_name
                ].shape
                != canonical_shape
            ):
                raise ValueError(
                    f"{field_name} shape must match "
                    "canonical_scalar_detail."
                )

        confidence = arrays[
            "canonical_confidence"
        ]

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

        try:
            maximum = float(
                self.maximum_absolute_amplitude
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "maximum_absolute_amplitude must be numeric."
            ) from exc

        if (
            not np.isfinite(
                maximum
            )
            or maximum <= 0.0
        ):
            raise ValueError(
                "maximum_absolute_amplitude must be finite "
                "and greater than zero."
            )

        if np.any(
            np.abs(
                arrays[
                    "bounded_amplitude"
                ]
            )
            > maximum + 1e-12
        ):
            raise ValueError(
                "bounded_amplitude exceeds "
                "maximum_absolute_amplitude."
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
            or self.mapped_vertex_count
            > canonical_shape[0]
        ):
            raise ValueError(
                "mapped_vertex_count must be inside "
                "the canonical vertex range."
            )

        for (
            field_name,
            array,
        ) in arrays.items():
            snapshot = array.copy()
            snapshot.setflags(
                write=False
            )

            object.__setattr__(
                self,
                field_name,
                snapshot,
            )

        object.__setattr__(
            self,
            "maximum_absolute_amplitude",
            maximum,
        )


class AtlasCanonicalHeadViewResidualDetailBridge:
    @classmethod
    def resolve(
        cls,
        *,
        observation: AtlasCanonicalHeadResidualDetailObservation,
        correspondence: AtlasCanonicalHeadDenseCorrespondence,
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
            AtlasCanonicalHeadDenseCorrespondence,
        ):
            raise TypeError(
                "correspondence must be an "
                "AtlasCanonicalHeadDenseCorrespondence."
            )

        amplitude_result = (
            AtlasCanonicalHeadResidualDetailAmplitudeResolver
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
