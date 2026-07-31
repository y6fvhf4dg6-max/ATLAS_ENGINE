import pytest

from CORE.atlas_terrain_following_landcover_builder import (
    AtlasTerrainFollowingLandcoverBuilder,
)


def _terrain():
    return {
        "top_points": [
            [
                (0.0, 0.0, 1.0),
                (100.0, 0.0, 2.0),
                (200.0, 0.0, 3.0),
            ],
            [
                (0.0, 100.0, 2.0),
                (100.0, 100.0, 3.0),
                (200.0, 100.0, 4.0),
            ],
            [
                (0.0, 200.0, 3.0),
                (100.0, 200.0, 4.0),
                (200.0, 200.0, 5.0),
            ],
        ],
        "metadata": {
            "size_x_mm": 200.0,
            "size_y_mm": 200.0,
            "size_mm": 200.0,
        },
    }


def test_builder_creates_surface_without_vertical_walls():
    surfaces = [
        {
            "id": "grass_1",
            "surface_type": "grass",
            "park_type": "worldcover:grass",
            "geometry": [
                (25.0, 25.0),
                (175.0, 25.0),
                (175.0, 175.0),
                (25.0, 175.0),
            ],
        }
    ]

    meshes = AtlasTerrainFollowingLandcoverBuilder.build(
        surfaces=surfaces,
        terrain_mesh=_terrain(),
        height_mm=0.12,
    )

    assert len(meshes) == 1

    mesh = meshes[0]

    assert mesh["type"] == "terrain_following_landcover"
    assert mesh["surface_type"] == "grass"
    assert mesh["walls"] == []
    assert mesh["bottom"] == []
    assert mesh["triangles"]


def test_every_output_vertex_follows_terrain_with_exact_offset():
    surfaces = [
        {
            "id": "grass_2",
            "surface_type": "grass",
            "geometry": [
                (0.0, 0.0),
                (100.0, 0.0),
                (100.0, 100.0),
                (0.0, 100.0),
            ],
        }
    ]

    meshes = AtlasTerrainFollowingLandcoverBuilder.build(
        surfaces=surfaces,
        terrain_mesh=_terrain(),
        height_mm=0.12,
    )

    vertices = {
        point
        for triangle in meshes[0]["triangles"]
        for point in triangle
    }

    expected_vertices = {
        (0.0, 0.0, 1.12),
        (100.0, 0.0, 2.12),
        (100.0, 100.0, 3.12),
        (0.0, 100.0, 2.12),
    }

    assert len(vertices) == len(expected_vertices)

    for expected in expected_vertices:
        assert any(
            actual[0] == pytest.approx(
                expected[0],
                abs=1e-9,
            )
            and actual[1] == pytest.approx(
                expected[1],
                abs=1e-9,
            )
            and actual[2] == pytest.approx(
                expected[2],
                abs=1e-9,
            )
            for actual in vertices
        )


def test_surface_is_clipped_to_product_bounds_without_edge_wall():
    surfaces = [
        {
            "id": "grass_3",
            "surface_type": "grass",
            "geometry": [
                (-20.0, 20.0),
                (40.0, 20.0),
                (40.0, 80.0),
                (-20.0, 80.0),
            ],
        }
    ]

    meshes = AtlasTerrainFollowingLandcoverBuilder.build(
        surfaces=surfaces,
        terrain_mesh=_terrain(),
        height_mm=0.12,
    )

    assert len(meshes) == 1
    assert meshes[0]["walls"] == []

    for triangle in meshes[0]["triangles"]:
        for x, y, _z in triangle:
            assert 0.0 <= x <= 200.0
            assert 0.0 <= y <= 200.0


def test_empty_surface_input_returns_empty_list():
    assert (
        AtlasTerrainFollowingLandcoverBuilder.build(
            surfaces=[],
            terrain_mesh=_terrain(),
            height_mm=0.12,
        )
        == []
    )


def test_non_positive_height_is_rejected():
    try:
        AtlasTerrainFollowingLandcoverBuilder.build(
            surfaces=[],
            terrain_mesh=_terrain(),
            height_mm=0.0,
        )
    except ValueError as error:
        assert "height_mm" in str(error)
    else:
        raise AssertionError("Expected ValueError")


