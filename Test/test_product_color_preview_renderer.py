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
        label_plate_spec=AtlasLabelPlateSpec(
            height_mm=8.0,
        ),
        label_text_spec=AtlasLabelTextSpec(
            primary_text="KÖLN",
            secondary_text="2001",
            graduation_cap=True,
        ),
    )

    batches = scene["material_batches"]

    assert batches["label_plate"]["rgb"] == profile.label_plate_rgb
    assert batches["label_text"]["rgb"] == profile.label_text_rgb

    assert len(batches["label_plate"]["meshes"]) == 1
    assert len(batches["label_text"]["meshes"]) == 3

    assert batches["label_plate"]["meshes"][0]["type"] == "label_plate"
    assert batches["label_text"]["meshes"][0]["type"] == "label_text"
    assert batches["label_text"]["meshes"][1]["type"] == "label_text"
    assert (
        batches["label_text"]["meshes"][2]["type"]
        == "label_graduation_cap"
    )

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


def test_renderer_builds_closed_print_solids_for_skillion_roof_colors():
    bottom = [
        (10.0, 20.0, 0.8),
        (12.0, 20.0, 0.8),
        (12.0, 22.0, 0.8),
        (10.0, 22.0, 0.8),
    ]
    body_top = [
        (10.0, 20.0, 5.0),
        (12.0, 20.0, 5.0),
        (12.0, 22.0, 5.0),
        (10.0, 22.0, 5.0),
    ]
    skillion_top = [
        (10.0, 20.0, 5.0),
        (12.0, 20.0, 5.0),
        (12.0, 22.0, 6.0),
        (10.0, 22.0, 6.0),
    ]

    bottom_triangles = [
        (bottom[0], bottom[2], bottom[1]),
        (bottom[0], bottom[3], bottom[2]),
    ]
    wall_triangles = [
        (bottom[0], bottom[1], body_top[1]),
        (bottom[0], body_top[1], body_top[0]),
        (bottom[1], bottom[2], body_top[2]),
        (bottom[1], body_top[2], body_top[1]),
        (bottom[2], bottom[3], body_top[3]),
        (bottom[2], body_top[3], body_top[2]),
        (bottom[3], bottom[0], body_top[0]),
        (bottom[3], body_top[0], body_top[3]),
    ]
    roof_triangles = [
        (
            skillion_top[0],
            skillion_top[1],
            skillion_top[2],
        ),
        (
            skillion_top[0],
            skillion_top[2],
            skillion_top[3],
        ),
    ]

    city_result = _city_result()
    city_result["mesh_groups"]["buildings"] = [
        {
            "type": "building",
            "bottom": bottom,
            "top": body_top,
            "triangles": [
                *bottom_triangles,
                *wall_triangles,
                *roof_triangles,
            ],
            "building_wall_triangles": wall_triangles,
            "building_roof_triangles": roof_triangles,
            "building_skillion_roof_triangles": roof_triangles,
            "building_skillion_roof_points": skillion_top,
            "building_flat_roof_triangles": [],
            "foundation_z": 0.8,
            "body_top_z": 5.0,
            "roof_top_z": 6.0,
            "roof_geometry": "skillion",
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


def test_renderer_excludes_playground_fully_covered_by_leisure_park():
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
            bottom_z=0.3,
            top_z=0.5,
            park_type="leisure:playground",
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

    assert len(park_meshes) == 1
    assert park_meshes[0]["park_type"] == "leisure:park"



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


def test_renderer_highlights_selected_building_entirely_in_red():
    selected_source_id = 125014714

    selected_wall = (
        (10.0, 20.0, 0.8),
        (11.0, 20.0, 0.8),
        (10.0, 20.0, 5.0),
    )
    selected_roof = (
        (10.0, 20.0, 5.0),
        (11.0, 20.0, 5.0),
        (10.0, 21.0, 5.0),
    )

    normal_wall = (
        (20.0, 20.0, 0.8),
        (21.0, 20.0, 0.8),
        (20.0, 20.0, 5.0),
    )
    normal_roof = (
        (20.0, 20.0, 5.0),
        (21.0, 20.0, 5.0),
        (20.0, 21.0, 5.0),
    )

    city_result = _city_result()
    city_result["mesh_groups"]["buildings"] = [
        {
            "type": "building",
            "source_id": selected_source_id,
            "triangles": [
                selected_wall,
                selected_roof,
            ],
            "building_wall_triangles": [selected_wall],
            "building_roof_triangles": [selected_roof],
        },
        {
            "type": "building",
            "source_id": 999,
            "triangles": [
                normal_wall,
                normal_roof,
            ],
            "building_wall_triangles": [normal_wall],
            "building_roof_triangles": [normal_roof],
        },
    ]

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=(
            AtlasProductPreviewMaterialProfile.koeln_premium_v1()
        ),
        highlighted_building_source_ids={
            selected_source_id,
        },
    )

    batches = scene["material_batches"]

    assert len(batches["building_walls"]["meshes"]) == 1
    assert len(batches["building_roofs"]["meshes"]) == 2

    selected_red_meshes = [
        mesh
        for mesh in batches["building_roofs"]["meshes"]
        if mesh.get("source_id") == selected_source_id
    ]

    assert len(selected_red_meshes) == 1
    assert selected_red_meshes[0]["type"] == "highlighted_building"

    expected_triangles = [
        tuple(
            (
                x - 50.0,
                y - 60.0,
                z,
            )
            for x, y, z in triangle
        )
        for triangle in (
            selected_wall,
            selected_roof,
        )
    ]

    assert (
        selected_red_meshes[0]["triangles"]
        == expected_triangles
    )

    assert all(
        mesh.get("source_id") != selected_source_id
        for mesh in batches["building_walls"]["meshes"]
    )


def test_renderer_maps_landmarks_to_separate_material_batch():
    city_result = _city_result()
    city_result["mesh_groups"]["landmarks"] = [
        _mesh("ancient_theatre", 25.0, 35.0, 1.2),
    ]

    profile = AtlasProductPreviewMaterialProfile.competitor_comparison_v1()

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=profile,
    )

    landmarks = scene["material_batches"]["landmarks"]

    assert landmarks["rgb"] == profile.landmark_rgb
    assert len(landmarks["meshes"]) == 1
    assert landmarks["meshes"][0]["type"] == "ancient_theatre"



