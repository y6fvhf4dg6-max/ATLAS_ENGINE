from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from CORE.atlas_canonical_head_residual_detail_amplitude_resolver import (
    AtlasCanonicalHeadResidualDetailAmplitudeResult,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadResidualDetailAmplitudePolicyResult:
    weighted_amplitude: np.ndarray
    bounded_amplitude: np.ndarray
    maximum_absolute_amplitude: float
    mapped_vertex_count: int
    connectivity_signature: str

    def __post_init__(self) -> None:
        weighted = np.asarray(
            self.weighted_amplitude,
            dtype=np.float64,
        )
        bounded = np.asarray(
            self.bounded_amplitude,
            dtype=np.float64,
        )

        if weighted.ndim != 1:
            raise ValueError(
                "weighted_amplitude must be one-dimensional."
            )

        if bounded.shape != weighted.shape:
            raise ValueError(
                "bounded_amplitude shape must match weighted_amplitude."
            )

        if not np.isfinite(
            weighted
        ).all():
            raise ValueError(
                "weighted_amplitude must contain only finite values."
            )

        if not np.isfinite(
            bounded
        ).all():
            raise ValueError(
                "bounded_amplitude must contain only finite values."
            )

        maximum = float(
            self.maximum_absolute_amplitude
        )

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
                bounded
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
            or self.mapped_vertex_count > weighted.shape[0]
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

        weighted = weighted.copy()
        bounded = bounded.copy()

        weighted.setflags(
            write=False
        )
        bounded.setflags(
            write=False
        )

        object.__setattr__(
            self,
            "weighted_amplitude",
            weighted,
        )
        object.__setattr__(
            self,
            "bounded_amplitude",
            bounded,
        )
        object.__setattr__(
            self,
            "maximum_absolute_amplitude",
            maximum,
        )
        object.__setattr__(
            self,
            "connectivity_signature",
            connectivity_signature,
        )


class AtlasCanonicalHeadResidualDetailAmplitudePolicy:
    @classmethod
    def apply(
        cls,
        *,
        amplitude_result: AtlasCanonicalHeadResidualDetailAmplitudeResult,
        maximum_absolute_amplitude: float,
    ) -> AtlasCanonicalHeadResidualDetailAmplitudePolicyResult:
        if not isinstance(
            amplitude_result,
            AtlasCanonicalHeadResidualDetailAmplitudeResult,
        ):
            raise TypeError(
                "amplitude_result must be an "
                "AtlasCanonicalHeadResidualDetailAmplitudeResult."
            )

        try:
            maximum = float(
                maximum_absolute_amplitude
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

        weighted_amplitude = (
            amplitude_result.canonical_scalar_detail
            * amplitude_result.canonical_confidence
        )

        bounded_amplitude = np.clip(
            weighted_amplitude,
            -maximum,
            maximum,
        )

        return (
            AtlasCanonicalHeadResidualDetailAmplitudePolicyResult(
                weighted_amplitude=weighted_amplitude,
                bounded_amplitude=bounded_amplitude,
                maximum_absolute_amplitude=maximum,
                mapped_vertex_count=(
                    amplitude_result.mapped_vertex_count
                ),
                connectivity_signature=(
                    amplitude_result.connectivity_signature
                ),
            )
        )
