from CORE.atlas_product_color_preview_renderer import (
    AtlasProductColorPreviewRenderer,
)
from CORE.atlas_product_preview_material_profile import (
    AtlasProductPreviewMaterialProfile,
)
from CORE.atlas_wall_frame_spec import AtlasWallFrameSpec


def _mesh(mesh_type, x, y, z):
    return {
        "type": mesh_type,
        "triangles": [
            (
                (x, y, z),
                (x + 1.0, y, z),
                (x, y + 1.0, z),
            ),
        ],
    }


def _city_result():
    return {
        "terrain_size_x_mm": 100.0,
        "terrain_size_y_mm": 120.0,
        "mesh_groups": {
            "terrain": [_mesh("terrain_closed_slab", 0.0, 0.0, 0.0)],
            "buildings": [_mesh("building", 10.0, 20.0, 0.8)],
            "roads": [_mesh("road", 30.0, 40.0, 0.4)],
            "parks": [_mesh("green_area", 50.0, 60.0, 0.3)],
            "trees": [_mesh("tree", 70.0, 80.0, 0.5)],
            "waters": [_mesh("water", 90.0, 100.0, 0.2)],
        },
    }


def test_renderer_builds_colored_batches_from_engine_mesh_groups():
    profile = AtlasProductPreviewMaterialProfile.competitor_comparison_v1()

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=_city_result(),
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=profile,
    )

    assert scene["type"] == "product_color_preview_scene"
    assert scene["profile_name"] == "COMPETITOR_COMPARISON_V1"

    batches = scene["material_batches"]

    assert batches["frame"]["rgb"] == profile.frame_rgb
    assert batches["terrain"]["rgb"] == profile.terrain_rgb
    assert batches["buildings"]["rgb"] == profile.building_rgb
    assert batches["roads"]["rgb"] == profile.road_rgb
    assert batches["parks"]["rgb"] == profile.green_rgb
    assert batches["trees"]["rgb"] == profile.tree_rgb
    assert batches["water"]["rgb"] == profile.water_rgb

    assert len(batches["frame"]["meshes"]) == 1
    assert len(batches["terrain"]["meshes"]) == 1
    assert len(batches["buildings"]["meshes"]) == 1
    assert len(batches["roads"]["meshes"]) == 1
    assert len(batches["parks"]["meshes"]) == 1
    assert len(batches["trees"]["meshes"]) == 1
    assert len(batches["water"]["meshes"]) == 1


def test_renderer_centers_city_meshes_inside_frame():
    profile = AtlasProductPreviewMaterialProfile.competitor_comparison_v1()

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=_city_result(),
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=profile,
    )

    terrain_mesh = scene["material_batches"]["terrain"]["meshes"][0]
    first_vertex = terrain_mesh["triangles"][0][0]

    assert scene["city_offset_x_mm"] == -50.0
    assert scene["city_offset_y_mm"] == -60.0
    assert first_vertex == (-50.0, -60.0, 0.0)


def test_renderer_does_not_modify_original_city_result():
    city_result = _city_result()
    original_vertex = (
        city_result["mesh_groups"]["terrain"][0]["triangles"][0][0]
    )

    AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=(
            AtlasProductPreviewMaterialProfile.competitor_comparison_v1()
        ),
    )

    assert (
        city_result["mesh_groups"]["terrain"][0]["triangles"][0][0]
        == original_vertex
    )


def test_renderer_maps_engine_waters_group_to_water_material_batch():
    city_result = _city_result()
    city_result["mesh_groups"]["waters"] = [
        _mesh("water", 90.0, 100.0, 0.2),
    ]

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=(
            AtlasProductPreviewMaterialProfile.competitor_comparison_v1()
        ),
    )

    assert len(scene["material_batches"]["water"]["meshes"]) == 1



