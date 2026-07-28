import pytest

from CORE.atlas_product_preview_material_profile import (
    AtlasProductPreviewMaterialProfile,
)


def test_competitor_comparison_v1_palette():
    profile = AtlasProductPreviewMaterialProfile.competitor_comparison_v1()

    assert profile.name == "COMPETITOR_COMPARISON_V1"
    assert profile.frame_rgb == (28, 28, 28)
    assert profile.building_rgb == (232, 228, 216)
    assert profile.terrain_rgb == (205, 190, 160)
    assert profile.road_rgb == (190, 184, 170)
    assert profile.green_rgb == (105, 137, 78)
    assert profile.tree_rgb == (73, 105, 58)
    assert profile.water_rgb == (104, 165, 184)


def test_preview_material_profile_is_immutable():
    profile = AtlasProductPreviewMaterialProfile.competitor_comparison_v1()

    with pytest.raises(AttributeError):
        profile.green_rgb = (0, 0, 0)


@pytest.mark.parametrize(
    "field_name",
    [
        "frame_rgb",
        "building_rgb",
        "building_wall_rgb",
        "building_roof_rgb",
        "terrain_rgb",
        "road_rgb",
        "green_rgb",
        "tree_rgb",
        "water_rgb",
    ],
)
def test_preview_material_profile_rejects_invalid_rgb(field_name):
    kwargs = {
        "name": "INVALID",
        "frame_rgb": (28, 28, 28),
        "building_rgb": (232, 228, 216),
        "building_wall_rgb": (232, 228, 216),
        "building_roof_rgb": (232, 228, 216),
        "terrain_rgb": (205, 190, 160),
        "road_rgb": (190, 184, 170),
        "green_rgb": (105, 137, 78),
        "tree_rgb": (73, 105, 58),
        "water_rgb": (104, 165, 184),
    }
    kwargs[field_name] = (256, 0, 0)

    with pytest.raises(ValueError):
        AtlasProductPreviewMaterialProfile(**kwargs)



def test_competitor_profile_exposes_semantic_building_surface_colors():
    profile = AtlasProductPreviewMaterialProfile.competitor_comparison_v1()

    assert profile.building_wall_rgb == profile.building_rgb
    assert profile.building_roof_rgb == (156, 48, 42)

def test_koeln_premium_v1_uses_locked_five_color_palette():
    profile = AtlasProductPreviewMaterialProfile.koeln_premium_v1()

    white = (245, 245, 240)
    red = (170, 35, 30)
    green = (80, 125, 65)
    black = (20, 20, 20)
    blue = (70, 140, 180)

    assert profile.name == "KOELN_PREMIUM_V1"

    assert profile.frame_rgb == white
    assert profile.terrain_rgb == white
    assert profile.building_rgb == white
    assert profile.building_wall_rgb == white
    assert profile.road_rgb == white
    assert profile.label_text_rgb == white

    assert profile.building_roof_rgb == red

    assert profile.green_rgb == green
    assert profile.tree_rgb == green

    assert profile.label_plate_rgb == black

    assert profile.water_rgb == blue

    assert {
        profile.frame_rgb,
        profile.terrain_rgb,
        profile.building_rgb,
        profile.building_wall_rgb,
        profile.building_roof_rgb,
        profile.road_rgb,
        profile.green_rgb,
        profile.tree_rgb,
        profile.water_rgb,
        profile.label_plate_rgb,
        profile.label_text_rgb,
    } == {
        white,
        red,
        green,
        black,
        blue,
    }

