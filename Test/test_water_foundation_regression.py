import pytest
from shapely.geometry import Point

from CORE.atlas_coastline_water_builder import (
    AtlasCoastlineWaterBuilder,
)
from CORE.atlas_coordinate_engine import (
    AtlasCoordinateEngine,
)
from CORE.atlas_water_foundation_builder import (
    AtlasWaterFoundationBuilder,
)


BBOX = (
    0.0,  # south
    0.0,  # west
    1.0,  # north
    1.0,  # east
)


def build_coastline(
    start,
    end,
):
    return [
        {
            "id": 1,
            "geometry": [
                start,
                end,
            ],
        }
    ]


def test_northbound_coastline_selects_east_side_as_water():
    coastlines = build_coastline(
        start=(0.0, 0.4),
        end=(1.0, 0.4),
    )

    polygons = (
        AtlasCoastlineWaterBuilder
        .build_water_polygons(
            coastlines=coastlines,
            bbox=BBOX,
            debug=False,
        )
    )

    assert len(polygons) == 1

    water_polygon = polygons[0]

    assert water_polygon.covers(
        Point(
            0.8,
            0.5,
        )
    )

    assert not water_polygon.covers(
        Point(
            0.2,
            0.5,
        )
    )

    assert water_polygon.centroid.x > 0.4


def test_southbound_coastline_selects_west_side_as_water():
    coastlines = build_coastline(
        start=(1.0, 0.4),
        end=(0.0, 0.4),
    )

    polygons = (
        AtlasCoastlineWaterBuilder
        .build_water_polygons(
            coastlines=coastlines,
            bbox=BBOX,
            debug=False,
        )
    )

    assert len(polygons) == 1

    water_polygon = polygons[0]

    assert water_polygon.covers(
        Point(
            0.2,
            0.5,
        )
    )

    assert not water_polygon.covers(
        Point(
            0.8,
            0.5,
        )
    )

    assert water_polygon.centroid.x < 0.4


def test_coastline_water_mesh_is_horizontal_and_printable():
    coastlines = build_coastline(
        start=(0.0, 0.4),
        end=(1.0, 0.4),
    )

    polygons = (
        AtlasCoastlineWaterBuilder
        .build_water_polygons(
            coastlines=coastlines,
            bbox=BBOX,
            debug=False,
        )
    )

    coordinate_engine = AtlasCoordinateEngine(
        origin_lat=0.0,
        origin_lon=0.0,
        xy_scale=1000.0,
        z_scale=5000.0,
    )

    terrain_mesh = {
        "metadata": {
            "base_z": 0.8,
            "min_height_m": 0.0,
            "z_scale": 5000.0,
        }
    }

    meshes = (
        AtlasWaterFoundationBuilder
        .build_coastline_water_meshes(
            water_polygons=polygons,
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_mesh,
            debug=False,
        )
    )

    assert len(meshes) == 1

    mesh = meshes[0]

    assert mesh["type"] == (
        "coastline_water_foundation"
    )

    assert mesh["placement_mode"] == (
        "horizontal_sea_level"
    )

    assert mesh["water_bottom_z"] == pytest.approx(
        0.8
    )

    assert mesh["water_surface_z"] == pytest.approx(
        0.9
    )

    assert len(mesh["triangles"]) > 0

    top_z_values = {
        round(
            point[2],
            9,
        )
        for point in mesh["top"]
    }

    bottom_z_values = {
        round(
            point[2],
            9,
        )
        for point in mesh["bottom"]
    }

    assert top_z_values == {0.9}
    assert bottom_z_values == {0.8}
