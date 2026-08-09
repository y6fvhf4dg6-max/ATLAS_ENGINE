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


def test_engine_merges_reader_and_nature_tree_rows():
    reader_row = {
        "id": "osm_row_1",
        "tree_type": "tree_row",
        "geometry": [
            (50.0, 7.0),
            (50.0001, 7.0001),
        ],
        "tags": {"natural": "tree_row"},
    }

    nature_row = {
        "id": "provider_row_1",
        "tree_type": "tree_row",
        "geometry": [
            (50.1, 7.1),
            (50.1001, 7.1001),
        ],
    }

    result = (
        AtlasFoundationFirstEngine
        ._resolve_vegetation_composition(
            existing_trees=[],
            existing_tree_rows=[reader_row],
            nature_data={
                "trees": [],
                "tree_rows": [nature_row],
                "forests": [],
            },
        )
    )

    assert tuple(
        item["id"] for item in result["tree_rows"]
    ) == (
        "osm_row_1",
        "provider_row_1",
    )


def test_engine_resolves_tree_rows_into_controlled_tree_members():
    tree_rows = [
        {
            "id": 800,
            "tree_type": "tree_row",
            "geometry": [
                (50.0000, 7.0000),
                (50.0001, 7.0000),
                (50.0002, 7.0000),
                (50.0003, 7.0000),
            ],
            "tags": {
                "natural": "tree_row",
            },
        },
    ]

    result = (
        AtlasFoundationFirstEngine
        ._resolve_tree_row_members(
            tree_rows=tree_rows,
            scale_ratio=5500.0,
            nozzle_diameter_mm=0.4,
        )
    )

    assert len(result) >= 2

    assert all(
        item["tree_kind"] == "park_tree_symbol"
        for item in result
    )

    assert all(
        item["tags"]["source"] == "osm_tree_row"
        for item in result
    )

    assert all(
        item["tags"]["source_tree_row_id"] == 800
        for item in result
    )


def test_engine_tree_row_members_skip_weak_rows():
    result = (
        AtlasFoundationFirstEngine
        ._resolve_tree_row_members(
            tree_rows=[
                {
                    "id": 801,
                    "tree_type": "tree_row",
                    "geometry": [
                        (50.0000, 7.0000),
                        (50.0001, 7.0000),
                        (50.0000, 7.0000),
                    ],
                    "tags": {
                        "natural": "tree_row",
                    },
                },
            ],
            scale_ratio=5500.0,
            nozzle_diameter_mm=0.4,
        )
    )

    assert result == []


def test_engine_tree_row_member_order_is_deterministic():
    rows = [
        {
            "id": 900,
            "tree_type": "tree_row",
            "geometry": [
                (50.0000, 7.0000),
                (50.0001, 7.0000),
                (50.0002, 7.0000),
            ],
            "tags": {
                "natural": "tree_row",
            },
        },
        {
            "id": 100,
            "tree_type": "tree_row",
            "geometry": [
                (50.1000, 7.1000),
                (50.1001, 7.1000),
                (50.1002, 7.1000),
            ],
            "tags": {
                "natural": "tree_row",
            },
        },
    ]

    first = (
        AtlasFoundationFirstEngine
        ._resolve_tree_row_members(
            tree_rows=rows,
            scale_ratio=5500.0,
            nozzle_diameter_mm=0.4,
        )
    )

    second = (
        AtlasFoundationFirstEngine
        ._resolve_tree_row_members(
            tree_rows=list(reversed(rows)),
            scale_ratio=5500.0,
            nozzle_diameter_mm=0.4,
        )
    )

    assert tuple(item["id"] for item in first) == tuple(
        item["id"] for item in second
    )


import pytest


@pytest.mark.parametrize(
    "nozzle_diameter_mm",
    (
        0.0,
        -0.4,
    ),
)
def test_engine_tree_row_members_reject_invalid_nozzle(
    nozzle_diameter_mm,
):
    with pytest.raises(
        ValueError,
        match="nozzle_diameter_mm must be positive",
    ):
        AtlasFoundationFirstEngine._resolve_tree_row_members(
            tree_rows=[
                {
                    "id": 1000,
                    "tree_type": "tree_row",
                    "geometry": [
                        (50.0000, 7.0000),
                        (50.0001, 7.0000),
                        (50.0002, 7.0000),
                    ],
                    "tags": {
                        "natural": "tree_row",
                    },
                },
            ],
            scale_ratio=5500.0,
            nozzle_diameter_mm=nozzle_diameter_mm,
        )


