from CORE.atlas_park_foundation_builder import (
    AtlasParkFoundationBuilder,
)


class CoordinateEngineStub:
    @staticmethod
    def geometry_to_stl_mm(geometry):
        return [
            (20.0, 20.0),
            (80.0, 20.0),
            (80.0, 80.0),
            (20.0, 80.0),
        ]


def _flat_terrain(z=2.0):
    return {
        "top_points": [
            [
                (0.0, 0.0, z),
                (200.0, 0.0, z),
            ],
            [
                (0.0, 200.0, z),
                (200.0, 200.0, z),
            ],
        ],
        "metadata": {
            "size_x_mm": 200.0,
            "size_y_mm": 200.0,
            "size_mm": 200.0,
        },
        "triangles": [
            (
                (0.0, 0.0, z),
                (200.0, 0.0, z),
                (0.0, 200.0, z),
            ),
            (
                (200.0, 0.0, z),
                (200.0, 200.0, z),
                (0.0, 200.0, z),
            ),
        ],
    }


def test_park_height_is_product_visible():
    assert AtlasParkFoundationBuilder.PARK_HEIGHT_MM == 0.30


def test_park_mesh_preserves_exact_park_height_above_terrain():
    park = {
        "id": 101,
        "geometry": [
            (50.0, 8.0),
            (50.0, 8.1),
            (50.1, 8.1),
            (50.1, 8.0),
        ],
        "park_type": "leisure:park",
    }

    mesh = AtlasParkFoundationBuilder._build_park_mesh(
        park=park,
        coordinate_engine=CoordinateEngineStub(),
        terrain_mesh=_flat_terrain(z=2.0),
    )

    assert mesh is not None
    assert mesh["park_type"] == "leisure:park"

    assert all(
        abs((top[2] - bottom[2]) - 0.30) < 1e-12
        for bottom, top in zip(
            mesh["bottom"],
            mesh["top"],
        )
    )


def test_park_mesh_remains_closed_after_height_change():
    park = {
        "id": 102,
        "geometry": [
            (50.0, 8.0),
            (50.0, 8.1),
            (50.1, 8.1),
            (50.1, 8.0),
        ],
        "park_type": "natural:scrub",
    }

    mesh = AtlasParkFoundationBuilder._build_park_mesh(
        park=park,
        coordinate_engine=CoordinateEngineStub(),
        terrain_mesh=_flat_terrain(),
    )

    assert mesh is not None
    assert len(mesh["bottom"]) == 4
    assert len(mesh["top"]) == 4
    assert len(mesh["walls"]) == 4
    assert mesh["triangles"]


class PassthroughCoordinateEngineStub:
    @staticmethod
    def geometry_to_stl_mm(geometry):
        return list(geometry)


def test_polygon_crossing_product_bounds_is_geometrically_clipped():
    points = [
        (-20.0, 40.0),
        (40.0, 40.0),
        (40.0, 80.0),
        (-20.0, 80.0),
    ]

    result = AtlasParkFoundationBuilder._clip_polygon_to_bounds(
        points=points,
        min_x=0.0,
        max_x=200.0,
        min_y=0.0,
        max_y=200.0,
    )

    assert result == [
        [
            (0.0, 40.0),
            (40.0, 40.0),
            (40.0, 80.0),
            (0.0, 80.0),
        ]
    ]


def test_polygon_covering_product_area_clips_to_full_product_rectangle():
    points = [
        (-20.0, -20.0),
        (220.0, -20.0),
        (220.0, 220.0),
        (-20.0, 220.0),
    ]

    result = AtlasParkFoundationBuilder._clip_polygon_to_bounds(
        points=points,
        min_x=0.0,
        max_x=200.0,
        min_y=0.0,
        max_y=200.0,
    )

    assert result == [
        [
            (0.0, 0.0),
            (200.0, 0.0),
            (200.0, 200.0),
            (0.0, 200.0),
        ]
    ]


def test_polygon_completely_outside_product_bounds_is_rejected():
    result = AtlasParkFoundationBuilder._clip_polygon_to_bounds(
        points=[
            (-30.0, 20.0),
            (-20.0, 20.0),
            (-20.0, 30.0),
            (-30.0, 30.0),
        ],
        min_x=0.0,
        max_x=200.0,
        min_y=0.0,
        max_y=200.0,
    )

    assert result == []


def test_valid_triangle_park_is_accepted():
    park = {
        "id": 201,
        "geometry": [
            (20.0, 20.0),
            (80.0, 20.0),
            (50.0, 80.0),
        ],
        "park_type": "worldcover:grass",
    }

    mesh = AtlasParkFoundationBuilder._build_park_mesh(
        park=park,
        coordinate_engine=PassthroughCoordinateEngineStub(),
        terrain_mesh=_flat_terrain(),
    )

    assert mesh is not None
    assert len(mesh["top"]) == 3
    assert mesh["triangles"]


def test_park_crossing_boundary_builds_from_clipped_polygon():
    park = {
        "id": 202,
        "geometry": [
            (-20.0, 40.0),
            (40.0, 40.0),
            (40.0, 80.0),
            (-20.0, 80.0),
        ],
        "park_type": "worldcover:grass",
    }

    mesh = AtlasParkFoundationBuilder._build_park_mesh(
        park=park,
        coordinate_engine=PassthroughCoordinateEngineStub(),
        terrain_mesh=_flat_terrain(),
    )

    assert mesh is not None

    assert mesh["top"] == [
        (0.0, 40.0, 2.30),
        (40.0, 40.0, 2.30),
        (40.0, 80.0, 2.30),
        (0.0, 80.0, 2.30),
    ]


def test_park_mesh_preserves_source_identity_for_semantic_processing():
    park = {
        "id": 8801,
        "geometry": [
            (20.0, 20.0),
            (40.0, 20.0),
            (40.0, 40.0),
            (20.0, 40.0),
        ],
        "park_type": "leisure:park",
        "tags": {
            "leisure": "park",
        },
    }

    mesh = AtlasParkFoundationBuilder._build_park_mesh(
        park=park,
        coordinate_engine=PassthroughCoordinateEngineStub(),
        terrain_mesh=_flat_terrain(),
    )

    assert mesh is not None
    assert mesh["source_id"] == 8801
