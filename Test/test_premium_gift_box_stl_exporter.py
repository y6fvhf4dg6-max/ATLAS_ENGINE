from pathlib import Path

import pytest

from CORE.atlas_premium_gift_box_spec import AtlasPremiumGiftBoxSpec
from CORE.atlas_premium_gift_box_stl_exporter import (
    AtlasPremiumGiftBoxSTLExporter,
)


def test_exporter_writes_separate_base_and_plain_lid_stls(tmp_path):
    spec = AtlasPremiumGiftBoxSpec.for_wall_collection(
        product_width_mm=220.0,
        product_height_mm=220.0,
        product_depth_mm=12.0,
    )

    result = AtlasPremiumGiftBoxSTLExporter.export(
        spec=spec,
        output_directory=tmp_path,
        product_name="premium_box_test",
    )

    base_path = Path(result["base_output_path"])
    lid_path = Path(result["lid_output_path"])

    assert base_path == tmp_path / "premium_box_test_BASE.stl"
    assert lid_path == tmp_path / "premium_box_test_LID.stl"

    assert base_path.exists()
    assert lid_path.exists()

    assert result["type"] == "premium_gift_box_stl_package"
    assert result["base_triangle_count"] > 0
    assert result["lid_triangle_count"] > 0

    base_text = base_path.read_text(encoding="utf-8")
    lid_text = lid_path.read_text(encoding="utf-8")

    assert base_text.startswith("solid ATLAS_PREMIUM_GIFT_BOX_BASE")
    assert lid_text.startswith("solid ATLAS_PREMIUM_GIFT_BOX_LID")


def test_exporter_reports_physical_dimensions(tmp_path):
    spec = AtlasPremiumGiftBoxSpec.for_wall_collection(
        product_width_mm=220.0,
        product_height_mm=220.0,
        product_depth_mm=12.0,
    )

    result = AtlasPremiumGiftBoxSTLExporter.export(
        spec=spec,
        output_directory=tmp_path,
        product_name="premium_box_test",
    )

    assert result["base_outer_width_mm"] == pytest.approx(226.8)
    assert result["base_outer_height_mm"] == pytest.approx(226.8)
    assert result["base_total_depth_mm"] == pytest.approx(17.4)

    assert result["lid_outer_width_mm"] == pytest.approx(231.6)
    assert result["lid_outer_height_mm"] == pytest.approx(231.6)
    assert result["lid_total_depth_mm"] == pytest.approx(10.0)
