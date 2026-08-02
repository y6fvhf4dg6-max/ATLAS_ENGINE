from shapely.geometry import Point

from CORE.atlas_foundation_first_engine import (
    AtlasFoundationFirstEngine,
)


BBOX = (
    52.4400,
    13.5680,
    52.4500,
    13.5800,
)


def test_engine_combines_inland_water_without_coastline():
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

    polygons = AtlasFoundationFirstEngine._build_water_polygons(
        waters=waters,
        coastlines=[],
        bbox=BBOX,
        debug=False,
    )

    assert len(polygons) == 1
    assert polygons[0].covers(
        Point(
            13.5730,
            52.4440,
        )
    )
