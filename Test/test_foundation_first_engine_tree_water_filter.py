from shapely.geometry import Polygon

from CORE.atlas_foundation_first_engine import (
    AtlasFoundationFirstEngine,
)


def _tree_mesh(
    *,
    center_x,
    center_y,
    source,
):
    bottom_z = 1.0
    top_z = 3.0
    radius = 0.2

    return {
        "type": "tree",
        "source": source,
        "tags": {
            "source": source,
        },
        "triangles": [
            (
                (
                    center_x - radius,
                    center_y - radius,
                    bottom_z,
                ),
                (
                    center_x + radius,
                    center_y - radius,
                    bottom_z,
                ),
                (
                    center_x,
                    center_y,
                    top_z,
                ),
            ),
            (
                (
                    center_x + radius,
                    center_y - radius,
                    bottom_z,
                ),
                (
                    center_x + radius,
                    center_y + radius,
                    bottom_z,
                ),
                (
                    center_x,
                    center_y,
                    top_z,
                ),
            ),
            (
                (
                    center_x + radius,
                    center_y + radius,
                    bottom_z,
                ),
                (
                    center_x - radius,
                    center_y + radius,
                    bottom_z,
                ),
                (
                    center_x,
                    center_y,
                    top_z,
                ),
            ),
            (
                (
                    center_x - radius,
                    center_y + radius,
                    bottom_z,
                ),
                (
                    center_x - radius,
                    center_y - radius,
                    bottom_z,
                ),
                (
                    center_x,
                    center_y,
                    top_z,
                ),
            ),
        ],
    }


def test_engine_removes_worldcover_tree_inside_water_polygon():
    water_polygon = Polygon(
        [
            (0.0, 0.0),
            (10.0, 0.0),
            (10.0, 10.0),
            (0.0, 10.0),
        ]
    )

    inside_tree = _tree_mesh(
        center_x=5.0,
        center_y=5.0,
        source="worldcover",
    )
    outside_tree = _tree_mesh(
        center_x=15.0,
        center_y=5.0,
        source="worldcover",
    )

    result = (
        AtlasFoundationFirstEngine
        ._remove_tree_meshes_inside_water_polygons(
            tree_meshes=[
                inside_tree,
                outside_tree,
            ],
            water_polygons_mm=[
                water_polygon,
            ],
        )
    )

    assert result == [outside_tree]


def test_engine_keeps_osm_tree_even_when_center_touches_water():
    water_polygon = Polygon(
        [
            (0.0, 0.0),
            (10.0, 0.0),
            (10.0, 10.0),
            (0.0, 10.0),
        ]
    )

    osm_tree = _tree_mesh(
        center_x=5.0,
        center_y=5.0,
        source="OSM",
    )

    result = (
        AtlasFoundationFirstEngine
        ._remove_tree_meshes_inside_water_polygons(
            tree_meshes=[osm_tree],
            water_polygons_mm=[water_polygon],
        )
    )

    assert result == [osm_tree]
