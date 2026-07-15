import pytest

from CORE.atlas_ancient_theatre_cavea_profile import (
    AtlasAncientTheatreCaveaProfile,
)


def test_cavea_profile_starts_at_inner_radius():
    height = (
        AtlasAncientTheatreCaveaProfile
        .height_at_radius(
            radius=16.0,
            inner_radius=16.0,
            outer_radius=46.0,
            rise=12.0,
        )
    )

    assert height == 0.0


def test_cavea_profile_reaches_full_outer_rise():
    height = (
        AtlasAncientTheatreCaveaProfile
        .height_at_radius(
            radius=46.0,
            inner_radius=16.0,
            outer_radius=46.0,
            rise=12.0,
        )
    )

    assert height == 12.0


def test_cavea_profile_is_monotonic():
    heights = [
        (
            AtlasAncientTheatreCaveaProfile
            .height_at_radius(
                radius=radius,
                inner_radius=16.0,
                outer_radius=46.0,
                rise=12.0,
            )
        )
        for radius in (
            16.0,
            22.0,
            28.0,
            34.0,
            40.0,
            46.0,
        )
    ]

    assert heights == sorted(heights)
    assert len(set(heights)) == len(heights)


def test_cavea_profile_is_inwardly_curved():
    quarter_height = (
        AtlasAncientTheatreCaveaProfile
        .normalized_height(
            radial_ratio=0.25,
        )
    )

    half_height = (
        AtlasAncientTheatreCaveaProfile
        .normalized_height(
            radial_ratio=0.50,
        )
    )

    three_quarter_height = (
        AtlasAncientTheatreCaveaProfile
        .normalized_height(
            radial_ratio=0.75,
        )
    )

    assert quarter_height < 0.25
    assert half_height < 0.50
    assert three_quarter_height < 0.75


def test_cavea_profile_clamps_outside_radius():
    below_inner = (
        AtlasAncientTheatreCaveaProfile
        .height_at_radius(
            radius=10.0,
            inner_radius=16.0,
            outer_radius=46.0,
            rise=12.0,
        )
    )

    beyond_outer = (
        AtlasAncientTheatreCaveaProfile
        .height_at_radius(
            radius=60.0,
            inner_radius=16.0,
            outer_radius=46.0,
            rise=12.0,
        )
    )

    assert below_inner == 0.0
    assert beyond_outer == 12.0


def test_invalid_cavea_profile_dimensions_fail():
    with pytest.raises(ValueError):
        (
            AtlasAncientTheatreCaveaProfile
            .height_at_radius(
                radius=20.0,
                inner_radius=30.0,
                outer_radius=20.0,
                rise=12.0,
            )
        )
