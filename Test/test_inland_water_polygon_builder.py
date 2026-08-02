from shapely.geometry import Point

from CORE.atlas_inland_water_polygon_builder import (
    AtlasInlandWaterPolygonBuilder,
)


BBOX = (
    52.4400,
    13.5680,
    52.4500,
    13.5800,
)


def test_closed_natural_water_way_becomes_polygon():
    waters = [
        {
            "id": 22980330,
            "geometry": [
                (52.4420, 13.5700),
                (52.4420, 13.5760),
                (52.4470, 13.5760),
                (52.4470, 13.5700),
            ],
            "tags": {
                "natural": "water",
                "water": "river",
            },
            "water_type": "water:river",
        }
    ]

    polygons = AtlasInlandWaterPolygonBuilder.build_polygons(
        waters=waters,
        bbox=BBOX,
        debug=False,
    )

    assert len(polygons) == 1

    polygon = polygons[0]

    assert polygon.is_valid
    assert polygon.geom_type == "Polygon"
    assert polygon.area > 0.0
    assert polygon.covers(
        Point(
            13.5730,
            52.4440,
        )
    )


def test_open_waterway_line_is_not_treated_as_surface_polygon():
    waters = [
        {
            "id": 50664988,
            "geometry": [
                (52.4420, 13.5700),
                (52.4440, 13.5730),
                (52.4470, 13.5760),
            ],
            "tags": {
                "waterway": "river",
            },
            "water_type": "waterway:river",
        }
    ]

    polygons = AtlasInlandWaterPolygonBuilder.build_polygons(
        waters=waters,
        bbox=BBOX,
        debug=False,
    )

    assert polygons == []


def test_overlapping_surface_waters_are_unioned_before_meshing():
    waters = [
        {
            "id": 28077549,
            "geometry": [
                (52.4420, 13.5700),
                (52.4420, 13.5750),
                (52.4460, 13.5750),
                (52.4460, 13.5700),
            ],
            "tags": {
                "natural": "water",
            },
            "water_type": "natural:water",
        },
        {
            "id": 275743871,
            "geometry": [
                (52.4450, 13.5740),
                (52.4450, 13.5770),
                (52.4480, 13.5770),
                (52.4480, 13.5740),
            ],
            "tags": {
                "natural": "water",
                "water": "river",
            },
            "water_type": "water:river",
        },
    ]

    polygons = AtlasInlandWaterPolygonBuilder.build_polygons(
        waters=waters,
        bbox=BBOX,
        debug=False,
    )

    assert len(polygons) == 1
    assert polygons[0].is_valid
    assert polygons[0].geom_type == "Polygon"
    assert polygons[0].area > 0.0
