import pytest

from CORE.atlas_label_plate_mesher import AtlasLabelPlateMesher
from CORE.atlas_label_plate_spec import AtlasLabelPlateSpec
from CORE.atlas_mesh_validator import AtlasMeshValidator


def _all_vertices(mesh):
    return [
        vertex
        for triangle in mesh["triangles"]
        for vertex in triangle
    ]


def test_label_plate_mesher_builds_closed_centered_rectangular_prism():
    mesh = AtlasLabelPlateMesher.build(
        spec=AtlasLabelPlateSpec(
            corner_radius_mm=0.0,
        ),
    )

    assert mesh["type"] == "label_plate"
    assert mesh["width_mm"] == pytest.approx(118.0)
    assert mesh["height_mm"] == pytest.approx(9.0)
    assert mesh["depth_mm"] == pytest.approx(1.2)
    assert len(mesh["triangles"]) == 12

    vertices = _all_vertices(mesh)

    assert min(x for x, _, _ in vertices) == pytest.approx(-59.0)
    assert max(x for x, _, _ in vertices) == pytest.approx(59.0)
    assert min(y for _, y, _ in vertices) == pytest.approx(-4.5)
    assert max(y for _, y, _ in vertices) == pytest.approx(4.5)
    assert min(z for _, _, z in vertices) == pytest.approx(0.0)
    assert max(z for _, _, z in vertices) == pytest.approx(1.2)

def test_label_plate_mesher_builds_closed_rounded_prism():
    mesh = AtlasLabelPlateMesher.build(
        spec=AtlasLabelPlateSpec(
            width_mm=118.0,
            height_mm=9.0,
            depth_mm=1.2,
            corner_radius_mm=2.0,
        ),
    )

    assert mesh["type"] == "label_plate"
    assert mesh["corner_radius_mm"] == pytest.approx(2.0)

    vertices = _all_vertices(mesh)

    assert min(x for x, _, _ in vertices) == pytest.approx(-59.0)
    assert max(x for x, _, _ in vertices) == pytest.approx(59.0)
    assert min(y for _, y, _ in vertices) == pytest.approx(-4.5)
    assert max(y for _, y, _ in vertices) == pytest.approx(4.5)
    assert min(z for _, _, z in vertices) == pytest.approx(0.0)
    assert max(z for _, _, z in vertices) == pytest.approx(1.2)

    sharp_corners = {
        (-59.0, -4.5),
        (59.0, -4.5),
        (59.0, 4.5),
        (-59.0, 4.5),
    }

    xy_vertices = {
        (
            round(float(x), 6),
            round(float(y), 6),
        )
        for x, y, _ in vertices
    }

    assert sharp_corners.isdisjoint(xy_vertices)
    assert len(mesh["triangles"]) > 12

    topology = AtlasMeshValidator._topology_report(mesh)

    assert topology["open_edge_count"] == 0
    assert topology["non_manifold_edge_count"] == 0