def test_renderer_splits_semantic_building_walls_and_roofs():
    wall_triangle = (
        (10.0, 20.0, 0.8),
        (11.0, 20.0, 0.8),
        (10.0, 20.0, 5.0),
    )
    roof_triangle = (
        (10.0, 20.0, 5.0),
        (11.0, 20.0, 5.0),
        (10.0, 21.0, 5.0),
    )

    city_result = _city_result()
    city_result["mesh_groups"]["buildings"] = [
        {
            "type": "building",
            "triangles": [wall_triangle, roof_triangle],
            "building_wall_triangles": [wall_triangle],
            "building_roof_triangles": [roof_triangle],
        },
    ]

    profile = AtlasProductPreviewMaterialProfile.competitor_comparison_v1()

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=profile,
    )

    batches = scene["material_batches"]

    assert batches["building_walls"]["rgb"] == profile.building_wall_rgb
    assert batches["building_roofs"]["rgb"] == profile.building_roof_rgb
    assert len(batches["building_walls"]["meshes"]) == 1
    assert len(batches["building_roofs"]["meshes"]) == 1
    assert batches["buildings"]["meshes"] == []


def test_renderer_adds_optional_label_plate_and_text_material_batches():
    from CORE.atlas_label_plate_spec import AtlasLabelPlateSpec
    from CORE.atlas_label_text_spec import AtlasLabelTextSpec

    profile = AtlasProductPreviewMaterialProfile.competitor_comparison_v1()

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=_city_result(),
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=profile,
        label_plate_spec=AtlasLabelPlateSpec(),
        label_text_spec=AtlasLabelTextSpec(
            primary_text="KÖLN",
            secondary_text="2001",
        ),
    )

    batches = scene["material_batches"]

    assert batches["label_plate"]["rgb"] == profile.label_plate_rgb
    assert batches["label_text"]["rgb"] == profile.label_text_rgb

    assert len(batches["label_plate"]["meshes"]) == 1
    assert len(batches["label_text"]["meshes"]) == 2

    assert batches["label_plate"]["meshes"][0]["type"] == "label_plate"
    assert batches["label_text"]["meshes"][0]["type"] == "label_text"
    assert batches["label_text"]["meshes"][1]["type"] == "label_text"

def test_renderer_uses_integrated_hidden_hanger_frame():
    profile = AtlasProductPreviewMaterialProfile.competitor_comparison_v1()

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=_city_result(),
        frame_spec=AtlasWallFrameSpec(
            outer_width_mm=150.0,
            outer_height_mm=150.0,
            frame_width_mm=8.0,
        ),
        frame_depth_mm=6.0,
        material_profile=profile,
    )

    frame_mesh = scene["material_batches"]["frame"]["meshes"][0]

    assert frame_mesh["type"] == "wall_frame_with_hidden_hangers"


def _open_edge_count(triangles):
    edge_counts = {}

    def point_key(point):
        return tuple(round(float(value), 6) for value in point)

    def edge_key(first, second):
        first = point_key(first)
        second = point_key(second)
        return (
            (first, second)
            if first <= second
            else (second, first)
        )

    for first, second, third in triangles:
        for edge in (
            edge_key(first, second),
            edge_key(second, third),
            edge_key(third, first),
        ):
            edge_counts[edge] = edge_counts.get(edge, 0) + 1

    return sum(
        count == 1
        for count in edge_counts.values()
    )


def test_renderer_builds_closed_print_solids_for_flat_roof_colors():
    bottom = [
        (10.0, 20.0, 0.8),
        (12.0, 20.0, 0.8),
        (12.0, 22.0, 0.8),
        (10.0, 22.0, 0.8),
    ]
    top = [
        (10.0, 20.0, 5.0),
        (12.0, 20.0, 5.0),
        (12.0, 22.0, 5.0),
        (10.0, 22.0, 5.0),
    ]

    bottom_triangles = [
        (bottom[0], bottom[2], bottom[1]),
        (bottom[0], bottom[3], bottom[2]),
    ]
    roof_triangles = [
        (top[0], top[1], top[2]),
        (top[0], top[2], top[3]),
    ]
    wall_triangles = [
        (bottom[0], bottom[1], top[1]),
        (bottom[0], top[1], top[0]),
        (bottom[1], bottom[2], top[2]),
        (bottom[1], top[2], top[1]),
        (bottom[2], bottom[3], top[3]),
        (bottom[2], top[3], top[2]),
        (bottom[3], bottom[0], top[0]),
        (bottom[3], top[0], top[3]),
    ]

    city_result = _city_result()
    city_result["mesh_groups"]["buildings"] = [
        {
            "type": "building",
            "bottom": bottom,
            "top": top,
            "triangles": [
                *bottom_triangles,
                *roof_triangles,
                *wall_triangles,
            ],
            "building_wall_triangles": wall_triangles,
            "building_roof_triangles": roof_triangles,
            "building_flat_roof_triangles": roof_triangles,
            "foundation_z": 0.8,
        },
    ]

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=(
            AtlasProductPreviewMaterialProfile.koeln_premium_v1()
        ),
    )

    wall_mesh = scene["material_batches"][
        "building_walls"
    ]["meshes"][0]
    roof_mesh = scene["material_batches"][
        "building_roofs"
    ]["meshes"][0]

    assert _open_edge_count(wall_mesh["triangles"]) == 0
    assert _open_edge_count(roof_mesh["triangles"]) == 0


