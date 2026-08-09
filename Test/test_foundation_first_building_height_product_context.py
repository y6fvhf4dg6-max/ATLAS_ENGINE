from CORE.atlas_coordinate_engine import (
    AtlasCoordinateEngine,
)
from CORE.atlas_foundation_first_engine import (
    AtlasFoundationFirstEngine,
)


def test_foundation_first_resolves_building_height_product_context():
    coordinate_engine = AtlasCoordinateEngine(
        origin_lat=50.0,
        origin_lon=8.0,
        xy_scale=5500.0,
        z_scale=5500.0,
    )

    buildings = (
        {
            "id": 100,
            "geometry": (
                (50.0001, 8.0001),
                (50.0001, 8.0002),
                (50.0002, 8.0002),
                (50.0002, 8.0001),
            ),
            "tags": {
                "building": "yes",
                "height": "24",
            },
        },
        {
            "id": 101,
            "geometry": (
                (50.0003, 8.0001),
                (50.0003, 8.0002),
                (50.0004, 8.0002),
                (50.0004, 8.0001),
            ),
            "tags": {
                "building": "yes",
                "height": "10",
            },
        },
    )

    roads = (
        {
            "id": 1,
            "geometry": (
                (50.0000, 8.0000),
                (50.0000, 8.0010),
            ),
            "tags": {
                "highway": "residential",
            },
        },
        {
            "id": 2,
            "geometry": (
                (50.0010, 8.0000),
                (50.0010, 8.0010),
            ),
            "tags": {
                "highway": "residential",
            },
        },
        {
            "id": 3,
            "geometry": (
                (50.0000, 8.0000),
                (50.0010, 8.0000),
            ),
            "tags": {
                "highway": "residential",
            },
        },
        {
            "id": 4,
            "geometry": (
                (50.0000, 8.0010),
                (50.0010, 8.0010),
            ),
            "tags": {
                "highway": "residential",
            },
        },
    )

    context = (
        AtlasFoundationFirstEngine
        ._resolve_building_height_product_context(
            buildings=buildings,
            roads=roads,
            landmarks=(),
            coordinate_engine=coordinate_engine,
        )
    )

    assert 100 in context
    assert 101 in context

    assert context[100]["source_height_m"] == 24.0
    assert context[101]["source_height_m"] == 10.0

    assert context[100]["block_median_height_m"] == 17.0
    assert context[101]["block_median_height_m"] == 17.0