def test_engine_vegetation_result_exposes_tree_row_member_count():
    existing_trees = []

    nature_data = {
        "trees": [],
        "tree_rows": [
            {
                "id": 1100,
                "tree_type": "tree_row",
                "geometry": [
                    (50.0000, 7.0000),
                    (50.0001, 7.0000),
                    (50.0002, 7.0000),
                ],
                "tags": {
                    "natural": "tree_row",
                },
            },
        ],
        "forests": [],
    }

    terrain_mesh = {
        "metadata": {
            "size_x_mm": 200.0,
            "size_y_mm": 200.0,
        },
        "top_points": (
            (
                (0.0, 0.0, 0.0),
                (200.0, 0.0, 0.0),
            ),
            (
                (0.0, 200.0, 0.0),
                (200.0, 200.0, 0.0),
            ),
        ),
    }

    result = AtlasFoundationFirstEngine._build_vegetation_meshes(
        existing_trees=existing_trees,
        nature_data=nature_data,
        coordinate_engine=_VegetationCoordinateEngine(),
        terrain_mesh=terrain_mesh,
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
        debug=False,
    )

    assert result["tree_row_member_count"] == len(
        result["tree_row_members"]
    )
    assert result["tree_row_member_count"] >= 2


def test_engine_tree_row_members_preserve_adjacent_structure_context():
    result = (
        AtlasFoundationFirstEngine
        ._resolve_tree_row_members(
            tree_rows=[
                {
                    "id": 1200,
                    "tree_type": "tree_row",
                    "geometry": [
                        (50.0000, 7.0000),
                        (50.0003, 7.0000),
                    ],
                    "tags": {
                        "natural": "tree_row",
                    },
                },
            ],
            roads=[
                {
                    "id": 2200,
                    "geometry": [
                        (50.0000, 7.00005),
                        (50.0003, 7.00005),
                    ],
                    "tags": {
                        "highway": "residential",
                    },
                },
            ],
            pedestrian_paths=[],
            scale_ratio=5500.0,
            nozzle_diameter_mm=0.4,
        )
    )

    assert result

    for member in result:
        assert (
            member["tags"]["adjacent_feature_type"]
            == "road"
        )
        assert (
            member["tags"]["adjacent_feature_id"]
            == 2200
        )
        assert (
            member["tags"]["tree_row_relationship"]
            == "parallel"
        )


def test_build_vegetation_meshes_routes_road_context_to_tree_row_members():
    nature_data = {
        "trees": [],
        "tree_rows": [
            {
                "id": 1300,
                "tree_type": "tree_row",
                "geometry": [
                    (50.0000, 7.0000),
                    (50.0003, 7.0000),
                ],
                "tags": {
                    "natural": "tree_row",
                },
            },
        ],
        "forests": [],
    }

    result = AtlasFoundationFirstEngine._build_vegetation_meshes(
        existing_trees=[],
        nature_data=nature_data,
        roads=[
            {
                "id": 2300,
                "geometry": [
                    (50.0000, 7.00005),
                    (50.0003, 7.00005),
                ],
                "tags": {
                    "highway": "residential",
                },
            },
        ],
        pedestrian_paths=[],
        coordinate_engine=_VegetationCoordinateEngine(),
        terrain_mesh={
            "top_points": (
                (
                    (0.0, 0.0, 0.0),
                    (200.0, 0.0, 0.0),
                ),
                (
                    (0.0, 200.0, 0.0),
                    (200.0, 200.0, 0.0),
                ),
            ),
        },
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
        debug=False,
    )

    assert result["tree_row_members"]

    for member in result["tree_row_members"]:
        assert (
            member["tags"]["adjacent_feature_id"]
            == 2300
        )


def test_engine_applies_semantic_surface_texture_by_park_source_identity():
    parks = [
        {
            "id": 8101,
            "geometry": [
                (20.0, 20.0),
                (21.35, 20.0),
                (21.35, 21.35),
                (20.0, 21.35),
            ],
            "park_type": "place:square",
            "tags": {
                "place": "square",
            },
        },
        {
            "id": 8102,
            "geometry": [
                (30.0, 30.0),
                (31.35, 30.0),
                (31.35, 31.35),
                (30.0, 31.35),
            ],
            "park_type": "natural:scrub",
            "tags": {
                "natural": "scrub",
            },
        },
    ]

    park_meshes = [
        {
            "type": "park_foundation",
            "source_id": 8102,
            "bottom": [
                (30.0, 30.0, 1.0),
                (31.35, 30.0, 1.0),
                (31.35, 31.35, 1.0),
                (30.0, 31.35, 1.0),
            ],
            "top": [
                (30.0, 30.0, 1.3),
                (31.35, 30.0, 1.3),
                (31.35, 31.35, 1.3),
                (30.0, 31.35, 1.3),
            ],
            "walls": [],
            "triangles": [],
        },
        {
            "type": "park_foundation",
            "source_id": 8101,
            "bottom": [
                (20.0, 20.0, 1.0),
                (21.35, 20.0, 1.0),
                (21.35, 21.35, 1.0),
                (20.0, 21.35, 1.0),
            ],
            "top": [
                (20.0, 20.0, 1.3),
                (21.35, 20.0, 1.3),
                (21.35, 21.35, 1.3),
                (20.0, 21.35, 1.3),
            ],
            "walls": [],
            "triangles": [],
        },
    ]

    result = (
        AtlasFoundationFirstEngine
        ._apply_semantic_surface_textures(
            park_meshes=park_meshes,
            parks=parks,
            pedestrian_paths=[],
        )
    )

    by_id = {
        mesh["source_id"]: mesh
        for mesh in result
    }

    assert (
        by_id[8101]["semantic_surface_texture"]
        ["surface_role"]
        == "plaza_ground"
    )

    assert (
        by_id[8101]["semantic_surface_texture"]
        ["texture_language"]
        == "paving"
    )

    assert (
        "semantic_surface_texture"
        not in by_id[8102]
    )


