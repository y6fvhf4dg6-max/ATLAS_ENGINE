from CORE.atlas_product_color_preview_obj_exporter import (
    AtlasProductColorPreviewOBJExporter,
)


def _mesh(x, y, z):
    return {
        "triangles": [
            (
                (x, y, z),
                (x + 1.0, y, z),
                (x, y + 1.0, z),
            ),
        ],
    }


def _scene():
    return {
        "type": "product_color_preview_scene",
        "profile_name": "COMPETITOR_COMPARISON_V1",
        "material_batches": {
            "frame": {
                "rgb": (28, 28, 28),
                "meshes": [_mesh(0.0, 0.0, 0.0)],
            },
            "terrain": {
                "rgb": (205, 190, 160),
                "meshes": [_mesh(10.0, 0.0, 0.0)],
            },
            "buildings": {
                "rgb": (232, 228, 216),
                "meshes": [_mesh(20.0, 0.0, 1.0)],
            },
            "roads": {
                "rgb": (190, 184, 170),
                "meshes": [],
            },
            "parks": {
                "rgb": (105, 137, 78),
                "meshes": [],
            },
            "trees": {
                "rgb": (73, 105, 58),
                "meshes": [],
            },
            "water": {
                "rgb": (104, 165, 184),
                "meshes": [],
            },
        },
    }


def test_obj_exporter_writes_obj_and_mtl_files(tmp_path):
    obj_path = tmp_path / "preview.obj"

    result = AtlasProductColorPreviewOBJExporter.export(
        scene=_scene(),
        output_path=obj_path,
    )

    mtl_path = tmp_path / "preview.mtl"

    assert result["type"] == "product_color_preview_obj"
    assert result["profile_name"] == "COMPETITOR_COMPARISON_V1"
    assert result["obj_path"] == obj_path
    assert result["mtl_path"] == mtl_path
    assert result["triangle_count"] == 3

    assert obj_path.exists()
    assert mtl_path.exists()

    obj_text = obj_path.read_text()
    mtl_text = mtl_path.read_text()

    assert "mtllib preview.mtl" in obj_text
    assert "usemtl frame" in obj_text
    assert "usemtl terrain" in obj_text
    assert "usemtl buildings" in obj_text
    assert "f 1 2 3" in obj_text

    assert "newmtl frame" in mtl_text
    assert "Kd 0.109804 0.109804 0.109804" in mtl_text
    assert "newmtl buildings" in mtl_text
