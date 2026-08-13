import pytest

from CORE.atlas_premium_gift_box_spec import (
    AtlasPremiumGiftBoxSpec,
)


def test_220mm_wall_collection_premium_box_contract():
    spec = AtlasPremiumGiftBoxSpec.for_wall_collection(
        product_width_mm=220.0,
        product_height_mm=220.0,
        product_depth_mm=12.0,
    )

    assert spec.inner_width_mm == pytest.approx(222.0)
    assert spec.inner_height_mm == pytest.approx(222.0)
    assert spec.inner_depth_mm == pytest.approx(15.0)

    assert spec.wall_thickness_mm == pytest.approx(2.4)
    assert spec.floor_thickness_mm == pytest.approx(2.4)

    assert spec.outer_width_mm == pytest.approx(226.8)
    assert spec.outer_height_mm == pytest.approx(226.8)
    assert spec.base_total_depth_mm == pytest.approx(17.4)

    assert spec.lid_clearance_per_side_mm == pytest.approx(0.40)
    assert spec.lid_wall_thickness_mm == pytest.approx(2.0)
    assert spec.lid_overlap_mm == pytest.approx(8.0)
    assert spec.lid_top_thickness_mm == pytest.approx(2.0)

    assert spec.lid_inner_width_mm == pytest.approx(227.6)
    assert spec.lid_inner_height_mm == pytest.approx(227.6)
    assert spec.lid_outer_width_mm == pytest.approx(231.6)
    assert spec.lid_outer_height_mm == pytest.approx(231.6)
    assert spec.lid_total_depth_mm == pytest.approx(10.0)


def test_premium_box_preserves_symmetric_product_clearance():
    spec = AtlasPremiumGiftBoxSpec.for_wall_collection(
        product_width_mm=220.0,
        product_height_mm=220.0,
        product_depth_mm=12.0,
    )

    assert (
        spec.inner_width_mm - spec.product_width_mm
    ) / 2.0 == pytest.approx(1.0)

    assert (
        spec.inner_height_mm - spec.product_height_mm
    ) / 2.0 == pytest.approx(1.0)

    assert (
        spec.inner_depth_mm - spec.product_depth_mm
    ) == pytest.approx(3.0)


def test_premium_box_and_lid_fit_p2s_plate():
    spec = AtlasPremiumGiftBoxSpec.for_wall_collection(
        product_width_mm=220.0,
        product_height_mm=220.0,
        product_depth_mm=12.0,
    )

    assert spec.outer_width_mm < 256.0
    assert spec.outer_height_mm < 256.0
    assert spec.lid_outer_width_mm < 256.0
    assert spec.lid_outer_height_mm < 256.0
