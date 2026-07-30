from pathlib import Path

import pytest

from CORE.atlas_relief_stl_exporter import (
    AtlasReliefSTLExporter,
)


def test_export_pipeline_result_writes_relief_mesh(
    monkeypatch,
    tmp_path,
) -> None:
    captured = {}
    output_path = tmp_path / "dalyan_relief.stl"
    mesh = {
        "type": "relief_mesh",
        "triangles": [
            (
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (0.0, 1.0, 0.0),
            ),
        ],
    }
    pipeline_result = {
        "type": "relief_image_pipeline_result",
        "relief_result": {
            "type": "relief_pipeline_result",
            "mesh": mesh,
        },
    }

    def fake_write(
        *,
        meshes,
        output_path,
        solid_name,
    ):
        captured["meshes"] = meshes
        captured["output_path"] = output_path
        captured["solid_name"] = solid_name
        return output_path

    monkeypatch.setattr(
        "CORE.atlas_relief_stl_exporter."
        "AtlasSTLWriter.write",
        fake_write,
    )

    result = AtlasReliefSTLExporter.export_pipeline_result(
        pipeline_result=pipeline_result,
        output_path=output_path,
        solid_name="DALYAN_ROCK_TOMBS_RELIEF",
    )

    assert result == output_path
    assert captured == {
        "meshes": [mesh],
        "output_path": output_path,
        "solid_name": "DALYAN_ROCK_TOMBS_RELIEF",
    }


def test_export_pipeline_result_rejects_missing_mesh(
    tmp_path,
) -> None:
    with pytest.raises(
        ValueError,
        match="relief mesh",
    ):
        AtlasReliefSTLExporter.export_pipeline_result(
            pipeline_result={
                "type": "relief_image_pipeline_result",
                "relief_result": {},
            },
            output_path=tmp_path / "invalid.stl",
        )


def test_export_pipeline_result_creates_parent_directory(
    monkeypatch,
    tmp_path,
) -> None:
    output_path = (
        tmp_path
        / "nested"
        / "dalyan_relief.stl"
    )
    pipeline_result = {
        "relief_result": {
            "mesh": {
                "type": "relief_mesh",
                "triangles": [],
            },
        },
    }

    monkeypatch.setattr(
        "CORE.atlas_relief_stl_exporter."
        "AtlasSTLWriter.write",
        lambda **kwargs: kwargs["output_path"],
    )

    AtlasReliefSTLExporter.export_pipeline_result(
        pipeline_result=pipeline_result,
        output_path=output_path,
    )

    assert output_path.parent.is_dir()


def test_export_pipeline_result_rejects_blank_solid_name(
    tmp_path,
) -> None:
    with pytest.raises(
        ValueError,
        match="solid_name",
    ):
        AtlasReliefSTLExporter.export_pipeline_result(
            pipeline_result={
                "relief_result": {
                    "mesh": {
                        "type": "relief_mesh",
                        "triangles": [],
                    },
                },
            },
            output_path=tmp_path / "relief.stl",
            solid_name="   ",
        )
