from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from CORE.atlas_rock_relief_illumination_normalizer import (
    AtlasRockReliefIlluminationNormalizer,
)


@dataclass(frozen=True)
class AtlasRockReliefPreprocessingPreset:
    name: str
    illumination_sigma: float
    detail_strength: float

    def __call__(
        self,
        values: Any,
    ) -> np.ndarray:
        return (
            AtlasRockReliefIlluminationNormalizer.normalize(
                values,
                illumination_sigma=self.illumination_sigma,
                detail_strength=self.detail_strength,
            )
        )


DALYAN_ROCK_TOMBS_ILLUMINATION_PRESET = (
    AtlasRockReliefPreprocessingPreset(
        name="dalyan-rock-tombs-illumination",
        illumination_sigma=14.0,
        detail_strength=0.80,
    )
)
