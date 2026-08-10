from CORE.atlas_customer_preview_parity import (
    AtlasCustomerPreviewParity,
)


def _production_result():
    return {
        "terrain_size_x_mm": 150.0,
        "terrain_size_y_mm": 150.0,
        "effective_scene_morphology": "historic_core",
        "morphology_composition_policy": {
            "terrain_emphasis": 0.40,
            "road_emphasis": 0.90,
            "urban_block_emphasis": 0.90,
            "vegetation_emphasis": 0.45,
            "water_emphasis": 0.55,
            "infrastructure_emphasis": 0.85,
            "landmark_emphasis": 1.00,
        },
        "city_composition_lod": {
            "scene_morphology": "historic_core",
            "product_size_mm": 150.0,
            "decisions": {
                "road_1": {
                    "retain": True,
                    "narrative_priority": 0.90,
                },
                "building_1": {
                    "retain": True,
                    "narrative_priority": 0.60,
                },
                "landmark_1": {
                    "retain": True,
                    "narrative_priority": 1.00,
                },
            },
        },
        "city_composition_suppressed_meshes": 2,
    }


def _preview_scene(production):
    return {
        "outer_width_mm": 170.0,
        "outer_height_mm": 170.0,
        "opening_width_mm": 150.0,
        "opening_height_mm": 150.0,
        "effective_scene_morphology": (
            production["effective_scene_morphology"]
        ),
        "morphology_composition_policy": (
            production["morphology_composition_policy"]
        ),
        "city_composition_lod": (
            production["city_composition_lod"]
        ),
        "city_composition_suppressed_meshes": (
            production[
                "city_composition_suppressed_meshes"
            ]
        ),
        "semantic_material_hierarchy": {
            "profile_name": "KOELN_PREMIUM_V1",
            "roles": {
                "generic_building": {},
                "landmark_wall": {},
                "vegetation": {},
                "water": {},
                "roads_hardscape": {},
                "terrain": {},
            },
        },
    }


def test_customer_preview_parity_accepts_matching_production_composition():
    production = _production_result()
    preview = _preview_scene(production)

    result = AtlasCustomerPreviewParity.resolve(
        production_result=production,
        preview_scene=preview,
    )

    assert result["matches"] is True
    assert result["mismatches"] == ()

    assert result["checks"][
        "scene_morphology"
    ] is True

    assert result["checks"][
        "composition_policy"
    ] is True

    assert result["checks"][
        "city_composition_lod"
    ] is True

    assert result["checks"][
        "suppressed_mesh_count"
    ] is True

    assert result["checks"][
        "product_size"
    ] is True

    assert result["checks"][
        "semantic_material_roles"
    ] is True


def test_customer_preview_parity_detects_changed_lod_decisions():
    production = _production_result()
    preview = _preview_scene(production)

    preview["city_composition_lod"] = {
        **production["city_composition_lod"],
        "decisions": {
            **production[
                "city_composition_lod"
            ]["decisions"],
            "road_1": {
                "retain": False,
                "narrative_priority": 0.90,
            },
        },
    }

    result = AtlasCustomerPreviewParity.resolve(
        production_result=production,
        preview_scene=preview,
    )

    assert result["matches"] is False

    assert (
        "city_composition_lod"
        in result["mismatches"]
    )


def test_customer_preview_parity_detects_changed_morphology_policy():
    production = _production_result()
    preview = _preview_scene(production)

    preview["morphology_composition_policy"] = {
        **production[
            "morphology_composition_policy"
        ],
        "road_emphasis": 0.20,
    }

    result = AtlasCustomerPreviewParity.resolve(
        production_result=production,
        preview_scene=preview,
    )

    assert result["matches"] is False

    assert (
        "composition_policy"
        in result["mismatches"]
    )


def test_customer_preview_parity_accepts_real_preview_renderer_output():
    from CORE.atlas_product_color_preview_renderer import (
        AtlasProductColorPreviewRenderer,
    )
    from CORE.atlas_product_preview_material_profile import (
        AtlasProductPreviewMaterialProfile,
    )
    from CORE.atlas_wall_frame_spec import (
        AtlasWallFrameSpec,
    )

    production = {
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
        "resolved_scene_morphology": "historic_core",
        "effective_scene_morphology": "historic_core",
        "morphology_composition_policy": {
            "terrain_emphasis": 0.40,
            "road_emphasis": 0.90,
            "urban_block_emphasis": 0.90,
            "vegetation_emphasis": 0.45,
            "water_emphasis": 0.55,
            "infrastructure_emphasis": 0.85,
            "landmark_emphasis": 1.00,
        },
        "city_composition_lod": {
            "scene_morphology": "historic_core",
            "product_size_mm": 150.0,
            "decisions": {},
        },
        "city_composition_suppressed_meshes": 0,
    }

    preview = (
        AtlasProductColorPreviewRenderer
        .build_scene(
            city_result=production,
            frame_spec=AtlasWallFrameSpec(
                outer_width_mm=170.0,
                outer_height_mm=170.0,
                frame_width_mm=10.0,
            ),
            frame_depth_mm=6.0,
            material_profile=(
                AtlasProductPreviewMaterialProfile
                .koeln_premium_v1()
            ),
        )
    )

    result = AtlasCustomerPreviewParity.resolve(
        production_result=production,
        preview_scene=preview,
    )

    assert result["matches"] is True
    assert result["mismatches"] == ()
