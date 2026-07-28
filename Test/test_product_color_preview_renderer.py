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
