import pytest

from CORE.atlas_foundation_first_engine import AtlasFoundationFirstEngine


BBOX = (
    39.92180,
    32.83280,
    39.92830,
    32.84110,
)


def test_fixed_scale_city_mode_preserves_requested_xy_scale():
    result = AtlasFoundationFirstEngine._resolve_scene_scale(
        bbox=BBOX,
        target_size_mm=200,
        bed_width_mm=256,
        bed_depth_mm=256,
        margin_mm=15,
        fixed_xy_scale=5500.0,
        use_fixed_xy_scale=True,
        debug=False,
    )

    assert result["xy_scale"] == pytest.approx(5500.0)
    assert result["size_x_mm"] > 0.0
    assert result["size_y_mm"] > 0.0


def test_dynamic_city_mode_keeps_existing_target_fit_behavior():
    result = AtlasFoundationFirstEngine._resolve_scene_scale(
        bbox=BBOX,
        target_size_mm=200,
        bed_width_mm=256,
        bed_depth_mm=256,
        margin_mm=15,
        fixed_xy_scale=5500.0,
        use_fixed_xy_scale=False,
        debug=False,
    )

    assert result["xy_scale"] > 0.0
    assert max(
        result["size_x_mm"],
        result["size_y_mm"],
    ) == pytest.approx(200.0)


def test_fixed_scale_city_mode_rejects_non_positive_scale():
    with pytest.raises(
        ValueError,
        match="xy_scale",
    ):
        AtlasFoundationFirstEngine._resolve_scene_scale(
            bbox=BBOX,
            target_size_mm=200,
            bed_width_mm=256,
            bed_depth_mm=256,
            margin_mm=15,
            fixed_xy_scale=0.0,
            use_fixed_xy_scale=True,
            debug=False,
        )


from CORE.atlas_product_area_engine import AtlasProductAreaEngine


@pytest.mark.parametrize(
    "product_size_mm",
    [
        140.0,
        200.0,
        260.0,
    ],
)
def test_product_area_bbox_resolves_back_to_requested_physical_size(
    product_size_mm,
):
    bbox = AtlasProductAreaEngine.build_bbox_from_center(
        center_lat=39.92505,
        center_lon=32.83695,
        product_size_mm=product_size_mm,
        scale_ratio=5500.0,
        debug=False,
    )

    result = AtlasFoundationFirstEngine._resolve_scene_scale(
        bbox=bbox,
        target_size_mm=product_size_mm,
        bed_width_mm=300,
        bed_depth_mm=300,
        margin_mm=15,
        fixed_xy_scale=5500.0,
        use_fixed_xy_scale=True,
        debug=False,
    )

    assert result["xy_scale"] == pytest.approx(5500.0)
    assert result["size_x_mm"] == pytest.approx(
        product_size_mm,
        abs=0.05,
    )
    assert result["size_y_mm"] == pytest.approx(
        product_size_mm,
        abs=0.05,
    )
