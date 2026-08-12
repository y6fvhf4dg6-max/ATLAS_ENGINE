from CORE.atlas_product_preview_material_profile import (
    AtlasProductPreviewMaterialProfile,
)
from CORE.atlas_semantic_material_hierarchy import (
    AtlasSemanticMaterialHierarchy,
)


def test_semantic_material_hierarchy_preserves_distinct_roles():
    profile = (
        AtlasProductPreviewMaterialProfile
        .koeln_premium_v1()
    )

    result = AtlasSemanticMaterialHierarchy.resolve(
        material_profile=profile,
        maximum_physical_color_count=5,
    )

    assert result["profile_name"] == "KOELN_PREMIUM_V1"

    roles = result["roles"]

    assert set(roles) >= {
        "generic_building",
        "landmark_wall",
        "landmark_roof",
        "vegetation",
        "water",
        "roads_hardscape",
        "terrain",
        "frame",
        "label_plate",
        "label_text",
    }

    assert (
        roles["generic_building"]["semantic_role"]
        == "generic_building"
    )
    assert (
        roles["terrain"]["semantic_role"]
        == "terrain"
    )
    assert (
        roles["roads_hardscape"]["semantic_role"]
        == "roads_hardscape"
    )


def test_semantic_roles_can_share_one_physical_material():
    profile = (
        AtlasProductPreviewMaterialProfile
        .koeln_premium_v1()
    )

    result = AtlasSemanticMaterialHierarchy.resolve(
        material_profile=profile,
        maximum_physical_color_count=5,
    )

    roles = result["roles"]

    assert (
        roles["generic_building"]["rgb"]
        == roles["terrain"]["rgb"]
    )

    assert (
        roles["generic_building"]["physical_material"]
        == roles["terrain"]["physical_material"]
    )

    assert (
        roles["roads_hardscape"]["rgb"]
        != roles["terrain"]["rgb"]
    )

    assert (
        roles["roads_hardscape"]["physical_material"]
        != roles["terrain"]["physical_material"]
    )

    assert (
        roles["generic_building"]["semantic_role"]
        != roles["terrain"]["semantic_role"]
    )


def test_semantic_material_hierarchy_respects_physical_color_limit():
    profile = (
        AtlasProductPreviewMaterialProfile
        .koeln_premium_v1()
    )

    result = AtlasSemanticMaterialHierarchy.resolve(
        material_profile=profile,
        maximum_physical_color_count=5,
    )

    assert result["physical_color_count"] <= 5


def test_semantic_material_hierarchy_reuses_profile_colors():
    profile = (
        AtlasProductPreviewMaterialProfile
        .koeln_premium_v1()
    )

    result = AtlasSemanticMaterialHierarchy.resolve(
        material_profile=profile,
        maximum_physical_color_count=5,
    )

    roles = result["roles"]

    assert (
        roles["generic_building"]["rgb"]
        == profile.building_rgb
    )
    assert (
        roles["landmark_wall"]["rgb"]
        == profile.landmark_rgb
    )
    assert (
        roles["landmark_roof"]["rgb"]
        == profile.building_roof_rgb
    )
    assert (
        roles["vegetation"]["rgb"]
        == profile.green_rgb
    )
    assert (
        roles["water"]["rgb"]
        == profile.water_rgb
    )
    assert (
        roles["roads_hardscape"]["rgb"]
        == profile.road_rgb
    )
    assert (
        roles["terrain"]["rgb"]
        == profile.terrain_rgb
    )


def test_semantic_material_hierarchy_rejects_invalid_color_limit():
    profile = (
        AtlasProductPreviewMaterialProfile
        .koeln_premium_v1()
    )

    try:
        AtlasSemanticMaterialHierarchy.resolve(
            material_profile=profile,
            maximum_physical_color_count=0,
        )
    except ValueError as exc:
        assert "maximum_physical_color_count" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid physical color limit to fail"
        )


def test_semantic_material_hierarchy_distinguishes_generic_roof_from_landmark_roof():
    profile = (
        AtlasProductPreviewMaterialProfile
        .koeln_premium_v1()
    )

    result = AtlasSemanticMaterialHierarchy.resolve(
        material_profile=profile,
        maximum_physical_color_count=5,
    )

    roles = result["roles"]

    assert (
        roles["generic_building_roof"][
            "semantic_role"
        ]
        == "generic_building_roof"
    )

    assert (
        roles["landmark_roof"][
            "semantic_role"
        ]
        == "landmark_roof"
    )

    assert (
        roles["generic_building_roof"]["rgb"]
        == profile.building_roof_rgb
    )

    assert (
        roles["landmark_roof"]["rgb"]
        == profile.building_roof_rgb
    )

    assert (
        roles["generic_building_roof"][
            "physical_material"
        ]
        == roles["landmark_roof"][
            "physical_material"
        ]
    )

    assert (
        roles["generic_building_roof"][
            "semantic_role"
        ]
        != roles["landmark_roof"][
            "semantic_role"
        ]
    )


def test_semantic_material_hierarchy_preserves_readability_when_color_is_shared():
    profile = (
        AtlasProductPreviewMaterialProfile
        .koeln_premium_v1()
    )

    result = AtlasSemanticMaterialHierarchy.resolve(
        material_profile=profile,
        maximum_physical_color_count=5,
    )

    roles = result["roles"]

    shared = (
        "generic_building",
        "terrain",
    )

    assert len(
        {
            roles[name]["rgb"]
            for name in shared
        }
    ) == 1

    assert len(
        {
            roles[name]["surface_treatment"]
            for name in shared
        }
    ) == len(shared)

    assert all(
        roles[name]["relief_priority"] >= 0.0
        for name in shared
    )

    assert (
        roles["roads_hardscape"]["rgb"]
        != roles["terrain"]["rgb"]
    )


def test_semantic_material_hierarchy_assigns_landmark_higher_readability_priority():
    profile = (
        AtlasProductPreviewMaterialProfile
        .koeln_premium_v1()
    )

    result = AtlasSemanticMaterialHierarchy.resolve(
        material_profile=profile,
        maximum_physical_color_count=5,
    )

    roles = result["roles"]

    assert (
        roles["landmark_wall"]["readability_priority"]
        >
        roles["generic_building"]["readability_priority"]
    )

    assert (
        roles["landmark_roof"]["readability_priority"]
        >
        roles["generic_building_roof"]["readability_priority"]
    )
