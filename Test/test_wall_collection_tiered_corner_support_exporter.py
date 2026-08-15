from pathlib import Path
import pytest

from CORE.atlas_wall_collection_tiered_corner_support_exporter import (
    AtlasWallCollectionTieredCornerSupportExporter,
)
from CORE.atlas_wall_collection_tiered_corner_support_spec import (
    AtlasWallCollectionTieredCornerSupportSpec,
)


def test_exporter_writes_four_corner_supports_as_one_print_set(
    monkeypatch,
    tmp_path,
):
    writes = []
    monkeypatch.setattr(
        "CORE.atlas_wall_collection_tiered_corner_support_exporter."
        "AtlasSTLWriter.write",
        lambda **kwargs: writes.append(kwargs),
    )
    spec = AtlasWallCollectionTieredCornerSupportSpec.for_scene(
        frame_width_mm=10.0,
        frame_depth_mm=6.0,
        scene_max_height_mm=29.0286,
    )

    result = AtlasWallCollectionTieredCornerSupportExporter.export(
        spec=spec,
        output_directory=tmp_path,
        product_name="BONN_BIRTHPLACE",
        product_width_mm=170.0,
        product_height_mm=170.0,
    )

    expected_path = Path(tmp_path) / "BONN_BIRTHPLACE_TIER_SUPPORT_SET.stl"
    assert result["output_path"] == expected_path
    assert result["part_count"] == 4
    assert result["total_height_mm"] == 37.6
    assert result["next_plate_base_z_mm"] == pytest.approx(31.2)
    assert len(writes) == 1
    assert writes[0]["output_path"] == expected_path
    assert len(writes[0]["meshes"]) == 4
    assert all(mesh["triangles"] for mesh in writes[0]["meshes"])


def test_exporter_rejects_empty_product_name(tmp_path):
    spec = AtlasWallCollectionTieredCornerSupportSpec.for_scene(
        frame_width_mm=10.0,
        frame_depth_mm=6.0,
        scene_max_height_mm=12.0,
    )

    try:
        AtlasWallCollectionTieredCornerSupportExporter.export(
            spec=spec,
            output_directory=tmp_path,
            product_name="   ",
            product_width_mm=170.0,
            product_height_mm=170.0,
        )
    except ValueError as error:
        assert "product_name" in str(error)
    else:
        raise AssertionError("empty product name must be rejected")



def test_exporter_writes_one_universal_support_master(
    monkeypatch,
    tmp_path,
):
    writes = []
    monkeypatch.setattr(
        "CORE.atlas_wall_collection_tiered_corner_support_exporter."
        "AtlasSTLWriter.write",
        lambda **kwargs: writes.append(kwargs),
    )
    spec = AtlasWallCollectionTieredCornerSupportSpec.for_module(
        product_capacity_mm=25.0,
    )

    result = (
        AtlasWallCollectionTieredCornerSupportExporter
        .export_universal_module(
            spec=spec,
            output_directory=tmp_path,
        )
    )

    expected = (
        Path(tmp_path)
        / "ATLAS_TIER_CORNER_SUPPORT_25MM.stl"
    )
    assert result["output_path"] == expected
    assert result["master_part_count"] == 1
    assert result["required_quantity_per_level"] == 4
    assert result["product_capacity_mm"] == pytest.approx(25.0)
    assert len(writes) == 1
    assert writes[0]["output_path"] == expected
    assert len(writes[0]["meshes"]) == 1
