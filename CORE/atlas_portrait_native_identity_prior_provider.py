from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from CORE.atlas_portrait_identity_prior_provider import (
    AtlasPortraitIdentityPriorResult,
)


@dataclass(frozen=True)
class AtlasPortraitNativeIdentityPriorProvider:
    """
    ATLAS-owned identity-space regularization prior.

    This is intentionally NOT a learned subject-specific identity model.
    It provides a deterministic zero-centered prior in the configured
    identity coefficient space, suitable for regularizing optimization.

    No third-party code, pretrained network, or external model weights
    are used by this provider.
    """

    identity_dimension: int
    confidence: float = 1.0

    @property
    def provider_name(self) -> str:
        return "atlas_native_zero_centered_identity_prior"

    @property
    def provider_version(self) -> str:
        return "1"

    @property
    def commercial_use_cleared(self) -> bool:
        return True

    def __post_init__(self) -> None:
        if not isinstance(self.identity_dimension, int):
            raise TypeError("identity_dimension must be an integer.")

        if self.identity_dimension <= 0:
            raise ValueError("identity_dimension must be positive.")

        if not (0.0 <= float(self.confidence) <= 1.0):
            raise ValueError("confidence must be within [0, 1].")

    def estimate_identity_prior(
        self,
        *,
        observations: object = None,
    ) -> AtlasPortraitIdentityPriorResult:
        # observations are deliberately unused:
        # this provider is a population-space regularizer, not a
        # subject-specific learned estimator.
        vector = np.zeros(
            self.identity_dimension,
            dtype=np.float64,
        )

        return AtlasPortraitIdentityPriorResult(
            identity_vector=vector,
            confidence=float(self.confidence),
            provider_name=self.provider_name,
            provider_version=self.provider_version,
            commercial_use_cleared=self.commercial_use_cleared,
        )

    def residual(
        self,
        *,
        identity_vector: np.ndarray,
    ) -> np.ndarray:
        """
        Return the unweighted identity-prior residual.

        Objective weighting remains the responsibility of
        Identity Recovery V2 objective composition.
        """

        identity = np.asarray(
            identity_vector,
            dtype=np.float64,
        )

        if identity.ndim != 1:
            raise ValueError(
                "identity_vector must be one-dimensional."
            )

        if identity.size != self.identity_dimension:
            raise ValueError(
                "identity_vector dimension does not match "
                "identity_dimension."
            )

        if not np.all(np.isfinite(identity)):
            raise ValueError(
                "identity_vector must contain only finite values."
            )

        prior = self.estimate_identity_prior()

        residual = identity - prior.identity_vector
        residual = residual.astype(np.float64, copy=False)
        residual.setflags(write=False)
        return residual
