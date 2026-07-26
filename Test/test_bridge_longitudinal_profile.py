import pytest

from CORE.atlas_bridge_longitudinal_profile import (
    AtlasBridgeLongitudinalProfile,
)


def test_bridge_profile_keeps_center_at_full_height():
    profile = AtlasBridgeLongitudinalProfile(
        shore_top_m=6.0,
        center_top_m=8.0,
        approach_ratio=0.20,
    )

    assert profile.top_z_at(0.50) == pytest.approx(8.0)


def test_bridge_profile_meets_shore_height_at_both_ends():
    profile = AtlasBridgeLongitudinalProfile(
        shore_top_m=6.0,
        center_top_m=8.0,
        approach_ratio=0.20,
    )

    assert profile.top_z_at(0.0) == pytest.approx(6.0)
    assert profile.top_z_at(1.0) == pytest.approx(6.0)


def test_bridge_profile_reaches_full_height_after_approach():
    profile = AtlasBridgeLongitudinalProfile(
        shore_top_m=6.0,
        center_top_m=8.0,
        approach_ratio=0.20,
    )

    assert profile.top_z_at(0.20) == pytest.approx(8.0)
    assert profile.top_z_at(0.80) == pytest.approx(8.0)


def test_bridge_profile_rises_smoothly_inside_approach():
    profile = AtlasBridgeLongitudinalProfile(
        shore_top_m=6.0,
        center_top_m=8.0,
        approach_ratio=0.20,
    )

    first_quarter = profile.top_z_at(0.05)
    midpoint = profile.top_z_at(0.10)
    last_quarter = profile.top_z_at(0.15)

    assert 6.0 < first_quarter < midpoint
    assert midpoint == pytest.approx(7.0)
    assert midpoint < last_quarter < 8.0


def test_bridge_profile_is_symmetric():
    profile = AtlasBridgeLongitudinalProfile(
        shore_top_m=6.0,
        center_top_m=8.0,
        approach_ratio=0.20,
    )

    for position in (0.0, 0.05, 0.10, 0.15, 0.20, 0.35, 0.50):
        assert profile.top_z_at(position) == pytest.approx(
            profile.top_z_at(1.0 - position)
        )


def test_bridge_profile_bottom_preserves_deck_thickness():
    profile = AtlasBridgeLongitudinalProfile(
        shore_top_m=6.0,
        center_top_m=8.0,
        approach_ratio=0.20,
        deck_thickness_m=1.0,
    )

    assert profile.bottom_z_at(0.0) == pytest.approx(5.0)
    assert profile.bottom_z_at(0.10) == pytest.approx(6.0)
    assert profile.bottom_z_at(0.50) == pytest.approx(7.0)


@pytest.mark.parametrize(
    "position",
    (-0.01, 1.01),
)
def test_bridge_profile_rejects_positions_outside_unit_interval(position):
    profile = AtlasBridgeLongitudinalProfile(
        shore_top_m=6.0,
        center_top_m=8.0,
        approach_ratio=0.20,
    )

    with pytest.raises(ValueError):
        profile.top_z_at(position)


@pytest.mark.parametrize(
    "approach_ratio",
    (0.0, -0.1, 0.5, 0.6),
)
def test_bridge_profile_rejects_invalid_approach_ratios(approach_ratio):
    with pytest.raises(ValueError):
        AtlasBridgeLongitudinalProfile(
            shore_top_m=6.0,
            center_top_m=8.0,
            approach_ratio=approach_ratio,
        )
