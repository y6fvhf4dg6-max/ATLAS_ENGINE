from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from CORE.atlas_canonical_head_residual_detail_observation import (
    AtlasCanonicalHeadResidualDetailObservation,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasCanonicalHeadResidualDetailScaleNormalizationResult:
    observation: AtlasCanonicalHeadResidualDetailObservation
    scale_factor: float
    image_reference_span_px: float
    canonical_reference_span: float

    def __post_init__(self) -> None:
        if not isinstance(
            self.observation,
            AtlasCanonicalHeadResidualDetailObservation,
        ):
            raise TypeError(
                "observation must be an "
                "AtlasCanonicalHeadResidualDetailObservation."
            )

        for field_name in (
            "scale_factor",
            "image_reference_span_px",
            "canonical_reference_span",
        ):
            value = float(
                getattr(self, field_name)
            )

            if (
                not np.isfinite(value)
                or value <= 0.0
            ):
                raise ValueError(
                    f"{field_name} must be finite "
                    "and greater than zero."
                )

            object.__setattr__(
                self,
                field_name,
                value,
            )


class AtlasCanonicalHeadResidualDetailScaleNormalizer:
    @classmethod
    def normalize(
        cls,
        *,
        observation: AtlasCanonicalHeadResidualDetailObservation,
        image_reference_span_px: float,
        canonical_reference_span: float,
    ) -> AtlasCanonicalHeadResidualDetailScaleNormalizationResult:
        if not isinstance(
            observation,
            AtlasCanonicalHeadResidualDetailObservation,
        ):
            raise TypeError(
                "observation must be an "
                "AtlasCanonicalHeadResidualDetailObservation."
            )

        image_span = cls._normalize_positive_finite(
            image_reference_span_px,
            name="image_reference_span_px",
        )
        canonical_span = cls._normalize_positive_finite(
            canonical_reference_span,
            name="canonical_reference_span",
        )

        scale_factor = (
            canonical_span
            / image_span
        )

        normalized_observation = (
            AtlasCanonicalHeadResidualDetailObservation(
                observation_id=observation.observation_id,
                source_view_id=observation.source_view_id,
                image_width=observation.image_width,
                image_height=observation.image_height,
                sample_indices=observation.sample_indices,
                sample_coordinates_normalized=(
                    observation.sample_coordinates_normalized
                ),
                scalar_detail=(
                    observation.scalar_detail
                    * scale_factor
                ),
                confidence=observation.confidence,
            )
        )

        return (
            AtlasCanonicalHeadResidualDetailScaleNormalizationResult(
                observation=normalized_observation,
                scale_factor=scale_factor,
                image_reference_span_px=image_span,
                canonical_reference_span=canonical_span,
            )
        )

    @staticmethod
    def _normalize_positive_finite(
        value: object,
        *,
        name: str,
    ) -> float:
        try:
            numeric = float(
                value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be numeric."
            ) from exc

        if (
            not np.isfinite(numeric)
            or numeric <= 0.0
        ):
            raise ValueError(
                f"{name} must be finite "
                "and greater than zero."
            )

        return numeric
