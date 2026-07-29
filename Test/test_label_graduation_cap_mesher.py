import pytest

from CORE.atlas_label_graduation_cap_mesher import (
    AtlasLabelGraduationCapMesher,
)
from CORE.atlas_mesh_validator import AtlasMeshValidator


def _bounds(mesh):
    points = [
        point
        for triangle in mesh["triangles"]
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


def test_graduation_cap_mesher_builds_closed_centered_printable_symbol():
    mesh = AtlasLabelGraduationCapMesher.build(
        width_mm=7.0,
        height_mm=5.0,
        depth_mm=0.6,
    )

    assert mesh["type"] == "label_graduation_cap"
    assert mesh["width_mm"] == pytest.approx(7.0)
    assert mesh["height_mm"] == pytest.approx(5.0)
    assert mesh["depth_mm"] == pytest.approx(0.6)
    assert mesh["triangles"]

    bounds = _bounds(mesh)

    assert bounds["min_x"] + bounds["max_x"] == pytest.approx(0.0)
    assert bounds["min_y"] + bounds["max_y"] == pytest.approx(0.0)
    assert bounds["max_x"] - bounds["min_x"] == pytest.approx(7.0)
    assert bounds["max_y"] - bounds["min_y"] == pytest.approx(5.0)
    assert bounds["min_z"] == pytest.approx(0.0)
    assert bounds["max_z"] == pytest.approx(0.6)

    report = AtlasMeshValidator._topology_report(mesh)

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


@pytest.mark.parametrize(
    "field_name",
    (
        "width_mm",
        "height_mm",
        "depth_mm",
    ),
)
def test_graduation_cap_mesher_rejects_non_positive_dimensions(
    field_name,
):
    values = {
        "width_mm": 7.0,
        "height_mm": 5.0,
        "depth_mm": 0.6,
    }
    values[field_name] = 0.0

    with pytest.raises(ValueError):
        AtlasLabelGraduationCapMesher.build(**values)
