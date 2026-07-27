import pytest

from CORE.atlas_label_text_mesher import AtlasLabelTextMesher
from CORE.atlas_mesh_validator import AtlasMeshValidator


def _bounds(triangles):
    points = [
        point
        for triangle in triangles
        for point in triangle
    ]
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    zs = [point[2] for point in points]

    return {
        "min_x": min(xs),
        "max_x": max(xs),
        "min_y": min(ys),
        "max_y": max(ys),
        "min_z": min(zs),
        "max_z": max(zs),
    }


def test_label_text_mesher_builds_closed_bold_text_with_holes():
    mesh = AtlasLabelTextMesher.build_line(
        text="KÖLN",
        height_mm=4.2,
        depth_mm=0.6,
        max_width_mm=108.0,
    )

    triangles = mesh["triangles"]
    bounds = _bounds(triangles)

    assert mesh["type"] == "label_text"
    assert mesh["text"] == "KÖLN"
    assert mesh["font_family"] == "DejaVu Sans"
    assert mesh["font_weight"] == "bold"

    assert triangles
    assert bounds["max_x"] - bounds["min_x"] <= 108.0 + 1e-6
    assert bounds["max_y"] - bounds["min_y"] == pytest.approx(
        4.2,
        abs=1e-6,
    )
    assert bounds["min_z"] == pytest.approx(0.0)
    assert bounds["max_z"] == pytest.approx(0.6)

    report = AtlasMeshValidator._topology_report(mesh)

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_label_text_mesher_centers_line_at_origin():
    mesh = AtlasLabelTextMesher.build_line(
        text="MEZUNİYET",
        height_mm=2.8,
        depth_mm=0.6,
        max_width_mm=108.0,
    )

    bounds = _bounds(mesh["triangles"])

    assert bounds["min_x"] + bounds["max_x"] == pytest.approx(0.0)
    assert bounds["min_y"] + bounds["max_y"] == pytest.approx(0.0)


@pytest.mark.parametrize(
    "field_name,value",
    (
        ("text", "   "),
        ("height_mm", 0.0),
        ("depth_mm", 0.0),
        ("max_width_mm", 0.0),
    ),
)
def test_label_text_mesher_rejects_invalid_inputs(field_name, value):
    values = {
        "text": "KÖLN",
        "height_mm": 4.2,
        "depth_mm": 0.6,
        "max_width_mm": 108.0,
    }
    values[field_name] = value

    with pytest.raises(ValueError):
        AtlasLabelTextMesher.build_line(**values)
