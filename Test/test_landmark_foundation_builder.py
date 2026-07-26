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


def _tower_landmark():
    return {
        "id": 101,
        "geometry_type": "way",
        "geometry": (
            (50.000, 8.000),
            (50.000, 8.010),
            (50.010, 8.010),
            (50.010, 8.000),
        ),
        "tags": {
            "man_made": "tower",
            "height": "60",
        },
    }


def test_tower_landmark_is_scaled_and_embedded_on_foundation():
    meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
        landmarks=[_tower_landmark()],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=FakeTerrain(),
        debug=False,
    )

    assert len(meshes) == 1

    mesh = meshes[0]

    assert mesh["type"] == "tower"
    assert mesh["landmark_id"] == 101
    assert mesh["placement_mode"] == "foundation_first"

    vertices = [
        vertex
        for triangle in mesh["triangles"]
        for vertex in triangle
    ]

    assert min(vertex[2] for vertex in vertices) == pytest.approx(2.5)
    assert max(vertex[2] for vertex in vertices) == pytest.approx(14.5)
    assert meshes[0]["foundation_z"] == pytest.approx(2.5)
    assert max(vertex[0] for vertex in vertices) == pytest.approx(10.0)
    assert max(vertex[1] for vertex in vertices) == pytest.approx(10.0)


def test_tower_landmark_accepts_foundation_terrain_slab_dict():
    terrain_slab = {
        "type": "terrain_closed_slab",
        "metadata": {
            "size_x_mm": 10.0,
            "size_y_mm": 10.0,
        },
        "top_points": [
            [
                (0.0, 0.0, 2.5),
                (10.0, 0.0, 2.5),
            ],
            [
                (0.0, 10.0, 2.5),
                (10.0, 10.0, 2.5),
            ],
        ],
    }

    meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
        landmarks=[_tower_landmark()],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=terrain_slab,
        debug=False,
    )

    assert len(meshes) == 1

    vertices = [
        vertex
        for triangle in meshes[0]["triangles"]
        for vertex in triangle
    ]

    assert min(vertex[2] for vertex in vertices) == pytest.approx(2.2)
    assert max(vertex[2] for vertex in vertices) == pytest.approx(14.2)
    assert meshes[0]["foundation_z"] == pytest.approx(2.2)


def _galata_bridge_landmark():
    return {
        "id": 280961352,
        "geometry_type": "way",
        "geometry": (
            (50.000, 8.000),
            (50.000, 8.080),
            (50.010, 8.080),
            (50.010, 8.000),
        ),
        "tags": {
            "man_made": "bridge",
            "name": "Galata Köprüsü",
            "wikidata": "Q81523",
        },
    }


def test_galata_bridge_preserves_continuous_deck_through_foundation_pipeline():
    meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
        landmarks=[_galata_bridge_landmark()],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=FakeTerrain(),
        debug=False,
    )

    assert len(meshes) == 1

    mesh = meshes[0]

    assert mesh["type"] == "bridge"
    assert mesh["landmark_id"] == 280961352
    assert mesh["metadata"]["bridge_segmented_deck"] is False
    assert "deck_sections" not in mesh

    assert len(mesh["bottom"]) > 4
    assert len(mesh["top"]) == len(mesh["bottom"])

    bottom_z_values = {
        point[2]
        for point in mesh["bottom"]
    }
    top_z_values = {
        point[2]
        for point in mesh["top"]
    }

    assert len(bottom_z_values) > 1
    assert len(top_z_values) > 1

    assert min(bottom_z_values) == pytest.approx(2.9)
    assert max(bottom_z_values) > min(bottom_z_values)

    assert min(top_z_values) == pytest.approx(3.7)
    assert max(top_z_values) > min(top_z_values)


def test_bridge_deck_thickness_uses_print_safe_minimum():
    source = _galata_bridge_landmark()

    meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
        landmarks=[source],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=FakeTerrain(),
        debug=False,
    )

    assert len(meshes) == 1

    mesh = meshes[0]

    assert (
        mesh["metadata"]["bridge_deck_thickness_m"]
        == pytest.approx(0.80)
    )

    top_by_xy = {
        (x, y): z
        for x, y, z in mesh["top"]
    }
    bottom_by_xy = {
        (x, y): z
        for x, y, z in mesh["bottom"]
    }

    for xy in top_by_xy:
        assert (
            top_by_xy[xy] - bottom_by_xy[xy]
            == pytest.approx(0.80)
        )


def test_galata_bridge_includes_four_printable_support_meshes():
    source = _galata_bridge_landmark()

    meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
        landmarks=[source],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=FakeTerrain(),
        debug=False,
    )

    assert len(meshes) == 1

    bridge = meshes[0]
    supports = bridge["supports"]

    assert len(supports) == 4

    for support in supports:
        assert len(support["bottom"]) == 4
        assert len(support["top"]) == 4
        assert len(support["triangles"]) == 12

    support_triangle_count = sum(
        len(support["triangles"])
        for support in supports
    )

    assert support_triangle_count == 48

    continuous_deck_triangle_count = (
        len(bridge["triangles"])
        - support_triangle_count
    )

    assert continuous_deck_triangle_count > 12
    assert len(bridge["triangles"]) == (
        continuous_deck_triangle_count
        + support_triangle_count
    )


def test_galata_bridge_supports_connect_inside_deck_bottom():
    source = _galata_bridge_landmark()

    meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
        landmarks=[source],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=FakeTerrain(),
        debug=False,
    )

    bridge = meshes[0]

    deck_bottom_z = min(
        point[2]
        for point in bridge["bottom"]
    )

    for support in bridge["supports"]:
        top_z_values = {
            point[2]
            for point in support["top"]
        }

        assert len(top_z_values) == 1
        assert next(
            iter(top_z_values)
        ) == pytest.approx(
            deck_bottom_z + 0.15
        )


def test_galata_bridge_supports_embed_into_continuous_deck():
    source = _galata_bridge_landmark()

    meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
        landmarks=[source],
        coordinate_engine=FakeCoordinateEngine(),
        terrain_mesh=FakeTerrain(),
        debug=False,
    )

    bridge = meshes[0]

    deck_bottom_z = min(
        point[2]
        for point in bridge["bottom"]
    )
    deck_top_z = max(
        point[2]
        for point in bridge["top"]
    )

    for support in bridge["supports"]:
        support_top_z_values = {
            point[2]
            for point in support["top"]
        }

        assert len(support_top_z_values) == 1

        support_top_z = next(
            iter(support_top_z_values)
        )

        assert support_top_z > deck_bottom_z
        assert support_top_z < deck_top_z
        assert (
            support_top_z - deck_bottom_z
            == pytest.approx(0.15)
        )
