import pytest

from CORE.atlas_wall_collection_tiered_corner_support_spec import (
    AtlasWallCollectionTieredCornerSupportSpec,
)


def test_bonn_tier_support_uses_physical_height_contract():
    spec = AtlasWallCollectionTieredCornerSupportSpec.for_scene(
        frame_width_mm=10.0,
        frame_depth_mm=6.0,
        scene_max_height_mm=29.0286,
    )

    assert spec.corner_engagement_mm == pytest.approx(8.0)
    assert spec.xy_fit_clearance_mm == pytest.approx(0.35)
    assert spec.vertical_clearance_mm == pytest.approx(2.0)
    assert spec.wall_thickness_mm == pytest.approx(2.0)
    assert spec.shelf_thickness_mm == pytest.approx(1.2)
    assert spec.print_height_increment_mm == pytest.approx(0.2)
    assert spec.next_plate_base_z_mm == pytest.approx(31.2)
    assert spec.plate_slot_height_mm == pytest.approx(6.4)
    assert spec.total_height_mm == pytest.approx(37.6)


def test_shorter_scenes_do_not_use_bonn_height():
    jamaica = AtlasWallCollectionTieredCornerSupportSpec.for_scene(
        frame_width_mm=10.0,
        frame_depth_mm=6.0,
        scene_max_height_mm=9.788,
    )
    seychelles = AtlasWallCollectionTieredCornerSupportSpec.for_scene(
        frame_width_mm=10.0,
        frame_depth_mm=6.0,
        scene_max_height_mm=10.683,
    )

    assert jamaica.next_plate_base_z_mm == pytest.approx(11.8)
    assert jamaica.total_height_mm == pytest.approx(18.2)
    assert seychelles.next_plate_base_z_mm == pytest.approx(12.8)
    assert seychelles.total_height_mm == pytest.approx(19.2)


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    (
        ("frame_width_mm", 0.0),
        ("frame_width_mm", float("nan")),
        ("frame_depth_mm", -1.0),
        ("frame_depth_mm", float("inf")),
        ("scene_max_height_mm", 0.0),
        ("scene_max_height_mm", float("nan")),
    ),
)
def test_tier_support_rejects_invalid_physical_dimensions(
    field_name,
    invalid_value,
):
    values = {
        "frame_width_mm": 10.0,
        "frame_depth_mm": 6.0,
        "scene_max_height_mm": 12.0,
    }
    values[field_name] = invalid_value

    with pytest.raises(ValueError):
        AtlasWallCollectionTieredCornerSupportSpec.for_scene(
            **values
        )


def test_tier_support_requires_engagement_inside_frame_band():
    with pytest.raises(
        ValueError,
        match="corner_engagement_mm",
    ):
        AtlasWallCollectionTieredCornerSupportSpec.for_scene(
            frame_width_mm=7.0,
            frame_depth_mm=6.0,
            scene_max_height_mm=12.0,
        )



@pytest.mark.parametrize(
    (
        "capacity_mm",
        "next_plate_base_z_mm",
        "total_height_mm",
    ),
    (
        (25.0, 27.0, 33.4),
        (50.0, 52.0, 58.4),
    ),
)
def test_universal_corner_support_uses_25mm_or_50mm_capacity(
    capacity_mm,
    next_plate_base_z_mm,
    total_height_mm,
):
    spec = AtlasWallCollectionTieredCornerSupportSpec.for_module(
        product_capacity_mm=capacity_mm,
    )

    assert spec.product_capacity_mm == pytest.approx(
        capacity_mm
    )
    assert spec.module_product_clearance_mm == pytest.approx(2.0)
    assert spec.next_plate_base_z_mm == pytest.approx(
        next_plate_base_z_mm
    )
    assert spec.total_height_mm == pytest.approx(
        total_height_mm
    )
    assert spec.bottom_connector == "female"
    assert spec.top_connector == "male"
    assert spec.connector_engagement_mm == pytest.approx(1.6)
    assert spec.connector_recess_depth_mm == pytest.approx(1.8)
    assert spec.connector_clearance_per_side_mm == pytest.approx(
        0.25
    )


@pytest.mark.parametrize(
    "capacity_mm",
    (0.0, 20.0, 30.0, 75.0, float("nan")),
)
def test_universal_corner_support_rejects_nonstandard_capacity(
    capacity_mm,
):
    with pytest.raises(
        ValueError,
        match="product_capacity_mm",
    ):
        AtlasWallCollectionTieredCornerSupportSpec.for_module(
            product_capacity_mm=capacity_mm,
        )