def test_engine_semantic_surface_textures_use_dense_terrain_following_mesh():
    parks = [
        {
            "id": 9101,
            "geometry": [
                (20.0, 20.0),
                (32.0, 20.0),
                (32.0, 32.0),
                (20.0, 32.0),
            ],
            "park_type": "place:square",
            "tags": {
                "place": "square",
            },
        },
    ]

    park_meshes = [
        {
            "type": "park_foundation",
            "source_id": 9101,
            "bottom": [
                (20.0, 20.0, 1.0),
                (32.0, 20.0, 1.0),
                (32.0, 32.0, 1.0),
                (20.0, 32.0, 1.0),
            ],
            "top": [
                (20.0, 20.0, 1.30),
                (32.0, 20.0, 1.30),
                (32.0, 32.0, 1.30),
                (20.0, 32.0, 1.30),
            ],
            "walls": [],
            "triangles": [],
        },
    ]

    terrain_mesh = {
        "top_points": [
            [
                (0.0, 0.0, 1.0),
                (200.0, 0.0, 1.0),
            ],
            [
                (0.0, 200.0, 1.0),
                (200.0, 200.0, 1.0),
            ],
        ],
        "metadata": {
            "size_x_mm": 200.0,
            "size_y_mm": 200.0,
            "size_mm": 200.0,
        },
    }

    result = (
        AtlasFoundationFirstEngine
        ._apply_semantic_surface_textures(
            park_meshes=park_meshes,
            parks=parks,
            pedestrian_paths=[],
            terrain_mesh=terrain_mesh,
        )
    )

    assert len(result) == 1

    mesh = result[0]

    assert mesh["source_id"] == 9101
    assert mesh["surface_texture_enabled"] is True
    assert len(mesh["top"]) > 4
    assert mesh["placement_mode"] == "terrain_following"
    assert (
        mesh["semantic_surface_texture"]["texture_language"]
        == "paving"
    )


def test_build_vegetation_meshes_passes_cartographic_context_to_tree_builder(
    monkeypatch,
):
    from CORE.atlas_lod_level_catalog import (
        AtlasLoDLevelCatalog,
    )

    captured = {}

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_engine."
        "AtlasTreeFoundationBuilder.build_trees",
        lambda **kwargs: (
            captured.update(kwargs)
            or []
        ),
    )

    monkeypatch.setattr(
        "CORE.atlas_foundation_first_engine."
        "AtlasForestCanopyFoundationBuilder.build",
        lambda **kwargs: [],
    )

    lod_level = AtlasLoDLevelCatalog.resolve(2)

    AtlasFoundationFirstEngine._build_vegetation_meshes(
        existing_trees=[
            {
                "id": 9100,
                "lat": 50.0,
                "lon": 7.0,
                "tree_type": "tree",
                "tree_kind": "park_tree_symbol",
                "tags": {
                    "natural": "tree",
                    "diameter_crown": "1.5",
                },
            },
        ],
        existing_tree_rows=[],
        nature_data={
            "trees": [],
            "tree_rows": [],
            "forests": [],
        },
        roads=[],
        pedestrian_paths=[],
        coordinate_engine=_VegetationCoordinateEngine(),
        terrain_mesh=object(),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.60,
        cartographic_product_size_mm=150.0,
        cartographic_lod_level=lod_level,
        debug=False,
    )

    assert captured[
        "cartographic_product_size_mm"
    ] == 150.0

    assert captured[
        "cartographic_nozzle_diameter_mm"
    ] == 0.60

    assert (
        captured[
            "cartographic_lod_level"
        ]
        is lod_level
    )
