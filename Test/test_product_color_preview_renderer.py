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
            "water": [_mesh("water", 90.0, 100.0, 0.2)],
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
