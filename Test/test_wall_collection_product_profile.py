import pytest

from CORE.atlas_wall_collection_product_profile import (
    AtlasWallCollectionProductProfile,
)


def test_landmark_memory_profile_preserves_product_settings():
    profile = AtlasWallCollectionProductProfile(
        name="landmark-memory",
        product_type="landmark",
        frame_width_mm=200.0,
        frame_height_mm=200.0,
        model_area_mm=150.0,
        model_min_height_mm=5.0,
        model_max_height_mm=18.0,
    )

    assert profile.name == "landmark-memory"
    assert profile.product_type == "landmark"
    assert profile.frame_width_mm == 200.0
    assert profile.frame_height_mm == 200.0
    assert profile.model_area_mm == 150.0
    assert profile.model_min_height_mm == 5.0
    assert profile.model_max_height_mm == 18.0


def test_wall_collection_product_profile_is_immutable():
    profile = AtlasWallCollectionProductProfile(
        name="landmark-memory",
        product_type="landmark",
        frame_width_mm=200.0,
        frame_height_mm=200.0,
        model_area_mm=150.0,
        model_min_height_mm=5.0,
        model_max_height_mm=18.0,
    )

    with pytest.raises(AttributeError):
        profile.model_area_mm = 160.0


def test_wall_collection_product_profile_normalizes_text_fields():
    profile = AtlasWallCollectionProductProfile(
        name="  landmark-memory  ",
        product_type="  LANDMARK  ",
        frame_width_mm=200.0,
        frame_height_mm=200.0,
        model_area_mm=150.0,
        model_min_height_mm=5.0,
        model_max_height_mm=18.0,
    )

    assert profile.name == "landmark-memory"
    assert profile.product_type == "landmark"


@pytest.mark.parametrize(
    "product_type",
    [
        "",
        "   ",
        "portrait",
        "bridge",
    ],
)
def test_wall_collection_product_profile_rejects_unknown_product_type(
    product_type,
):
    with pytest.raises(ValueError):
        AtlasWallCollectionProductProfile(
            name="wall-memory",
            product_type=product_type,
            frame_width_mm=200.0,
            frame_height_mm=200.0,
            model_area_mm=150.0,
            model_min_height_mm=5.0,
            model_max_height_mm=18.0,
        )
