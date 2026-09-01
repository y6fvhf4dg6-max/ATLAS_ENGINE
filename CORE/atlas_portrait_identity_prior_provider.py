from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass(frozen=True)
class AtlasPortraitIdentityPriorResult:
    """
    Vendor-independent identity prior result.

    The provider is responsible for producing an identity-space prior.
    ATLAS owns this contract; no third-party implementation details are
    assumed here.
    """

    identity_vector: np.ndarray
    confidence: float
    provider_name: str
    provider_version: str
    commercial_use_cleared: bool

    def __post_init__(self) -> None:
        vector = np.asarray(self.identity_vector, dtype=np.float64)

        if vector.ndim != 1:
            raise ValueError("identity_vector must be one-dimensional.")

        if vector.size == 0:
            raise ValueError("identity_vector must not be empty.")

        if not np.all(np.isfinite(vector)):
            raise ValueError(
                "identity_vector must contain only finite values."
            )

        if not (0.0 <= float(self.confidence) <= 1.0):
            raise ValueError("confidence must be within [0, 1].")

        if not self.provider_name.strip():
            raise ValueError("provider_name must not be empty.")

        if not self.provider_version.strip():
            raise ValueError("provider_version must not be empty.")

        vector = vector.copy()
        vector.setflags(write=False)

        object.__setattr__(self, "identity_vector", vector)


class AtlasPortraitIdentityPriorProvider(Protocol):
    """
    Production boundary for identity-prior producers.

    Implementations may use ATLAS-native algorithms or externally sourced
    components only after their code, model weights, data terms, and
    commercial-use conditions have been independently cleared.
    """

    @property
    def provider_name(self) -> str:
        ...

    @property
    def provider_version(self) -> str:
        ...

    @property
    def commercial_use_cleared(self) -> bool:
        ...

    def estimate_identity_prior(
        self,
        *,
        observations: object,
    ) -> AtlasPortraitIdentityPriorResult:
        ...


def require_commercially_cleared_prior(
    result: AtlasPortraitIdentityPriorResult,
) -> AtlasPortraitIdentityPriorResult:
    """
    Production gate: non-cleared priors cannot enter the fitting pipeline.
    """

    if not result.commercial_use_cleared:
        raise PermissionError(
            "Identity prior is not cleared for commercial production use."
        )

    return result
