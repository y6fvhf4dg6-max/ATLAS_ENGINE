import pytest

from CORE.atlas_wall_hanger_spec import AtlasWallHangerSpec


def test_150mm_wall_collection_uses_single_center_hanger():
    spec = AtlasWallHangerSpec.for_product_size(
        outer_width_mm=150.0,
        outer_height_mm=150.0,
        frame_width_mm=8.0,
        frame_depth_mm=6.0,
    )

    assert spec.hanger_count == 1
    assert spec.center_x_positions_mm == pytest.approx((0.0,))
    assert spec.head_diameter_mm == pytest.approx(5.0)
    assert spec.neck_width_mm == pytest.approx(3.0)
    assert spec.locking_travel_mm == pytest.approx(1.0)
    assert spec.recess_depth_mm == pytest.approx(3.0)


def test_200mm_wall_collection_uses_single_center_hanger():
    spec = AtlasWallHangerSpec.for_product_size(
        outer_width_mm=200.0,
        outer_height_mm=200.0,
        frame_width_mm=8.0,
        frame_depth_mm=6.0,
    )

    assert spec.hanger_count == 1
    assert spec.center_x_positions_mm == pytest.approx((0.0,))

def test_220mm_wall_collection_uses_single_center_hanger():
    spec = AtlasWallHangerSpec.for_product_size(
        outer_width_mm=220.0,
        outer_height_mm=220.0,
        frame_width_mm=10.0,
        frame_depth_mm=6.0,
    )

    assert spec.hanger_count == 1
    assert spec.center_x_positions_mm == pytest.approx((0.0,))


def test_260mm_wall_collection_uses_center_and_two_symmetric_hangers():
    spec = AtlasWallHangerSpec.for_product_size(
        outer_width_mm=260.0,
        outer_height_mm=260.0,
        frame_width_mm=8.0,
        frame_depth_mm=6.0,
    )

    assert spec.hanger_count == 3
    assert spec.center_x_positions_mm == pytest.approx(
        (-65.0, 0.0, 65.0)
    )


def test_wall_hanger_recess_preserves_front_wall_thickness():
    spec = AtlasWallHangerSpec.for_product_size(
        outer_width_mm=150.0,
        outer_height_mm=150.0,
        frame_width_mm=8.0,
        frame_depth_mm=6.0,
    )

    assert spec.front_wall_thickness_mm == pytest.approx(3.0)


def test_wall_hanger_rejects_unsupported_product_size():
    with pytest.raises(
        ValueError,
        match="unsupported Wall Collection product size",
    ):
        AtlasWallHangerSpec.for_product_size(
            outer_width_mm=180.0,
            outer_height_mm=180.0,
            frame_width_mm=8.0,
            frame_depth_mm=6.0,
        )


def test_wall_hanger_rejects_frame_too_narrow_for_keyhole():
    with pytest.raises(
        ValueError,
        match="frame width is too narrow",
    ):
        AtlasWallHangerSpec.for_product_size(
            outer_width_mm=150.0,
            outer_height_mm=150.0,
            frame_width_mm=5.0,
            frame_depth_mm=6.0,
        )


def test_wall_hanger_rejects_frame_too_shallow_for_recess():
    with pytest.raises(
        ValueError,
        match="frame depth is too shallow",
    ):
        AtlasWallHangerSpec.for_product_size(
            outer_width_mm=150.0,
            outer_height_mm=150.0,
            frame_width_mm=8.0,
            frame_depth_mm=4.0,
        )
