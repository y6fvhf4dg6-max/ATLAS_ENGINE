from collections import Counter

import math

import pytest

from CORE.atlas_church_footprint_resolver import (
    AtlasChurchFootprintResolver,
)
from CORE.atlas_church_tower_mesher import (
    AtlasChurchTowerMesher,
)
from CORE.atlas_church_tower_profile_system import (
    AtlasChurchTowerProfileSystem,
)


def _frame():
    return AtlasChurchFootprintResolver.resolve(
        (
            (0.0, 0.0),
            (30.0, 0.0),
            (30.0, 60.0),
            (0.0, 60.0),
        )
    )


def _profile():
    return AtlasChurchTowerProfileSystem.resolve(
        longitudinal_span=60.0,
        lateral_span=30.0,
        building_height=42.0,
        landmark_class="cathedral",
    )


def _topology(triangles):
    counts = Counter()

    def point_key(point):
        return tuple(
            round(float(value), 8)
            for value in point
        )

    for first, second, third in triangles:
        for point_a, point_b in (
            (first, second),
            (second, third),
            (third, first),
        ):
            edge = tuple(
                sorted(
                    (
                        point_key(point_a),
                        point_key(point_b),
                    )
                )
            )
            counts[edge] += 1

    return {
        "open_edges": sum(
            count == 1
            for count in counts.values()
        ),
        "non_manifold_edges": sum(
            count > 2
            for count in counts.values()
        ),
    }


def test_tower_mesher_builds_all_profile_towers():
    mesh = AtlasChurchTowerMesher.build(
        frame=_frame(),
        profile=_profile(),
        building_height=42.0,
    )

    assert mesh["type"] == "church_tower_system"

    assert tuple(
        tower["tower_type"]
        for tower in mesh["towers"]
    ) == (
        "crossing_tower",
        "outer_polygon_tower",
        "west_tower_left",
        "west_tower_right",
    )


def test_crossing_tower_has_octagonal_body_and_roof():
    mesh = AtlasChurchTowerMesher.build(
        frame=_frame(),
        profile=_profile(),
        building_height=42.0,
    )

    crossing = next(
        tower
        for tower in mesh["towers"]
        if tower["tower_type"] == "crossing_tower"
    )

    assert crossing["body_shape"] == "polygon"
    assert len(crossing["body_bottom_ring"]) == 8
    assert len(crossing["body_top_ring"]) == 8
    assert len(crossing["roof_base_ring"]) == 8
    assert crossing["roof_shape"] == "polygon_spire"


def test_outer_polygon_tower_is_wider_than_generic_west_tower():
    mesh = AtlasChurchTowerMesher.build(
        frame=_frame(),
        profile=_profile(),
        building_height=42.0,
    )

    front = next(
        tower
        for tower in mesh["towers"]
        if tower["tower_type"]
        == "outer_polygon_tower"
    )
    west = next(
        tower
        for tower in mesh["towers"]
        if tower["tower_type"]
        == "west_tower_left"
    )

    assert front["lateral_span"] > west["lateral_span"]
    assert front["roof_shape"] == "polygon_spire"
    assert len(front["roof_base_ring"]) >= 6


def test_crossing_tower_is_wider_than_outer_polygon_tower():
    mesh = AtlasChurchTowerMesher.build(
        frame=_frame(),
        profile=_profile(),
        building_height=42.0,
    )

    crossing = next(
        tower
        for tower in mesh["towers"]
        if tower["tower_type"] == "crossing_tower"
    )
    front = next(
        tower
        for tower in mesh["towers"]
        if tower["tower_type"]
        == "outer_polygon_tower"
    )

    assert crossing["lateral_span"] > front["lateral_span"]
    assert (
        crossing["longitudinal_span"]
        > front["longitudinal_span"]
    )


def test_each_tower_is_closed_and_manifold():
    mesh = AtlasChurchTowerMesher.build(
        frame=_frame(),
        profile=_profile(),
        building_height=42.0,
    )

    for tower in mesh["towers"]:
        topology = _topology(
            tower["triangles"]
        )

        assert topology["open_edges"] == 0
        assert topology["non_manifold_edges"] == 0


def test_crossing_tower_uses_two_stage_octagonal_roof_transition():
    mesh = AtlasChurchTowerMesher.build(
        frame=_frame(),
        profile=_profile(),
        building_height=42.0,
    )

    crossing = next(
        tower
        for tower in mesh["towers"]
        if tower["tower_type"] == "crossing_tower"
    )

    assert crossing["roof_transition_type"] == (
        "two_stage_octagonal_taper"
    )

    assert len(
        crossing["roof_transition_lower_ring"]
    ) == 8
    assert len(
        crossing["roof_transition_upper_ring"]
    ) == 8


