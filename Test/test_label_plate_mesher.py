import pytest

from CORE.atlas_label_plate_mesher import AtlasLabelPlateMesher
from CORE.atlas_label_plate_spec import AtlasLabelPlateSpec


def _all_vertices(mesh):
    return [
        vertex
        for triangle in mesh["triangles"]
        for vertex in triangle
    ]


def test_label_plate_mesher_builds_closed_centered_rectangular_prism():
    mesh = AtlasLabelPlateMesher.build(
        spec=AtlasLabelPlateSpec(),
    )

    assert mesh["type"] == "label_plate"
    assert mesh["width_mm"] == pytest.approx(118.0)
    assert mesh["height_mm"] == pytest.approx(14.0)
    assert mesh["depth_mm"] == pytest.approx(1.2)
    assert len(mesh["triangles"]) == 12

    vertices = _all_vertices(mesh)

    assert min(x for x, _, _ in vertices) == pytest.approx(-59.0)
    assert max(x for x, _, _ in vertices) == pytest.approx(59.0)
    assert min(y for _, y, _ in vertices) == pytest.approx(-7.0)
    assert max(y for _, y, _ in vertices) == pytest.approx(7.0)
    assert min(z for _, _, z in vertices) == pytest.approx(0.0)
    assert max(z for _, _, z in vertices) == pytest.approx(1.2)
