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


def test_engine_resolves_nature_data_into_tree_and_canopy_inputs():
    existing_trees = [
        {
            "id": 100,
            "tree_type": "tree",
            "tags": {"source": "osm"},
        },
    ]

    nature_data = {
        "trees": [
            {
                "id": "worldcover_0",
                "lat": 50.0,
                "lon": 7.0,
                "tree_type": "tree",
                "tags": {
                    "source": "worldcover",
                    "class_id": 10,
                    "resolution_m": 10,
                },
            },
        ],
        "tree_rows": [],
        "forests": [
            {
                "id": "forest_cell_0",
                "lat": 50.0,
                "lon": 7.0,
                "class_id": 10,
                "source": "worldcover",
                "resolution_m": 10,
            },
        ],
    }

    result = (
        AtlasFoundationFirstEngine
        ._resolve_vegetation_composition(
            existing_trees=existing_trees,
            nature_data=nature_data,
        )
    )

    assert tuple(
        item["id"] for item in result["tree_input"]
    ) == (100,)

    assert len(result["forest_canopy_surfaces"]) == 1
    assert (
        result["forest_canopy_surfaces"][0]["surface_type"]
        == "forest"
    )


class _VegetationCoordinateEngine:
    xy_scale = 5500.0

    @staticmethod
    def latlon_to_stl_mm(lat, lon):
        return (float(lon), float(lat))

    @staticmethod
    def geometry_to_stl_mm(geometry):
        return geometry


def test_engine_builds_tree_and_canopy_meshes_from_composition():
    existing_trees = [
        {
            "id": 100,
            "lat": 2.0,
            "lon": 2.0,
            "tree_type": "tree",
            "tags": {"source": "osm"},
        },
    ]

    nature_data = {
        "trees": [],
        "tree_rows": [],
        "forests": [
            {
                "id": "forest_cell_0",
                "lat": 5.0,
                "lon": 5.0,
                "class_id": 10,
                "source": "worldcover",
                "resolution_m": 10,
            },
        ],
    }

    terrain_mesh = {
        "metadata": {
            "size_x_mm": 10.0,
            "size_y_mm": 10.0,
        },
        "top_points": (
            ((0.0, 0.0, 0.0), (10.0, 0.0, 0.0)),
            ((0.0, 10.0, 0.0), (10.0, 10.0, 0.0)),
        ),
    }

    result = AtlasFoundationFirstEngine._build_vegetation_meshes(
        existing_trees=existing_trees,
        nature_data=nature_data,
        coordinate_engine=_VegetationCoordinateEngine(),
        terrain_mesh=terrain_mesh,
        debug=False,
    )

    assert len(result["tree_meshes"]) == 1
    assert len(result["forest_canopy_meshes"]) == 1

    assert (
        result["forest_canopy_meshes"][0]["type"]
        == "forest_canopy_foundation"
    )


def test_engine_prepares_scene_vegetation_and_respects_castle_only():
    nature_data = {
        "trees": [
            {
                "id": "worldcover_0",
                "lat": 5.0,
                "lon": 5.0,
                "tree_type": "tree",
                "tags": {
                    "source": "worldcover",
                    "class_id": 10,
                    "resolution_m": 10,
                },
            },
        ],
        "tree_rows": [],
        "forests": [
            {
                "id": "forest_cell_0",
                "lat": 5.0,
                "lon": 5.0,
                "class_id": 10,
                "source": "worldcover",
                "resolution_m": 10,
            },
        ],
    }

    terrain_mesh = {
        "metadata": {
            "size_x_mm": 10.0,
            "size_y_mm": 10.0,
        },
        "top_points": (
            ((0.0, 0.0, 0.0), (10.0, 0.0, 0.0)),
            ((0.0, 10.0, 0.0), (10.0, 10.0, 0.0)),
        ),
    }

    normal = AtlasFoundationFirstEngine._prepare_scene_vegetation(
        existing_trees=[
            {
                "id": 100,
                "lat": 2.0,
                "lon": 2.0,
                "tree_type": "tree",
                "tags": {"source": "osm"},
            },
        ],
        nature_data=nature_data,
        coordinate_engine=_VegetationCoordinateEngine(),
        terrain_mesh=terrain_mesh,
        castle_only=False,
        debug=False,
    )

    assert len(normal["tree_meshes"]) == 1
    assert len(normal["forest_canopy_meshes"]) == 1

    castle = AtlasFoundationFirstEngine._prepare_scene_vegetation(
        existing_trees=[],
        nature_data=nature_data,
        coordinate_engine=_VegetationCoordinateEngine(),
        terrain_mesh=terrain_mesh,
        castle_only=True,
        debug=False,
    )

    assert castle["tree_meshes"] == []
    assert castle["forest_canopy_meshes"] == []


def test_engine_appends_forest_canopy_meshes_to_final_vegetation_groups():
    tree_meshes = [{"type": "tree_foundation", "id": "tree_1"}]
    canopy_meshes = [
        {
            "type": "forest_canopy_foundation",
            "surface_id": "forest_1",
        }
    ]

    result = AtlasFoundationFirstEngine._assemble_vegetation_output(
        tree_meshes=tree_meshes,
        forest_canopy_meshes=canopy_meshes,
    )

    assert result["meshes"] == [
        tree_meshes[0],
        canopy_meshes[0],
    ]
    assert result["mesh_groups"]["trees"] == tree_meshes
    assert (
        result["mesh_groups"]["forest_canopies"]
        == canopy_meshes
    )
