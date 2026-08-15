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



def test_modular_box_uses_25mm_and_50mm_product_capacity_modules():
    spec = AtlasPremiumGiftBoxSpec.for_original_wall_collection_v1()

    assert spec.middle_module_capacities_mm == (25.0, 50.0)
    assert spec.module_product_clearance_mm == pytest.approx(2.0)
    assert spec.connector_engagement_mm == pytest.approx(1.6)
    assert spec.connector_recess_depth_mm == pytest.approx(1.8)
    assert spec.connector_clearance_per_side_mm == pytest.approx(0.25)


@pytest.mark.parametrize(
    ("capacity_mm", "usable_height_mm"),
    (
        (25.0, 27.0),
        (50.0, 52.0),
    ),
)
def test_middle_module_capacity_includes_product_clearance(
    capacity_mm,
    usable_height_mm,
):
    spec = AtlasPremiumGiftBoxSpec.for_original_wall_collection_v1()

    assert spec.middle_module_usable_height_mm(
        capacity_mm
    ) == pytest.approx(usable_height_mm)


@pytest.mark.parametrize("capacity_mm", (25.0, 50.0))
def test_middle_module_accepts_only_standard_capacities(capacity_mm):
    spec = AtlasPremiumGiftBoxSpec.for_original_wall_collection_v1()

    assert (
        spec.validate_middle_module_capacity(capacity_mm)
        == capacity_mm
    )


@pytest.mark.parametrize(
    "capacity_mm",
    (0.0, 20.0, 30.0, 75.0, float("nan")),
)
def test_middle_module_rejects_nonstandard_single_capacities(
    capacity_mm,
):
    spec = AtlasPremiumGiftBoxSpec.for_original_wall_collection_v1()

    with pytest.raises(ValueError, match="middle module capacity"):
        spec.validate_middle_module_capacity(capacity_mm)


def test_middle_module_composes_larger_capacity_from_standards():
    spec = AtlasPremiumGiftBoxSpec.for_original_wall_collection_v1()

    assert spec.compose_middle_module_capacities(25.0) == (25.0,)
    assert spec.compose_middle_module_capacities(50.0) == (50.0,)
    assert spec.compose_middle_module_capacities(75.0) == (
        50.0,
        25.0,
    )
    assert spec.compose_middle_module_capacities(100.0) == (
        50.0,
        50.0,
    )

def test_personalization_insert_dimensions_follow_box_standard():
    mini = AtlasPremiumGiftBoxSpec.for_mini_wall_collection_v1()
    original = AtlasPremiumGiftBoxSpec.for_original_wall_collection_v1()
    grande = AtlasPremiumGiftBoxSpec.for_wall_collection(
        product_width_mm=220.0,
        product_height_mm=220.0,
        product_depth_mm=12.0,
    )

    assert mini.personalization_plate_size_mm == pytest.approx(
        (80.0, 24.0)
    )
    assert original.personalization_plate_size_mm == pytest.approx(
        (110.0, 28.0)
    )
    assert grande.personalization_plate_size_mm == pytest.approx(
        (140.0, 32.0)
    )

    for spec in (mini, original, grande):
        assert spec.personalization_plate_thickness_mm == pytest.approx(
            1.2
        )
        assert spec.personalization_recess_depth_mm == pytest.approx(
            0.8
        )
        assert (
            spec.personalization_fit_clearance_per_side_mm
            == pytest.approx(0.20)
        )
        assert spec.personalization_text_depth_mm == pytest.approx(0.6)
        assert spec.personalization_max_lines == 2
        assert spec.personalization_recess_size_mm == pytest.approx(
            (
                spec.personalization_plate_size_mm[0] + 0.4,
                spec.personalization_plate_size_mm[1] + 0.4,
            )
        )


def test_personalization_rejects_more_than_two_lines():
    spec = AtlasPremiumGiftBoxSpec.for_original_wall_collection_v1()

    with pytest.raises(
        ValueError,
        match="at most 2",
    ):
        spec.validate_personalization_lines(
            ("FIRST", "SECOND", "THIRD")
        )


def test_personalization_accepts_one_or_two_nonempty_lines():
    spec = AtlasPremiumGiftBoxSpec.for_original_wall_collection_v1()

    assert spec.validate_personalization_lines(
        ("FÜR ANNA",)
    ) == ("FÜR ANNA",)

    assert spec.validate_personalization_lines(
        ("FÜR ANNA", "BONN · 2026")
    ) == ("FÜR ANNA", "BONN · 2026")