def test_renderer_builds_closed_print_solids_for_gable_roof_colors():
    bottom = [
        (10.0, 20.0, 0.8),
        (12.0, 20.0, 0.8),
        (12.0, 22.0, 0.8),
        (10.0, 22.0, 0.8),
    ]
    top = [
        (10.0, 20.0, 5.0),
        (12.0, 20.0, 5.0),
        (12.0, 22.0, 5.0),
        (10.0, 22.0, 5.0),
    ]

    wall_triangles = [
        (bottom[0], bottom[1], top[1]),
        (bottom[0], top[1], top[0]),
        (bottom[1], bottom[2], top[2]),
        (bottom[1], top[2], top[1]),
        (bottom[2], bottom[3], top[3]),
        (bottom[2], top[3], top[2]),
        (bottom[3], bottom[0], top[0]),
        (bottom[3], top[0], top[3]),
    ]
    bottom_triangles = [
        (bottom[0], bottom[2], bottom[1]),
        (bottom[0], bottom[3], bottom[2]),
    ]

    ridge_start = (10.0, 21.0, 6.0)
    ridge_end = (12.0, 21.0, 6.0)

    roof_triangles = [
        (top[0], top[1], ridge_end),
        (top[0], ridge_end, ridge_start),
        (top[3], ridge_start, ridge_end),
        (top[3], ridge_end, top[2]),
        (top[0], ridge_start, top[3]),
        (top[1], top[2], ridge_end),
        (top[0], top[3], top[2]),
        (top[0], top[2], top[1]),
    ]

    city_result = _city_result()
    city_result["mesh_groups"]["buildings"] = [
        {
            "type": "building",
            "bottom": bottom,
            "top": top,
            "triangles": [
                *bottom_triangles,
                *wall_triangles,
                *roof_triangles,
            ],
            "building_wall_triangles": wall_triangles,
            "building_roof_triangles": roof_triangles,
            "building_gable_roof_triangles": roof_triangles,
            "building_flat_roof_triangles": [],
            "foundation_z": 0.8,
            "body_top_z": 5.0,
            "roof_top_z": 6.0,
            "roof_geometry": "gable",
        },
    ]

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=(
            AtlasProductPreviewMaterialProfile.koeln_premium_v1()
        ),
    )

    wall_mesh = scene["material_batches"][
        "building_walls"
    ]["meshes"][0]
    roof_mesh = scene["material_batches"][
        "building_roofs"
    ]["meshes"][0]

    assert _open_edge_count(wall_mesh["triangles"]) == 0
    assert _open_edge_count(roof_mesh["triangles"]) == 0


