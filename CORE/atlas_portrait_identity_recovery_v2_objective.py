from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np

from CORE.atlas_portrait_identity_recovery_v2_spec import (
    AtlasPortraitIdentityRecoveryV2Spec,
)


@dataclass(frozen=True)
class AtlasPortraitIdentityRecoveryV2ObjectiveResult:
    residual_vector: np.ndarray
    weighted_channel_sse: Mapping[str, float]
    channel_sizes: Mapping[str, int]

    @property
    def total_sse(self) -> float:
        return float(np.dot(self.residual_vector, self.residual_vector))

    @property
    def residual_count(self) -> int:
        return int(self.residual_vector.size)


class AtlasPortraitIdentityRecoveryV2Objective:
    """
    Deterministic residual composer for Identity Recovery V2.

    Evidence producers supply unweighted residual arrays.
    This layer applies sqrt(channel_weight) and concatenates them into
    one least-squares residual vector.
    """

    CHANNEL_ORDER = (
        "static_landmarks",
        "dense_landmarks",
        "face_oval",
        "silhouette",
        "photometric",
        "surface_normals",
        "identity_prior",
    )

    @classmethod
    def compose(
        cls,
        *,
        spec: AtlasPortraitIdentityRecoveryV2Spec,
        residuals_by_channel: Mapping[str, np.ndarray],
    ) -> AtlasPortraitIdentityRecoveryV2ObjectiveResult:
        if not isinstance(spec, AtlasPortraitIdentityRecoveryV2Spec):
            raise TypeError(
                "spec must be an AtlasPortraitIdentityRecoveryV2Spec instance."
            )

        known = set(cls.CHANNEL_ORDER)
        supplied = set(residuals_by_channel)
        enabled = set(spec.enabled_channels)

        unknown = supplied - known
        if unknown:
            raise ValueError(
                "unknown residual channels: " + ", ".join(sorted(unknown))
            )

        missing = [
            channel
            for channel in cls.CHANNEL_ORDER
            if channel in enabled and channel not in supplied
        ]
        if missing:
            raise ValueError(
                "missing enabled residual channels: " + ", ".join(missing)
            )

        disabled_supplied = [
            channel
            for channel in cls.CHANNEL_ORDER
            if channel not in enabled and channel in supplied
        ]
        if disabled_supplied:
            raise ValueError(
                "residuals supplied for disabled channels: "
                + ", ".join(disabled_supplied)
            )

        weighted_blocks = []
        weighted_channel_sse = {}
        channel_sizes = {}

        for channel in cls.CHANNEL_ORDER:
            if channel not in enabled:
                continue

            residual = np.asarray(
                residuals_by_channel[channel],
                dtype=np.float64,
            )

            if residual.size == 0:
                raise ValueError(
                    f"{channel} residual must not be empty."
                )

            if not np.all(np.isfinite(residual)):
                raise ValueError(
                    f"{channel} residual must contain only finite values."
                )

            flat = residual.reshape(-1)
            weight = float(spec.weights[channel])
            weighted = np.sqrt(weight) * flat

            weighted_blocks.append(weighted)
            channel_sizes[channel] = int(flat.size)
            weighted_channel_sse[channel] = float(
                np.dot(weighted, weighted)
            )

        if not weighted_blocks:
            raise ValueError(
                "Identity Recovery V2 objective requires at least one "
                "enabled residual channel."
            )

        residual_vector = np.concatenate(weighted_blocks).astype(
            np.float64,
            copy=False,
        )
        residual_vector.setflags(write=False)

        return AtlasPortraitIdentityRecoveryV2ObjectiveResult(
            residual_vector=residual_vector,
            weighted_channel_sse=weighted_channel_sse,
            channel_sizes=channel_sizes,
        )
