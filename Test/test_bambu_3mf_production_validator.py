import json
import zipfile
from pathlib import Path

import pytest

from CORE.atlas_bambu_3mf_production_validator import (
    AtlasBambu3MFProductionValidator,
)


MODEL_SETTINGS = """<?xml version="1.0" encoding="UTF-8"?>
<config>
  <object id="5">
    <metadata key="name" value="sample_product"/>
    <metadata face_count="30"/>
    <part id="1" subtype="normal_part">
      <metadata key="name" value="black.stl"/>
      <metadata key="source_file" value="black.stl"/>
      <mesh_stat
        face_count="10"
        edges_fixed="0"
        degenerate_facets="0"
        facets_removed="0"
        facets_reversed="0"
        backwards_edges="0"/>
    </part>
    <part id="2" subtype="normal_part">
      <metadata key="name" value="white.stl"/>
      <metadata key="source_file" value="white.stl"/>
      <mesh_stat
        face_count="20"
        edges_fixed="0"
        degenerate_facets="0"
        facets_removed="0"
        facets_reversed="0"
        backwards_edges="0"/>
    </part>
  </object>
</config>
"""

PROJECT_SETTINGS = json.dumps(
    {
        "printer_model": "Bambu Lab P2S",
        "printer_variant": "0.4",
        "layer_height": "0.2",
        "enable_support": "0",
    }
)

PLATE_SETTINGS = json.dumps(
    {
        "bed_type": "textured_plate",
        "nozzle_diameter": 0.4,
        "first_layer_time": 900.0,
    }
)


def _write_3mf(
    path: Path,
    *,
    model_settings: str = MODEL_SETTINGS,
    project_settings: str = PROJECT_SETTINGS,
    plate_settings: str = PLATE_SETTINGS,
) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "Metadata/model_settings.config",
            model_settings,
        )
        archive.writestr(
            "Metadata/project_settings.config",
            project_settings,
        )
        archive.writestr(
            "Metadata/plate_1.json",
            plate_settings,
        )
    return path


def test_validates_general_bambu_3mf_production_metadata(tmp_path):
    path = _write_3mf(tmp_path / "product.3mf")

    result = AtlasBambu3MFProductionValidator.validate(path)

    assert result.object_face_count == 30
    assert result.part_face_count == 30
    assert result.part_count == 2
    assert result.face_counts_match is True
    assert result.has_mesh_repairs is False
    assert result.printer_model == "Bambu Lab P2S"
    assert result.nozzle_diameter_mm == pytest.approx(0.4)
    assert result.layer_height_mm == pytest.approx(0.2)
    assert result.support_enabled is False
    assert result.bed_type == "textured_plate"
    assert result.is_structurally_valid is True


def test_detects_face_count_mismatch(tmp_path):
    model_settings = MODEL_SETTINGS.replace(
        'face_count="30"',
        'face_count="31"',
        1,
    )
    path = _write_3mf(
        tmp_path / "mismatch.3mf",
        model_settings=model_settings,
    )

    result = AtlasBambu3MFProductionValidator.validate(path)

    assert result.object_face_count == 31
    assert result.part_face_count == 30
    assert result.face_counts_match is False
    assert result.is_structurally_valid is False


def test_detects_bambu_mesh_repairs(tmp_path):
    model_settings = MODEL_SETTINGS.replace(
        'edges_fixed="0"',
        'edges_fixed="2"',
        1,
    )
    path = _write_3mf(
        tmp_path / "repaired.3mf",
        model_settings=model_settings,
    )

    result = AtlasBambu3MFProductionValidator.validate(path)

    assert result.has_mesh_repairs is True
    assert result.mesh_repair_count == 2
    assert result.is_structurally_valid is False


@pytest.mark.parametrize(
    "missing_member",
    (
        "Metadata/model_settings.config",
        "Metadata/project_settings.config",
        "Metadata/plate_1.json",
    ),
)
def test_rejects_missing_required_metadata(
    tmp_path,
    missing_member,
):
    path = tmp_path / "missing.3mf"

    members = {
        "Metadata/model_settings.config": MODEL_SETTINGS,
        "Metadata/project_settings.config": PROJECT_SETTINGS,
        "Metadata/plate_1.json": PLATE_SETTINGS,
    }
    members.pop(missing_member)

    with zipfile.ZipFile(path, "w") as archive:
        for name, content in members.items():
            archive.writestr(name, content)

    with pytest.raises(
        ValueError,
        match="missing required metadata",
    ):
        AtlasBambu3MFProductionValidator.validate(path)


def test_rejects_missing_3mf_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        AtlasBambu3MFProductionValidator.validate(
            tmp_path / "missing.3mf"
        )


def test_rejects_non_zip_3mf(tmp_path):
    path = tmp_path / "invalid.3mf"
    path.write_text("not a zip archive")

    with pytest.raises(ValueError, match="valid 3MF archive"):
        AtlasBambu3MFProductionValidator.validate(path)
