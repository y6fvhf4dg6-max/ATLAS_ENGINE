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



def test_120mm_mini_wall_collection_box_standard():
    spec = AtlasPremiumGiftBoxSpec.for_mini_wall_collection_v1()

    assert spec.product_width_mm == pytest.approx(120.0)
    assert spec.product_height_mm == pytest.approx(120.0)
    assert spec.product_depth_mm == pytest.approx(20.0)

    assert spec.inner_width_mm == pytest.approx(122.0)
    assert spec.inner_height_mm == pytest.approx(122.0)
    assert spec.inner_depth_mm == pytest.approx(23.0)

    assert spec.outer_width_mm == pytest.approx(126.8)
    assert spec.outer_height_mm == pytest.approx(126.8)
    assert spec.base_total_depth_mm == pytest.approx(25.4)

    assert spec.lid_inner_width_mm == pytest.approx(127.6)
    assert spec.lid_inner_height_mm == pytest.approx(127.6)
    assert spec.lid_outer_width_mm == pytest.approx(131.6)
    assert spec.lid_outer_height_mm == pytest.approx(131.6)
    assert spec.lid_total_depth_mm == pytest.approx(10.0)


def test_170mm_original_wall_collection_box_standard():
    spec = AtlasPremiumGiftBoxSpec.for_original_wall_collection_v1()

    assert spec.product_width_mm == pytest.approx(170.0)
    assert spec.product_height_mm == pytest.approx(170.0)
    assert spec.product_depth_mm == pytest.approx(30.0)

    assert spec.inner_width_mm == pytest.approx(172.0)
    assert spec.inner_height_mm == pytest.approx(172.0)
    assert spec.inner_depth_mm == pytest.approx(33.0)

    assert spec.outer_width_mm == pytest.approx(176.8)
    assert spec.outer_height_mm == pytest.approx(176.8)
    assert spec.base_total_depth_mm == pytest.approx(35.4)

    assert spec.lid_inner_width_mm == pytest.approx(177.6)
    assert spec.lid_inner_height_mm == pytest.approx(177.6)
    assert spec.lid_outer_width_mm == pytest.approx(181.6)
    assert spec.lid_outer_height_mm == pytest.approx(181.6)
    assert spec.lid_total_depth_mm == pytest.approx(10.0)


@pytest.mark.parametrize(
    "factory_name",
    (
        "for_mini_wall_collection_v1",
        "for_original_wall_collection_v1",
    ),
)
def test_new_standard_boxes_fit_p2s_plate(factory_name):
    factory = getattr(
        AtlasPremiumGiftBoxSpec,
        factory_name,
    )
    spec = factory()

    assert spec.outer_width_mm < 256.0
    assert spec.outer_height_mm < 256.0
    assert spec.lid_outer_width_mm < 256.0
    assert spec.lid_outer_height_mm < 256.0
