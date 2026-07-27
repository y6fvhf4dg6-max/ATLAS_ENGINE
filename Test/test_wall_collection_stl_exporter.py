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
