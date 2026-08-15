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



def test_exporter_writes_requested_standard_middle_modules(tmp_path):
    spec = AtlasPremiumGiftBoxSpec.for_original_wall_collection_v1()

    result = AtlasPremiumGiftBoxSTLExporter.export(
        spec=spec,
        output_directory=tmp_path,
        product_name="atlas_original_modular",
        middle_module_capacities_mm=(50.0, 25.0),
    )

    assert result["middle_module_capacities_mm"] == (
        50.0,
        25.0,
    )
    assert len(result["middle_module_output_paths"]) == 2

    assert (
        tmp_path
        / "atlas_original_modular_MIDDLE_50MM_01.stl"
    ) in result["middle_module_output_paths"]

    assert (
        tmp_path
        / "atlas_original_modular_MIDDLE_25MM_02.stl"
    ) in result["middle_module_output_paths"]

    assert all(
        path.exists()
        for path in result["middle_module_output_paths"]
    )

def test_exporter_writes_optional_personalization_plate_and_text(
    tmp_path,
):
    spec = AtlasPremiumGiftBoxSpec.for_original_wall_collection_v1()

    result = AtlasPremiumGiftBoxSTLExporter.export(
        spec=spec,
        output_directory=tmp_path,
        product_name="atlas_original_personalized",
        personalization_lines=(
            "FÜR ANNA",
            "BONN · 2026",
        ),
    )

    plate_path = (
        tmp_path
        / "atlas_original_personalized_PERSONALIZATION_PLATE.stl"
    )
    text_path = (
        tmp_path
        / "atlas_original_personalized_PERSONALIZATION_TEXT.stl"
    )

    assert result["personalization_plate_output_path"] == plate_path
    assert result["personalization_text_output_path"] == text_path
    assert result["personalization_lines"] == (
        "FÜR ANNA",
        "BONN · 2026",
    )
    assert plate_path.exists()
    assert text_path.exists()
    assert result["personalization_plate_triangle_count"] > 0
    assert result["personalization_text_triangle_count"] > 0


def test_exporter_keeps_personalization_optional(tmp_path):
    spec = AtlasPremiumGiftBoxSpec.for_original_wall_collection_v1()

    result = AtlasPremiumGiftBoxSTLExporter.export(
        spec=spec,
        output_directory=tmp_path,
        product_name="atlas_original_plain",
    )

    assert result["personalization_plate_output_path"] is None
    assert result["personalization_text_output_path"] is None
    assert result["personalization_lines"] == ()
