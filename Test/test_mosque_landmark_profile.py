from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_mosque_landmark_profile import (
    AtlasMosqueLandmarkProfile,
)


def test_default_profile_defines_single_dome_single_minaret():
    profile = AtlasMosqueLandmarkProfile()

    assert profile.grammar_name == (
        "single_dome_single_minaret"
    )
    assert profile.dome_count == 1
    assert profile.minaret_count == 1
    assert profile.has_dome_drum is True
    assert profile.has_balcony is True
    assert profile.uses_real_footprint is True


def test_profile_carries_physical_output_context():
    profile = AtlasMosqueLandmarkProfile(
        scale_ratio=3000.0,
        nozzle_diameter_mm=0.4,
    )

    assert profile.scale_ratio == pytest.approx(
        3000.0
    )
    assert profile.nozzle_diameter_mm == pytest.approx(
        0.4
    )


def test_profile_normalizes_grammar_name():
    profile = AtlasMosqueLandmarkProfile(
        grammar_name=(
            " SINGLE_DOME_SINGLE_MINARET "
        ),
    )

    assert profile.grammar_name == (
        "single_dome_single_minaret"
    )


@pytest.mark.parametrize(
    "grammar_name",
    [
        "",
        "footprint_fallback",
        "basilica_hall",
    ],
)
def test_profile_rejects_unsupported_grammar(
    grammar_name,
):
    with pytest.raises(
        ValueError,
        match="single_dome_single_minaret",
    ):
        AtlasMosqueLandmarkProfile(
            grammar_name=grammar_name,
        )


@pytest.mark.parametrize(
    "dome_count,minaret_count",
    [
        (0, 1),
        (2, 1),
        (1, 0),
        (1, 2),
        (True, 1),
        (1, False),
    ],
)
def test_profile_requires_one_dome_and_one_minaret(
    dome_count,
    minaret_count,
):
    with pytest.raises(ValueError):
        AtlasMosqueLandmarkProfile(
            dome_count=dome_count,
            minaret_count=minaret_count,
        )


@pytest.mark.parametrize(
    "scale_ratio,nozzle_diameter_mm",
    [
        (0.0, 0.4),
        (-3000.0, 0.4),
        (3000.0, 0.0),
        (3000.0, -0.4),
    ],
)
def test_profile_rejects_invalid_physical_context(
    scale_ratio,
    nozzle_diameter_mm,
):
    with pytest.raises(ValueError):
        AtlasMosqueLandmarkProfile(
            scale_ratio=scale_ratio,
            nozzle_diameter_mm=nozzle_diameter_mm,
        )


def test_profile_is_immutable():
    profile = AtlasMosqueLandmarkProfile()

    with pytest.raises(FrozenInstanceError):
        profile.minaret_count = 2

def test_profile_supports_multi_dome_multi_minaret_grammar():
    profile = AtlasMosqueLandmarkProfile(
        grammar_name="multi_dome_multi_minaret",
        dome_count=3,
        minaret_count=2,
    )

    assert profile.grammar_name == (
        "multi_dome_multi_minaret"
    )
    assert profile.dome_count == 3
    assert profile.minaret_count == 2


@pytest.mark.parametrize(
    "dome_count,minaret_count",
    [
        (1, 2),
        (2, 1),
        (0, 2),
        (2, 0),
        (9, 2),
        (2, 9),
        (True, 2),
        (2, False),
    ],
)
def test_multi_grammar_requires_bounded_multiple_components(
    dome_count,
    minaret_count,
):
    with pytest.raises(ValueError):
        AtlasMosqueLandmarkProfile(
            grammar_name=(
                "multi_dome_multi_minaret"
            ),
            dome_count=dome_count,
            minaret_count=minaret_count,
        )


@pytest.mark.parametrize(
    "dome_count,minaret_count",
    [
        (2, 1),
        (1, 2),
        (2, 2),
    ],
)
def test_single_grammar_still_requires_exactly_one_component(
    dome_count,
    minaret_count,
):
    with pytest.raises(ValueError):
        AtlasMosqueLandmarkProfile(
            grammar_name=(
                "single_dome_single_minaret"
            ),
            dome_count=dome_count,
            minaret_count=minaret_count,
        )