def test_renderer_builds_closed_print_solids_for_hipped_roof_colors():
    bottom = [
        (10.0, 20.0, 0.8),
        (12.0, 20.0, 0.8),
        (12.0, 22.0, 0.8),
        (10.0, 22.0, 0.8),
    ]
    top = [
        (10.0, 20.0, 5.0),
        (12.0, 20.0, 5.0),
        (12.0, 22.0, 5.0),
        (10.0, 22.0, 5.0),
    ]

    wall_triangles = [
        (bottom[0], bottom[1], top[1]),
        (bottom[0], top[1], top[0]),
        (bottom[1], bottom[2], top[2]),
        (bottom[1], top[2], top[1]),
        (bottom[2], bottom[3], top[3]),
        (bottom[2], top[3], top[2]),
        (bottom[3], bottom[0], top[0]),
        (bottom[3], top[0], top[3]),
    ]
    bottom_triangles = [
        (bottom[0], bottom[2], bottom[1]),
        (bottom[0], bottom[3], bottom[2]),
    ]

    apex = (11.0, 21.0, 6.0)
    roof_triangles = [
        (top[0], top[1], apex),
        (top[1], top[2], apex),
        (top[2], top[3], apex),
        (top[3], top[0], apex),
    ]

    city_result = _city_result()
    city_result["mesh_groups"]["buildings"] = [
        {
            "type": "building",
            "bottom": bottom,
            "top": top,
            "triangles": [
                *bottom_triangles,
                *wall_triangles,
                *roof_triangles,
            ],
            "building_wall_triangles": wall_triangles,
            "building_roof_triangles": roof_triangles,
            "building_hipped_roof_triangles": roof_triangles,
            "building_flat_roof_triangles": [],
            "foundation_z": 0.8,
            "body_top_z": 5.0,
            "roof_top_z": 6.0,
            "roof_apex": apex,
            "roof_geometry": "hipped",
        },
    ]

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=(
            AtlasProductPreviewMaterialProfile.koeln_premium_v1()
        ),
    )

    wall_mesh = scene["material_batches"][
        "building_walls"
    ]["meshes"][0]
    roof_mesh = scene["material_batches"][
        "building_roofs"
    ]["meshes"][0]

    assert _open_edge_count(wall_mesh["triangles"]) == 0
    assert _open_edge_count(roof_mesh["triangles"]) == 0



def test_flat_roof_color_solid_uses_actual_bottom_ring_z():
    bottom_z = 1.4
    foundation_z = 0.8

    bottom = [
        (10.0, 20.0, bottom_z),
        (12.0, 20.0, bottom_z),
        (12.0, 22.0, bottom_z),
        (10.0, 22.0, bottom_z),
    ]
    top = [
        (10.0, 20.0, 5.0),
        (12.0, 20.0, 5.0),
        (12.0, 22.0, 5.0),
        (10.0, 22.0, 5.0),
    ]

    wall_triangles = [
        (bottom[0], bottom[1], top[1]),
        (bottom[0], top[1], top[0]),
        (bottom[1], bottom[2], top[2]),
        (bottom[1], top[2], top[1]),
        (bottom[2], bottom[3], top[3]),
        (bottom[2], top[3], top[2]),
        (bottom[3], bottom[0], top[0]),
        (bottom[3], top[0], top[3]),
    ]
    roof_triangles = [
        (top[0], top[1], top[2]),
        (top[0], top[2], top[3]),
    ]

    city_result = _city_result()
    city_result["mesh_groups"]["buildings"] = [
        {
            "type": "building",
            "bottom": bottom,
            "top": top,
            "triangles": [
                *wall_triangles,
                *roof_triangles,
            ],
            "building_wall_triangles": wall_triangles,
            "building_roof_triangles": roof_triangles,
            "building_flat_roof_triangles": roof_triangles,
            "foundation_z": foundation_z,
        },
    ]

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=(
            AtlasProductPreviewMaterialProfile.koeln_premium_v1()
        ),
    )

    wall_mesh = scene["material_batches"][
        "building_walls"
    ]["meshes"][0]

    assert _open_edge_count(wall_mesh["triangles"]) == 0


