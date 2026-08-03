import pytest
from shapely.geometry import Polygon

from CORE.atlas_coordinate_engine import AtlasCoordinateEngine
from CORE.atlas_water_foundation_builder import (
    AtlasWaterFoundationBuilder,
)


def test_inland_water_is_horizontal_above_highest_sampled_terrain():
    polygon = Polygon(
        [
            (0.0, 0.0),
            (0.001, 0.0),
            (0.001, 0.001),
            (0.0, 0.001),
        ]
    )

    coordinate_engine = AtlasCoordinateEngine(
        origin_lat=0.0,
        origin_lon=0.0,
        xy_scale=1000.0,
        z_scale=5000.0,
    )

    terrain_mesh = {
        "top_points": [
            [
                (0.0, 0.0, 1.0),
                (111.0, 0.0, 1.5),
            ],
            [
                (0.0, 111.0, 1.7),
                (111.0, 111.0, 2.0),
            ],
        ],
        "metadata": {
            "size_x_mm": 111.0,
            "size_y_mm": 111.0,
            "size_mm": 111.0,
            "base_z": 0.8,
            "min_height_m": 0.0,
            "z_scale": 5000.0,
        },
    }

    meshes = AtlasWaterFoundationBuilder.build_inland_water_meshes(
        water_polygons=[polygon],
        coordinate_engine=coordinate_engine,
        terrain_mesh=terrain_mesh,
        debug=False,
    )

    assert len(meshes) == 1

    mesh = meshes[0]

    assert mesh["type"] == "inland_water_foundation"
    assert mesh["water_type"] == "inland"
    assert mesh["placement_mode"] == (
        "horizontal_above_terrain"
    )
    assert mesh["water_bottom_z"] == pytest.approx(2.0)
    assert mesh["water_surface_z"] == pytest.approx(2.1)

    assert {
        round(point[2], 9)
        for point in mesh["bottom"]
    } == {2.0}

    assert {
        round(point[2], 9)
        for point in mesh["top"]
    } == {2.1}

    assert len(mesh["triangles"]) > 0
