from CORE.atlas_foundation_first_engine import (
    AtlasFoundationFirstEngine,
)


def _road_mesh(
    *,
    minimum_x,
    maximum_x,
    minimum_y,
    maximum_y,
):
    bottom = [
        (minimum_x, minimum_y, 0.0),
        (maximum_x, minimum_y, 0.0),
        (maximum_x, maximum_y, 0.0),
        (minimum_x, maximum_y, 0.0),
    ]
    top = [
        (minimum_x, minimum_y, 0.4),
        (maximum_x, minimum_y, 0.4),
        (maximum_x, maximum_y, 0.4),
        (minimum_x, maximum_y, 0.4),
    ]

    return {
        "type": "road_foundation",
        "bottom": bottom,
        "top": top,
        "walls": [],
        "triangles": [
            (bottom[0], bottom[1], bottom[2]),
            (bottom[0], bottom[2], bottom[3]),
            (top[0], top[2], top[1]),
            (top[0], top[3], top[2]),
        ],
    }


def test_road_bounds_filter_removes_crossing_closed_meshes():
    inside = _road_mesh(
        minimum_x=10.0,
        maximum_x=20.0,
        minimum_y=10.0,
        maximum_y=20.0,
    )
    crossing = _road_mesh(
        minimum_x=90.0,
        maximum_x=110.0,
        minimum_y=10.0,
        maximum_y=20.0,
    )

    result = (
        AtlasFoundationFirstEngine
        ._keep_road_meshes_inside_product_bounds(
            road_meshes=[inside, crossing],
            product_max_x=100.0,
            product_max_y=100.0,
        )
    )

    assert result == [inside]
