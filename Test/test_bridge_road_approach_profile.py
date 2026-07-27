import pytest

from CORE.atlas_bridge_road_approach_profile import (
    AtlasBridgeRoadApproachProfile,
)


def test_approach_profile_descends_from_bridge_to_road():
    profile = AtlasBridgeRoadApproachProfile(
        bridge_top_z=1.60,
        road_top_z=0.80,
        length_mm=3.00,
    )

    assert profile.top_z_at(0.0) == pytest.approx(1.60)
    assert profile.top_z_at(1.0) == pytest.approx(0.80)
    assert profile.top_z_at(0.5) == pytest.approx(1.20)


def test_approach_profile_clamps_normalized_position():
    profile = AtlasBridgeRoadApproachProfile(
        bridge_top_z=1.60,
        road_top_z=0.80,
        length_mm=3.00,
    )

    assert profile.top_z_at(-1.0) == pytest.approx(1.60)
    assert profile.top_z_at(2.0) == pytest.approx(0.80)


def test_approach_profile_preserves_deck_thickness():
    profile = AtlasBridgeRoadApproachProfile(
        bridge_top_z=1.60,
        road_top_z=0.80,
        length_mm=3.00,
        deck_thickness_mm=0.80,
    )

    assert profile.bottom_z_at(0.0) == pytest.approx(0.80)
    assert profile.bottom_z_at(1.0) == pytest.approx(0.00)
    assert (
        profile.top_z_at(0.35)
        - profile.bottom_z_at(0.35)
    ) == pytest.approx(0.80)


@pytest.mark.parametrize(
    "kwargs",
    (
        {
            "bridge_top_z": 1.60,
            "road_top_z": 0.80,
            "length_mm": 0.0,
        },
        {
            "bridge_top_z": 1.60,
            "road_top_z": 0.80,
            "length_mm": -1.0,
        },
        {
            "bridge_top_z": 1.60,
            "road_top_z": 0.80,
            "length_mm": 3.0,
            "deck_thickness_mm": 0.0,
        },
    ),
)
def test_approach_profile_rejects_invalid_dimensions(kwargs):
    with pytest.raises(ValueError):
        AtlasBridgeRoadApproachProfile(**kwargs)