def test_gable_roof_color_solid_uses_actual_bottom_ring_z():
    bottom_z = 1.4
    foundation_z = 0.8

    bottom = [
        (10.0, 20.0, bottom_z),
        (12.0, 20.0, bottom_z),
        (12.0, 22.0, bottom_z),
        (10.0, 22.0, bottom_z),
    ]
    top = [
        (10.0, 20.0, 5.0),
        (12.0, 20.0, 5.0),
        (12.0, 22.0, 5.0),
        (10.0, 22.0, 5.0),
    ]

    wall_triangles = [
        (bottom[0], bottom[1], top[1]),
        (bottom[0], top[1], top[0]),
        (bottom[1], bottom[2], top[2]),
        (bottom[1], top[2], top[1]),
        (bottom[2], bottom[3], top[3]),
        (bottom[2], top[3], top[2]),
        (bottom[3], bottom[0], top[0]),
        (bottom[3], top[0], top[3]),
    ]

    ridge_start = (10.0, 21.0, 6.0)
    ridge_end = (12.0, 21.0, 6.0)

    roof_triangles = [
        (top[0], top[1], ridge_end),
        (top[0], ridge_end, ridge_start),
        (top[3], ridge_start, ridge_end),
        (top[3], ridge_end, top[2]),
        (top[0], ridge_start, top[3]),
        (top[1], top[2], ridge_end),
        (top[0], top[3], top[2]),
        (top[0], top[2], top[1]),
    ]

    city_result = _city_result()
    city_result["mesh_groups"]["buildings"] = [
        {
            "type": "building",
            "bottom": bottom,
            "top": top,
            "triangles": [
                *wall_triangles,
                *roof_triangles,
            ],
            "building_wall_triangles": wall_triangles,
            "building_roof_triangles": roof_triangles,
            "building_flat_roof_triangles": [],
            "foundation_z": foundation_z,
            "body_top_z": 5.0,
            "roof_top_z": 6.0,
            "roof_geometry": "gable",
        },
    ]

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=(
            AtlasProductPreviewMaterialProfile.koeln_premium_v1()
        ),
    )

    wall_mesh = scene["material_batches"][
        "building_walls"
    ]["meshes"][0]

    assert _open_edge_count(wall_mesh["triangles"]) == 0


def test_renderer_excludes_same_height_building_part_fully_covered_by_parent():
    def building_mesh(
        *,
        x0,
        y0,
        x1,
        y1,
        bottom_z,
        top_z,
        source_id,
        is_building_part,
    ):
        bottom = [
            (x0, y0, bottom_z),
            (x1, y0, bottom_z),
            (x1, y1, bottom_z),
            (x0, y1, bottom_z),
        ]
        top = [
            (x0, y0, top_z),
            (x1, y0, top_z),
            (x1, y1, top_z),
            (x0, y1, top_z),
        ]

        bottom_triangles = [
            (bottom[0], bottom[2], bottom[1]),
            (bottom[0], bottom[3], bottom[2]),
        ]
        roof_triangles = [
            (top[0], top[1], top[2]),
            (top[0], top[2], top[3]),
        ]
        wall_triangles = [
            (bottom[0], bottom[1], top[1]),
            (bottom[0], top[1], top[0]),
            (bottom[1], bottom[2], top[2]),
            (bottom[1], top[2], top[1]),
            (bottom[2], bottom[3], top[3]),
            (bottom[2], top[3], top[2]),
            (bottom[3], bottom[0], top[0]),
            (bottom[3], top[0], top[3]),
        ]

        return {
            "type": "building",
            "source_id": source_id,
            "is_building_part": is_building_part,
            "bottom": bottom,
            "top": top,
            "foundation_z": bottom_z,
            "body_top_z": top_z,
            "triangles": [
                *bottom_triangles,
                *wall_triangles,
                *roof_triangles,
            ],
            "building_wall_triangles": wall_triangles,
            "building_roof_triangles": roof_triangles,
            "building_flat_roof_triangles": roof_triangles,
        }

    parent_mesh = building_mesh(
        x0=10.0,
        y0=20.0,
        x1=20.0,
        y1=30.0,
        bottom_z=0.8,
        top_z=5.0,
        source_id="parent",
        is_building_part=False,
    )
    covered_part_mesh = building_mesh(
        x0=12.0,
        y0=22.0,
        x1=18.0,
        y1=28.0,
        bottom_z=0.8,
        top_z=5.0,
        source_id="covered-part",
        is_building_part=True,
    )

    city_result = _city_result()
    city_result["mesh_groups"]["buildings"] = [
        parent_mesh,
        covered_part_mesh,
    ]

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=(
            AtlasProductPreviewMaterialProfile.koeln_premium_v1()
        ),
    )

    assert len(
        scene["material_batches"]["building_walls"]["meshes"]
    ) == 1
    assert len(
        scene["material_batches"]["building_roofs"]["meshes"]
    ) == 1


