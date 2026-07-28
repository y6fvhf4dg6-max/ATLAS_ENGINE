from pathlib import Path

from CORE.atlas_wall_collection_multicolor_stl_exporter import (
    AtlasWallCollectionMulticolorSTLExporter,
)


def _mesh(x):
    return {
        "type": "test_mesh",
        "triangles": [
            (
                (x, 0.0, 0.0),
                (x + 1.0, 0.0, 0.0),
                (x, 1.0, 0.0),
            ),
        ],
    }


def test_multicolor_exporter_merges_material_batches_into_five_color_stls(
    monkeypatch,
    tmp_path,
):
    white = (245, 245, 240)
    red = (170, 35, 30)
    green = (80, 125, 65)
    black = (20, 20, 20)
    blue = (70, 140, 180)

    scene = {
        "type": "product_color_preview_scene",
        "profile_name": "KOELN_PREMIUM_V1",
        "material_batches": {
            "frame": {
                "rgb": white,
                "meshes": [_mesh(0.0)],
            },
            "terrain": {
                "rgb": white,
                "meshes": [_mesh(10.0)],
            },
            "building_walls": {
                "rgb": white,
                "meshes": [_mesh(20.0)],
            },
            "building_roofs": {
                "rgb": red,
                "meshes": [_mesh(30.0)],
            },
            "parks": {
                "rgb": green,
                "meshes": [_mesh(40.0)],
            },
            "trees": {
                "rgb": green,
                "meshes": [_mesh(50.0)],
            },
            "water": {
                "rgb": blue,
                "meshes": [_mesh(60.0)],
            },
            "label_plate": {
                "rgb": black,
                "meshes": [_mesh(70.0)],
            },
            "label_text": {
                "rgb": white,
                "meshes": [_mesh(80.0)],
            },
            "roads": {
                "rgb": white,
                "meshes": [],
            },
        },
    }

    writes = []

    def fake_write(meshes, output_path, solid_name="ATLAS_MODEL"):
        writes.append(
            {
                "meshes": meshes,
                "output_path": Path(output_path),
                "solid_name": solid_name,
            }
        )
        return output_path

    monkeypatch.setattr(
        "CORE.atlas_wall_collection_multicolor_stl_exporter."
        "AtlasSTLWriter.write",
        fake_write,
    )

    result = AtlasWallCollectionMulticolorSTLExporter.export_scene(
        scene=scene,
        output_directory=tmp_path,
        product_name="koeln_premium",
    )

    assert result["type"] == "wall_collection_multicolor_stl_package"
    assert result["profile_name"] == "KOELN_PREMIUM_V1"
    assert result["color_count"] == 5
    assert result["part_count"] == 5

    assert set(result["parts"]) == {
        "white",
        "red",
        "green",
        "black",
        "blue",
    }

    assert len(writes) == 5

    assert result["parts"]["white"]["rgb"] == white
    assert result["parts"]["red"]["rgb"] == red
    assert result["parts"]["green"]["rgb"] == green
    assert result["parts"]["black"]["rgb"] == black
    assert result["parts"]["blue"]["rgb"] == blue

    assert len(result["parts"]["white"]["source_batches"]) == 4
    assert set(result["parts"]["white"]["source_batches"]) == {
        "frame",
        "terrain",
        "building_walls",
        "label_text",
    }

    assert set(result["parts"]["green"]["source_batches"]) == {
        "parks",
        "trees",
    }

    assert result["parts"]["blue"]["source_batches"] == (
        "water",
    )

    assert result["parts"]["white"]["output_path"] == (
        tmp_path / "koeln_premium__white.stl"
    )
    assert result["parts"]["red"]["output_path"] == (
        tmp_path / "koeln_premium__red.stl"
    )
    assert result["parts"]["green"]["output_path"] == (
        tmp_path / "koeln_premium__green.stl"
    )
    assert result["parts"]["black"]["output_path"] == (
        tmp_path / "koeln_premium__black.stl"
    )
    assert result["parts"]["blue"]["output_path"] == (
        tmp_path / "koeln_premium__blue.stl"
    )