def test_renderer_routes_highlighted_building_components_to_roof_batch():
    city_result = _city_result()
    city_result["mesh_groups"]["buildings"] = [
        {
            "type": "liedberg_gate_tower",
            "source_id": 143975871,
            "architectural_role": "gate_tower_body",
            "triangles": [
                (
                    (10.0, 20.0, 1.0),
                    (11.0, 20.0, 1.0),
                    (10.0, 21.0, 2.0),
                ),
            ],
        },
    ]

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=(
            AtlasProductPreviewMaterialProfile.koeln_premium_v1()
        ),
        highlighted_building_source_ids={
            143975871,
        },
    )

    batches = scene["material_batches"]

    assert batches["buildings"]["meshes"] == []
    assert len(batches["building_roofs"]["meshes"]) == 1
    assert (
        batches["building_roofs"]["meshes"][0]["source_id"]
        == 143975871
    )


def test_renderer_routes_selected_landmark_to_roof_batch():
    city_result = _city_result()
    city_result["mesh_groups"]["landmarks"] = [
        {
            "type": "tower",
            "landmark_id": 143975860,
            "architectural_role": "muehlenturm_ruin_body",
            "triangles": [
                (
                    (10.0, 20.0, 1.0),
                    (11.0, 20.0, 1.0),
                    (10.0, 21.0, 2.0),
                ),
            ],
        },
    ]

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=(
            AtlasProductPreviewMaterialProfile.koeln_premium_v1()
        ),
        highlighted_landmark_ids={
            143975860,
        },
    )

    batches = scene["material_batches"]

    assert batches["landmarks"]["meshes"] == []
    assert len(batches["building_roofs"]["meshes"]) == 1
    assert (
        batches["building_roofs"]["meshes"][0]["landmark_id"]
        == 143975860
    )


def test_forest_canopies_route_to_tree_color_batch():
    assert (
        AtlasProductColorPreviewRenderer.GROUP_TO_BATCH[
            "forest_canopies"
        ]
        == "trees"
    )


