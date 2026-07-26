import pytest

from CORE.atlas_landmark_foundation_builder import (
    AtlasLandmarkFoundationBuilder,
)


class FakeCoordinateEngine:
    def geometry_to_stl_mm(self, geometry):
        return [
            (
                (lon - 8.0) * 1000.0,
                (lat - 50.0) * 1000.0,
            )
            for lat, lon in geometry
        ]

    def latlon_to_local_meters(self, lat, lon):
        return (
            (lon - 8.0) * 100_000.0,
            (lat - 50.0) * 100_000.0,
        )

    def height_to_stl_mm(self, height_m):
        return float(height_m) / 5.0


class FakeTerrain:
    def sample_height(self, x, y):
        return 2.5


def _galata_bridge_landmark():
    return {
        "id": 280961352,
        "geometry_type": "way",
        "geometry": (
            (50.000, 8.000),
            (50.000, 8.020),
            (50.000, 8.040),
            (50.000, 8.060),
            (50.000, 8.080),
            (50.010, 8.080),
            (50.010, 8.060),
            (50.010, 8.040),
            (50.010, 8.020),
            (50.010, 8.000),
        ),
        "tags": {
            "man_made": "bridge",
            "name": "Galata Köprüsü",
            "wikidata": "Q81523",
        },
    }


def _build_bridge():
    meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
        landmarks=[_galata_bridge_landmark()],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=FakeTerrain(),
        debug=False,
    )

    assert len(meshes) == 1
    return meshes[0]


def test_galata_bridge_uses_one_continuous_profiled_deck():
    bridge = _build_bridge()

    assert bridge["metadata"]["bridge_segmented_deck"] is False
    assert "deck_sections" not in bridge

    assert len(bridge["top"]) > 4
    assert len(bridge["bottom"]) == len(bridge["top"])


def test_galata_bridge_deck_rises_to_center_then_descends():
    bridge = _build_bridge()

    top = tuple(bridge["top"])

    minimum_x = min(point[0] for point in top)
    maximum_x = max(point[0] for point in top)
    center_x = (minimum_x + maximum_x) * 0.5

    end_tolerance = 1e-8

    start_z = [
        point[2]
        for point in top
        if abs(point[0] - minimum_x) <= end_tolerance
    ]
    center_z = [
        point[2]
        for point in top
        if abs(point[0] - center_x) <= end_tolerance
    ]
    end_z = [
        point[2]
        for point in top
        if abs(point[0] - maximum_x) <= end_tolerance
    ]

    assert start_z
    assert center_z
    assert end_z

    assert min(center_z) > max(start_z)
    assert min(center_z) > max(end_z)

    assert max(start_z) == pytest.approx(max(end_z))


def test_galata_bridge_keeps_constant_printable_deck_thickness():
    bridge = _build_bridge()

    top_by_xy = {
        (round(x, 8), round(y, 8)): z
        for x, y, z in bridge["top"]
    }
    bottom_by_xy = {
        (round(x, 8), round(y, 8)): z
        for x, y, z in bridge["bottom"]
    }

    assert top_by_xy.keys() == bottom_by_xy.keys()

    for xy in top_by_xy:
        assert (
            top_by_xy[xy] - bottom_by_xy[xy]
            == pytest.approx(0.80)
        )


def test_galata_bridge_deck_remains_above_foundation_and_water():
    bridge = _build_bridge()

    foundation_z = bridge["foundation_z"]
    minimum_deck_bottom_z = min(
        point[2]
        for point in bridge["bottom"]
    )

    assert minimum_deck_bottom_z > foundation_z


def test_galata_supports_rise_to_local_profiled_deck():
    bridge = _build_bridge()

    assert len(bridge["supports"]) == 4

    support_top_levels = []

    for support in bridge["supports"]:
        top_z_values = {
            round(point[2], 8)
            for point in support["top"]
        }

        assert len(top_z_values) == 1

        support_top_z = next(iter(top_z_values))
        support_top_levels.append(support_top_z)

        assert support_top_z > bridge["foundation_z"]
        assert support_top_z < max(
            point[2]
            for point in bridge["top"]
        )

    assert len(set(support_top_levels)) >= 2



def test_galata_profiled_deck_densifies_long_edges():
    bridge = _build_bridge()

    source_point_count = len(
        _galata_bridge_landmark()["geometry"]
    )

    assert len(bridge["top"]) > source_point_count
    assert len(bridge["bottom"]) == len(bridge["top"])


def test_galata_profile_has_multiple_intermediate_height_levels():
    bridge = _build_bridge()

    top_levels = {
        round(point[2], 6)
        for point in bridge["top"]
    }

    assert len(top_levels) >= 5


def _topology_counts(triangles):
    from collections import Counter

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


def test_galata_profiled_base_deck_is_closed_and_manifold():
    bridge = _build_bridge()

    support_triangle_count = sum(
        len(support["triangles"])
        for support in bridge.get("supports", ())
    )

    parapet_triangle_count = sum(
        len(parapet["triangles"])
        for parapet in bridge.get("parapets", ())
    )

    component_triangle_count = (
        support_triangle_count
        + parapet_triangle_count
    )

    base_triangles = bridge["triangles"][
        :-component_triangle_count
    ]

    topology = _topology_counts(base_triangles)

    assert topology["open_edges"] == 0
    assert topology["non_manifold_edges"] == 0
