import pytest

from CORE.atlas_church_tower_profile_system import (
    AtlasChurchTowerProfileSystem,
)


def _profile():
    return AtlasChurchTowerProfileSystem.resolve(
        longitudinal_span=60.0,
        lateral_span=30.0,
        building_height=42.0,
        landmark_class="cathedral",
    )


def test_cathedral_tower_system_defines_crossing_and_front_polygon_towers():
    profile = _profile()

    assert tuple(
        tower.tower_type
        for tower in profile.towers
    ) == (
        "crossing_tower",
        "front_polygon_tower",
        "west_tower_left",
        "west_tower_right",
    )


def test_crossing_tower_is_wider_than_old_generic_tower_ratio():
    profile = _profile()

    crossing = profile.tower(
        "crossing_tower"
    )

    assert crossing.body_shape == "polygon"
    assert crossing.polygon_sides == 8
    assert crossing.lateral_ratio >= 0.28
    assert crossing.longitudinal_ratio >= 0.18


def test_front_polygon_tower_is_wider_and_polygonal():
    profile = _profile()

    front = profile.tower(
        "front_polygon_tower"
    )

    assert front.body_shape == "polygon"
    assert front.polygon_sides >= 6
    assert front.lateral_ratio >= 0.20
    assert front.longitudinal_ratio >= 0.14


def test_front_polygon_tower_uses_polygon_spire():
    profile = _profile()

    front = profile.tower(
        "front_polygon_tower"
    )

    assert front.roof_shape == "polygon_spire"
    assert front.roof_sides == front.polygon_sides
    assert front.roof_top_ratio > front.body_top_ratio


def test_crossing_tower_is_taller_than_front_polygon_tower():
    profile = _profile()

    crossing = profile.tower(
        "crossing_tower"
    )
    front = profile.tower(
        "front_polygon_tower"
    )

    assert crossing.body_top_ratio > front.body_top_ratio
    assert crossing.roof_top_ratio > front.roof_top_ratio


def test_crossing_and_front_towers_are_centered_on_longitudinal_axis():
    profile = _profile()

    crossing = profile.tower(
        "crossing_tower"
    )
    front = profile.tower(
        "front_polygon_tower"
    )

    assert crossing.center_lateral_ratio == 0.0
    assert front.center_lateral_ratio == 0.0
    assert (
        front.center_longitudinal_ratio
        < crossing.center_longitudinal_ratio
    )


@pytest.mark.parametrize(
    "longitudinal_span,lateral_span,building_height",
    [
        (0.0, 30.0, 42.0),
        (60.0, 0.0, 42.0),
        (60.0, 30.0, 0.0),
        (-1.0, 30.0, 42.0),
        (60.0, -1.0, 42.0),
        (60.0, 30.0, -1.0),
    ],
)
def test_rejects_non_positive_dimensions(
    longitudinal_span,
    lateral_span,
    building_height,
):
    with pytest.raises(ValueError):
        AtlasChurchTowerProfileSystem.resolve(
            longitudinal_span=longitudinal_span,
            lateral_span=lateral_span,
            building_height=building_height,
            landmark_class="cathedral",
        )