def test_renderer_places_forest_canopy_meshes_in_tree_material_batch():
    city_result = _city_result()
    canopy = _mesh(
        "forest_canopy_foundation",
        72.0,
        82.0,
        0.3,
    )
    city_result["mesh_groups"]["forest_canopies"] = [
        canopy,
    ]

    profile = (
        AtlasProductPreviewMaterialProfile
        .competitor_comparison_v1()
    )

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=profile,
    )

    tree_meshes = scene["material_batches"]["trees"]["meshes"]

    assert len(tree_meshes) == 2
    assert any(
        mesh["type"] == "forest_canopy_foundation"
        for mesh in tree_meshes
    )
    assert scene["material_batches"]["trees"]["rgb"] == (
        profile.tree_rgb
    )


def test_preview_scene_exposes_semantic_material_hierarchy_metadata():
    profile = (
        AtlasProductPreviewMaterialProfile
        .koeln_premium_v1()
    )

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result={
            "terrain_size_x_mm": 150.0,
            "terrain_size_y_mm": 150.0,
            "mesh_groups": {
                "terrain": [],
                "buildings": [],
                "roads": [],
                "parks": [],
                "elevated_areas": [],
                "artworks": [],
                "landmarks": [],
                "trees": [],
                "forest_canopies": [],
                "waters": [],
                "castle_walls": [],
                "castle_shells": [],
                "castle_tower_caps": [],
            },
        },
        frame_spec=AtlasWallFrameSpec(
            outer_width_mm=170.0,
            outer_height_mm=170.0,
            frame_width_mm=10.0,
        ),
        frame_depth_mm=6.0,
        material_profile=profile,
    )

    assert (
        scene["semantic_material_hierarchy"][
            "profile_name"
        ]
        == "KOELN_PREMIUM_V1"
    )

    batches = scene["material_batches"]

    assert (
        batches["terrain"]["semantic_role"]
        == "terrain"
    )
    assert (
        batches["building_walls"]["semantic_role"]
        == "generic_building"
    )
    assert (
        batches["building_roofs"]["semantic_role"]
        == "generic_building_roof"
    )
    assert (
        batches["roads"]["semantic_role"]
        == "roads_hardscape"
    )
    assert (
        batches["parks"]["semantic_role"]
        == "vegetation"
    )
    assert (
        batches["trees"]["semantic_role"]
        == "vegetation"
    )
    assert (
        batches["water"]["semantic_role"]
        == "water"
    )

    assert (
        batches["terrain"]["physical_material"]
        == batches["building_walls"][
            "physical_material"
        ]
    )

    assert (
        batches["roads"]["physical_material"]
        == batches["frame"]["physical_material"]
        == batches["label_text"]["physical_material"]
    )

    assert (
        batches["roads"]["physical_material"]
        != batches["terrain"]["physical_material"]
    )

    assert (
        batches["terrain"]["surface_treatment"]
        != batches["building_walls"][
            "surface_treatment"
        ]
    )


def test_preview_scene_preserves_production_composition_metadata():
    profile = (
        AtlasProductPreviewMaterialProfile
        .koeln_premium_v1()
    )

    city_result = {
        "terrain_size_x_mm": 150.0,
        "terrain_size_y_mm": 150.0,
        "mesh_groups": {
            "terrain": [],
            "buildings": [],
            "roads": [],
            "parks": [],
            "elevated_areas": [],
            "artworks": [],
            "landmarks": [],
            "trees": [],
            "forest_canopies": [],
            "waters": [],
            "castle_walls": [],
            "castle_shells": [],
            "castle_tower_caps": [],
        },
        "resolved_scene_morphology": "dense_urban",
        "effective_scene_morphology": "historic_core",
        "morphology_composition_policy": {
            "road_emphasis": 0.90,
            "landmark_emphasis": 1.00,
        },
        "city_composition_lod": {
            "scene_morphology": "historic_core",
            "product_size_mm": 150.0,
            "decisions": {
                "road_1": {
                    "retain": True,
                },
            },
        },
        "city_composition_suppressed_meshes": 3,
    }

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(
            outer_width_mm=170.0,
            outer_height_mm=170.0,
            frame_width_mm=10.0,
        ),
        frame_depth_mm=6.0,
        material_profile=profile,
    )

    assert (
        scene["resolved_scene_morphology"]
        == city_result["resolved_scene_morphology"]
    )

    assert (
        scene["effective_scene_morphology"]
        == city_result["effective_scene_morphology"]
    )

    assert (
        scene["morphology_composition_policy"]
        is city_result["morphology_composition_policy"]
    )

    assert (
        scene["city_composition_lod"]
        is city_result["city_composition_lod"]
    )

    assert (
        scene["city_composition_suppressed_meshes"]
        == 3
    )