class CoordinateEngineStub:
    @staticmethod
    def geometry_to_stl_mm(geometry):
        return [
            (
                (lon - 8.0) * 1000.0,
                (lat - 50.0) * 1000.0,
            )
            for lat, lon in geometry
        ]


def test_builder_converts_geographic_geometry_with_coordinate_engine():
    surfaces = [
        {
            "id": "grass_geo_1",
            "surface_type": "grass",
            "source": "worldcover",
            "geometry": [
                (50.000, 8.000),
                (50.000, 8.100),
                (50.100, 8.100),
                (50.100, 8.000),
            ],
        }
    ]

    meshes = AtlasTerrainFollowingLandcoverBuilder.build(
        surfaces=surfaces,
        terrain_mesh=_terrain(),
        height_mm=0.12,
        coordinate_engine=CoordinateEngineStub(),
    )

    assert len(meshes) == 1

    vertices = {
        point
        for triangle in meshes[0]["triangles"]
        for point in triangle
    }

    expected_vertices = {
        (0.0, 0.0, 1.12),
        (100.0, 0.0, 2.12),
        (100.0, 100.0, 3.12),
        (0.0, 100.0, 2.12),
    }

    assert len(vertices) == len(expected_vertices)

    for expected in expected_vertices:
        assert any(
            actual[0] == pytest.approx(
                expected[0],
                abs=1e-9,
            )
            and actual[1] == pytest.approx(
                expected[1],
                abs=1e-9,
            )
            and actual[2] == pytest.approx(
                expected[2],
                abs=1e-9,
            )
            for actual in vertices
        )


def test_builder_preserves_stl_geometry_without_coordinate_engine():
    surfaces = [
        {
            "id": "grass_mm_1",
            "surface_type": "grass",
            "geometry": [
                (0.0, 0.0),
                (100.0, 0.0),
                (100.0, 100.0),
                (0.0, 100.0),
            ],
        }
    ]

    meshes = AtlasTerrainFollowingLandcoverBuilder.build(
        surfaces=surfaces,
        terrain_mesh=_terrain(),
        height_mm=0.12,
    )

    assert len(meshes) == 1


def test_surface_is_subdivided_by_terrain_grid_vertices():
    surfaces = [
        {
            "id": "grass_grid_1",
            "surface_type": "grass",
            "geometry": [
                (0.0, 0.0),
                (200.0, 0.0),
                (200.0, 200.0),
                (0.0, 200.0),
            ],
        }
    ]

    meshes = AtlasTerrainFollowingLandcoverBuilder.build(
        surfaces=surfaces,
        terrain_mesh=_terrain(),
        height_mm=0.12,
    )

    assert len(meshes) == 1

    vertices = {
        (
            round(point[0], 9),
            round(point[1], 9),
            round(point[2], 9),
        )
        for triangle in meshes[0]["triangles"]
        for point in triangle
    }

    # Landcover must preserve the terrain grid's interior vertex.
    # A single polygon triangulation would omit this point and create
    # large planar facets across the terrain.
    assert (100.0, 100.0, 3.12) in vertices

    assert {
        (0.0, 0.0, 1.12),
        (200.0, 0.0, 3.12),
        (200.0, 200.0, 5.12),
        (0.0, 200.0, 3.12),
    }.issubset(vertices)


def test_landcover_uses_multiple_terrain_cells():
    surfaces = [
        {
            "id": "grass_grid_2",
            "surface_type": "grass",
            "geometry": [
                (0.0, 0.0),
                (200.0, 0.0),
                (200.0, 200.0),
                (0.0, 200.0),
            ],
        }
    ]

    meshes = AtlasTerrainFollowingLandcoverBuilder.build(
        surfaces=surfaces,
        terrain_mesh=_terrain(),
        height_mm=0.12,
    )

    # 3 x 3 terrain points define 2 x 2 cells.
    # Each cell contains two terrain triangles.
    assert len(meshes[0]["triangles"]) == 8
