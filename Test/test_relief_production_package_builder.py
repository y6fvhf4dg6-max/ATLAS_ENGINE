import json
from pathlib import Path

import pytest

from CORE.atlas_relief_production_package_builder import (
    AtlasReliefProductionPackageBuilder,
)


def _write(path: Path, content: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def test_builds_persistent_relief_production_package(tmp_path):
    stl_path = _write(
        tmp_path / "input" / "relief.stl",
        b"solid DALYAN\nendsolid DALYAN\n",
    )
    preview_path = _write(
        tmp_path / "input" / "preview.png",
        b"preview",
    )
    source_path = _write(
        tmp_path / "input" / "source.png",
        b"source",
    )

    package_directory = (
        tmp_path / "products" / "dalyan_rock_tombs_80x50mm"
    )

    result = AtlasReliefProductionPackageBuilder.build(
        package_directory=package_directory,
        product_id="dalyan_rock_tombs_80x50mm",
        display_name="Dalyan Rock Tombs",
        width_mm=80.0,
        depth_mm=50.0,
        stl_path=stl_path,
        preview_path=preview_path,
        source_path=source_path,
        profile_name="rock-carved-landmark",
        production_variant="illumination-normalized",
        quality_report={
            "triangle_count": 95036,
            "open_edge_count": 0,
            "non_manifold_edge_count": 0,
            "is_printable_topology": True,
        },
    )

    final_stl = (
        package_directory
        / "STL"
        / "dalyan_rock_tombs_relief_80x50mm_FINAL.stl"
    )
    final_preview = (
        package_directory
        / "PREVIEW"
        / "dalyan_rock_tombs_FINAL_shaded.png"
    )
    final_source = (
        package_directory
        / "SOURCE"
        / "rock_tombs_illumination_normalized.png"
    )
    manifest_path = (
        package_directory
        / "production_manifest.json"
    )

    quality_report_path = (
        package_directory
        / "REPORTS"
        / "print_quality_report.json"
    )

    assert final_stl.read_bytes() == stl_path.read_bytes()
    assert final_preview.read_bytes() == preview_path.read_bytes()
    assert final_source.read_bytes() == source_path.read_bytes()
    assert result["manifest_path"] == manifest_path

    quality_report = json.loads(
        quality_report_path.read_text()
    )
    assert quality_report["triangle_count"] == 95036
    assert quality_report["open_edge_count"] == 0
    assert quality_report["non_manifold_edge_count"] == 0
    assert quality_report["is_printable_topology"] is True

    manifest = json.loads(manifest_path.read_text())

    assert manifest["product_id"] == "dalyan_rock_tombs_80x50mm"
    assert manifest["display_name"] == "Dalyan Rock Tombs"
    assert manifest["product_type"] == "relief"
    assert manifest["dimensions_mm"] == {
        "width": 80.0,
        "depth": 50.0,
    }
    assert manifest["profile_name"] == "rock-carved-landmark"
    assert manifest["production_variant"] == "illumination-normalized"
    assert manifest["files"]["final_stl"] == (
        "STL/dalyan_rock_tombs_relief_80x50mm_FINAL.stl"
    )
    assert manifest["files"]["final_3mf"] == (
        "dalyan_rock_tombs_80x50mm_FINAL.3mf"
    )
    assert manifest["status"]["stl_ready"] is True
    assert manifest["status"]["quality_report_ready"] is True
    assert manifest["status"]["bambu_3mf_ready"] is False


def test_rejects_missing_required_input_file(tmp_path):
    with pytest.raises(
        FileNotFoundError,
        match="stl_path",
    ):
        AtlasReliefProductionPackageBuilder.build(
            package_directory=tmp_path / "package",
            product_id="dalyan",
            display_name="Dalyan",
            width_mm=80.0,
            depth_mm=50.0,
            stl_path=tmp_path / "missing.stl",
            preview_path=_write(
                tmp_path / "preview.png",
                b"preview",
            ),
            source_path=_write(
                tmp_path / "source.png",
                b"source",
            ),
            profile_name="rock-carved-landmark",
            production_variant="illumination-normalized",
        )
