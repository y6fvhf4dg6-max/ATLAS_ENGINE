from CORE.atlas_wall_collection_stl_exporter import (
    AtlasWallCollectionSTLExporter,
)
from CORE.atlas_wall_frame_spec import AtlasWallFrameSpec


def _city_result():
    terrain = {
        "type": "terrain_closed_slab",
        "triangles": [
            (
                (0.0, 0.0, 0.0),
                (100.0, 0.0, 0.0),
                (100.0, 120.0, 0.0),
            ),
        ],
    }

    building = {
        "type": "building",
        "triangles": [
            (
                (10.0, 20.0, 0.8),
                (20.0, 20.0, 0.8),
                (20.0, 30.0, 4.0),
            ),
        ],
    }

    return {
        "terrain_size_x_mm": 100.0,
        "terrain_size_y_mm": 120.0,
        "mesh_groups": {
            "terrain": [terrain],
            "buildings": [building],
        },
    }


def test_wall_collection_exporter_writes_combined_product_meshes(
    monkeypatch,
    tmp_path,
):
    captured = {}

    def fake_write(meshes, output_path, solid_name="ATLAS_MODEL"):
        captured["meshes"] = meshes
        captured["output_path"] = output_path
        captured["solid_name"] = solid_name
        return output_path

    monkeypatch.setattr(
        "CORE.atlas_wall_collection_stl_exporter."
        "AtlasSTLWriter.write",
        fake_write,
    )

    output_path = tmp_path / "wall_collection.stl"

    result = AtlasWallCollectionSTLExporter.export(
        city_result=_city_result(),
        output_path=output_path,
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
    )

    assert captured["output_path"] == output_path
    assert captured["solid_name"] == "ATLAS_WALL_COLLECTION"
    assert len(captured["meshes"]) == 3

    assert result["output_path"] == output_path
    assert result["type"] == "wall_collection_product"
    assert result["mesh_count"] == 3
    assert result["outer_width_mm"] == 150.0
    assert result["outer_height_mm"] == 150.0
    assert result["opening_width_mm"] == 134.0
    assert result["opening_height_mm"] == 134.0


def test_wall_collection_exporter_forwards_label_plate_and_text_specs(
    monkeypatch,
    tmp_path,
):
    from CORE.atlas_label_plate_spec import AtlasLabelPlateSpec
    from CORE.atlas_label_text_spec import AtlasLabelTextSpec

    captured = {}

    def fake_build(**kwargs):
        captured["build_kwargs"] = kwargs
        return {
            "type": "wall_collection_product",
            "meshes": [
                {"type": "frame", "triangles": []},
                {"type": "city", "triangles": []},
                {"type": "label_plate", "triangles": []},
                {"type": "label_text", "triangles": []},
            ],
            "outer_width_mm": 150.0,
            "outer_height_mm": 150.0,
            "opening_width_mm": 134.0,
            "opening_height_mm": 134.0,
            "frame_depth_mm": 6.0,
            "city_offset_x_mm": -50.0,
            "city_offset_y_mm": -60.0,
        }

    def fake_write(meshes, output_path, solid_name="ATLAS_MODEL"):
        captured["meshes"] = meshes
        captured["output_path"] = output_path
        captured["solid_name"] = solid_name
        return output_path

    monkeypatch.setattr(
        "CORE.atlas_wall_collection_stl_exporter."
        "AtlasWallCollectionProductBuilder.build",
        fake_build,
    )
    monkeypatch.setattr(
        "CORE.atlas_wall_collection_stl_exporter."
        "AtlasSTLWriter.write",
        fake_write,
    )

    label_plate_spec = AtlasLabelPlateSpec(
        width_mm=118.0,
        height_mm=14.0,
        depth_mm=1.2,
    )
    label_text_spec = AtlasLabelTextSpec(
        primary_text="KÖLN",
        secondary_text="50.9375° N · 6.9603° E",
    )

    result = AtlasWallCollectionSTLExporter.export(
        city_result=_city_result(),
        output_path=tmp_path / "wall_collection_labelled.stl",
        frame_spec=AtlasWallFrameSpec(),
        frame_depth_mm=6.0,
        label_plate_spec=label_plate_spec,
        label_text_spec=label_text_spec,
    )

    assert captured["build_kwargs"]["label_plate_spec"] is label_plate_spec
    assert captured["build_kwargs"]["label_text_spec"] is label_text_spec
    assert result["mesh_count"] == 4
