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
