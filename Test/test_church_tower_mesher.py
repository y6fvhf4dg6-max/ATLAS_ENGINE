from collections import Counter

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
