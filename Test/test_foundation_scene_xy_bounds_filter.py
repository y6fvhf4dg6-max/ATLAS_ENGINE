from CORE.atlas_foundation_scene_xy_bounds_filter import (
    AtlasFoundationSceneXYBoundsFilter,
)


def _mesh(
    *,
    mesh_type,
    minimum_x,
    maximum_x,
    minimum_y,
    maximum_y,
):
    return {
        "type": mesh_type,
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


def test_filter_keeps_mesh_fully_inside_product_bounds():
    meshes = [
        _mesh(
            mesh_type="bridge",
            minimum_x=10.0,
            maximum_x=90.0,
            minimum_y=20.0,
            maximum_y=80.0,
        )
    ]

    result = AtlasFoundationSceneXYBoundsFilter.keep_fully_inside(
        meshes=meshes,
        min_x=0.0,
        max_x=100.0,
        min_y=0.0,
        max_y=100.0,
    )

    assert result == meshes


def test_filter_removes_bridge_crossing_product_bounds():
    meshes = [
        _mesh(
            mesh_type="bridge",
            minimum_x=-20.0,
            maximum_x=30.0,
            minimum_y=20.0,
            maximum_y=80.0,
        )
    ]

    result = AtlasFoundationSceneXYBoundsFilter.keep_fully_inside(
        meshes=meshes,
        min_x=0.0,
        max_x=100.0,
        min_y=0.0,
        max_y=100.0,
    )

    assert result == []


def test_filter_removes_road_crossing_product_bounds():
    meshes = [
        _mesh(
            mesh_type="road_foundation",
            minimum_x=-0.25,
            maximum_x=5.0,
            minimum_y=20.0,
            maximum_y=30.0,
        )
    ]

    result = AtlasFoundationSceneXYBoundsFilter.keep_fully_inside(
        meshes=meshes,
        min_x=0.0,
        max_x=100.0,
        min_y=0.0,
        max_y=100.0,
    )

    assert result == []


def test_filter_supports_small_numeric_tolerance():
    meshes = [
        _mesh(
            mesh_type="bridge",
            minimum_x=-0.00005,
            maximum_x=100.00005,
            minimum_y=0.0,
            maximum_y=100.0,
        )
    ]

    result = AtlasFoundationSceneXYBoundsFilter.keep_fully_inside(
        meshes=meshes,
        min_x=0.0,
        max_x=100.0,
        min_y=0.0,
        max_y=100.0,
        tolerance=0.0001,
    )

    assert result == meshes