def test_preview_uses_production_filtered_mesh_groups_without_reintroducing_suppressed_geometry():
    profile = (
        AtlasProductPreviewMaterialProfile
        .koeln_premium_v1()
    )

    retained_road = {
        "type": "road_foundation",
        "source_id": 1001,
        "triangles": [
            (
                (0.0, 0.0, 0.2),
                (1.0, 0.0, 0.2),
                (0.0, 1.0, 0.2),
            ),
        ],
    }

    city_result = {
        "terrain_size_x_mm": 150.0,
        "terrain_size_y_mm": 150.0,
        "mesh_groups": {
            "terrain": [],
            "buildings": [],
            "roads": [retained_road],
            "parks": [],
            "elevated_areas": [],
            "artworks": [],
            "landmarks": [],
            "trees": [],
            "forest_canopies": [],
            "waters": [],
            "castle_walls": [],
            "castle_shells": [],
            "castle_tower_caps": [],
        },
        "city_composition_lod": {
            "decisions": {
                "road_1001": {
                    "retain": True,
                },
                "road_2002": {
                    "retain": False,
                },
            },
        },
        "city_composition_suppressed_meshes": 1,
    }

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(
            outer_width_mm=170.0,
            outer_height_mm=170.0,
            frame_width_mm=10.0,
        ),
        frame_depth_mm=6.0,
        material_profile=profile,
    )

    preview_roads = scene[
        "material_batches"
    ]["roads"]["meshes"]

    assert len(preview_roads) == 1
    assert (
        preview_roads[0]["source_id"]
        == 1001
    )

    assert all(
        mesh.get("source_id") != 2002
        for batch in scene["material_batches"].values()
        for mesh in batch["meshes"]
        if isinstance(mesh, dict)
    )


def test_preview_highlighting_reports_only_geometry_present_in_production_scene():
    profile = (
        AtlasProductPreviewMaterialProfile
        .koeln_premium_v1()
    )

    retained_landmark_id = 101
    suppressed_landmark_id = 202

    city_result = {
        "terrain_size_x_mm": 150.0,
        "terrain_size_y_mm": 150.0,
        "mesh_groups": {
            "terrain": [],
            "buildings": [],
            "roads": [],
            "parks": [],
            "elevated_areas": [],
            "artworks": [],
            "landmarks": [
                {
                    "type": "tower",
                    "landmark_id": retained_landmark_id,
                    "triangles": [
                        (
                            (10.0, 10.0, 1.0),
                            (11.0, 10.0, 1.0),
                            (10.0, 11.0, 2.0),
                        ),
                    ],
                },
            ],
            "trees": [],
            "forest_canopies": [],
            "waters": [],
            "castle_walls": [],
            "castle_shells": [],
            "castle_tower_caps": [],
        },
        "city_composition_lod": {
            "decisions": {
                "landmark_101": {
                    "retain": True,
                },
                "landmark_202": {
                    "retain": False,
                },
            },
        },
        "city_composition_suppressed_meshes": 1,
    }

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(
            outer_width_mm=170.0,
            outer_height_mm=170.0,
            frame_width_mm=10.0,
        ),
        frame_depth_mm=6.0,
        material_profile=profile,
        highlighted_landmark_ids={
            retained_landmark_id,
            suppressed_landmark_id,
        },
    )

    highlighting = scene["highlighting"]

    assert set(
        highlighting["requested_landmark_ids"]
    ) == {
        str(retained_landmark_id),
        str(suppressed_landmark_id),
    }

    assert highlighting[
        "applied_landmark_ids"
    ] == (
        str(retained_landmark_id),
    )

    assert (
        str(suppressed_landmark_id)
        not in highlighting["applied_landmark_ids"]
    )

    assert all(
        mesh.get("landmark_id")
        != suppressed_landmark_id
        for batch in scene["material_batches"].values()
        for mesh in batch["meshes"]
        if isinstance(mesh, dict)
    )
