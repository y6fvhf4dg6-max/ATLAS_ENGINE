from CORE.atlas_product_preview_material_profile import (
    AtlasProductPreviewMaterialProfile,
)
from Test.preview_meckenheim_jungholzweg_2_3_wall_collection import (
    CITY_OUTPUT_PATH,
    DEFAULT_PRIMARY_TEXT,
    DEFAULT_SECONDARY_TEXT,
    HIGHLIGHTED_BUILDING_SOURCE_IDS,
    MULTICOLOR_OUTPUT_DIRECTORY,
    MULTICOLOR_PRODUCT_NAME,
    PRODUCT_OUTPUT_PATH,
    build_parser,
)


def test_meckenheim_production_v2_uses_locked_label_defaults():
    arguments = build_parser().parse_args([])

    assert arguments.primary_text == "JUNGHOLZWEG 2/3"
    assert arguments.secondary_text == "MECKENHEIM"


def test_meckenheim_production_v2_locks_target_homes():
    assert HIGHLIGHTED_BUILDING_SOURCE_IDS == {
        220593156,
        389176145,
    }


def test_meckenheim_production_v2_uses_distinct_output_paths():
    assert "PRODUCTION_V2" in CITY_OUTPUT_PATH
    assert "PRODUCTION_V2" in PRODUCT_OUTPUT_PATH
    assert "PRODUCTION_V2" in MULTICOLOR_OUTPUT_DIRECTORY
    assert "PRODUCTION_V2" in MULTICOLOR_PRODUCT_NAME


def test_meckenheim_home_v2_uses_bonn_priority_palette():
    profile = AtlasProductPreviewMaterialProfile.meckenheim_home_v2()

    black = (20, 20, 20)
    white = (245, 245, 240)
    desert_tan = (205, 190, 160)
    brick_red = (156, 48, 42)
    dark_green = (73, 105, 58)
    blue = (70, 140, 180)

    assert profile.name == "MECKENHEIM_HOME_V2"
    assert profile.frame_rgb == black
    assert profile.label_text_rgb == black
    assert profile.terrain_rgb == white
    assert profile.road_rgb == white
    assert profile.label_plate_rgb == white
    assert profile.building_rgb == desert_tan
    assert profile.building_wall_rgb == desert_tan
    assert profile.building_roof_rgb == desert_tan
    assert profile.landmark_rgb == desert_tan
    assert profile.landmark_roof_rgb == brick_red
    assert profile.green_rgb == dark_green
    assert profile.tree_rgb == dark_green
    assert profile.water_rgb == blue
