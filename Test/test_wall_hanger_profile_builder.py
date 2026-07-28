import pytest
from shapely.geometry import Polygon

from CORE.atlas_wall_frame_spec import AtlasWallFrameSpec
from CORE.atlas_wall_hanger_profile_builder import (
    AtlasWallHangerProfileBuilder,
)
from CORE.atlas_wall_hanger_spec import AtlasWallHangerSpec


def test_wall_hanger_profile_builds_valid_keyhole_inside_top_frame_band():
    frame_spec = AtlasWallFrameSpec()
    hanger_spec = AtlasWallHangerSpec.for_product_size(
        outer_width_mm=150.0,
        outer_height_mm=150.0,
        frame_width_mm=8.0,
        frame_depth_mm=6.0,
    )

    profile = AtlasWallHangerProfileBuilder.build(
        frame_spec=frame_spec,
        hanger_spec=hanger_spec,
        center_x_mm=0.0,
    )

    ring = profile["ring"]
    polygon = Polygon(ring)

    assert profile["type"] == "wall_hanger_keyhole_profile"
    assert profile["center_x_mm"] == pytest.approx(0.0)
    assert polygon.is_valid
    assert polygon.area > 0.0

    min_x, min_y, max_x, max_y = polygon.bounds

    assert min_x == pytest.approx(-2.75, abs=0.02)
    assert max_x == pytest.approx(2.75, abs=0.02)

    assert min_y >= 67.0
    assert max_y <= 75.0

    assert profile["head_center_y_mm"] < profile["neck_top_y_mm"]


def test_wall_hanger_profile_preserves_requested_horizontal_position():
    frame_spec = AtlasWallFrameSpec(
        outer_width_mm=260.0,
        outer_height_mm=260.0,
        frame_width_mm=8.0,
    )
    hanger_spec = AtlasWallHangerSpec.for_product_size(
        outer_width_mm=260.0,
        outer_height_mm=260.0,
        frame_width_mm=8.0,
        frame_depth_mm=6.0,
    )

    profile = AtlasWallHangerProfileBuilder.build(
        frame_spec=frame_spec,
        hanger_spec=hanger_spec,
        center_x_mm=65.0,
    )

    polygon = Polygon(profile["ring"])
    min_x, _, max_x, _ = polygon.bounds

    assert (min_x + max_x) / 2.0 == pytest.approx(65.0)


def test_wall_hanger_profile_rejects_position_outside_frame():
    frame_spec = AtlasWallFrameSpec()
    hanger_spec = AtlasWallHangerSpec.for_product_size(
        outer_width_mm=150.0,
        outer_height_mm=150.0,
        frame_width_mm=8.0,
        frame_depth_mm=6.0,
    )

    with pytest.raises(
        ValueError,
        match="hanger profile exceeds frame bounds",
    ):
        AtlasWallHangerProfileBuilder.build(
            frame_spec=frame_spec,
            hanger_spec=hanger_spec,
            center_x_mm=74.0,
        )