def test_crossing_tower_transition_narrows_above_preserved_body_top():
    mesh = AtlasChurchTowerMesher.build(
        frame=_frame(),
        profile=_profile(),
        building_height=42.0,
    )

    crossing = next(
        tower
        for tower in mesh["towers"]
        if tower["tower_type"] == "crossing_tower"
    )

    body_ring = crossing["body_top_ring"]
    lower_ring = crossing[
        "roof_transition_lower_ring"
    ]
    upper_ring = crossing[
        "roof_transition_upper_ring"
    ]

    def span(ring):
        xs = [point[0] for point in ring]
        ys = [point[1] for point in ring]
        return (
            max(xs) - min(xs),
            max(ys) - min(ys),
        )

    body_x, body_y = span(body_ring)
    lower_x, lower_y = span(lower_ring)
    upper_x, upper_y = span(upper_ring)

    assert lower_x == pytest.approx(
        body_x,
        abs=1e-8,
    )
    assert lower_y == pytest.approx(
        body_y,
        abs=1e-8,
    )

    assert upper_x < lower_x
    assert upper_y < lower_y


def test_crossing_tower_spire_starts_from_narrow_upper_transition_ring():
    mesh = AtlasChurchTowerMesher.build(
        frame=_frame(),
        profile=_profile(),
        building_height=42.0,
    )

    crossing = next(
        tower
        for tower in mesh["towers"]
        if tower["tower_type"] == "crossing_tower"
    )

    assert crossing["roof_base_ring"] == (
        crossing["roof_transition_upper_ring"]
    )

    assert (
        crossing["roof_transition_upper_z"]
        > crossing["body_top_z"]
    )
    assert (
        crossing["roof_top_z"]
        > crossing["roof_transition_upper_z"]
    )


def test_crossing_tower_two_stage_roof_remains_closed_and_manifold():
    mesh = AtlasChurchTowerMesher.build(
        frame=_frame(),
        profile=_profile(),
        building_height=42.0,
    )

    crossing = next(
        tower
        for tower in mesh["towers"]
        if tower["tower_type"] == "crossing_tower"
    )

    topology = _topology(
        crossing["triangles"]
    )

    assert topology["open_edges"] == 0
    assert topology["non_manifold_edges"] == 0


def test_crossing_tower_spire_height_is_derived_from_upper_ring_span():
    mesh = AtlasChurchTowerMesher.build(
        frame=_frame(),
        profile=_profile(),
        building_height=42.0,
    )

    crossing = next(
        tower
        for tower in mesh["towers"]
        if tower["tower_type"] == "crossing_tower"
    )

    upper_ring = crossing[
        "roof_transition_upper_ring"
    ]

    xs = [point[0] for point in upper_ring]
    ys = [point[1] for point in upper_ring]

    upper_span = max(
        max(xs) - min(xs),
        max(ys) - min(ys),
    )

    spire_height = (
        crossing["roof_top_z"]
        - crossing["roof_transition_upper_z"]
    )

    assert crossing["roof_height_basis"] == (
        "upper_transition_ring_span_30_degree_pitch"
    )
    assert crossing["roof_pitch_degrees"] == pytest.approx(
        30.0,
    )
    assert spire_height == pytest.approx(
        upper_span
        / 2.0
        * math.tan(
            math.radians(30.0)
        ),
        rel=1e-8,
        abs=1e-8,
    )


def test_crossing_tower_geometry_derived_spire_is_shorter_than_profile_cap():
    profile = _profile()

    mesh = AtlasChurchTowerMesher.build(
        frame=_frame(),
        profile=profile,
        building_height=42.0,
    )

    crossing_profile = profile.tower(
        "crossing_tower"
    )
    crossing = next(
        tower
        for tower in mesh["towers"]
        if tower["tower_type"] == "crossing_tower"
    )

    profile_cap_z = (
        42.0
        * crossing_profile.roof_top_ratio
    )

    assert crossing["roof_top_z"] < profile_cap_z


def test_crossing_tower_uses_resolved_outer_octagonal_tower_center():
    mesh = AtlasChurchTowerMesher.build(
        frame=_frame(),
        profile=_profile(),
        building_height=42.0,
    )

    crossing = next(
        tower
        for tower in mesh["towers"]
        if tower["tower_type"] == "crossing_tower"
    )
    outer_octagon = next(
        tower
        for tower in mesh["towers"]
        if tower["tower_type"] == "outer_polygon_tower"
    )

    assert crossing["center_longitudinal"] == pytest.approx(
        outer_octagon["center_longitudinal"],
        abs=1e-12,
    )
    assert crossing["center_lateral"] == pytest.approx(
        outer_octagon["center_lateral"],
        abs=1e-12,
    )
