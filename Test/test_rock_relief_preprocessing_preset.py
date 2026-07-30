import numpy as np
import pytest

from CORE.atlas_rock_relief_illumination_normalizer import (
    AtlasRockReliefIlluminationNormalizer,
)
from CORE.atlas_rock_relief_preprocessing_preset import (
    AtlasRockReliefPreprocessingPreset,
    DALYAN_ROCK_TOMBS_ILLUMINATION_PRESET,
)


def test_dalyan_preset_has_locked_parameters():
    preset = DALYAN_ROCK_TOMBS_ILLUMINATION_PRESET

    assert isinstance(
        preset,
        AtlasRockReliefPreprocessingPreset,
    )
    assert preset.name == "dalyan-rock-tombs-illumination"
    assert preset.illumination_sigma == 14.0
    assert preset.detail_strength == 0.80


def test_dalyan_preset_is_callable_and_matches_normalizer():
    source = np.tile(
        np.linspace(
            0.15,
            0.90,
            64,
            dtype=np.float64,
        ),
        (32, 1),
    )
    source[:, 30:34] += 0.08

    result = DALYAN_ROCK_TOMBS_ILLUMINATION_PRESET(
        source
    )

    expected = (
        AtlasRockReliefIlluminationNormalizer.normalize(
            source,
            illumination_sigma=14.0,
            detail_strength=0.80,
        )
    )

    assert result.shape == source.shape
    assert result.dtype == np.float64
    assert np.allclose(result, expected)


def test_rock_relief_preprocessing_preset_is_immutable():
    preset = DALYAN_ROCK_TOMBS_ILLUMINATION_PRESET

    with pytest.raises(
        (AttributeError, TypeError),
    ):
        preset.detail_strength = 0.50
