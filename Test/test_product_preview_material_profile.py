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
        "terrain_rgb": (205, 190, 160),
        "road_rgb": (190, 184, 170),
        "green_rgb": (105, 137, 78),
        "tree_rgb": (73, 105, 58),
        "water_rgb": (104, 165, 184),
    }
    kwargs[field_name] = (256, 0, 0)

    with pytest.raises(ValueError):
        AtlasProductPreviewMaterialProfile(**kwargs)
