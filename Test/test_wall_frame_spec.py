import pytest

from CORE.atlas_wall_frame_spec import AtlasWallFrameSpec


def test_default_wall_frame_fits_inside_150_mm_product():
    spec = AtlasWallFrameSpec()

    assert spec.outer_width_mm == pytest.approx(150.0)
    assert spec.outer_height_mm == pytest.approx(150.0)
    assert spec.frame_width_mm == pytest.approx(8.0)
    assert spec.inner_width_mm == pytest.approx(134.0)
    assert spec.inner_height_mm == pytest.approx(134.0)


def test_wall_frame_rejects_non_positive_inner_opening():
    with pytest.raises(ValueError):
        AtlasWallFrameSpec(
            outer_width_mm=150.0,
            outer_height_mm=150.0,
            frame_width_mm=75.0,
        )
