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


def test_renderer_maps_linear_infrastructure_to_roads_hardscape_batch():
    railway_mesh = _mesh(
        "linear_infrastructure_solid",
        40.0,
        50.0,
        0.4,
    )
    railway_mesh["semantic_class"] = "railway"
    railway_mesh["source_id"] = 94247467

    city_result = {
        "terrain_size_x_mm": 100.0,
        "terrain_size_y_mm": 120.0,
        "mesh_groups": {
            "terrain": [
                _mesh(
                    "terrain_closed_slab",
                    0.0,
                    0.0,
                    0.0,
                )
            ],
            "buildings": [],
            "roads": [
                _mesh(
                    "road",
                    30.0,
                    40.0,
                    0.4,
                )
            ],
            "linear_infrastructure": [
                railway_mesh,
            ],
            "parks": [],
            "trees": [],
            "waters": [],
        },
    }

    profile = (
        AtlasProductPreviewMaterialProfile
        .koeln_premium_v1()
    )

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        material_profile=profile,
    )

    road_meshes = (
        scene["material_batches"]["roads"]["meshes"]
    )

    assert len(road_meshes) == 2
    assert any(
        mesh.get("source_id") == 94247467
        for mesh in road_meshes
    )
