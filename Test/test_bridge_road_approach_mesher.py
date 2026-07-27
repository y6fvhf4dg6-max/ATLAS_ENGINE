from collections import Counter

from CORE.atlas_bridge_road_approach_mesher import (
    AtlasBridgeRoadApproachMesher,
)
from CORE.atlas_bridge_road_approach_profile import (
    AtlasBridgeRoadApproachProfile,
)


def _topology(triangles):
    def vertex_key(point):
        return tuple(
            round(float(value), 8)
            for value in point
        )

    def edge_key(first, second):
        return tuple(
            sorted(
                (
                    vertex_key(first),
                    vertex_key(second),
                )
            )
        )

    counts = Counter()

    for first, second, third in triangles:
        counts[edge_key(first, second)] += 1
        counts[edge_key(second, third)] += 1
        counts[edge_key(third, first)] += 1

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


def test_bridge_approach_mesher_builds_closed_ramp_prism():
    profile = AtlasBridgeRoadApproachProfile(
        bridge_top_z=1.60,
        road_top_z=0.80,
        length_mm=3.00,
        deck_thickness_mm=0.80,
    )

    mesh = AtlasBridgeRoadApproachMesher.build(
        start_edge=(
            (0.0, -2.0),
            (0.0, 2.0),
        ),
        outward_axis=(1.0, 0.0),
        profile=profile,
    )

    assert len(mesh["top"]) == 4
    assert len(mesh["bottom"]) == 4
    assert len(mesh["triangles"]) == 12

    topology = _topology(mesh["triangles"])

    assert topology["open_edges"] == 0
    assert topology["non_manifold_edges"] == 0


def test_bridge_approach_mesher_reaches_requested_length_and_levels():
    profile = AtlasBridgeRoadApproachProfile(
        bridge_top_z=1.60,
        road_top_z=0.80,
        length_mm=3.00,
        deck_thickness_mm=0.80,
    )

    mesh = AtlasBridgeRoadApproachMesher.build(
        start_edge=(
            (10.0, 20.0),
            (10.0, 26.0),
        ),
        outward_axis=(1.0, 0.0),
        profile=profile,
    )

    start_top = mesh["top"][:2]
    end_top = mesh["top"][2:]

    assert {point[0] for point in start_top} == {10.0}
    assert {point[0] for point in end_top} == {13.0}

    assert {point[2] for point in start_top} == {1.60}
    assert {point[2] for point in end_top} == {0.80}

    assert {
        top[2] - bottom[2]
        for top, bottom in zip(
            mesh["top"],
            mesh["bottom"],
        )
    } == {0.80}


def test_bridge_approach_mesher_normalizes_outward_axis():
    profile = AtlasBridgeRoadApproachProfile(
        bridge_top_z=1.60,
        road_top_z=0.80,
        length_mm=3.00,
    )

    mesh = AtlasBridgeRoadApproachMesher.build(
        start_edge=(
            (0.0, 0.0),
            (0.0, 4.0),
        ),
        outward_axis=(10.0, 0.0),
        profile=profile,
    )

    assert mesh["top"][2][0] == 3.0
    assert mesh["top"][3][0] == 3.0

def test_bridge_approach_mesher_uses_explicit_target_edge():
    profile = AtlasBridgeRoadApproachProfile(
        bridge_top_z=1.60,
        road_top_z=0.80,
        length_mm=3.00,
        deck_thickness_mm=0.80,
    )

    mesh = AtlasBridgeRoadApproachMesher.build(
        start_edge=(
            (0.0, -2.0),
            (0.0, 2.0),
        ),
        outward_axis=(1.0, 0.0),
        target_edge=(
            (0.8, -1.5),
            (1.2, 2.5),
        ),
        profile=profile,
    )

    assert mesh["top"][2][:2] == (
        0.8,
        -1.5,
    )
    assert mesh["top"][3][:2] == (
        1.2,
        2.5,
    )

    topology = _topology(mesh["triangles"])

    assert topology["open_edges"] == 0
    assert topology["non_manifold_edges"] == 0