def _park_mesh(
    *,
    x0,
    y0,
    x1,
    y1,
    bottom_z,
    top_z,
    park_type,
):
    bottom = [
        (x0, y0, bottom_z),
        (x1, y0, bottom_z),
        (x1, y1, bottom_z),
        (x0, y1, bottom_z),
    ]
    top = [
        (x0, y0, top_z),
        (x1, y0, top_z),
        (x1, y1, top_z),
        (x0, y1, top_z),
    ]

    triangles = [
        (top[0], top[1], top[2]),
        (top[0], top[2], top[3]),
        (bottom[0], bottom[2], bottom[1]),
        (bottom[0], bottom[3], bottom[2]),
        (bottom[0], bottom[1], top[1]),
        (bottom[0], top[1], top[0]),
        (bottom[1], bottom[2], top[2]),
        (bottom[1], top[2], top[1]),
        (bottom[2], bottom[3], top[3]),
        (bottom[2], top[3], top[2]),
        (bottom[3], bottom[0], top[0]),
        (bottom[3], top[0], top[3]),
    ]

    return {
        "type": "park_foundation",
        "park_type": park_type,
        "bottom": bottom,
        "top": top,
        "triangles": triangles,
    }


def test_renderer_excludes_landuse_grass_fully_covered_by_leisure_park():
    city_result = _city_result()
    city_result["mesh_groups"]["parks"] = [
        _park_mesh(
            x0=10.0,
            y0=10.0,
            x1=30.0,
            y1=30.0,
            bottom_z=0.3,
            top_z=0.5,
            park_type="leisure:park",
        ),
        _park_mesh(
            x0=15.0,
            y0=15.0,
            x1=25.0,
            y1=25.0,
            bottom_z=0.35,
            top_z=0.62,
            park_type="landuse:grass",
        ),
    ]

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=(
            AtlasProductPreviewMaterialProfile.koeln_premium_v1()
        ),
    )

    assert len(
        scene["material_batches"]["parks"]["meshes"]
    ) == 1


def test_renderer_keeps_leisure_parks_that_only_share_boundary_edge():
    city_result = _city_result()
    city_result["mesh_groups"]["parks"] = [
        _park_mesh(
            x0=10.0,
            y0=10.0,
            x1=20.0,
            y1=20.0,
            bottom_z=0.3,
            top_z=0.5,
            park_type="leisure:park",
        ),
        _park_mesh(
            x0=20.0,
            y0=10.0,
            x1=30.0,
            y1=20.0,
            bottom_z=0.3,
            top_z=0.5,
            park_type="leisure:park",
        ),
    ]

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=(
            AtlasProductPreviewMaterialProfile.koeln_premium_v1()
        ),
    )

    assert len(
        scene["material_batches"]["parks"]["meshes"]
    ) == 2


def _non_manifold_edge_count(triangles):
    edge_counts = {}

    def point_key(point):
        return tuple(round(float(value), 6) for value in point)

    def edge_key(first, second):
        first = point_key(first)
        second = point_key(second)
        return (
            (first, second)
            if first <= second
            else (second, first)
        )

    for first, second, third in triangles:
        for edge in (
            edge_key(first, second),
            edge_key(second, third),
            edge_key(third, first),
        ):
            edge_counts[edge] = edge_counts.get(edge, 0) + 1

    return sum(
        count > 2
        for count in edge_counts.values()
    )


def test_renderer_removes_internal_walls_between_adjacent_same_color_parks():
    city_result = _city_result()
    city_result["mesh_groups"]["parks"] = [
        _park_mesh(
            x0=10.0,
            y0=10.0,
            x1=20.0,
            y1=20.0,
            bottom_z=0.3,
            top_z=0.5,
            park_type="leisure:park",
        ),
        _park_mesh(
            x0=20.0,
            y0=10.0,
            x1=30.0,
            y1=20.0,
            bottom_z=0.3,
            top_z=0.5,
            park_type="leisure:park",
        ),
    ]

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=(
            AtlasProductPreviewMaterialProfile.koeln_premium_v1()
        ),
    )

    park_meshes = scene["material_batches"]["parks"]["meshes"]

    assert len(park_meshes) == 2

    combined_triangles = [
        triangle
        for mesh in park_meshes
        for triangle in mesh["triangles"]
    ]

    assert _non_manifold_edge_count(combined_triangles) == 0


