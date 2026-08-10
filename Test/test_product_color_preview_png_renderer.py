from PIL import Image

from CORE.atlas_product_color_preview_png_renderer import (
    AtlasProductColorPreviewPNGRenderer,
)


def _mesh(x, y, z):
    return {
        "triangles": [
            (
                (x, y, z),
                (x + 10.0, y, z),
                (x, y + 10.0, z + 2.0),
            ),
        ],
    }


def _scene():
    return {
        "type": "product_color_preview_scene",
        "profile_name": "COMPETITOR_COMPARISON_V1",
        "outer_width_mm": 150.0,
        "outer_height_mm": 150.0,
        "material_batches": {
            "frame": {
                "rgb": (28, 28, 28),
                "meshes": [_mesh(-75.0, -75.0, 0.0)],
            },
            "terrain": {
                "rgb": (205, 190, 160),
                "meshes": [_mesh(-50.0, -50.0, 1.0)],
            },
            "buildings": {
                "rgb": (232, 228, 216),
                "meshes": [_mesh(-10.0, -10.0, 4.0)],
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


def test_png_renderer_writes_valid_image(tmp_path):
    output_path = tmp_path / "preview.png"

    result = AtlasProductColorPreviewPNGRenderer.render(
        scene=_scene(),
        output_path=output_path,
        image_width_px=640,
        image_height_px=640,
    )

    assert result["type"] == "product_color_preview_png"
    assert result["profile_name"] == "COMPETITOR_COMPARISON_V1"
    assert result["output_path"] == output_path
    assert result["image_width_px"] == 640
    assert result["image_height_px"] == 640
    assert result["triangle_count"] == 3
    assert output_path.exists()
    assert output_path.stat().st_size > 0

    with Image.open(output_path) as image:
        assert image.format == "PNG"
        assert image.size == (640, 640)


def test_png_preview_reports_consistent_product_aware_camera_framing(
    tmp_path,
):
    scene = {
        "type": "product_color_preview_scene",
        "profile_name": "CAMERA_PARITY_TEST",
        "outer_width_mm": 170.0,
        "outer_height_mm": 170.0,
        "material_batches": {},
    }

    result = AtlasProductColorPreviewPNGRenderer.render(
        scene=scene,
        output_path=tmp_path / "camera_parity.png",
        image_width_px=800,
        image_height_px=600,
    )

    assert result["camera"] == {
        "elevation_deg": 58.0,
        "azimuth_deg": -58.0,
    }

    assert result["framing"] == {
        "outer_width_mm": 170.0,
        "outer_height_mm": 170.0,
        "x_min_mm": -85.0,
        "x_max_mm": 85.0,
        "y_min_mm": -85.0,
        "y_max_mm": 85.0,
    }
