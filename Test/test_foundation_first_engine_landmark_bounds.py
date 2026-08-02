from CORE.atlas_foundation_first_engine import (
    AtlasFoundationFirstEngine,
)


def _mesh(
    *,
    landmark_id,
    minimum_x,
    maximum_x,
    minimum_y,
    maximum_y,
):
    return {
        "type": "landmark",
        "landmark_id": landmark_id,
        "triangles": [
            (
                (minimum_x, minimum_y, 1.0),
                (maximum_x, minimum_y, 1.0),
                (maximum_x, maximum_y, 1.0),
            ),
            (
                (minimum_x, minimum_y, 1.0),
                (maximum_x, maximum_y, 1.0),
                (minimum_x, maximum_y, 1.0),
            ),
        ],
    }


def test_engine_keeps_landmark_fully_inside_product_bounds():
    landmark = _mesh(
        landmark_id=100,
        minimum_x=10.0,
        maximum_x=90.0,
        minimum_y=10.0,
        maximum_y=90.0,
    )

    result = (
        AtlasFoundationFirstEngine
        ._keep_landmark_meshes_inside_product_bounds(
            landmark_meshes=[landmark],
            product_max_x=100.0,
            product_max_y=100.0,
        )
    )

    assert result == [landmark]


def test_engine_removes_landmark_crossing_product_bounds():
    landmark = _mesh(
        landmark_id=200,
        minimum_x=80.0,
        maximum_x=110.0,
        minimum_y=10.0,
        maximum_y=90.0,
    )

    result = (
        AtlasFoundationFirstEngine
        ._keep_landmark_meshes_inside_product_bounds(
            landmark_meshes=[landmark],
            product_max_x=100.0,
            product_max_y=100.0,
        )
    )

    assert result == []