def test_renderer_separates_same_color_parks_touching_only_at_one_vertex():
    city_result = _city_result()
    city_result["mesh_groups"]["parks"] = [
        _park_mesh(
            x0=10.0,
            y0=10.0,
            x1=20.0,
            y1=20.0,
            bottom_z=0.3,
            top_z=0.5,
            park_type="leisure:park",
        ),
        _park_mesh(
            x0=20.0,
            y0=20.0,
            x1=30.0,
            y1=30.0,
            bottom_z=0.3,
            top_z=0.5,
            park_type="leisure:park",
        ),
    ]

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=(
            AtlasProductPreviewMaterialProfile.koeln_premium_v1()
        ),
    )

    park_meshes = scene["material_batches"]["parks"]["meshes"]

    assert len(park_meshes) == 2

    combined_triangles = [
        triangle
        for mesh in park_meshes
        for triangle in mesh["triangles"]
    ]

    assert _open_edge_count(combined_triangles) == 0
    assert _non_manifold_edge_count(combined_triangles) == 0


def test_renderer_separates_adjacent_different_height_building_color_solids():
    def building_mesh(
        *,
        x0,
        y0,
        x1,
        y1,
        bottom_z,
        top_z,
        source_id,
    ):
        bottom = [
            (x0, y0, bottom_z),
            (x1, y0, bottom_z),
            (x1, y1, bottom_z),
            (x0, y1, bottom_z),
        ]
        top = [
            (x0, y0, top_z),
            (x1, y0, top_z),
            (x1, y1, top_z),
            (x0, y1, top_z),
        ]

        bottom_triangles = [
            (bottom[0], bottom[2], bottom[1]),
            (bottom[0], bottom[3], bottom[2]),
        ]
        roof_triangles = [
            (top[0], top[1], top[2]),
            (top[0], top[2], top[3]),
        ]
        wall_triangles = [
            (bottom[0], bottom[1], top[1]),
            (bottom[0], top[1], top[0]),
            (bottom[1], bottom[2], top[2]),
            (bottom[1], top[2], top[1]),
            (bottom[2], bottom[3], top[3]),
            (bottom[2], top[3], top[2]),
            (bottom[3], bottom[0], top[0]),
            (bottom[3], top[0], top[3]),
        ]

        return {
            "type": "building",
            "source_id": source_id,
            "is_building_part": True,
            "bottom": bottom,
            "top": top,
            "foundation_z": bottom_z,
            "body_top_z": top_z,
            "triangles": [
                *bottom_triangles,
                *wall_triangles,
                *roof_triangles,
            ],
            "building_wall_triangles": wall_triangles,
            "building_roof_triangles": roof_triangles,
            "building_flat_roof_triangles": roof_triangles,
        }

    city_result = _city_result()
    city_result["mesh_groups"]["buildings"] = [
        building_mesh(
            x0=10.0,
            y0=10.0,
            x1=20.0,
            y1=20.0,
            bottom_z=0.8,
            top_z=3.0,
            source_id="lower-part",
        ),
        building_mesh(
            x0=20.0,
            y0=10.0,
            x1=30.0,
            y1=20.0,
            bottom_z=0.8,
            top_z=6.0,
            source_id="higher-part",
        ),
    ]

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=(
            AtlasProductPreviewMaterialProfile.koeln_premium_v1()
        ),
    )

    wall_meshes = scene["material_batches"][
        "building_walls"
    ]["meshes"]
    roof_meshes = scene["material_batches"][
        "building_roofs"
    ]["meshes"]

    assert len(wall_meshes) == 2
    assert len(roof_meshes) == 2

    wall_triangles = [
        triangle
        for mesh in wall_meshes
        for triangle in mesh["triangles"]
    ]
    roof_triangles = [
        triangle
        for mesh in roof_meshes
        for triangle in mesh["triangles"]
    ]

    assert _open_edge_count(wall_triangles) == 0
    assert _non_manifold_edge_count(wall_triangles) == 0
    assert _open_edge_count(roof_triangles) == 0
    assert _non_manifold_edge_count(roof_triangles) == 0
