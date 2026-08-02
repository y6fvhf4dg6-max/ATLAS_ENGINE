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
        "outer_polygon_tower",
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


def test_outer_polygon_tower_is_wider_and_polygonal():
    profile = _profile()

    front = profile.tower(
        "outer_polygon_tower"
    )

    assert front.body_shape == "polygon"
    assert front.polygon_sides >= 6
    assert front.lateral_ratio >= 0.20
    assert front.longitudinal_ratio >= 0.14


def test_outer_polygon_tower_uses_polygon_spire():
    profile = _profile()

    front = profile.tower(
        "outer_polygon_tower"
    )

    assert front.roof_shape == "polygon_spire"
    assert front.roof_sides == front.polygon_sides
    assert front.roof_top_ratio > front.body_top_ratio


def test_crossing_tower_is_taller_than_outer_polygon_tower():
    profile = _profile()

    crossing = profile.tower(
        "crossing_tower"
    )
    front = profile.tower(
        "outer_polygon_tower"
    )

    assert crossing.body_top_ratio > front.body_top_ratio
    assert crossing.roof_top_ratio > front.roof_top_ratio


def test_crossing_and_outer_towers_have_distinct_placement():
    profile = _profile()

    crossing = profile.tower(
        "crossing_tower"
    )
    front = profile.tower(
        "outer_polygon_tower"
    )

    assert crossing.center_lateral_ratio == 0.0
    assert abs(front.center_lateral_ratio) >= 0.28
    assert (
        front.center_longitudinal_ratio
        > crossing.center_longitudinal_ratio
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


def test_bonner_muenster_crossing_tower_has_broad_body_and_compact_spire():
    profile = _profile()

    crossing = profile.tower(
        "crossing_tower"
    )

    assert crossing.lateral_ratio >= 0.40
    assert crossing.longitudinal_ratio >= 0.26

    assert (
        crossing.roof_top_ratio
        - crossing.body_top_ratio
    ) <= 0.14


def test_bonner_muenster_outer_polygon_tower_is_broad_with_compact_roof():
    profile = _profile()

    front = profile.tower(
        "outer_polygon_tower"
    )

    assert front.lateral_ratio >= 0.28
    assert front.longitudinal_ratio >= 0.18

    assert (
        front.roof_top_ratio
        - front.body_top_ratio
    ) <= 0.12


def test_crossing_tower_remains_wider_than_outer_polygon_tower():
    profile = _profile()

    crossing = profile.tower(
        "crossing_tower"
    )
    front = profile.tower(
        "outer_polygon_tower"
    )

    assert crossing.lateral_ratio > front.lateral_ratio
    assert (
        crossing.longitudinal_ratio
        > front.longitudinal_ratio
    )


def test_bonner_muenster_has_no_centered_front_polygon_tower():
    profile = _profile()

    tower_types = tuple(
        tower.tower_type
        for tower in profile.towers
    )

    assert "front_polygon_tower" not in tower_types


def test_bonner_muenster_uses_offset_outer_polygon_tower():
    profile = _profile()

    outer = profile.tower(
        "outer_polygon_tower"
    )

    assert outer.body_shape == "polygon"
    assert outer.polygon_sides == 8
    assert outer.roof_shape == "polygon_spire"
    assert outer.roof_sides == 8

    assert abs(
        outer.center_lateral_ratio
    ) >= 0.28

    assert outer.center_longitudinal_ratio > 0.0


def test_outer_polygon_tower_is_not_on_crossing_tower_axis():
    profile = _profile()

    crossing = profile.tower(
        "crossing_tower"
    )
    outer = profile.tower(
        "outer_polygon_tower"
    )

    assert crossing.center_lateral_ratio == 0.0
    assert (
        outer.center_lateral_ratio
        != crossing.center_lateral_ratio
    )


def test_outer_polygon_tower_has_broad_body_and_compact_multifaceted_roof():
    profile = _profile()

    outer = profile.tower(
        "outer_polygon_tower"
    )

    assert outer.lateral_ratio >= 0.20
    assert outer.longitudinal_ratio >= 0.14

    assert (
        outer.roof_top_ratio
        - outer.body_top_ratio
    ) <= 0.12


def test_bonner_outer_tower_is_positioned_toward_eastern_outer_edge():
    profile = _profile()

    outer = profile.tower(
        "outer_polygon_tower"
    )

    assert outer.center_longitudinal_ratio >= 0.30
    assert abs(outer.center_lateral_ratio) >= 0.40


def test_bonner_outer_tower_is_shorter_than_west_towers():
    profile = _profile()

    outer = profile.tower(
        "outer_polygon_tower"
    )
    west = profile.tower(
        "west_tower_right"
    )

    assert outer.body_top_ratio < west.body_top_ratio
    assert outer.roof_top_ratio < west.roof_top_ratio

    assert outer.body_top_ratio == pytest.approx(0.4464)
    assert outer.roof_top_ratio == pytest.approx(0.5208)


def test_bonner_outer_tower_has_broad_octagonal_silhouette():
    profile = _profile()

    outer = profile.tower(
        "outer_polygon_tower"
    )

    assert outer.polygon_sides == 8
    assert outer.roof_sides == 8
    assert outer.lateral_ratio >= 0.32
    assert outer.longitudinal_ratio >= 0.20


def test_cathedral_crossing_tower_is_centered_on_nave_transept_intersection():
    profile = _profile()

    crossing = profile.tower(
        "crossing_tower"
    )

    assert crossing.center_longitudinal_ratio == 0.0
    assert crossing.center_lateral_ratio == 0.0
