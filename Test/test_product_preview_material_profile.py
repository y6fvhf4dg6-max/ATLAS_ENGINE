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
        "landmark_rgb",
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
        "landmark_rgb": (184, 142, 92),
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

    black = (20, 20, 20)
    desert_tan = (205, 190, 160)
    brick_red = (156, 48, 42)
    dark_green = (73, 105, 58)
    blue = (70, 140, 180)

    assert profile.name == "KOELN_PREMIUM_V1"

    assert profile.frame_rgb == black
    assert profile.road_rgb == black
    assert profile.label_text_rgb == black

    assert profile.terrain_rgb == desert_tan
    assert profile.building_rgb == desert_tan
    assert profile.building_wall_rgb == desert_tan
    assert profile.landmark_rgb == desert_tan
    assert profile.label_plate_rgb == desert_tan

    assert profile.building_roof_rgb == brick_red

    assert profile.green_rgb == dark_green
    assert profile.tree_rgb == dark_green

    assert profile.water_rgb == blue

    assert {
        profile.frame_rgb,
        profile.terrain_rgb,
        profile.building_rgb,
        profile.building_wall_rgb,
        profile.building_roof_rgb,
        profile.landmark_rgb,
        profile.road_rgb,
        profile.green_rgb,
        profile.tree_rgb,
        profile.water_rgb,
        profile.label_plate_rgb,
        profile.label_text_rgb,
    } == {
        black,
        desert_tan,
        brick_red,
        dark_green,
        blue,
    }

def test_preview_material_profile_exposes_separate_landmark_color():
    profile = AtlasProductPreviewMaterialProfile(
        name="LANDMARK_TEST",
        frame_rgb=(20, 20, 20),
        building_rgb=(245, 245, 240),
        building_wall_rgb=(245, 245, 240),
        building_roof_rgb=(170, 35, 30),
        landmark_rgb=(184, 142, 92),
        terrain_rgb=(225, 211, 180),
        road_rgb=(225, 211, 180),
        green_rgb=(80, 125, 65),
        tree_rgb=(80, 125, 65),
        water_rgb=(70, 140, 180),
    )

    assert profile.landmark_rgb == (184, 142, 92)


def test_preview_material_profile_rejects_invalid_landmark_rgb():
    with pytest.raises(ValueError):
        AtlasProductPreviewMaterialProfile(
            name="INVALID_LANDMARK",
            frame_rgb=(20, 20, 20),
            building_rgb=(245, 245, 240),
            building_wall_rgb=(245, 245, 240),
            building_roof_rgb=(170, 35, 30),
            landmark_rgb=(256, 142, 92),
            terrain_rgb=(225, 211, 180),
            road_rgb=(225, 211, 180),
            green_rgb=(80, 125, 65),
            tree_rgb=(80, 125, 65),
            water_rgb=(70, 140, 180),
        )


def test_dalyan_kaunos_premium_v1_uses_locked_five_color_palette():
    profile = (
        AtlasProductPreviewMaterialProfile.dalyan_kaunos_premium_v1()
    )

    ivory = (242, 235, 218)
    sandstone = (190, 145, 92)
    olive = (91, 112, 63)
    charcoal = (26, 25, 23)
    mediterranean_blue = (66, 126, 151)

    assert profile.name == "DALYAN_KAUNOS_PREMIUM_V1"

    assert profile.frame_rgb == charcoal
    assert profile.label_text_rgb == charcoal

    assert profile.terrain_rgb == ivory
    assert profile.road_rgb == ivory
    assert profile.building_rgb == ivory
    assert profile.building_wall_rgb == ivory
    assert profile.building_roof_rgb == ivory
    assert profile.label_plate_rgb == ivory

    assert profile.landmark_rgb == sandstone

    assert profile.green_rgb == olive
    assert profile.tree_rgb == olive

    assert profile.water_rgb == mediterranean_blue

    assert {
        profile.frame_rgb,
        profile.terrain_rgb,
        profile.building_rgb,
        profile.building_wall_rgb,
        profile.building_roof_rgb,
        profile.landmark_rgb,
        profile.road_rgb,
        profile.green_rgb,
        profile.tree_rgb,
        profile.water_rgb,
        profile.label_plate_rgb,
        profile.label_text_rgb,
    } == {
        ivory,
        sandstone,
        olive,
        charcoal,
        mediterranean_blue,
    }

